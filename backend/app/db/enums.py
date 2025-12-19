from enum import Enum
#  Usage: repository.insert_action(x_id, user_id, ACTION.value)
# TODO: docs
__doc__ = "Holds all Enums for this project. "

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
    