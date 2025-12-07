# app/db/repository.py
from app.db.connection import get_pool
from contextlib import asynccontextmanager

@asynccontextmanager
async def get_cursor(commit: bool = False):
    pool = await get_pool()
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            yield cur
        if commit:
            await conn.commit()

class Repository:
    """ Handles actions that need Database interactions. SQL querys are all written here, connection pool is in a separate file. """

    @staticmethod
    async def insert_client(client_id: str):
        query = """
        INSERT INTO Clients (client_id)
        VALUES (%s)
        ON DUPLICATE KEY UPDATE client_id=client_id
        """
        async with get_cursor(commit=True) as cur:
            await cur.execute(query, (client_id,))

    @staticmethod
    async def existing_client(client_id: str):
        """ Check if client exists. """
        query = "SELECT client_id FROM Clients WHERE client_id=%s"
        async with get_cursor() as cur:
            await cur.execute(query, (client_id,))
            exists = await cur.fetchone()
            return True if exists else False
        
    @staticmethod
    async def get_client(client_id: str):
        """ Get client information. """
        query = "SELECT client_id, client_email FROM Clients WHERE client_id=%s"
        async with get_cursor() as cur:
            await cur.execute(query, (client_id,))
            row = await cur.fetchone()
            if row:
                cid, client_email = row
                return cid, client_email
            return None, None

    @staticmethod
    async def insert_new_wb(client_id: str, wb_id: str, wb_name: str, invite_key: str = "uuid.uuid4"):

        # M:N querys
        query_wb = """
        INSERT INTO Whiteboards (wb_id, wb_name, invite_key)
        VALUES (%s, %s, %s)
        """
        query_mapping = """
        INSERT INTO Client_Whiteboards (client_id, wb_id)
        VALUES (%s, %s)
        """

        async with get_cursor(commit=True) as cur:
            await cur.execute(query_wb, (wb_id, wb_name, invite_key))
            await cur.execute(query_mapping, (client_id, wb_id))

        return wb_id, invite_key
    
    @staticmethod
    async def get_client_groups(client_id: str):
        query = """
        SELECT wb_id, wb_name FROM Whiteboards
        INNER JOIN Client_Whiteboards USING(wb_id)
        WHERE client_id=%s
        """
        async with get_cursor() as cur:
            await cur.execute(query, (client_id,))
            rows = await cur.fetchall()
            # Liste von dicts zurückgeben
            return [{"wb_id": row[0], "wb_name": row[1]} for row in rows]
    
    @staticmethod
    async def set_mail(client_id: str, mail: str):
        query = "UPDATE Clients SET client_email=%s WHERE client_id=%s"
        async with get_cursor(commit=True) as cur:
            await cur.execute(query, (mail, client_id))

    # // START (Task 2)
    @staticmethod
    async def set_admin(client_id: str)->None: 
        query = "UPDATE Clients SET isAdmin = CASE WHEN client_id=%s THEN 1 ELSE 0 END"
        async with get_cursor(commit=True) as cur:
            await cur.execute(query, (client_id,))
    
    @staticmethod
    async def get_current_admin()-> str: 
        query = "SELECT client_id FROM Clients WHERE isAdmin=1 LIMIT 1" # end query when admin found
        async with get_cursor() as cur:
            await cur.execute(query)
            row = await cur.fetchone()
            return row[0]
        
    @staticmethod
    async def rm_admin()->None:
        """ Remove admin on app shutdown """
        query = "UPDATE Clients SET isAdmin = 0 WHERE isAdmin=1 LIMIT 1"
        async with get_cursor(commit=True) as cur:
            await cur.execute(query)
    # // END (Task 2)


