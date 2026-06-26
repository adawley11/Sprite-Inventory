# app/backend/scripts/seed_sprites.py
"""
Seed the sprites table from app.backend.sprites_data.SPRITES.

Usage:
  # SQLite (local)
  DATABASE_URL=sqlite:///./data/sprites.db python -m app.backend.scripts.seed_sprites

  # Postgres
  DATABASE_URL=postgresql://user:pass@host:5432/dbname python -m app.backend.scripts.seed_sprites

Run this from the project root so package imports work (python -m ...).
"""
import os
import json
from sqlalchemy import (
    create_engine, MetaData, Table, Column, String, Text
)
from sqlalchemy.types import JSON as SA_JSON
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.sql import select
from datetime import datetime

# Import your sprites data. This assumes app/backend is a package and project root
# is on PYTHONPATH when running `python -m` from the repo root.
try:
    from app.backend import sprites_data
except Exception as e:
    raise SystemExit("Failed to import sprites_data from app.backend: {}\nRun this as a module from the repo root: `python -m app.backend.scripts.seed_sprites`".format(e))

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./data/sprites.db")

engine = create_engine(DATABASE_URL, future=True)
metadata = MetaData()

# Basic sprites table - images stored as JSON/JSONB depending on DB
sprites_table = Table(
    "sprites",
    metadata,
    Column("id", String, primary_key=True),
    Column("name", String, nullable=False),
    Column("rarity", String),
    Column("type", String),
    Column("power", Text),
    Column("color", String),
    Column("images", SA_JSON),  # JSON on Postgres, fallback to TEXT-based JSON on SQLite
    Column("created_at", String, default=lambda: datetime.utcnow().isoformat()),
    Column("updated_at", String, default=lambda: datetime.utcnow().isoformat(), onupdate=lambda: datetime.utcnow().isoformat()),
)


def row_from_sprite(s):
    return {
        "id": s.get("id"),
        "name": s.get("name"),
        "rarity": s.get("rarity"),
        "type": s.get("type"),
        "power": s.get("power"),
        "color": s.get("color"),
        "images": s.get("images"),
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
    }


def upsert_sprites():
    metadata.create_all(engine)
    with engine.connect() as conn:
        trans = conn.begin()
        try:
            count = 0
            for s in sprites_data.SPRITES:
                data = row_from_sprite(s)
                sel = select(sprites_table.c.id).where(sprites_table.c.id == data["id"])  # noqa: E231
                exists = conn.execute(sel).first()
                if exists:
                    upd = sprites_table.update().where(sprites_table.c.id == data["id"]).values(
                        name=data["name"],
                        rarity=data["rarity"],
                        type=data["type"],
                        power=data["power"],
                        color=data["color"],
                        images=data["images"],
                        updated_at=data["updated_at"],
                    )
                    conn.execute(upd)
                else:
                    ins = sprites_table.insert().values(**data)
                    conn.execute(ins)
                count += 1
            trans.commit()
            print(f"Seeding complete: inserted/updated {count} sprites.")
        except SQLAlchemyError as e:
            trans.rollback()
            print("Error seeding sprites:", e)
            raise


if __name__ == "__main__":
    upsert_sprites()
