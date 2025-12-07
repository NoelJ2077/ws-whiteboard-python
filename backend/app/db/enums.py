from enum import Enum
#  Usage: repository.insert_action(wb_id, user_id, ACTION.value)
# TODO: docs
__doc__ = "Holds all Enums for this project. "

class WbAction(str, Enum):
    """Usage for whiteboard actions.
    - line
    - rect
    - circle
    - freehand
    - erase
    - text
    - wave
    """
    LINE = "line"
    RECT = "rect"
    CIRCLE = "circle"
    FREEHAND = "freehand"
    ERASE = "erase"
    TEXT = "text"
    WAVE = "wave"

class WbSysAction(str, Enum):
    """Usage for whiteboard system actions."""
    CREATE = "create"
    RENAME = "rename"
    DELETE = "delete"
    CHAT_MESSAGE = "chat_message" # When a client sends a msg from this wb.


class ClientAction(str, Enum):
    """Usage for client lifecycle and system events.
    - Handshake (connection start -> js: ws())
    - Healthcheck (check connection every x seconds)
    - Timeout (log problems)
    - Disconnect (disconnect when tab is closed)
    - Error (unexpected errors)
    - Reloadt (reload tab)
    """
    HANDSHAKE = "handshake"
    HEALTHCHECK = "healthcheck"
    TIMEOUT = "timeout"
    DISCONNECT = "disconnect"
    ERROR = "error"
    RELOADT = "reloadt"
    # JOIN = "join"               # wenn Nutzer einem Whiteboard beitritt
    # LEAVE = "leave"             # wenn Nutzer ein Whiteboard verlässt
    # AUTH_FAILED = "auth_failed" # optional für Security

class ServerCommands(str, Enum):
    """ Task1 server commands 
    - INFO (client_id) -> returns client information
    - LIVELOG = enable/disable live logs, requires a password
    - HELP = show all Servercommands
    """
    INFO = "info"
    LIVELOG = "livelog"
    HELP = "help"

class ClientCommands(str, Enum):
    """ Task (xy) """
    INFO = "info"
    HELP = "help"
    