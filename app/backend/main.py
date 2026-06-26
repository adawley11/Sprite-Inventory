# app/backend/main.py
from fastapi import FastAPI
from .api_sprites import router as sprites_router

app = FastAPI(title="Sprite Inventory API")

# Register routers
app.include_router(sprites_router)

# Health check
@app.get("/healthz")
def healthz():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.backend.main:app", host="0.0.0.0", port=8000, reload=True)
