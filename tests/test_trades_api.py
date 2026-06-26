# tests/test_trades_api.py
import os
import subprocess
from fastapi.testclient import TestClient
from app.backend.main import app

TEST_DB = "sqlite:///./data/test_sprites.db"


def setup_module(module):
    # ensure DB seeded
    os.environ["DATABASE_URL"] = TEST_DB
    subprocess.check_call(["python", "-m", "app.backend.scripts.seed_sprites"])


def test_create_and_get_listing():
    client = TestClient(app)
    listing = {
        "id": "listing-1",
        "title": "Offering water sprite",
        "offered": ["water"],
        "wanted": ["fire"],
        "contact_username": "trader123"
    }
    r = client.post("/api/trades", json=listing, headers={"Authorization": "Bearer alice"})
    assert r.status_code == 200
    data = r.json()
    assert data["id"] == "listing-1"

    r2 = client.get("/api/trades/listing-1")
    assert r2.status_code == 200
    assert r2.json()["title"] == "Offering water sprite"


def test_post_offer():
    client = TestClient(app)
    offer = {"id": "offer-1", "offered": ["fire"], "message": "I can trade"}
    r = client.post("/api/trades/listing-1/offers", json=offer, headers={"Authorization": "Bearer bob"})
    assert r.status_code == 200
    data = r.json()
    assert data["id"] == "offer-1"

    r2 = client.get("/api/trades/listing-1/offers")
    assert r2.status_code == 200
    offers = r2.json()
    assert any(o["id"] == "offer-1" for o in offers)
