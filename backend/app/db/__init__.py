# app/db/__init__.py
import asyncio, os, aiomysql, re
from app.utils.logger import Logger
from app.utils.config import Config

# Create the db tables from sql file tables.sql

Log = Logger(name="app-db-init")

async def init_db(retries=10, delay=3):
    sql_file = os.path.join(os.path.dirname(__file__), "tables.sql")
    if not os.path.exists(sql_file):
        Log.warning(f"⚠️ SQL file not found: {sql_file}")
        return

    # SQL laden
    with open(sql_file, "r", encoding="utf-8") as f:
        sql_text = f.read()

    # remove sql comments
    sql_text = re.sub(r"--.*", "", sql_text)

    # split
    statements = [s.strip() for s in sql_text.split(";") if s.strip()]

    for attempt in range(1, retries + 1):
        try:
            conn = await aiomysql.connect(
                host=Config.DB_HOST,
                port=Config.DB_PORT,
                user=Config.DB_USER,
                password=Config.DB_PASSWORD,
                db=Config.DB_NAME,
                autocommit=True
            )
            async with conn.cursor() as cur:
                for stmt in statements:
                    try:
                        await cur.execute(stmt)
                    except Exception as e:
                        Log.warning(f"⚠️ Statement failed: {e}\n{stmt}\n")

            conn.close()
            Log.debug("✅ DB initialized and connected.")
            return

        except Exception as e:
            Log.warning(f"MySQL connection failed ({attempt}/{retries}): {e}")
            await asyncio.sleep(delay)

    raise Exception("Cannot connect to MySQL after multiple retries")
