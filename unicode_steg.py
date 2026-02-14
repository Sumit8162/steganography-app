"""
unicode_steg.py — Hide secret messages inside normal-looking text
using invisible Unicode zero-width characters.

Works through Messenger, WhatsApp, Telegram — any platform that transmits
text without stripping Unicode characters (i.e. all major chat apps).

How it works:
  bit 0  →  U+200B  ZERO WIDTH SPACE
  bit 1  →  U+200C  ZERO WIDTH NON-JOINER
  The payload is wrapped with START/END markers and includes a 2-byte
  checksum so wrong passwords are detected reliably.
"""

import hashlib

# ── Invisible character constants ─────────────────────────────────────────────

ZERO   = '\u200B'   # bit 0
ONE    = '\u200C'   # bit 1
START  = '\uFEFF'   # payload start marker
END    = '\u200D'   # payload end marker
INVISIBLE = {ZERO, ONE, START, END}

# ── Helpers ───────────────────────────────────────────────────────────────────

def xor_cipher(data: bytes, key: str) -> bytes:
    if not key:
        return data
    kb = key.encode('utf-8')
    return bytes(b ^ kb[i % len(kb)] for i, b in enumerate(data))


def _checksum(data: bytes) -> bytes:
    """2-byte checksum so we can detect wrong passwords."""
    return hashlib.md5(data).digest()[:2]


def strip_invisible(text: str) -> str:
    """Return only the visible characters."""
    return ''.join(ch for ch in text if ch not in INVISIBLE)


def has_hidden_message(text: str) -> bool:
    return START in text and END in text


# ── Encode ────────────────────────────────────────────────────────────────────

def encode_text(cover_text: str, secret: str, password: str = "") -> tuple:
    """
    Hide `secret` inside `cover_text`.
    Returns (True, steg_text) or (False, error_message).
    """
    if not cover_text.strip():
        return False, "Cover text cannot be empty."
    if not secret.strip():
        return False, "Secret message cannot be empty."

    raw = secret.encode('utf-8')

    # Prepend 2-byte checksum of the plaintext so we can verify on decode
    checksum = _checksum(raw)
    payload  = checksum + raw

    # Optionally encrypt (checksum is also encrypted so wrong pwd fails cleanly)
    if password:
        payload = xor_cipher(payload, password)

    # Convert to invisible chars
    bits      = ''.join(format(byte, '08b') for byte in payload)
    invisible = START + ''.join(ONE if b == '1' else ZERO for b in bits) + END

    # Insert after first character
    result = cover_text[0] + invisible + cover_text[1:]
    return True, result


# ── Decode ────────────────────────────────────────────────────────────────────

def decode_text(steg_text: str, password: str = "") -> tuple:
    """
    Extract a hidden message.
    Returns (True, message) or (False, error_message).
    """
    start_idx = steg_text.find(START)
    end_idx   = steg_text.find(END)

    if start_idx == -1 or end_idx == -1 or end_idx <= start_idx:
        return False, "No hidden message found in this text."

    hidden_chars = steg_text[start_idx + 1 : end_idx]

    bits = ''
    for ch in hidden_chars:
        if ch == ONE:
            bits += '1'
        elif ch == ZERO:
            bits += '0'

    if not bits or len(bits) % 8 != 0:
        return False, "Hidden data is corrupted or incomplete."

    payload = bytes(int(bits[i:i+8], 2) for i in range(0, len(bits), 8))

    # Decrypt if password given
    if password:
        payload = xor_cipher(payload, password)

    # Verify checksum (first 2 bytes)
    if len(payload) < 3:
        return False, "Hidden data is too short — possibly corrupted."

    stored_checksum = payload[:2]
    raw             = payload[2:]

    if _checksum(raw) != stored_checksum:
        return False, (
            "Wrong password — the message could not be unlocked.\n"
            "Make sure you're using the same password that was used to hide it."
        )

    try:
        return True, raw.decode('utf-8')
    except UnicodeDecodeError:
        return False, "Could not decode — message may be corrupted."
