"""
The Bright Moon University - Database Connection & Lifecycle Control
File: database/connection.py
Description: Initializes the SQLite engine using stable absolute paths and handles session generation.
"""

import os
from sqlmodel import SQLModel, create_engine, Session

# 1. Dynamically find the absolute folder path of your portal project root
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 2. Force both the server and seed scripts to use the exact same file path and name
DATABASE_FILE = os.path.join(BASE_DIR, "bright_moon.db")
DATABASE_URL = f"sqlite:///{DATABASE_FILE}"

# Connect the engine with write safety layers for SQLite multi-threading
engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False}
)

def init_db():
    """Compiles local metadata blueprints to generate physical tables on disk."""
    SQLModel.metadata.create_all(engine)

def get_session():
    """Dependency provider yielding clear transaction channels for API endpoints."""
    with Session(engine) as session:
        yield session