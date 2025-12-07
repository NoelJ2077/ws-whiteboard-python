from app.db.repository import Repository

async def info(client_id: str) -> str:
    cid, email = await Repository.get_client(client_id)
    modulname = __name__.split(".")[-1]
    return f"(.{modulname}) Client-ID: {cid}, Client-Name: {email}"
