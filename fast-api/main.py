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
from routers import talent_cards

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
app.include_router(talent_cards.router, tags=["Talent Cards"])

@app.get("/")
def read_root():
    """
    Root endpoint with application information and available features
    """
    return {
        "message": "Welcome to Talent Card Agent API",
        "description": "Professional talent card generation with Workday integration",
        "features": {
            "talent_cards": "/talent-card/{employee_id}?tenant={csc|gms} - Generate Workday talent cards"
        },
        "usage": {
            "default_tenant": "/talent-card/21103 (uses WORKDAY_TENANT env variable, defaults to 'gms')",
            "specify_gms": "/talent-card/21103?tenant=gms",
            "specify_csc": "/talent-card/1000130722?tenant=csc"
        },
        "sample_employees": {
            "CSC": [1000130722, 1000252689],
            "GMS": [21103, 21001]
        },
        "environment": "Heroku" if os.getenv("DYNO") else "Azure" if os.getenv("WEBSITE_INSTANCE_ID") else "Local Development"
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8001))
    uvicorn.run(app, host="0.0.0.0", port=port)