from typing import Optional

from pydantic import BaseModel
from cryptography.fernet import Fernet


class HTTPKeyCredentials(BaseModel):
    key: str


class SessionData(BaseModel):
    pilot: Optional[str] = "Agricola"
    process: Optional[str] = None
    asset: Optional[str] = None



def encrypt(shkey, key):
    key_enc = key.encode()
    f = Fernet(shkey)
    encrypted = f.encrypt(key_enc)
    return encrypted

def decrypt(shkey, key):
    f = Fernet(shkey)
    decrypted = f.decrypt(key)