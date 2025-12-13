# dilithium_stub.py
import base64
import hashlib
from dilithium_py.dilithium import Dilithium2

# --- Dilithium Keygen ---
def generate_keys():
    pk, sk = Dilithium2.keygen()
    return sk, pk

sk, pk = generate_keys()
print("SK len:", len(sk), "PK len:", len(pk))

# --- Sign arbitrary data bytes ---
def sign_bytes(sk, data_bytes):
    return Dilithium2.sign(sk, data_bytes)


# --- Verify signature ---
def verify_bytes(pk, data_bytes, signature):
    return Dilithium2.verify(pk, data_bytes, signature)


# --- Hash for vote receipts ---
def receipt_hash(enc_bytes, signature):
    h = hashlib.sha3_256()
    h.update(enc_bytes + signature)
    return h.hexdigest()


# --- Base64 helpers (for DB storage) ---
def b64encode_bytes(b):
    return base64.b64encode(b).decode()


def b64decode_str(s):
    return base64.b64decode(s)
