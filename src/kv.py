import hashlib

def to_key(b):
    return hashlib.md5(b).digest()

