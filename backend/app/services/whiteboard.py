import uuid

from app.utils.logger import Logger
from app.db.repository import Repository
from app.db.enums import WbSysAction

Log = Logger(name="app-services-Whiteboard")

class Whiteboard:
    """ - TODO: On hold, only the creation of a test wb is used on startup.
    
    Whiteboard actions. relys on class(Repository) for all Database writing.
    Only Database reading is done directly over Whiteboard.
    """
    async def save_action(wb_id, user_id, action_type, data):
        """Safe action into database"""

    async def get_actions(wb_id):
        """Load a whiteboard. Usage on page refresh or first load after opening site"""

    async def create_wb(client_id, wb_name):
        """ create a whiteboard and insert the client into M:N table """
        wb_name = wb_name if str(wb_name) else "my Board"
        wb_id = str(uuid.uuid4())
        invite_key = str(uuid.uuid4())
        await Repository.insert_new_wb(client_id, wb_id, wb_name, invite_key)
        Log.info(f"inserted new wb: {wb_name} - for c: {client_id}", db_table="cl", db_data={"client_id": client_id, "event_type": WbSysAction.CREATE.value, "event_data_intern": f"created & inserted a new wb with id: {wb_id}"})

        return wb_id, invite_key