import os
import tenseal as ts
from secretsharing import PlaintextToHexSecretSharer

BFV_CTX_FILE = "bfv_context.ctx"

# --- Create or load BFV context ---
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

# --- Serialize and split secret key ---
bfv_hex = ctx.serialize(save_secret_key=True).hex()
shares = PlaintextToHexSecretSharer.split_secret(bfv_hex, 2, 2)

# --- Print / save shares ---
print("Agent 1 share:", shares[0])
print("Agent 2 share:", shares[1])

with open("share1.txt", "w") as f:
    f.write(shares[0])

with open("share2.txt", "w") as f:
    f.write(shares[1])
