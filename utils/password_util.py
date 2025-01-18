from passlib.context import CryptContext
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.fernet import Fernet
import base64
import string
import os
import secrets

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Генерация ключа из мастер-пароля
def generate_key_from_password(password: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,  # Длина ключа для Fernet
        salt=salt,
        iterations=500_000,
        backend=default_backend()
    )
    return base64.urlsafe_b64encode(kdf.derive(password.encode()))

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(password: str, hashed_password: str) -> bool:
    return pwd_context.verify(password, hashed_password)

def encrypt_password(password: str, master_password: str, salt: bytes) -> str:
    key = generate_key_from_password(master_password, salt)
    cipher = Fernet(key)
    return cipher.encrypt(password.encode()).decode()

def decrypt_password(encrypted_password: str, master_password: str, salt: bytes) -> str:
    key = generate_key_from_password(master_password, salt)
    cipher = Fernet(key)
    return cipher.decrypt(encrypted_password.encode()).decode()

def generate_salt() -> bytes:
    return os.urandom(32)

def encode_salt(salt: bytes) -> str:
    return base64.b64encode(salt).decode()

def decode_salt(salt: str) -> bytes:
    return base64.b64decode(salt)

def generate_password(length=12):

    current_length = length
    # Множество символов для пароля
    lowercase = string.ascii_lowercase
    uppercase = string.ascii_uppercase
    digits = string.digits
    punctuation = "!@#$%^&*()-_=+[]{}|;:,.<>?/~"

    # Проверка на минимальную длину для безопасного пароля
    if length < 12:
        current_length = 12

    # Составляем обязательные части пароля
    password = [
        secrets.choice(lowercase),
        secrets.choice(uppercase),
        secrets.choice(digits),
        secrets.choice(punctuation),
    ]

    # Заполняем оставшуюся длину случайными символами из всех категорий
    all_chars = lowercase + uppercase + digits + punctuation
    password += [secrets.choice(all_chars) for _ in range(current_length - 4)]

    # Перемешиваем пароль, чтобы символы шли в случайном порядке
    secrets.SystemRandom().shuffle(password)

    # Преобразуем список в строку и возвращаем пароль
    return ''.join(password)
