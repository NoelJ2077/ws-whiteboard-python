# backend/app/utils/logger.py
import logging, sys, asyncio
from typing import Literal, TypedDict, Optional, NotRequired, overload

from app.db.connection import get_pool

class ActionLogDict(TypedDict, total=False):
    wb_id: int
    client_id: str
    action_type: str
    x1: Optional[int]
    y1: Optional[int]
    x2: Optional[int]
    y2: Optional[int]
    color: Optional[str]
    thickness: Optional[int]
    text_content: Optional[str]

class ClientLogDict(TypedDict, total=False):
    client_id: str
    event_type: str
    event_data_intern: Optional[str]

class DBHandler(logging.Handler):
    """Write logs into a database table (Actions_log / Client_log).

    Choose table for logging in the log call:
        - "al" -> Actions_log
        - "cl" -> Client_log
    
    Sample:
        # Log whiteboard action
        Log.info(
            "Client drew a line",
            db_table="al",
            db_data={"wb_id": 5, "client_id": "uuid-1234", "action_type": "line"}
        )

        # Log a client event (TODO: implement)
        Log.info(
            "Handshake received",
            db_table="cl",
            db_data={"client_id": "uuid-1234", "event_type": "handshake"}
        )

        # only console logging, no db transaction
        Log.info("Server started")
    """

    def __init__(self, default_table=None):
        super().__init__()
        self.default_table = default_table

    def emit(self, record):
        table = getattr(record, "db_table", self.default_table)
        data = getattr(record, "db_data", None)
        
        if table is None:
            return  # No DB logging

        #print(f"Logging to table: {table} with data: {data}")

        try:
            loop = asyncio.get_running_loop()
            loop.create_task(self._write_to_db(table, record.levelname, record.msg, data))
        except RuntimeError:
            # Log synchronously or queue for later if no loop is running
            print(f"⚠️ No running event loop, logging to console only: {record.msg}")

    def _handle_task_result(self, task):
        try:
            task.result()
        except asyncio.CancelledError:
            print("⚠️ DB logging task was cancelled")
        except Exception as e:
            print(f"⚠️ DB logging task failed: {e}")

    async def _write_to_db(self, table: Literal["cl","al"], level, msg, data: dict):
        try:
            pool = await get_pool()
            async with pool.acquire() as conn:
                async with conn.cursor() as cur:
                    if table == "al" and isinstance(data, dict):
                        sql = """
                        INSERT INTO Actions_log 
                        (wb_id, client_id, action_type, x1, y1, x2, y2, color, thickness, text_content, timestamp)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
                        """
                        await cur.execute(sql, (
                            data.get("wb_id"),
                            data.get("client_id"),
                            data.get("action_type"),
                            data.get("x1"),
                            data.get("y1"),
                            data.get("x2"),
                            data.get("y2"),
                            data.get("color"),
                            data.get("thickness"),
                            data.get("text_content")
                        ))
                    elif table == "cl" and isinstance(data, dict):
                        sql = """
                        INSERT INTO Client_log
                        (client_id, event_type, event_data_intern, timestamp)
                        VALUES (%s, %s, %s, NOW())
                        """
                        await cur.execute(sql, (
                            data.get("client_id"),
                            data.get("event_type"),
                            data.get("event_data_intern") or msg
                        ))
                    else:
                        sql = f"INSERT INTO {table} (event_type, event_data) VALUES (%s, %s)"
                        await cur.execute(sql, (level, msg))
                    await conn.commit()
            # Do NOT close the pool here
        except Exception as e:
            print(f"⚠️ Failed to write log to DB: {e}")

class Logger:
    """ Logger to log to console and optionally to database.
    For a simple Console log, only 1 string is needed.
    - Log.obj("string")

    Include a db-record:
    - Log.obji("string", "cl", db_data={})
    - db_table: Literal["cl", "al"]
    - db_data: dict

    See typing help when using Log.level(arg: type)
    """

    def __init__(self, name="wb-app"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)

        if not self.logger.handlers:
            # Console handler
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(logging.DEBUG)
            formatter = logging.Formatter(
                "%(name)s [%(asctime)s] [%(levelname)s] : %(message)s",
                datefmt="%H:%M:%S %d:%m:%Y"
            )
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)

            db_handler = DBHandler()
            db_handler.setFormatter(formatter)
            self.logger.addHandler(db_handler)

    def _log(self, level, msg: str, db_table: str=None, db_data: dict=None, *args, **kwargs):
        extra = kwargs.pop("extra", {})
        extra.update({"db_table": db_table, "db_data": db_data})
        self.logger.log(level, msg, *args, extra=extra, **kwargs)

    # DEBUG
    @overload
    def debug(self, msg: str, db_table: Literal["cl"], db_data: ClientLogDict, *args, **kwargs): ...
    @overload
    def debug(self, msg: str, db_table: Literal["al"], db_data: ActionLogDict, *args, **kwargs): ...
    def debug(self, msg, db_table=None, db_data=None, *args, **kwargs):
        self._log(logging.DEBUG, msg, db_table, db_data, *args, **kwargs)

    # INFO
    @overload
    def info(self, msg: str, db_table: Literal["cl"], db_data: ClientLogDict, *args, **kwargs): ...
    @overload
    def info(self, msg: str, db_table: Literal["al"], db_data: ActionLogDict, *args, **kwargs): ...
    def info(self, msg, db_table=None, db_data=None, *args, **kwargs):
        self._log(logging.INFO, msg, db_table, db_data, *args, **kwargs)

    # WARNING
    @overload
    def warning(self, msg: str, db_table: Literal["cl"], db_data: ClientLogDict, *args, **kwargs): ...
    @overload
    def warning(self, msg: str, db_table: Literal["al"], db_data: ActionLogDict, *args, **kwargs): ...
    def warning(self, msg, db_table=None, db_data=None, *args, **kwargs):
        self._log(logging.WARNING, msg, db_table, db_data, *args, **kwargs)

    # ERROR
    @overload
    def error(self, msg: str, db_table: Literal["cl"], db_data: ClientLogDict, *args, **kwargs): ...
    @overload
    def error(self, msg: str, db_table: Literal["al"], db_data: ActionLogDict, *args, **kwargs): ...
    def error(self, msg, db_table=None, db_data=None, *args, **kwargs):
        self._log(logging.ERROR, msg, db_table, db_data, *args, **kwargs)

    # CRITICAL
    @overload
    def critical(self, msg: str, db_table: Literal["cl"], db_data: ClientLogDict, *args, **kwargs): ...
    @overload
    def critical(self, msg: str, db_table: Literal["al"], db_data: ActionLogDict, *args, **kwargs): ...
    def critical(self, msg, db_table=None, db_data=None, *args, **kwargs):
        self._log(logging.CRITICAL, msg, db_table, db_data, *args, **kwargs)
