from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import os
import json
from typing import List, Dict, Optional
from pathlib import Path

# Import Workday client
from src.workday_client import WorkdayClient

# Create FastAPI instance
app = FastAPI(title="Employee Management API", version="1.0.0")

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

# Set up templates
templates = Jinja2Templates(directory="templates")

# Workday client setup
def load_workday_config() -> Dict:
    """Load Workday API configuration"""
    config_file = Path("config/workday_config.json")
    if not config_file.exists():
        raise FileNotFoundError(
            f"Configuration file not found: {config_file}\n"
            f"Please create config/workday_config.json with API credentials."
        )
    
    with open(config_file, 'r', encoding='utf-8') as f:
        return json.load(f)

# Initialize Workday client
try:
    workday_config = load_workday_config()
    workday_client = WorkdayClient(workday_config)
except Exception as e:
    print(f"Warning: Could not initialize Workday client: {e}")
    workday_client = None

# Environment detection
def is_local_environment() -> bool:
    """Check if running locally (not Heroku)"""
    return os.getenv('DYNO') is None

# Load employee data
def load_employees() -> List[Dict]:
    """Load employee data from JSON file"""
    try:
        with open("data/employees.json", "r") as file:
            data = json.load(file)
            return data["employees"]
    except FileNotFoundError:
        return []

def get_employee_by_id(employee_id: int) -> Optional[Dict]:
    """Get a specific employee by ID"""
    employees = load_employees()
    for employee in employees:
        if employee["employee_id"] == employee_id:
            return employee
    return None

@app.get("/")
def read_root():
    """
    Root endpoint that returns a welcome message
    """
    return {
        "message": "Hello World! This is a FastAPI Employee Management System running on Heroku!",
        "features": [
            "Employee directory at /employees",
            "Individual employee pages at /employee/{id}",
            "JSON API endpoints at /api/employee/{id}",
            "Interactive docs at /docs"
        ],
        "sample_employees": [101, 102, 103, 104, 105, 106]
    }

# HTML ENDPOINTS
@app.get("/employees", response_class=HTMLResponse)
async def employees_page(request: Request):
    """
    HTML page showing all employees
    """
    employees = load_employees()
    return templates.TemplateResponse("employees.html.jinja", {
        "request": request, 
        "employees": employees
    })

@app.get("/employee/{employee_id}", response_class=HTMLResponse)
async def employee_page(request: Request, employee_id: int):
    """
    Employee page - returns HTML
    """
    employee = get_employee_by_id(employee_id)
    if not employee:
        return templates.TemplateResponse("employee_not_found.html.jinja", {
            "request": request,
            "employee_id": employee_id
        }, status_code=404)
    
    return templates.TemplateResponse("employee.html.jinja", {
        "request": request,
        "employee": employee
    })

@app.get("/talent-card/{employee_id}", response_class=HTMLResponse)
async def talent_card_page(request: Request, employee_id: str):
    """
    Talent Card page - fetches data from Workday API and renders talent card HTML
    
    This endpoint:
    1. Fetches fresh employee data from Workday REST API
    2. Renders the talent-card.html.jinja template 
    3. Returns HTML response for Power Automate integration
    4. Optionally saves HTML file locally for development
    """
    if not workday_client:
        raise HTTPException(
            status_code=500, 
            detail="Workday client not configured. Please check config/workday_config.json"
        )
    
    try:
        # Fetch employee profile data from Workday API
        print(f"Fetching talent card data for employee {employee_id}...")
        profile_data = workday_client.get_employee_profile(employee_id)
        
        # Render talent card template to string
        from jinja2 import Environment, FileSystemLoader
        
        # Create a Jinja2 environment for direct string rendering
        env = Environment(loader=FileSystemLoader("templates"))
        template = env.get_template("talent-card.html.jinja")
        
        # Render template with profile data
        html_string = template.render(**profile_data)
        
        # Save to local file if running in local environment
        if is_local_environment():
            output_dir = Path("output")
            output_dir.mkdir(exist_ok=True)
            output_file = output_dir / f"talent-card-{employee_id}.html"
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(html_string)
            
            print(f"✓ Talent card saved locally: {output_file}")
        
        # Extract employee name for logging
        entry = profile_data.get('Report_Entry', [{}])[0]
        worker_field = entry.get('Worker', '')
        employee_name = worker_field.split('(')[0].strip() if worker_field else f"employee {employee_id}"
        
        print(f"✓ Talent card generated for {employee_name}")
        
        # Return HTML response
        return HTMLResponse(content=html_string)
        
    except Exception as e:
        print(f"Error generating talent card for employee {employee_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate talent card: {str(e)}"
        )

