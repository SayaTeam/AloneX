# ALONE-CODER
from os import getenv
from dotenv import load_dotenv

load_dotenv()

def get_int(key: str, default: int = 0) -> int:
    val = getenv(key, "").strip()
    if not val:
        return default
    try:
        return int(val)
    except ValueError:
        return default

class Config:
    def __init__(self):
        self.API_ID = get_int("API_ID", 17596251)
        self.API_HASH = getenv("API_HASH", "e58343b4c0193e293e391daf97603fcd")

        self.BOT_TOKEN = getenv("BOT_TOKEN", "")
        self.MONGO_URL = getenv("MONGO_URL", "")

        self.LOGGER_ID = get_int("LOGGER_ID", 0)
        self.OWNER_ID = get_int("OWNER_ID", 0)
        
        session1 = getenv("SESSION", getenv("SESSION1", ""))
        self.SESSION1 = session1 if session1 and session1 != "?" else ""
        self.SESSION2 = getenv("SESSION2", None)
        self.SESSION3 = getenv("SESSION3", None)

        self.PORT = get_int("PORT", 8080)

        self.SUPPORT_CHANNEL = getenv("SUPPORT_CHANNEL", "https://t.me/ErrorQuote")
        self.SUPPORT_CHAT = getenv("SUPPORT_CHAT", "https://t.me/ErrorQuote")

        self.AUTO_END: bool = getenv("AUTO_END", "False").lower() in ("true", "1", "t", "yes")
        self.AUTO_LEAVE: bool = getenv("AUTO_LEAVE", "False").lower() in ("true", "1", "t", "yes")
        self.VIDEO_PLAY: bool = getenv("VIDEO_PLAY", "True").lower() in ("true", "1", "t", "yes")

        self.QUEUE_LIMIT = get_int("QUEUE_LIMIT", 500000000)
        self.DURATION_LIMIT = get_int("DURATION_LIMIT", 5400000000)
        self.PLAYLIST_LIMIT = get_int("PLAYLIST_LIMIT", 20000000000)
        self.COOKIES_URL = [
            url for url in getenv("COOKIES_URL", "").split(" ")
            if url and "batbin.me" in url
        ]
        self.DEFAULT_THUMB = getenv("DEFAULT_THUMB", "https://files.catbox.moe/pd8fv9.jpg")
        self.PING_IMG = getenv("PING_IMG", "https://files.catbox.moe/pd8fv9.jpg")
        self.START_IMG = getenv("START_IMG", "https://files.catbox.moe/pd8fv9.jpg")

    def check(self):
        missing = [
            var
            for var in ["API_ID", "API_HASH", "BOT_TOKEN", "MONGO_URL", "LOGGER_ID", "OWNER_ID", "SESSION1"]
            if not getattr(self, var) or getattr(self, var) in ["?", 0, "0", "Apna Bot Token", "Apna Mongo Db Dalo"]
        ]
        if missing:
            raise SystemExit(f"Missing or invalid required environment variables: {', '.join(missing)}")
