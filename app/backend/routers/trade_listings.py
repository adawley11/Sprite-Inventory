from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
import os
from sqlalchemy import (
    create_engine, MetaData, Table, Column, String, Text, JSON, select, insert, update
)
from datetime import datetime
from app.backend.deps import get_current_user

router = APIRouter(prefix="/api")

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./data/sprites.db")
engine = create_engine(DATABASE_URL, future=True)
metadata = MetaData()

trade_listings = Table(
    "trade_listings",
    metadata,
    Column("id", String, primary_key=True),
    Column("user_id", String, nullable=False),
    Column("title", String),
    Column("offered", JSON),
    Column("wanted", JSON),
    Column("contact_username", String),
    Column("status", String),
    Column("created_at", String),
    Column("updated_at", String),
)

trade_offers = Table(
    "trade_offers",
    metadata,
    Column("id", String, primary_key=True),
    Column("listing_id", String),
    Column("from_user_id", String),
    Column("offered", JSON),
    Column("message", Text),
    Column("status", String),
    Column("created_at", String),
)

metadata.create_all(engine)


@router.get("/trades", response_model=List[dict])
def list_listings(status: Optional[str] = None):
    with engine.connect() as conn:
        sel = select(trade_listings)
        if status:
            sel = sel.where(trade_listings.c.status == status)
        rows = conn.execute(sel).mappings().all()
        return [dict(r) for r in rows]


@router.post("/trades", response_model=dict)
def create_listing(payload: dict, current_user=Depends(get_current_user)):
    uid = current_user.get("id")
    if not payload.get("id"):
        raise HTTPException(status_code=400, detail="id is required")
    data = {
        "id": payload["id"],
        "user_id": uid,
        "title": payload.get("title"),
        "offered": payload.get("offered", []),
        "wanted": payload.get("wanted", []),
        "contact_username": payload.get("contact_username"),
        "status": payload.get("status", "open"),
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
    }
    with engine.connect() as conn:
        ins = insert(trade_listings).values(**data)
        conn.execute(ins)
    return data


@router.get("/trades/{listing_id}", response_model=dict)
def get_listing(listing_id: str):
    with engine.connect() as conn:
        sel = select(trade_listings).where(trade_listings.c.id == listing_id)
        row = conn.execute(sel).mappings().first()
        if not row:
            raise HTTPException(status_code=404, detail="Not found")
        return dict(row)


@router.post("/trades/{listing_id}/offers", response_model=dict)
def post_offer(listing_id: str, payload: dict, current_user=Depends(get_current_user)):
    uid = current_user.get("id")
    if not payload.get("id"):
        raise HTTPException(status_code=400, detail="id is required")
    data = {
        "id": payload["id"],
        "listing_id": listing_id,
        "from_user_id": uid,
        "offered": payload.get("offered", []),
        "message": payload.get("message"),
        "status": payload.get("status", "pending"),
        "created_at": datetime.utcnow().isoformat(),
    }
    with engine.connect() as conn:
        ins = insert(trade_offers).values(**data)
        conn.execute(ins)
    return data


@router.get("/trades/{listing_id}/offers", response_model=List[dict])
def list_offers(listing_id: str):
    with engine.connect() as conn:
        sel = select(trade_offers).where(trade_offers.c.listing_id == listing_id)
        rows = conn.execute(sel).mappings().all()
        return [dict(r) for r in rows]
