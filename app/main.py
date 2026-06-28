"""
KrishakBondhu — FastAPI Application Entry Point
কৃষক বন্ধু (Farmer's Friend) Backend Server
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.db.mongodb import connect_to_mongodb, close_mongodb_connection
from app.ml.predictor import load_model

from app.api.v1.auth import router as auth_router
from app.api.v1.disease import router as disease_router
from app.api.v1.posts import router as posts_router
from app.api.v1.expert import router as expert_router
from app.api.v1.admin import router as admin_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    # Startup
    await connect_to_mongodb()
    load_model()
    print("KrishakBondhu Backend is ready!")
    yield
    # Shutdown
    await close_mongodb_connection()
    print("KrishakBondhu Backend shutting down...")


app = FastAPI(
    title="KrishakBondhu API",
    description="কৃষক বন্ধু — AI-powered agricultural assistant for disease detection, community support, and expert consultation.",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API v1 routers
app.include_router(auth_router, prefix="/api/v1")
app.include_router(disease_router, prefix="/api/v1")
app.include_router(posts_router, prefix="/api/v1")
app.include_router(expert_router, prefix="/api/v1")
app.include_router(admin_router, prefix="/api/v1")


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "message": "🌿 KrishakBondhu API is running!",
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    """Health check for monitoring."""
    return {"status": "healthy"}
