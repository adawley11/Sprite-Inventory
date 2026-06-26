# tests/test_sprites_api.py
import os
import shutil
from fastapi.testclient import TestClient
from app.backend.main import app

TEST_DB = "sqlite:///./data/test_sprites.db"


def setup_module(module):
    # ensure clean test DB
    try:
        os.remove("./data/test_sprites.db")
    except Exception:
        pass
    os.environ["DATABASE_URL"] = TEST_DB
    # seed
    import subprocess
    subprocess.check_call(["python", "-m", "app.backend.scripts.seed_sprites"])


def test_list_sprites():
    client = TestClient(app)
    r = client.get("/api/sprites")
    assert r.status_code == 200
    assert isinstance(r.json(), list)

