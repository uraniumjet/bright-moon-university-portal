"""
The Bright Moon University - Core Security Engine
File: core/security.py
Description: Manages secure password hashing and verification using native hashlib SHA-256.
"""

import hashlib

# Static cryptographic salt pepper to reinforce security strings across the platform
SYSTEM_SALT = "BrightMoonUniversity_Secret_Salt_Token_2026"

def hash_password(password: str) -> str:
    """
    Transforms raw text inputs into an isolated, secure hex digest hash 
    using SHA-256 with an appended salt string.
    """
    salted_password = password + SYSTEM_SALT
    return hashlib.sha256(salted_password.encode('utf-8')).hexdigest()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies a login attempt password string against its stored hash pattern match.
    """
    return hash_password(plain_password) == hashed_password