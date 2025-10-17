"""
Health Check and System Information Endpoints

Provides system health checks and environment information.
Useful for monitoring and debugging the application.
"""

from fastapi import APIRouter
import os

router = APIRouter()

@router.get("/health")
def health_check():
    """
    Health check endpoint for monitoring
    """
    return {"status": "healthy", "message": "API is running successfully"}

@router.get("/info")
def get_info():
    """
    Endpoint that returns environment and system information
    """
    port = os.getenv("PORT", "8000")
    return {
        "app": "Talent Card Agent - FastAPI",
        "port": port,
        "environment": "Heroku" if os.getenv("DYNO") else "Local",
        "features": [
            "Employee directory",
            "Talent card generation with Workday API",
            "Power Automate integration",
            "HTML/PDF generation support"
        ]
    }

@router.get("/items/{item_id}")
def read_item(item_id: int, q: str = None):
    """
    Example endpoint with path and query parameters
    """
    return {"item_id": item_id, "q": q, "message": f"You requested item {item_id}"}