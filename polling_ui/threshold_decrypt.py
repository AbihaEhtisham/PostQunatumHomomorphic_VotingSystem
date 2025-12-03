def load_threshold_bfv_context():
    share1 = open("share1.txt").read().strip()
    share2 = open("share2.txt").read().strip()

    recovered_hex = SecretSharer.recover_secret([share1, share2])
    recovered_bytes = bytes.fromhex(recovered_hex)

    ctx = ts.context_from(recovered_bytes)  # full secret key restored
    return ctx
