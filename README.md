# Websocket Modul 2025 IT4b APP

Requirements:
requirements.txt
Docker (creates 2 images)

# Start frontend:
python3 -m http.server 3000

# DOCKER build img servicename(db|backend) or --build
docker-compose up --build
docker-compose up db
# DOCKER update img after code changes on running container
docker-compose restart backend
# DOCKER start serivce
docker-compose start db

# mysql commands from Docker terminal 
mysql -u username -p pw

# create req.txt from working dir:
#TOOD command

# Ports
mysql: 3306
http: 3000 (python3 -m http.server 3000)

whiteboard-app/
  
  .env
  docker-compose.yaml        # Entrypoint for "compose up --build"
  README.md

  backend/                   # BACKEND
    Dockerfile
    main.py                  # Entrypoint (log, db, websocket)
    requirements.txt
    testing.py               # 1 record for all 5 tables

    app/
      db/                    # MySQL
        __init__.py          # init DB from tables.sql
        connection.py        # aiomysql connection handler
        enums.py             # ActionType, ClientType
        repository.py        # DB reads/writes
        tables.sql           # DB schema
        rm.sql               # unused

      services/              # Business Logic
        taskhandler.py              
        whiteboard.py        
        Modulaufgaben/
          __init__.py       # Import all modules with their functions. 
          Client/
            __init__.py      
            help.py
            info.py
          Server/
            __init__.py
            help.py
            info.py
            livelog.py
          Server_Info/
            __init__.py
            server_info.py
          Serveradmin/
            __init__.py
            serveradmin.py
          
      utils/                 # Logging system
        __init__.py
        config.py            # load .env
        logger.py            # DB + console logging

      ws/
        __init__.py
        router.py            # FastAPI routes
        manager.py           # client mgmt, broadcast, send_to, disconnect

  frontend/                  # FRONTEND
    css/
      main.css               # design v2
      style.css              # bootstrap / canvas

    index.html               # whiteboard dashboard
    chat.html                # Chat
    serverconsole.html       # Server actions

    js/
      client.js              # WS client

    templates/
      login.html
      logout.html
      register.html