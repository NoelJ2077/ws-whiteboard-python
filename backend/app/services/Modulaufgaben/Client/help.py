from app.db.enums import ClientCommands

async def help() -> str:
    commands = [cmd.value for cmd in ClientCommands]
    modulname = __name__.split(".")[-1]
    return f"(.{modulname}) Available ClientCommands: {', '.join(commands)}"
