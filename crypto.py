# crypto.py
import tenseal as ts
from dilithium_py.dilithium import Dilithium2
import hashlib
import base64
import os

BFV_CTX_FILE = "bfv_ctx.ctx"

# ---- BFV setup ----
def load_or_create_bfv_context():
    if os.path.exists(BFV_CTX_FILE):
        with open(BFV_CTX_FILE, "rb") as f:
            ctx = ts.context_from(f.read())
    else:
        ctx = ts.context(
            ts.SCHEME_TYPE.BFV,
            poly_modulus_degree=8192,
            plain_modulus=1032193
        )
        ctx.generate_galois_keys()
        ctx.generate_relin_keys()
        with open(BFV_CTX_FILE, "wb") as f:
            f.write(ctx.serialize(save_secret_key=True))
    return ctx

# Encrypt a vote (integer 0-4 for candidate)
def encrypt_vote(context, vec):
    if not isinstance(vec, list):                   # vec must be a list          
        raise ValueError("Input must be a list")
    enc_vec = ts.bfv_vector(context, vec)
    return enc_vec.serialize()                       # returns bytes

# Decrypt BFV ciphertext
def decrypt_vote(context, enc_bytes):
    enc_vec = ts.bfv_vector_from(context, enc_bytes)
    return enc_vec.decrypt()[0]

# Dilithium per-voter keygen
def generate_keys():
    pk, sk = Dilithium2.keygen()
    return pk, sk

# Sign arbitrary bytes
def sign_bytes(sk, data_bytes):
    return Dilithium2.sign(sk, data_bytes)

# Verify signature
def verify_bytes(pk, data_bytes, signature):
    return Dilithium2.verify(pk, data_bytes, signature)

# Generate vote receipt hash
def receipt_hash(enc_bytes, signature):
    h = hashlib.sha3_256()
    h.update(enc_bytes + signature)
    return h.hexdigest()

# Helper to base64 encode/decode for DB storage
def b64encode_bytes(b):
    return base64.b64encode(b).decode()

def b64decode_str(s):
    return base64.b64decode(s)