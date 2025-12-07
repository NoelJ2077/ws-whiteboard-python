#/app/ws/connectionmanager.py
from fastapi import WebSocket
from logging import Logger
from collections import defaultdict
from datetime import datetime, timezone

Log = Logger(name="app-ws-manager")

class ConnectionManager:
    """ WS Connection Manager, handles incoming message inputs and clients, plus updates the current admin and holds all active connections."""
    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}  # client_id -> ws
        self.groups: dict[str, set[WebSocket]] = defaultdict(set)
        # // START (Task 2)
        self.curr_admin = None
        self.start_time = datetime.now(timezone.utc)
        # // END (Task 2)

    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket
        # // START (Task 2)
        if not self.curr_admin: # set to admin, if it is first user
            self.curr_admin = client_id
        # // END (Task 2)

    def disconnect(self, client_id: str):
        ws = self.active_connections.pop(client_id, None)
        if ws:
            for group in self.groups.values():
                group.discard(ws)

        # // START (Task 2)
        old_admin = self.curr_admin
        if old_admin == client_id:
            self.curr_admin = next(iter(self.active_connections), None) # Fallback if last user left => No admin

        admin_changed = bool((old_admin != self.curr_admin))
        return {"admin_changed": admin_changed, "new_admin": self.curr_admin}
        # // END (Task 2)

    # ====== Send different types of messages ======
    async def send_personal_msg(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def send_p2p_msg(self, message: str, target_id: str):
        Log.debug(f"Target ID, {target_id}")
        target_ws = self.active_connections.get(target_id)
        if target_ws:
            await target_ws.send_text(message)
    
    #TODO: implement
    async def send_group_msg(self, message: str, group_id: str):
        for ws in self.groups.get(group_id, set()):
            await ws.send_text(message)

    async def broadcast(self, message: str):
        for ws in self.active_connections.values():
            await ws.send_text(message)

    # ====== Goups ======
    def add_to_group(self, websocket: WebSocket, group_id: str):
        self.groups[group_id].add(websocket)

    def remove_from_group(self, websocket: WebSocket, group_id: str):
        if group_id in self.groups:
            self.groups[group_id].discard(websocket)

    # ===== Whiteboard ===== 
    # TODO: irgendwann
