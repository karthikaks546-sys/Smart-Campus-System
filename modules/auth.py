"""
modules/auth.py
Simple authentication support for the Smart Campus app.
"""
import hashlib


def hash_password(password: str) -> str:
    """Return a stable hash for the given password."""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def verify_password(password: str, stored_hash: str) -> bool:
    """Verify a password against a stored hash."""
    return hash_password(password) == stored_hash
