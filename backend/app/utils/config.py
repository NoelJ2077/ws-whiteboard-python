# utils/config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Config():
    DB_HOST = os.environ["DB_HOST"]
    DB_PORT = int(os.environ["DB_PORT"])
    DB_USER = os.environ["DB_USER"]
    DB_PASSWORD = os.environ["DB_PASSWORD"]
    DB_NAME = os.environ["DB_NAME"]

    WS_HOST = os.environ["WS_HOST"]
    WS_PORT = int(os.environ["WS_PORT"])

    # For @server livelog
    ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL")
    ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD")

