from app.db.connection import get_pool
import uuid

#dummy_cl_id = str(uuid.uuid4().hex[:24])
# won't be called, use only for testing in console

CL_ID = "9dcb2448b9d04c07b9a899e5"

async def create_dummy_user():
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
