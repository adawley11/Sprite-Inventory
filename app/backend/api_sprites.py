from fastapi import APIRouter, HTTPException
from typing import List, Optional
from . import sprites_data

router = APIRouter(prefix="/api")


@router.get("/sprites", response_model=List[dict])
def list_sprites(rarity: Optional[str] = None, type: Optional[str] = None, q: Optional[str] = None):
    """List all sprites with optional filtering by rarity, type, and text query (name or id).

    Example: /api/sprites?rarity=Legendary&type=Combat&q=king
    """
    results = sprites_data.SPRITES

    if rarity:
        results = [s for s in results if s.get("rarity") and s.get("rarity").lower() == rarity.lower()]
    if type:
        results = [s for s in results if s.get("type") and s.get("type").lower() == type.lower()]
    if q:
        qlow = q.lower()
        results = [s for s in results if qlow in s.get("name", "").lower() or qlow in s.get("id", "").lower()]

    return results


@router.get("/sprites/{sprite_id}", response_model=dict)
def get_sprite(sprite_id: str):
    """Return a single sprite by id."""
    for s in sprites_data.SPRITES:
        if s.get("id") == sprite_id:
            return s
    raise HTTPException(status_code=404, detail="Sprite not found")
