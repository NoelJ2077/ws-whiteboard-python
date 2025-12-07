# backend/main.py
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.db import init_db
from app.db.repository import Repository
from app.utils.logger import Logger
from app.ws import ws_router

# tests
from app.db.enums import WbAction, ClientAction
from testing import create_dummy_user, create_dummy_wb, assign_dummy_wb, CL_ID, WB_ID

Log = Logger(name="app-main")

# test wb
async def testapp():
    await create_dummy_user()
    await create_dummy_wb()
    await assign_dummy_wb()

    Log.info("Dummy user + whiteboard created and assigned")

    aldata = {
        "wb_id": WB_ID, "client_id": CL_ID,
        "action_type": WbAction.LINE.value,
        "x1": 10, "y1": 10, "x2": 100, "y2": 100,
        "color": "red", "thickness": 2,
        "text_content": None
    }
    cldata = {
        "client_id": CL_ID,
        "event_type": ClientAction.HANDSHAKE.value,
        "event_data_intern": "Test log..."
    }

    try:
        Log.debug("Log record Action", "al", aldata)
        Log.debug("Log record Client", "cl", cldata)
        Log.debug("Startup logging done.")
        return True
    except RuntimeError as e:
        Log.debug(f"Error while logging test records: {e}")
        return False

# Lifespan: start/stop
@asynccontextmanager
async def lifespan(app: FastAPI):
    
    cond = 1# Only needed the first time to make tables and fill with dummy data. 
    if cond == 1:
        await init_db()
        await testapp()

    yield  # run(app)

    # rm admin on ctrl+c (console)
    Repository.rm_admin()
    Log.debug("Shutting down...")

app = FastAPI(lifespan=lifespan)

app.include_router(ws_router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"], #py http 
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

# check server
@app.get("/")
async def root():
    return {"status": "Backend läuft :D"}

# start run()
"""
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

RUN backend:
cd ws-whiteboard-python\backend
docker-compose up --build

RUN frontend:
cd ws-whiteboard-python\frontend
python3 -m http.server 3000

"""
