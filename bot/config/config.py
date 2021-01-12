import os


class config:
    BOT_TOKEN = os.environ.get("BOT_TOKEN")
    API_HASH = os.environ.get("API_HASH")
    API_ID = int(os.environ.get("API_ID"))
    LOG_CHANNEL = int(os.environ.get("LOG_CHANNEL", 0))
    MAX_TIME_TO_SOLVE = int(os.environ.get("MAX_TIME_TO_SOLVE", 120))  # SECONDS
    KICK_TIME = int(os.environ.get("KICK_TIME", 4))  # hours
    HCAPTCHA_API = os.environ.get("HCAPTCHA_API")
    FQDN = os.environ.get("FQDN", "http://192.168.8.100").rstrip('/')
