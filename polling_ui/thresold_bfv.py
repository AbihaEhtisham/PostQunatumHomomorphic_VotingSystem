#threshold_bfv.py
import tenseal as ts
from secretsharing import SecretSharer  # pip install secretsharing

# --- Create/load BFV context ---
bfv_ctx = ts.context(
    ts.SCHEME_TYPE.BFV,
    poly_modulus_degree=4096,
    plain_modulus=1032193
)
bfv_ctx.generate_galois_keys()
bfv_ctx.generate_relin_keys()

# --- Serialize BFV secret key to hex ---
ctx_full_bytes = bfv_ctx.serialize(save_secret_key=True)
bfv_hex = ctx_full_bytes.hex()

# --- Split BFV key using Shamir (2-of-2 example) ---
shares = SecretSharer.split_secret(bfv_hex, 2, 2)
print("Key Shares:")
for i, share in enumerate(shares):
    print(f"Share {i+1}: {share}")

# --- Reconstruct BFV key ---
recovered_hex = SecretSharer.recover_secret(shares)
recovered_bytes = bytes.fromhex(recovered_hex)

# --- Load recovered key into new BFV context ---
bfv_ctx2 = ts.context_from(recovered_bytes)
print("Reconstruction successful:", bfv_ctx2 is not None)
