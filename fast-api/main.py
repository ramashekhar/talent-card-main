"""
Talent Card Agent - FastAPI Application

A focused FastAPI application for generating professional talent cards
from Workday API with Power Automate integration support.

Features:
- Workday API integration for live talent data
- Professional A4 landscape talent card generation  
- Employee testing pages (for development/testing)
- Power Automate compatible HTML output
- Secure, in-memory processing (no persistent data storage)
"""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os

# Import routers
from routers import employee, talent_cards, health

# Create FastAPI instance
app = FastAPI(
    title="Talent Card Agent API",
    description="Professional talent card generation with Workday integration",
    version="2.0.0"
)

# Add CORS middleware for Power Automate integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://make.powerautomate.com",
        "https://flow.microsoft.com", 
        "https://teams.microsoft.com",
        "https://outlook.office.com",
        "*"  # Allow all for testing - restrict in production
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include routers
app.include_router(employee.router, tags=["Employee Testing"])
app.include_router(talent_cards.router, tags=["Talent Cards"])
app.include_router(health.router, tags=["System"])

@app.get("/")
def read_root():
    """
    Root endpoint with application information and available features
    """
    return {
        "message": "Welcome to Talent Card Agent API",
        "description": "Professional talent card generation with Workday integration",
        "features": {
            "talent_cards": "/talent-card/{employee_id} - Generate Workday talent cards (MAIN FEATURE)",
            "employee_testing": "/employee/{employee_id} - Test employee pages (local data)",
            "system": "/health, /info - System status and information",
            "documentation": "/docs - Interactive API documentation"
        },
        "sample_employees_testing": [101, 102, 103, 104, 105, 106],
        "sample_workday_id": "1000130722",
        "environment": "Heroku" if os.getenv("DYNO") else "Local Development"
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)