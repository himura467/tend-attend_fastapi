import os

from dotenv import load_dotenv

load_dotenv()

_FRONTEND_URLS = os.getenv("FRONTEND_URLS")
assert _FRONTEND_URLS, "FRONTEND_URLS environment variable must be set"
ALLOWED_ORIGINS = _FRONTEND_URLS.split(",")
COOKIE_DOMAIN = os.getenv("COOKIE_DOMAIN")

ACCESS_TOKEN_NAME = "acctkn"
REFRESH_TOKEN_NAME = "reftkn"
