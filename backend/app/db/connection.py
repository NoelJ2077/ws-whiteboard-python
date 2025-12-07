# backend/app/db/connection.py
import aiomysql, asyncio
from app.utils.config import Config

_pool = None
_pool_lock = asyncio.Lock()

async def init_pool():
    """Connection pool for all transactions"""
    global _pool
    async with _pool_lock:
        if _pool is None:
            _pool = await aiomysql.create_pool(
                host=Config.DB_HOST,
                port=Config.DB_PORT,
                user=Config.DB_USER,
                password=Config.DB_PASSWORD,
                db=Config.DB_NAME,
                autocommit=True,
                minsize=1,
                maxsize=10,
            )
        return _pool

async def get_pool():
    """ get current connection """
    global _pool
    if _pool is None:
        await init_pool()
    return _pool

async def get_conn():
    """ help function, gets 1 connection """
    pool = await get_pool()
    return await pool.acquire()

async def release_conn(conn):
    """ back to the pool """
    pool = await get_pool()
    pool.release(conn)