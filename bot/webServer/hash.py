import hashlib
import hmac

from ..config import config


def checkHash(data_check_string: str, hashC: str) -> bool:
    if not hashC:
        return False
    m = hashlib.sha256()
    m.update(config.BOT_TOKEN.encode())
    secretKey = m.digest()
    if hmac.new(secretKey, data_check_string.encode(), hashlib.sha256).hexdigest() == hashC:
        return True
    return False


def getCheckString(argDict) -> str:
    return "\n".join(arg + '=' + argDict[arg] for arg in sorted(argDict) if arg != "hash")