# JSON API ENDPOINTS
@app.get("/api/employees")
def api_get_all_employees():
    """
    JSON API endpoint to get all employees
    """
    employees = load_employees()
    return {"employees": employees, "count": len(employees)}

@app.get("/api/employee/{employee_id}")
def api_get_employee(employee_id: int):
    """
    API endpoint to get employee data as JSON
    """
    employee = get_employee_by_id(employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    return employee

@app.get("/api/employee/{employee_id}/link")
def api_get_employee_link(employee_id: int, request: Request):
    """
    Power Automate friendly endpoint - returns link information
    """
    employee = get_employee_by_id(employee_id)
    if not employee:
        return {
            "success": False,
            "error": "Employee not found",
            "employee_id": employee_id,
            "message": f"Employee with ID {employee_id} does not exist."
        }
    
    # Build the full URL dynamically
    base_url = str(request.url).replace("/api/employee/" + str(employee_id) + "/link", "")
    profile_url = f"{base_url}/employee/{employee_id}"
    
    return {
        "success": True,
        "employee_id": employee_id,
        "employee_name": employee["name"],
        "profile_url": profile_url,
        "message": f"Employee profile for {employee['name']}: {profile_url}",
        "employee_data": employee
    }

@app.get("/api/employee/{employee_id}/html")
def api_get_employee_html_content(employee_id: int, request: Request):
    """
    Returns HTML content for saving to SharePoint
    """
    employee = get_employee_by_id(employee_id)
    if not employee:
        return {
            "success": False,
            "error": "Employee not found",
            "employee_id": employee_id
        }
    
    # Generate the same HTML that the template would create
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Employee Details - {employee['name']}</title>
    <link rel="stylesheet" href="{str(request.url).replace('/api/employee/' + str(employee_id) + '/html', '')}/static/style.css">
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Employee Profile</h1>
            <p>FastAPI Employee Management System</p>
        </div>

        <div class="employee-card">
            <div class="employee-name">{employee['name']}</div>
            
            <div class="employee-info">
                <div class="info-item">
                    <div class="info-label">Employee ID</div>
                    <div class="info-value">{employee['employee_id']}</div>
                </div>
                
                <div class="info-item">
                    <div class="info-label">Position</div>
                    <div class="info-value">{employee['position']}</div>
                </div>
                
                <div class="info-item">
                    <div class="info-label">Department</div>
                    <div class="info-value">{employee['department']}</div>
                </div>
                
                <div class="info-item">
                    <div class="info-label">Manager</div>
                    <div class="info-value">{employee['manager']}</div>
                </div>
                
                <div class="info-item">
                    <div class="info-label">Email</div>
                    <div class="info-value">
                        <a href="mailto:{employee['email']}">{employee['email']}</a>
                    </div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>"""

    return {
        "success": True,
        "employee_id": employee_id,
        "employee_name": employee["name"],
        "html_content": html_content,
        "suggested_filename": f"employee_{employee_id}_{employee['name'].lower().replace(' ', '_')}.html"
    }

@app.get("/health")
def health_check():
    """
    Health check endpoint
    """
    return {"status": "healthy", "message": "API is running successfully"}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: str = None):
    """
    Example endpoint with path and query parameters
    """
    return {"item_id": item_id, "q": q, "message": f"You requested item {item_id}"}

@app.get("/info")
def get_info():
    """
    Endpoint that returns some environment information
    """
    port = os.getenv("PORT", "8000")
    return {
        "app": "Simple FastAPI",
        "port": port,
        "environment": "Heroku" if os.getenv("DYNO") else "Local"
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)