import hashlib
import base64
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.hashes import SHA256
from cryptography.fernet import Fernet
import string
import random

# Генерация ключа из мастер-пароля
def generate_key_from_password(password: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=SHA256(),
        length=32,  # Длина ключа для Fernet
        salt=salt,
        iterations=100_000,
    )
    return base64.urlsafe_b64encode(kdf.derive(password.encode()))

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, hashed_password: str) -> bool:
    return hash_password(password) == hashed_password

def encrypt_password(password: str, master_password: str, salt: bytes) -> str:
    key = generate_key_from_password(master_password, salt)
    cipher = Fernet(key)
    return cipher.encrypt(password.encode()).decode()

def decrypt_password(encrypted_password: str, master_password: str, salt: bytes) -> str:
    key = generate_key_from_password(master_password, salt)
    cipher = Fernet(key)
    return cipher.decrypt(encrypted_password.encode()).decode()

def generate_password(length=12):
    chars = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(random.choice(chars) for _ in range(length))
