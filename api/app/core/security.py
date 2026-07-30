"""AES-256-GCM token encryption at rest (D-17)."""

from __future__ import annotations

import os

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from app.core.config import get_settings


def _aes_key() -> bytes:
    raw = get_settings().ENCRYPTION_KEY.encode()
    if len(raw) < 32:
        raw = raw.ljust(32, b"0")
    return raw[:32]


def encrypt_token(plain_text: str) -> str:
    aesgcm = AESGCM(_aes_key())
    nonce = os.urandom(12)
    ciphertext = aesgcm.encrypt(nonce, plain_text.encode(), None)
    return (nonce + ciphertext).hex()


def decrypt_token(cipher_text_hex: str) -> str:
    data = bytes.fromhex(cipher_text_hex)
    nonce = data[:12]
    ciphertext = data[12:]
    aesgcm = AESGCM(_aes_key())
    return aesgcm.decrypt(nonce, ciphertext, None).decode()
