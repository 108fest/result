import hashlib
import secrets


def hash_password(password: str) -> str:
    # MVP constraint from requirements: unsalted password hash.
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def verify_password(raw_password: str, password_hash: str) -> bool:
    return hash_password(raw_password) == password_hash


def generate_session_token() -> str:
    return secrets.token_urlsafe(48)
