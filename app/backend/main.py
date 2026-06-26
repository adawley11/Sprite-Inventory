from fastapi import FastAPI
from .api_sprites import router as sprites_router
from .routers import user_sprites, trade_listings

app = FastAPI(title="Sprite Inventory API")

# Register routers
app.include_router(sprites_router)
app.include_router(user_sprites.router)
app.include_router(trade_listings.router)

# Health check
@app.get("/healthz")
def healthz():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.backend.main:app", host="0.0.0.0", port=8000, reload=True)
