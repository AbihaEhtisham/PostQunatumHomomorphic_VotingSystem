# bfv.py
import builtins
builtins.long = int
import tenseal as ts
import os
from secretsharing import SecretSharer


# set BASE_DIR to the directory of this file if not defined elsewhere
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

BFV_CTX_FILE = os.path.join(BASE_DIR, "bfv_context.ctx")
# SHARE1_FILE = os.path.join(BASE_DIR, "share1.txt")
# SHARE2_FILE = os.path.join(BASE_DIR, "share2.txt")

"""def load_or_create_bfv_context():
    shares = None
    if os.path.exists(BFV_CTX_FILE):
        with open(BFV_CTX_FILE, "rb") as f:
            ctx = ts.context_from(f.read())
        shares = None
    else:
        ctx = ts.context(
            ts.SCHEME_TYPE.BFV,
            poly_modulus_degree=8192,
            plain_modulus=1032193
        )
        ctx.generate_galois_keys()
        ctx.generate_relin_keys()
        # ⚠️ Save WITHOUT SECRET KEY
        with open(BFV_CTX_FILE, "wb") as f:
            f.write(ctx.serialize(save_secret_key=False))  

        # ⚠️ Create SECRET KEY SHARES here
    if not os.path.exists(SHARE1_FILE) or not os.path.exists(SHARE2_FILE):
        full_bytes = ctx.serialize(save_secret_key=True)
        full_hex = full_bytes.hex()

        shares = SecretSharer.split_secret(full_hex, 2, 2)
        with open(SHARE1_FILE, "w") as f1, open(SHARE2_FILE, "w") as f2: 
           f1.write(shares[0]) 
           f2.write(shares[1])

    return ctx, shares"""

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
        # Save WITHOUT secret key
        with open(BFV_CTX_FILE, "wb") as f:
            f.write(ctx.serialize(save_secret_key=True))
    return ctx


def encrypt_vote(context, vec):
    if not isinstance(vec, list):
        raise ValueError("Input must be a list")
    enc_vec = ts.bfv_vector(context, vec)
    return enc_vec.serialize()


def decrypt_vote(context, enc_bytes):
    ctx = ts.context_from(secret_key_bytes)
    enc_vec = ts.bfv_vector_from(context, enc_bytes)
    return enc_vec.decrypt()

if __name__ == "__main__":
    ctx = load_or_create_bfv_context()
    print("BFV context loaded/created.")
    # If shares were created by load_or_create_bfv_context(), it returns them.
    """if shares is not None:
        print("Shares were just created:") 
        print("Agent 1 share:", shares[0]) 
        print("Agent 2 share:", shares[1])
    else:
        if os.path.exists(SHARE1_FILE) and os.path.exists(SHARE2_FILE):
          with open(SHARE1_FILE) as f1, open(SHARE2_FILE) as f2: 
            print("Shares already exist:") 
            print("Agent 1 share:", f1.read()) 
            print("Agent 2 share:", f2.read()) 
        else: 
            print("Shares files missing, you may need to delete bfv_context.ctx to recreate shares.")"""


