import base64
import os

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from dotenv import load_dotenv

from .constants import IV_LENGTH

load_dotenv()

ENCRYPTION_KEY_BASE64 = os.getenv("ENCRYPTION_KEY")

def encrypt_private_key(private_key: str) -> str:
    if not ENCRYPTION_KEY_BASE64:
        raise ValueError("Encryption key not found in environment variables. Set ENCRYPTION_KEY.")
    
    encryption_key = base64.b64decode(ENCRYPTION_KEY_BASE64)

    iv = os.urandom(IV_LENGTH)

    cipher = Cipher(algorithms.AES(encryption_key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()

    padding_length = 16 - (len(private_key) % 16)
    padded_private_key = private_key + (chr(padding_length) * padding_length)

    encrypted = encryptor.update(padded_private_key.encode()) + encryptor.finalize()

    return base64.b64encode(iv + encrypted).decode()
