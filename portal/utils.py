import jwt
from datetime import datetime, timedelta, timezone
from cryptography.fernet import Fernet
from django.conf import settings

def get_cipher():
    return Fernet(settings.ENCRYPTION_KEY)

def encrypt_data(text):
    if not text:
        return text
    if str(text).startswith('gAAAAA'):
        return text
    cipher = get_cipher()
    return cipher.encrypt(str(text).encode('utf-8')).decode('utf-8')

def decrypt_data(encrypted_text):
    if not encrypted_text or not str(encrypted_text).startswith('gAAAAA'):
        return encrypted_text
    cipher = get_cipher()
    try:
        return cipher.decrypt(encrypted_text.encode('utf-8')).decode('utf-8')
    except Exception:
        return "Decryption Error"

# --- JWT LOGIC UPDATED FOR EMAIL ---
def generate_jwt(email):
    payload = {
        'email': email,
        'exp': datetime.now(timezone.utc) + timedelta(minutes=15),
        'iat': datetime.now(timezone.utc)
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')

def verify_jwt(token):
    if not token:
        return None
    try:
        decoded_payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        return decoded_payload.get('email')
    except jwt.ExpiredSignatureError:
        return None 
    except jwt.InvalidTokenError:
        return None