# pqcrypto/kyber_dilithium_stub.py
"""
Stubs for Kyber (KEM) and Dilithium (signature).
Replace with real liboqs/pyoqs or wasm implementations.
"""

import os
import base64
from typing import Tuple

# For prototype we use simple symmetric key approach.
# In production, use liboqs / pyoqs:
#  - Kyber: encapsulate/decapsulate for confidentiality
#  - Dilithium: sign/verify for integrity

KYBER_PK_PATH = os.path.join(os.path.dirname(__file__), 'kyber_pub.bin')
KYBER_SK_PATH = os.path.join(os.path.dirname(__file__), 'kyber_priv.bin')

def get_kyber_public_bytes() -> bytes:
    # Prototype: return a fixed bytes blob; production should return real Kyber public key bytes
    if os.path.exists(KYBER_PK_PATH):
        return open(KYBER_PK_PATH, 'rb').read()
    pk = b'PROTOTYPE_KYBER_PUBLIC'
    with open(KYBER_PK_PATH, 'wb') as f: f.write(pk)
    with open(KYBER_SK_PATH, 'wb') as f: f.write(b'PROTOTYPE_KYBER_SECRET')
    return pk

def kyber_decapsulate_bytes(kem_ciphertext: bytes, enc_payload: bytes) -> bytes:
    """
    Prototype decapsulation: here we simply assume enc_payload is plaintext bytes.
    Production: decapsulate using Kyber private key to obtain a shared key, then decrypt enc_payload.
    """
    # In prototype, enc_payload is plaintext (not encrypted) -> return it.
    return enc_payload

def dilithium_verify_bytes(pubkey: bytes, message: bytes, signature: bytes) -> bool:
    """
    Prototype signature verification: in prototype we accept empty pubkey (always true)
    Production: use Dilithium verify function.
    """
    if not signature:
        return False
    # naive: accept any non-empty signature in prototype
    return True
