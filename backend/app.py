from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from starlette.middleware.sessions import SessionMiddleware
from backend.core.config import SECRET_KEY
import os

app = FastAPI(title="ClubHub API", docs_url="/docs", redoc_url="/redoc")

# --- Session Middleware ---
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)

# --- Register Routers ---
from backend.auth.routes import router as auth_router
from backend.activities.routes import router as activities_router
from backend.clubs.routes import router as clubs_router
from backend.members.routes import router as members_router

app.include_router(auth_router, prefix="/api/auth", tags=["Auth"])
app.include_router(activities_router, prefix="/api/activities", tags=["Activities"])
app.include_router(clubs_router, prefix="/api/clubs", tags=["Clubs"])
app.include_router(members_router, prefix="/api/members", tags=["Members"])

# --- Serve Frontend Static Files ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

app.mount("/frontend", StaticFiles(directory=os.path.join(BASE_DIR, "frontend"), html=True), name="frontend")
app.mount("/uploads", StaticFiles(directory=os.path.join(BASE_DIR, "uploads")), name="uploads")


@app.get("/")
def index():
    return RedirectResponse(url="/frontend/auth/login.html")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app:app", host="0.0.0.0", port=5000, reload=True)
