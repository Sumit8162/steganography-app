"""
steg_core.py — Pure steganography logic (no GUI, no file paths).
Works entirely with bytes/BytesIO so Streamlit can pass uploaded files directly.
"""

from PIL import Image
import io

# ── Constants ────────────────────────────────────────────────────────────────

TERMINATOR  = b'\x00\x00\x00\x00\x00'
LOSSY_EXTS  = {".jpg", ".jpeg"}
SUPPORTED   = {".png", ".bmp", ".jpg", ".jpeg", ".tiff", ".tif", ".webp"}

# ── Helpers ──────────────────────────────────────────────────────────────────

def xor_cipher(data: bytes, key: str) -> bytes:
    """XOR-encrypt / decrypt bytes with a string key."""
    if not key:
        return data
    kb = key.encode("utf-8")
    return bytes(b ^ kb[i % len(kb)] for i, b in enumerate(data))


def get_max_chars(pixel_count: int) -> int:
    """Max characters hideable: 3 bits per pixel (RGB), minus terminator."""
    return (pixel_count * 3) // 8 - len(TERMINATOR)


def image_to_rgb_pixels(img: Image.Image):
    """Strip alpha, return flat bytearray + (width, height)."""
    img = img.convert("RGB")
    return bytearray(img.tobytes()), img.width, img.height


def pixels_to_png_bytes(pixels: bytearray, width: int, height: int) -> bytes:
    """Reconstruct image from flat RGB bytearray → PNG bytes."""
    out = Image.frombytes("RGB", (width, height), bytes(pixels))
    buf = io.BytesIO()
    out.save(buf, format="PNG")
    return buf.getvalue()

# ── Encode ───────────────────────────────────────────────────────────────────

def encode(img: Image.Image, message: str, password: str = "") -> tuple[bool, str, bytes]:
    """
    Hide `message` in `img`.
    Returns (success, info_message, png_bytes).
    """
    pixels, w, h = image_to_rgb_pixels(img)
    max_chars = get_max_chars(w * h)

    raw = message.encode("utf-8")
    if password:
        raw = xor_cipher(raw, password)
    payload = raw + TERMINATOR

    if len(payload) > max_chars + len(TERMINATOR):
        return False, (
            f"Message too long. This image can hold up to "
            f"{max_chars:,} characters, but your message has "
            f"{len(message):,}."
        ), b""

    bits = "".join(format(byte, "08b") for byte in payload)
    for i, bit in enumerate(bits):
        pixels[i] = (pixels[i] & 0xFE) | int(bit)

    return True, f"Encoded {len(message):,} characters into a {w}×{h} image.", \
           pixels_to_png_bytes(pixels, w, h)

# ── Decode ───────────────────────────────────────────────────────────────────

def decode(img: Image.Image, password: str = "") -> tuple[bool, str]:
    """
    Extract a hidden message from `img`.
    Returns (success, message_or_error).
    """
    pixels, _, _ = image_to_rgb_pixels(img)

    decoded = bytearray()
    bits    = []

    for byte_val in pixels:
        bits.append(byte_val & 1)
        if len(bits) == 8:
            decoded.append(int("".join(str(b) for b in bits), 2))
            bits = []
            if (len(decoded) >= len(TERMINATOR) and
                    decoded[-len(TERMINATOR):] == TERMINATOR):
                raw = bytes(decoded[:-len(TERMINATOR)])
                if password:
                    raw = xor_cipher(raw, password)
                try:
                    return True, raw.decode("utf-8")
                except UnicodeDecodeError:
                    return False, (
                        "Could not decode the message.\n"
                        "Possible causes: wrong password, or no message was encoded here."
                    )

    return False, "No hidden message found in this image."
