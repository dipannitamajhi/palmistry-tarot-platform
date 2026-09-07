from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine, Base
from app.models import user, reading, notification  # noqa: F401 — importing registers these tables with Base
from app.routers import tarot, palm, auth, admin, users, dashboard, reports, notifications

# Creates the SQLite file and the `users` table on first run, based on the
# models we've imported (import app.models.user runs via app.routers.auth).
# In a real production app you'd use a migration tool (Alembic) instead of
# this, so you can version-control schema changes — but this is the right
# starting point while learning.
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Palmistry & Tarot Intelligence API",
    description="Backend for palm analysis and tarot reading generation.",
    version="0.1.0",
)

# CORS = Cross-Origin Resource Sharing. Browsers block a webpage on one
# origin (localhost:5173) from calling an API on another origin
# (localhost:8000) unless the API explicitly allows it. This is a security
# feature, not a bug — we're just telling it our frontend is trusted.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Each router owns one feature area. As the project grows (auth, dashboards,
# recommendations — see the spec's module list), you add one router file
# per module instead of piling everything into this one file.
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(admin.router)
app.include_router(tarot.router)
app.include_router(palm.router)
app.include_router(dashboard.router)
app.include_router(reports.router)
app.include_router(notifications.router)


@app.get("/")
def health_check():
    return {"status": "ok", "message": "Palmistry & Tarot API is running."}
