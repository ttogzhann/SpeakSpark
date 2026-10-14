"""Owned E2E-only server. Never starts against the developer database."""
import json
import socket
import sys
from pathlib import Path

backend_root, workspace, token = sys.argv[1:]
sys.path.insert(0, backend_root)
import app.database_config as config
from sqlalchemy.orm import sessionmaker

config.engine.dispose()
config.engine = config.create_sqlite_engine(Path(workspace) / "e2e.sqlite")
config.SessionLocal = sessionmaker(bind=config.engine, autoflush=False, autocommit=False)
from app.main import app
import uvicorn

server = uvicorn.Server(uvicorn.Config(app, host="127.0.0.1", log_level="warning"))

@app.get(f"/__e2e__/{token}")
def ready():
    return {"token": token}

@app.post(f"/__e2e__/{token}/shutdown")
def shutdown():
    server.should_exit = True
    return {"stopping": True}

with socket.socket() as listener:
    listener.bind(("127.0.0.1", 0))
    listener.listen(128)
    (Path(workspace) / "server.json").write_text(json.dumps({"port": listener.getsockname()[1]}))
    try:
        server.run(sockets=[listener])
    finally:
        config.engine.dispose()
