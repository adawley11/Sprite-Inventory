# README additions

## Development: migrations, seeding, running server, and tests

1. Install dependencies

```bash
pip install sqlalchemy alembic fastapi uvicorn pytest
# If using Postgres:
pip install psycopg2-binary
```

2. Configure DATABASE_URL env var

```bash
export DATABASE_URL=postgresql://user:pass@host:5432/dbname
# or for local dev sqlite
export DATABASE_URL=sqlite:///./data/sprites.db
```

3. Run migrations (if using Alembic)

```bash
alembic upgrade head
```

4. Seed the DB

```bash
python -m app.backend.scripts.seed_sprites
```

5. Generate frontend bundle (optional)

```bash
python app/frontend/scripts/generate_sprites_bundle.py --out app/frontend/src/data/sprites.json
```

6. Run server

```bash
uvicorn app.backend.main:app --reload --host 0.0.0.0 --port 8000
```

7. Run tests

```bash
pytest tests/
```
