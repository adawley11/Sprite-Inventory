from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
import os
from sqlalchemy import (
    create_engine, MetaData, Table, Column, String, Integer, Boolean, Text, JSON, select, insert, update, delete
)
from datetime import datetime
from app.backend.deps import get_current_user

router = APIRouter(prefix="/api")

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./data/sprites.db")
engine = create_engine(DATABASE_URL, future=True)
metadata = MetaData()

user_sprites = Table(
    "user_sprites",
    metadata,
    Column("id", String, primary_key=True),
    Column("user_id", String, nullable=False),
    Column("sprite_id", String),
    Column("have", Boolean, server_default="true"),
    Column("count", Integer, server_default="1"),
    Column("mastery", Integer),
    Column("variant", String),
    Column("public", Boolean, server_default="true"),
    Column("notes", Text),
    Column("updated_at", String),
)

# Ensure table exists for simple setups
metadata.create_all(engine)


@router.get("/me/sprites", response_model=List[dict])
def list_user_sprites(user_id: Optional[str] = None, current_user=Depends(get_current_user)):
    """List sprites for the current user (or for the provided user_id if supplied)."""
    uid = user_id or current_user.get("id")
    with engine.connect() as conn:
        sel = select(user_sprites).where(user_sprites.c.user_id == uid)
        rows = conn.execute(sel).mappings().all()
        return [dict(r) for r in rows]


@router.post("/me/sprites", response_model=dict)
def add_user_sprite(payload: dict, current_user=Depends(get_current_user)):
    """Add or upsert a user_sprite row. Expects JSON with at least `id` and `sprite_id`."""
    uid = current_user.get("id")
    if not payload.get("id") or not payload.get("sprite_id"):
        raise HTTPException(status_code=400, detail="id and sprite_id are required")
    data = {
        "id": payload["id"],
        "user_id": uid,
        "sprite_id": payload.get("sprite_id"),
        "have": payload.get("have", True),
        "count": payload.get("count", 1),
        "mastery": payload.get("mastery"),
        "variant": payload.get("variant"),
        "public": payload.get("public", True),
        "notes": payload.get("notes"),
        "updated_at": datetime.utcnow().isoformat(),
    }
    with engine.connect() as conn:
        # upsert-like behavior (simple): try update, if 0 rows insert
        upd = update(user_sprites).where(user_sprites.c.id == data["id"]).values(**data)
        res = conn.execute(upd)
        if res.rowcount == 0:
            ins = insert(user_sprites).values(**data)
            conn.execute(ins)
    return data


@router.put("/me/sprites/{entry_id}", response_model=dict)
def update_user_sprite(entry_id: str, payload: dict, current_user=Depends(get_current_user)):
    uid = current_user.get("id")
    with engine.connect() as conn:
        sel = select(user_sprites).where(user_sprites.c.id == entry_id).where(user_sprites.c.user_id == uid)
        row = conn.execute(sel).first()
        if not row:
            raise HTTPException(status_code=404, detail="Not found")
        upd = update(user_sprites).where(user_sprites.c.id == entry_id).values(**{**payload, "updated_at": datetime.utcnow().isoformat()})
        conn.execute(upd)
        sel2 = select(user_sprites).where(user_sprites.c.id == entry_id)
        new = conn.execute(sel2).mappings().first()
        return dict(new)


@router.delete("/me/sprites/{entry_id}")
def delete_user_sprite(entry_id: str, current_user=Depends(get_current_user)):
    uid = current_user.get("id")
    with engine.connect() as conn:
        del_stmt = delete(user_sprites).where(user_sprites.c.id == entry_id).where(user_sprites.c.user_id == uid)
        res = conn.execute(del_stmt)
        if res.rowcount == 0:
            raise HTTPException(status_code=404, detail="Not found")
    return {"ok": True}
