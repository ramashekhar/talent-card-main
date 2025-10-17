"""
Employee Testing Endpoints

Provides employee pages for testing purposes using local JSON data.
Used for development and testing both locally and on Heroku.
Main functionality is handled by talent_cards.py with Workday API.
"""

from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import json
from typing import Dict, Optional

router = APIRouter()
templates = Jinja2Templates(directory="templates")

def load_employees() -> list:
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

@router.get("/employee/{employee_id}", response_class=HTMLResponse)
async def get_employee(request: Request, employee_id: int):
    """
    Individual employee page - returns HTML from local directory
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