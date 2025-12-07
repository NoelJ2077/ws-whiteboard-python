# app/ws/handler.py
import json
from app.services.taskhandler import TaskHandler
from app.services.Modulaufgaben import Namespaces as _cmd_modules_
from app.utils.logger import Logger
from app.db.repository import Repository

Log = Logger(name="app-ws-messagehandler")

class MessageHandler:
    """ requires: class(ConnectionManager) """
    def __init__(self, manager):
        """ manager: class(ConnectionManager)  """
        self.manager = manager
        self.taskhandler = TaskHandler()

        # standard message handlers
        self.std_handlers = {
            "personal": self._handle_personal,
            "p2p": self._handle_p2p,
            "group": self._handle_group,
            "broadcast": self._handle_broadcast,
            "set_email": self._handle_set_email,
        }

        # add command input for all namespaces dynamically
        for ns in _cmd_modules_:
            self.std_handlers[f"{ns}cmd"] = self._handle_commandinput
        
        #Log.info(f"handlers: {self.std_handlers}")

    async def handle_message(self, client_id: str, websocket, data: dict):
        msg_type = data.get("type")
        message = data.get("message", "")

        handler = self.std_handlers.get(msg_type)
        if handler:
            #Log.debug(f"exec with: {client_id}, {data}, {message}") 
            await handler(client_id, websocket, data, message)
        else:
            await self.manager.send_personal_msg(json.dumps({
                "type": "error",
                "message": f"Unknown input type: {msg_type}"
            }), websocket)

    # standard, not @ handlers
    async def _handle_personal(self, client_id, websocket, data, message):
        await self.manager.send_personal_msg(json.dumps({
            "type": "personal",
            "message": message
        }), websocket)

    async def _handle_p2p(self, client_id, websocket, data, message):
        target_id = data.get("client_id")
        await self.manager.send_p2p_msg(json.dumps({
            "type": "p2p",
            "sender": client_id,
            "message": message
        }), target_id)

    async def _handle_group(self, client_id, websocket, data, message):
        group_id = data.get("group_id")
        await self.manager.send_group_msg(json.dumps({
            "type": "group",
            "group_id": group_id,
            "message": message
        }), group_id)

    async def _handle_broadcast(self, client_id, websocket, data, message):
        await self.manager.broadcast(json.dumps({
            "type": "broadcast",
            "message": message
        }))

    async def _handle_set_email(self, client_id, websocket, data, message):
        email = message.strip()
        if not email:
            await self.manager.send_personal_msg(json.dumps({
                "type": "error",
                "message": "Email can't be empty!"
            }), websocket)
            return

        await Repository.set_mail(client_id, email)
        await self.manager.send_personal_msg(json.dumps({
            "type": "set_email",
            "message": f"{email} was inserted into tb clients!"
        }), websocket)

    # cmd handler 
    async def _handle_commandinput(self, client_id, websocket, data, message):
        if not message:
            await self._send_error(websocket, "Empty message")
            return

        # parse command
        prefix, command, msg = self._parse_command(data.get("type", ""), message)
        if not prefix:
            await self._send_error(websocket, f"Unknown message type {data.get('type')}")
            return

        # exec cmd
        result = await self.taskhandler.handle_execute_command(
            prefix, command, client_id=client_id, message=msg, extras={"manager": self.manager,} # TODO: extras dynamisch?
        )

        # // START (Task 2)
        # special case @serveradmin -> inputfield is the message itself instead of the function called. 
        #Log.debug(f"prefix, {prefix}")
        if prefix == "serveradmin":
            admin_id = await Repository.get_current_admin()
            admin_ws = self.manager.active_connections.get(admin_id)
            if admin_ws:
                await self.manager.send_personal_msg(json.dumps({
                    "type": f"{prefix}cmd",
                    "message": result,
                    "from_client_id": client_id
                }), admin_ws)    
        else: # all other prefixes
            await self.manager.send_personal_msg(json.dumps({
                "type": f"{prefix}cmd",
                "message": result
            }), websocket)

    def _parse_command(self, msg_type: str, text: str):
        """Return (prefix, command, msg) tuple"""
        
        if not msg_type.endswith("cmd"):
            return None, None, None

        norm_prefix = msg_type[:-3].lower() # here, get the input command type
        #Log.debug(f"norm_prefix, {norm_prefix}")
        if norm_prefix == "serveradmin":
            return "serveradmin", "serveradmin", text
        elif norm_prefix == "server_info": # Special case, cmd comes as server-info but can't use - in python and js so we use _ instead.
            return "server_info", "server_info", text
        # // END (Task 2) Anpassung, damit die Businesslogik gleich bleibt, 
        # ist bei @serveradmin das Inputfeld nicht die Funktion sonder direkt die MSG die an den Admin geht. 

        if not text.startswith("@"):
            return None, None, None

        parts = text.split(maxsplit=1)
        prefix = parts[0][1:].lower()  # "@server" → "server"
        command = parts[1].strip() if len(parts) > 1 else ""
        return prefix, command, command

    async def _send_error(self, websocket, message):
        await self.manager.send_personal_msg(json.dumps({
            "type": "error",
            "message": message
        }), websocket)
