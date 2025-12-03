import builtins
builtins.long = int
from secretsharing import SecretSharer

def split_secret(secret_hex):
    return SecretSharer.split_secret(secret_hex, 2, 2)

def combine_shares(shares):
    return SecretSharer.recover_secret(shares)


