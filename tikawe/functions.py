import hashlib
import secrets

def hashit(pwd: str) -> str:
    return hashlib.sha3_256(pwd.encode('utf-8')).hexdigest()

def token(user_ids: list) -> int:
    while True:
        token = secrets.randbelow(16777216)
        for i in user_ids:
            if i[0] == token:
                continue
        return token