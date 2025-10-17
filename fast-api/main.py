from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
import json
from typing import List, Dict, Optional

# Create FastAPI instance
app = FastAPI(title="Employee Management API", version="1.0.0")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Set up templates
templates = Jinja2Templates(directory="templates")

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