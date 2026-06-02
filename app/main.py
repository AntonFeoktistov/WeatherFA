from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import auth, locations

app = FastAPI(
    title="Weather App API",
    description="API для работы с погодой и локациями пользователей",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(locations.router)


@app.get("/")
async def root():
    return {
        "message": "Weather App API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
    }


@app.get("/health")
async def health_check():
    return {"status": "ok"}
