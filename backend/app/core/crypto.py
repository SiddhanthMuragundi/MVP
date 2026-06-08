"""Encryption of stored LLM API keys using AES-256-GCM.

The key is reversible on purpose: the plaintext provider key has to be sent to
OpenAI/Anthropic/Gemini on every call, so it cannot be a one-way hash. Each
encryption uses a fresh random 12-byte nonce, stored alongside the ciphertext.
"""
from __future__ import annotations

import base64
import hashlib
import os

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from ..config import settings

_NONCE_BYTES = 12


def _load_key() -> bytes:
    raw = settings.ENCRYPTION_KEY or "tdc-dev-insecure-encryption-key"
    try:
        decoded = base64.b64decode(raw)
        if len(decoded) == 32:
            return decoded
    except Exception:
        pass
    # Not a 32-byte base64 value: derive a stable 32-byte key (dev convenience).
    return hashlib.sha256(raw.encode()).digest()


_KEY = _load_key()


def encrypt_key(plaintext: str) -> str:
    nonce = os.urandom(_NONCE_BYTES)
    ciphertext = AESGCM(_KEY).encrypt(nonce, plaintext.encode(), None)
    return base64.b64encode(nonce + ciphertext).decode()


def decrypt_key(blob: str) -> str:
    data = base64.b64decode(blob)
    nonce, ciphertext = data[:_NONCE_BYTES], data[_NONCE_BYTES:]
    return AESGCM(_KEY).decrypt(nonce, ciphertext, None).decode()


def mask_key(plaintext: str) -> str:
    """Return a display-safe hint like ``sk-…a1b2`` — never the full key."""
    if not plaintext:
        return ""
    prefix = plaintext[:3]
    tail = plaintext[-4:] if len(plaintext) >= 4 else plaintext
    return f"{prefix}…{tail}"
