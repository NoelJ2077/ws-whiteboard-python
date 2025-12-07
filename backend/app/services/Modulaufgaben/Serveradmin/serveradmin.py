from app.db.repository import Repository
from app.utils.logger import Logger
from datetime import datetime
from zoneinfo import ZoneInfo

Log = Logger(name="testlog")

async def serveradmin(client_id: str, msg: str="Error while passing usermessage!") -> str:
    """ // Start (Task 2) & // End -> Senden von Nachrichten an den Administrator (Ganzes Skript inkl Ordern Serveradmin/ ist Teil von Task2) """
    admin = await Repository.get_current_admin()
    tz = ZoneInfo("Europe/Zurich")
    timestamp = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S %Z")  # z.B. "2025-12-05 15:32:01 CET"

    if not admin:
        return f"[{timestamp} Error: no admin is set, can't send msg - contact administrator!"    
    elif admin == client_id:
        return f"[{timestamp}] From self(admin) msg: {msg}"
    else:
        return f"[{timestamp}] From client {client_id} msg: {msg}"
    