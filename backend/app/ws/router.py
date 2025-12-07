# app/ws/router.py
import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.db.repository import Repository
from app.utils.logger import Logger
from app.ws import ConnectionManager
from app.ws.messagehandler import MessageHandler
from app.services.whiteboard import Whiteboard

Log = Logger(name="app-ws-router")

ws_router = APIRouter()
manager = ConnectionManager()
handler = MessageHandler(manager=manager)


# Main-route, entry point
@ws_router.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await manager.connect(websocket, client_id)
    if not await Repository.existing_client(client_id):
        await Repository.insert_client(client_id)
    
    # // START (Task 2)
    Log.info(f"Current Admin: {manager.curr_admin}")
    if manager.curr_admin == client_id: # open page -> sets user as admin -> then compare. Second user will not meet condition -> check manager object-logic
        await Repository.set_admin(client_id)

    # TODO: implementation here only temporary. 
    admin = await Repository.get_current_admin()
    await websocket.send_text(json.dumps({"type": "admin_status", "curr_admin": admin if admin else None}))

    try: # await input command
        while True:
            raw = await websocket.receive_text()
            data = json.loads(raw)
            # admin logik nötig?
            await handler.handle_message(client_id, websocket, data)
    except WebSocketDisconnect: # Achtung, wird auch bei reload des Tabs zu disconnect führen, JS holt die id einfach wieder aus der Tab-chache. 
        result = manager.disconnect(client_id)
        if result["admin_changed"]:
            Log.info(f"New Admin: {result["new_admin"]}")
            await Repository.set_admin(client_id=result["new_admin"])
            # msg to all clients:
            for ws in manager.active_connections.values():
                await ws.send_text(json.dumps({"type": "admin_status", "curr_admin": result["new_admin"]}))
    # // END (Task 2)

# Get Client
@ws_router.get("ws/client/{client_id}")
async def get_client_mail(client_id: str):
        _, email = await Repository.get_client(client_id)
        if email:
            return {"email": email}
        else:
            return {"email": None}
        
# Get all types of input commands
@ws_router.get("/api/services/get_all_inputs/{client_id}")
async def get_all_inputs(client_id: str):
    # TODO: Dynamisch machen aus Class(Enum)
    MESSAGE_TYPE_META = {
    "personal":       {"label": "[Personal]",        "color": "#2e8b57"},
    "p2p":            {"label": "[P2P]",             "color": "#1e90ff"},
    "group":          {"label": "[Group]",           "color": "#ff8c00"},
    "broadcast":      {"label": "[Broadcast]",       "color": "#9370db"},
    "set_email":      {"label": "[setMail]",         "color": "#a319daff"},

    "servercmd":      {"label": "[ServerCMD]",       "color": "#20b2aa"},
    "clientcmd":      {"label": "[ClientCMD]",       "color": "#ffd700"},
    "serveradmincmd": {"label": "[ServerAdminCMD]",  "color": "#3db93dff"},
    "server_infocmd": {"label": "[Server-InfoCMD]",  "color": "#008b8b"},
    "error":          {"label": "[Error]",           "color": "#c73838"},
}
    

    return MESSAGE_TYPE_META

# get client group(s) TODO: nicht fertig
@ws_router.get("/api/client/{client_id}/groups")
async def get_client_groups(client_id: str):
    groups = await Repository.get_client_groups(client_id)
    return {"groups": groups}

# Test-Route (z.B. test.html) (TEST)
@ws_router.websocket("/ws/test/{client_id}")
async def test_socket(websocket: WebSocket, client_id: str):
    await manager.connect(websocket)
    await websocket.send_text(f"Hello {client_id}, this is /ws/test/")
    # nur für Experimente gedacht

# WB On Hold: is used on startup. 
@ws_router.websocket("/ws/create/{client_id}")
async def create_wb_socket(websocket: WebSocket, client_id: str):
    await manager.connect(websocket)

    if await Repository.existing_client(client_id):
        new_wb = await Whiteboard.create_wb(client_id)
        await websocket.send_text(f"Whiteboard {new_wb} created for {client_id}")
    else:
        await Repository.insert_client(client_id)
        await websocket.send_text(f"Client {client_id} registered, please retry create.")
