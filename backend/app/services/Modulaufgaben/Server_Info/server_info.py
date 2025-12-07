#from app.db.repository import Repository direkt über Manager den Admin nehmen, ist Effizienter!
from datetime import datetime, timezone
from app.utils.logger import Logger

Log = Logger(name="testlog")

async def server_info(manager: object = "Failed to pass manager!") -> dict:
    """ Get connected client, uptime & current admin. """
    
    now = datetime.now(timezone.utc)
    uptime_delta = now - manager.start_time
    uptime_sec = int(uptime_delta.total_seconds())

    hours, remainder = divmod(uptime_sec, 3600)
    minutes, seconds = divmod(remainder, 60)
    uptime_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    
    msg = {
        "clients": len(manager.active_connections),
        "start_time": manager.start_time.replace(tzinfo=timezone.utc).isoformat().replace("+00:00", "Z"),
        "uptime_seconds": uptime_sec,
        "uptime": uptime_str,
        "admin": manager.curr_admin
    }
    Log.debug(f"msg: {msg}")
    return msg
