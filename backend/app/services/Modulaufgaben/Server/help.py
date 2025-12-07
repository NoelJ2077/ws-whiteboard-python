from app.db.enums import ServerCommands

async def help() -> str:
    commands = [cmd.value for cmd in ServerCommands]
    modulname = __name__.split(".")[-1]
    return f"(.{modulname}) Available ServerCommands: {', '.join(commands)}"
