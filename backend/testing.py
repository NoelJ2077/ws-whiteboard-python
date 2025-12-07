from app.db.connection import get_pool
import asyncio, uuid

#dummy_cl_id = str(uuid.uuid4().hex[:24])
#dummy_wb_uuid = str(uuid.uuid4())
# won't be called, use only for testing in console
#print(f"cl_id: {cl_id}, wb_id: {wb_uuid}")

CL_ID = "9dcb2448b9d04c07b9a899e5"
WB_ID = "02dd1d20-4a0a-4409-b0bd-712dfc9d6e8e"

async def create_dummy_user():
    """ Equals to opening the whiteboard in a browser. """
    pool = await get_pool()
    cl_id = "9dcb2448b9d04c07b9a899e5"
    async with pool.acquire() as conn:
        #print(cl_id)
        async with conn.cursor() as cur:
            await cur.execute("SELECT client_id FROM Clients WHERE client_id=%s", (cl_id))
            exists = await cur.fetchone()
            if exists:
                print("User already exists, skipping insert.")
                return

            sql = "INSERT into Clients (client_id, client_email) VALUES (%s, %s)"
            await cur.execute(sql, (cl_id, "noelgamemc@gmail.com"))
        await conn.commit()

async def create_dummy_wb():
    """ Equals to creating a new whiteboard """
    pool = await get_pool()
    #wb_uuid = "02dd1d20-4a0a-4409-b0bd-712dfc9d6e8e"
    wb_uuid = WB_ID
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute("SELECT wb_id FROM Whiteboards WHERE wb_id=%s", (wb_uuid))
            exists = await cur.fetchone()
            if exists:
                print("Dummy WB exists.")
                return
            
            sql = "INSERT into Whiteboards(wb_id, wb_name, invite_key) VALUES (%s, %s, %s)"
            await cur.execute(sql, (wb_uuid, "dummy_wb_1", uuid.uuid4()))
        await conn.commit()

async def assign_dummy_wb():
    """ Assign the new wb to client, so that the user can see & work with this wb. """
    pool = await get_pool()
    cl_id = CL_ID
    wb_uuid = WB_ID
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute("SELECT wb_id FROM Client_Whiteboards WHERE wb_id=%s", (wb_uuid))
            exists = await cur.fetchone()
            if exists:
                print("Dummy wb already assigned.")
                return

            sql = "INSERT into Client_Whiteboards(client_id, wb_id) VALUES (%s, %s)"
            await cur.execute(sql, (cl_id, wb_uuid))
        await conn.commit()
