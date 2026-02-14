"""
app.py — Streamlit web interface for Image Steganography
Run:  streamlit run app.py
"""

import streamlit as st
from PIL import Image
import io
import os
from steg_core import encode, decode, get_max_chars, LOSSY_EXTS, SUPPORTED

# ── Page config ───────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Image Steganography",
    page_icon="🔐",
    layout="centered",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────

st.markdown("""
<style>
    /* Page background */
    .stApp { background: #000000; }

    /* Cards */
    .card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem 2rem;
        margin-bottom: 1.2rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }

    /* Title */
    .main-title {
        text-align: center;
        font-size: 2.2rem;
        font-weight: 800;
        color: #1a202c;
        margin-bottom: 0;
    }
    .main-subtitle {
        text-align: center;
        color: #718096;
        font-size: 0.95rem;
        margin-bottom: 1.5rem;
    }

    /* Success / error banners */
    .success-box {
        background: #c6f6d5; border-left: 4px solid #38a169;
        border-radius: 8px; padding: 0.8rem 1rem;
        color: #22543d; margin-top: 0.8rem;
    }
    .error-box {
        background: #fed7d7; border-left: 4px solid #e53e3e;
        border-radius: 8px; padding: 0.8rem 1rem;
        color: #742a2a; margin-top: 0.8rem;
    }
    .warn-box {
        background: #fefcbf; border-left: 4px solid #d69e2e;
        border-radius: 8px; padding: 0.8rem 1rem;
        color: #744210; margin-top: 0.4rem; margin-bottom: 0.4rem;
    }
    .info-box {
        background: #bee3f8; border-left: 4px solid #3182ce;
        border-radius: 8px; padding: 0.8rem 1rem;
        color: #2a4365; margin-top: 0.4rem;
    }

    /* Capacity badge */
    .cap-badge {
        display: inline-block;
        background: #ebf8ff; color: #2b6cb0;
        border-radius: 20px; padding: 3px 12px;
        font-size: 0.85rem; font-weight: 600;
        margin-top: 6px;
    }

    /* Hide Streamlit branding */
    #MainMenu, footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ── Title ─────────────────────────────────────────────────────────────────────

st.markdown('<p class="main-title">🔐 Image Steganography</p>', unsafe_allow_html=True)
st.markdown(
    '<p class="main-subtitle">Hide secret messages inside images using LSB steganography</p>',
    unsafe_allow_html=True)

# ── Mode tabs ─────────────────────────────────────────────────────────────────

tab_encode, tab_decode, tab_code = st.tabs([
    "🔒  Encode — Hide a Message",
    "🔓  Decode — Extract a Message",
    "💻  Source Code",
])

# ═══════════════════════════════════════════════════════════════════════════════
# ENCODE TAB
# ═══════════════════════════════════════════════════════════════════════════════

with tab_encode:

    st.markdown("### Step 1 — Upload your image")
    uploaded = st.file_uploader(
        "Supported formats: PNG, BMP, TIFF, WebP, JPG",
        type=["png", "bmp", "jpg", "jpeg", "tiff", "tif", "webp"],
        key="enc_upload",
        label_visibility="collapsed",
    )

    if uploaded:
        ext = os.path.splitext(uploaded.name)[1].lower()
        is_lossy = ext in LOSSY_EXTS

        # Show preview + capacity
        img = Image.open(uploaded)
        col_img, col_info = st.columns([1, 1])

        with col_img:
            st.image(img, caption=uploaded.name, use_container_width=True)

        with col_info:
            w, h = img.size
            max_chars = get_max_chars(w * h)
            st.markdown(f"""
            <div style="padding-top:10px">
                <b>File:</b> {uploaded.name}<br>
                <b>Size:</b> {w} × {h} px<br>
                <b>Format:</b> {'JPEG → will save as PNG ⚠' if is_lossy else ext.upper().lstrip('.')}<br>
                <span class="cap-badge">📊 Capacity: up to {max_chars:,} characters</span>
            </div>
            """, unsafe_allow_html=True)

            if is_lossy:
                st.markdown(
                    '<div class="warn-box">⚠ JPEG is lossy. Your image will be saved '
                    'as <b>PNG</b> to preserve the hidden data.</div>',
                    unsafe_allow_html=True)

        st.divider()
        st.markdown("### Step 2 — Type your secret message")

        message = st.text_area(
            "Secret message",
            height=140,
            placeholder="Type anything here — only people with this app and the password can read it.",
            label_visibility="collapsed",
        )

        # Live character counter
        char_count = len(message)
        if char_count > 0:
            pct   = char_count / max_chars
            color = "#e53e3e" if pct > 1 else ("#d69e2e" if pct > 0.85 else "#38a169")
            st.markdown(
                f'<p style="text-align:right; color:{color}; font-size:0.85rem; margin:0">'
                f'{char_count:,} / {max_chars:,} characters</p>',
                unsafe_allow_html=True)

        st.divider()
        st.markdown("### Step 3 — Password *(optional)*")
        password = st.text_input(
            "Password",
            type="password",
            placeholder="Leave blank for no encryption",
            label_visibility="collapsed",
        )
        if password:
            st.markdown(
                '<div class="info-box">🔑 Message will be XOR-encrypted. '
                'The same password is needed to decode it.</div>',
                unsafe_allow_html=True)

        st.divider()
        st.markdown("### Step 4 — Encode & Download")

        if st.button("🔒  Encode Message", type="primary", use_container_width=True):
            if not message.strip():
                st.markdown(
                    '<div class="error-box">✗ Please type a message before encoding.</div>',
                    unsafe_allow_html=True)
            elif char_count > max_chars:
                st.markdown(
                    f'<div class="error-box">✗ Message too long '
                    f'({char_count:,} chars). Max for this image: {max_chars:,}.</div>',
                    unsafe_allow_html=True)
            else:
                with st.spinner("Encoding…"):
                    uploaded.seek(0)
                    img = Image.open(uploaded)
                    success, info, png_bytes = encode(img, message.strip(), password)

                if success:
                    stem = os.path.splitext(uploaded.name)[0]
                    out_name = stem + "_encoded.png"

                    st.markdown(
                        f'<div class="success-box">✓ {info}</div>',
                        unsafe_allow_html=True)

                    st.download_button(
                        label="⬇  Download Encoded Image",
                        data=png_bytes,
                        file_name=out_name,
                        mime="image/png",
                        use_container_width=True,
                    )

                    # Show side-by-side comparison
                    st.markdown("#### Original vs Encoded")
                    c1, c2 = st.columns(2)
                    uploaded.seek(0)
                    c1.image(Image.open(uploaded), caption="Original", use_container_width=True)
                    c2.image(Image.open(io.BytesIO(png_bytes)), caption="Encoded (looks identical)", use_container_width=True)
                else:
                    st.markdown(
                        f'<div class="error-box">✗ {info}</div>',
                        unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# DECODE TAB
# ═══════════════════════════════════════════════════════════════════════════════

with tab_decode:

    st.markdown("### Step 1 — Upload the encoded image")
    uploaded_dec = st.file_uploader(
        "Upload the encoded image (must be PNG, BMP, TIFF, or WebP — not JPEG)",
        type=["png", "bmp", "tiff", "tif", "webp"],
        key="dec_upload",
        label_visibility="collapsed",
    )

    if uploaded_dec:
        img_dec = Image.open(uploaded_dec)
        w, h    = img_dec.size

        col1, col2 = st.columns([1, 1])
        with col1:
            st.image(img_dec, caption=uploaded_dec.name, use_container_width=True)
        with col2:
            st.markdown(f"""
            <div style="padding-top:10px">
                <b>File:</b> {uploaded_dec.name}<br>
                <b>Size:</b> {w} × {h} px<br>
                <b>Format:</b> {os.path.splitext(uploaded_dec.name)[1].upper().lstrip('.')}
            </div>
            """, unsafe_allow_html=True)

        st.divider()
        st.markdown("### Step 2 — Password *(if one was used)*")
        password_dec = st.text_input(
            "Password",
            type="password",
            placeholder="Leave blank if no password was used",
            label_visibility="collapsed",
            key="dec_pwd",
        )

        st.divider()
        st.markdown("### Step 3 — Decode")

        if st.button("🔓  Decode Message", type="primary", use_container_width=True):
            with st.spinner("Decoding…"):
                uploaded_dec.seek(0)
                img_dec = Image.open(uploaded_dec)
                success, result = decode(img_dec, password_dec)

            if success:
                st.markdown(
                    '<div class="success-box">✓ Message decoded successfully!</div>',
                    unsafe_allow_html=True)
                st.markdown("#### Hidden Message")
                st.text_area(
                    "Result",
                    value=result,
                    height=180,
                    label_visibility="collapsed",
                )
                # Copy button via download (Streamlit doesn't have a native clipboard API)
                st.download_button(
                    "⬇  Save message as .txt",
                    data=result.encode("utf-8"),
                    file_name="decoded_message.txt",
                    mime="text/plain",
                )
            else:
                st.markdown(
                    f'<div class="error-box">✗ {result}</div>',
                    unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# SOURCE CODE TAB
# ═══════════════════════════════════════════════════════════════════════════════

with tab_code:

    st.markdown("## 💻 Source Code")
    st.markdown(
        "This is the original **desktop application** code (built with Python + Tkinter) "
        "that this web app is based on. The web version uses the same core logic.")

    st.divider()

    # ── Section 1: Constants & Imports ──────────────────────────────────────
    st.markdown("### 📦 Imports & Constants")
    st.markdown(
        "We import **Pillow** for image handling and **Tkinter** for the desktop GUI. "
        "The `TERMINATOR` is a sequence of 5 null bytes appended to the end of every "
        "hidden message so the decoder knows where the message ends.")
    st.code('''import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image

TERMINATOR = b\'\\x00\\x00\\x00\\x00\\x00\'  # 5 null bytes — safe end-of-message marker

SUPPORTED_READ = {
    ".bmp": "BMP", ".png": "PNG",
    ".jpg": "JPEG", ".jpeg": "JPEG",
    ".tiff": "TIFF", ".tif": "TIFF", ".webp": "WebP",
}
LOSSY_EXTS = {".jpg", ".jpeg"}''', language="python")

    st.divider()

    # ── Section 2: XOR Cipher ───────────────────────────────────────────────
    st.markdown("### 🔑 XOR Encryption")
    st.markdown(
        "XOR encryption works by combining each byte of the message with a byte from "
        "the password key. The same function is used to both **encrypt** and **decrypt** "
        "— XORing twice with the same key restores the original data.")
    st.code('''def xor_cipher(data: bytes, key: str) -> bytes:
    """XOR-encrypt or decrypt raw bytes with a string key."""
    if not key:
        return data
    key_bytes = key.encode("utf-8")
    return bytes(b ^ key_bytes[i % len(key_bytes)] for i, b in enumerate(data))''',
        language="python")

    st.divider()

    # ── Section 3: Capacity ─────────────────────────────────────────────────
    st.markdown("### 📊 Capacity Calculation")
    st.markdown(
        "Each pixel has 3 colour channels (Red, Green, Blue). We hide **1 bit** in the "
        "least significant bit (LSB) of each channel — so 3 bits per pixel. "
        "Every 8 bits = 1 character, giving us `pixels × 3 ÷ 8` characters of capacity.")
    st.code('''def get_max_chars(pixel_count: int) -> int:
    usable_bytes = (pixel_count * 3) // 8
    return usable_bytes - len(TERMINATOR)''', language="python")

    st.divider()

    # ── Section 4: Encode ───────────────────────────────────────────────────
    st.markdown("### 🔒 Encode Function — Hiding the Message")
    st.markdown(
        "The encode function converts the message to binary, then writes each bit into "
        "the **least significant bit** of each pixel channel value. Changing only the "
        "last bit means the colour changes by at most 1 out of 255 — completely invisible to the eye.")
    st.code('''def encode_image(image_path, secret_message, output_path, password=""):
    # Load image pixels via Pillow
    pixels, width, height = load_rgb_pixels(image_path)

    # Optionally encrypt with XOR, then add terminator
    raw = secret_message.encode("utf-8")
    if password:
        raw = xor_cipher(raw, password)
    payload = raw + TERMINATOR

    # Convert payload to a string of 1s and 0s
    bits = "".join(format(byte, "08b") for byte in payload)

    # Write each bit into the LSB of each pixel channel
    for i, bit in enumerate(bits):
        pixels[i] = (pixels[i] & 0xFE) | int(bit)
    #              ↑ clears last bit     ↑ sets it to our bit

    # Always save as PNG (lossless) to preserve the hidden bits
    save_pixels_as_png(pixels, width, height, output_path)''', language="python")

    st.divider()

    # ── Section 5: Decode ───────────────────────────────────────────────────
    st.markdown("### 🔓 Decode Function — Extracting the Message")
    st.markdown(
        "Decoding is the reverse: read the LSB from each pixel channel, collect 8 bits "
        "at a time to form a byte, and keep going until the 5 null-byte terminator is found.")
    st.code('''def decode_image(image_path, password=""):
    pixels, width, height = load_rgb_pixels(image_path)

    decoded = bytearray()
    bits = []

    for byte_val in pixels:
        bits.append(byte_val & 1)      # extract the last bit
        if len(bits) == 8:
            decoded.append(int("".join(str(b) for b in bits), 2))
            bits = []
            # Stop as soon as we find the terminator
            if decoded[-5:] == b\'\\x00\\x00\\x00\\x00\\x00\':
                raw = bytes(decoded[:-5])
                if password:
                    raw = xor_cipher(raw, password)
                return True, raw.decode("utf-8")

    return False, "No hidden message found."''', language="python")

    st.divider()

    # ── Section 6: Full code expander ───────────────────────────────────────
    st.markdown("### 📄 Full Desktop App Code")
    st.markdown("Expand below to see the complete original source code including the Tkinter GUI.")

    with st.expander("Click to show full code"):
        st.code('''"""
Image Steganography Tool
Supports: PNG, BMP, TIFF, WebP  (lossless — data is preserved)
          JPG / JPEG             (lossy — auto-converted to PNG before encoding)

Requires: Pillow  →  pip install Pillow
"""

import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image

TERMINATOR = b\'\\x00\\x00\\x00\\x00\\x00\'

SUPPORTED_READ = {
    ".bmp": "BMP", ".png": "PNG",
    ".jpg": "JPEG", ".jpeg": "JPEG",
    ".tiff": "TIFF", ".tif": "TIFF", ".webp": "WebP",
}
LOSSLESS_EXTS = {".bmp", ".png", ".tiff", ".tif", ".webp"}
LOSSY_EXTS    = {".jpg", ".jpeg"}


def xor_cipher(data: bytes, key: str) -> bytes:
    if not key:
        return data
    key_bytes = key.encode("utf-8")
    return bytes(b ^ key_bytes[i % len(key_bytes)] for i, b in enumerate(data))


def get_max_chars(pixel_count: int) -> int:
    return (pixel_count * 3) // 8 - len(TERMINATOR)


def detect_format(path: str):
    ext = os.path.splitext(path)[1].lower()
    if ext not in SUPPORTED_READ:
        return None, False, f"Unsupported type: {ext}"
    try:
        with Image.open(path) as img:
            img.verify()
    except Exception as e:
        return None, False, str(e)
    return ext, ext in LOSSY_EXTS, None


def load_rgb_pixels(path: str):
    with Image.open(path) as img:
        img = img.convert("RGB")
        return bytearray(img.tobytes()), img.width, img.height


def save_pixels_as_png(pixels, width, height, output_path):
    img = Image.frombytes("RGB", (width, height), bytes(pixels))
    img.save(output_path, format="PNG")


def encode_image(image_path, secret_message, output_path, password=""):
    ext, is_lossy, err = detect_format(image_path)
    if err:
        return False, err
    pixels, width, height = load_rgb_pixels(image_path)
    raw = secret_message.encode("utf-8")
    if password:
        raw = xor_cipher(raw, password)
    payload = raw + TERMINATOR
    bits = "".join(format(byte, "08b") for byte in payload)
    for i, bit in enumerate(bits):
        pixels[i] = (pixels[i] & 0xFE) | int(bit)
    save_pixels_as_png(pixels, width, height, output_path)
    return True, f"Encoded successfully! Saved to: {output_path}"


def decode_image(image_path, password=""):
    ext, _, err = detect_format(image_path)
    if err:
        return False, err
    if ext in LOSSY_EXTS:
        return False, "JPEG cannot be decoded."
    pixels, _, _ = load_rgb_pixels(image_path)
    decoded, bits = bytearray(), []
    for byte_val in pixels:
        bits.append(byte_val & 1)
        if len(bits) == 8:
            decoded.append(int("".join(str(b) for b in bits), 2))
            bits = []
            if decoded[-5:] == TERMINATOR:
                raw = bytes(decoded[:-5])
                if password:
                    raw = xor_cipher(raw, password)
                return True, raw.decode("utf-8")
    return False, "No hidden message found."


class SteganographyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Steganography Tool")
        self.root.geometry("660x660")
        # ... (full GUI code) ...


def main():
    root = tk.Tk()
    SteganographyApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
''', language="python")

# ── Footer ────────────────────────────────────────────────────────────────────

st.divider()
st.markdown(
    '<p style="text-align:center; color:#a0aec0; font-size:0.8rem">'
    'LSB Steganography · Built with Python & Streamlit · School Project</p>',
    unsafe_allow_html=True)
