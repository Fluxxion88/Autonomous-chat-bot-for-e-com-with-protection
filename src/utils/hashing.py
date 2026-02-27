import hashlib

def generate_hash(value: str) -> str:
    """
    Generate SHA-256 hash of a UTF-8 encoded string.
    """
    return hashlib.sha256(value.encode('utf-8')).hexdigest()
