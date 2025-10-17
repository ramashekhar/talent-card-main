from fastapi import FastAPI, Request, HTTPException, Query
from fastapi.responses import HTMLResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
import json
from typing import List, Dict, Optional
from playwright.async_api import async_playwright
import asyncio

# Set Playwright environment variables for Heroku
if os.getenv("DYNO"):  # Running on Heroku
    os.environ["PLAYWRIGHT_BROWSERS_PATH"] = "/app/.playwright"

# Try to import WeasyPrint for fallback
try:
    from weasyprint import HTML, CSS
    WEASYPRINT_AVAILABLE = True
except ImportError:
    WEASYPRINT_AVAILABLE = False

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

async def generate_pdf_with_weasyprint(html_content: str) -> bytes:
    """Generate PDF using WeasyPrint as fallback"""
    try:
        if not WEASYPRINT_AVAILABLE:
            raise Exception("WeasyPrint not available")
        
        # Generate PDF from HTML string
        pdf_bytes = HTML(string=html_content).write_pdf()
        return pdf_bytes
    except Exception as e:
        raise Exception(f"WeasyPrint PDF generation failed: {str(e)}")

async def ensure_playwright_ready():
    """Ensure Playwright browsers are installed and ready"""
    if os.getenv("DYNO"):  # Running on Heroku
        try:
            # Try to install browsers if not present
            import subprocess
            result = subprocess.run(
                ["python", "-m", "playwright", "install", "chromium"],
                capture_output=True, text=True, timeout=120
            )
            return True
        except Exception as e:
            print(f"Playwright setup failed: {e}")
            return False
    return True

async def generate_pdf_from_html(html_content: str, employee_name: str = "employee") -> bytes:
    """Generate PDF from HTML content using Playwright with WeasyPrint fallback"""
    
    # First, try WeasyPrint (more reliable on Heroku)
    if WEASYPRINT_AVAILABLE:
        try:
            print("Attempting PDF generation with WeasyPrint...")
            return await generate_pdf_with_weasyprint(html_content)
        except Exception as e:
            print(f"WeasyPrint failed: {e}, trying Playwright...")
    
    # Fallback to Playwright
    try:
        # Ensure Playwright is ready
        if not await ensure_playwright_ready():
            raise HTTPException(status_code=500, detail="PDF service initialization failed")
            
        print("Attempting PDF generation with Playwright...")
        async with async_playwright() as p:
            # Launch browser with Heroku-compatible settings
            browser = await p.chromium.launch(
                headless=True,
                args=[
                    '--no-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-gpu',
                    '--no-first-run',
                    '--no-zygote',
                    '--single-process',
                    '--disable-extensions',
                    '--disable-background-timer-throttling',
                    '--disable-backgrounding-occluded-windows',
                    '--disable-renderer-backgrounding'
                ]
            )
            page = await browser.new_page()
            await page.set_content(html_content, wait_until='networkidle')
            
            # Generate PDF with professional settings
            pdf_bytes = await page.pdf(
                format='A4',
                margin={
                    'top': '20mm',
                    'bottom': '20mm', 
                    'left': '20mm',
                    'right': '20mm'
                },
                print_background=True,  # Include background colors/images
                prefer_css_page_size=True
            )
            
            await browser.close()
            return pdf_bytes
    except Exception as e:
        # Final fallback error
        error_msg = f"Both PDF generation methods failed. Playwright: {str(e)}"
        if not WEASYPRINT_AVAILABLE:
            error_msg += " WeasyPrint: Not available"
        print(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)

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
            "PDF generation with ?format=pdf parameter",
            "JSON API endpoints at /api/employee/{id}",
            "Interactive docs at /docs"
        ],
        "sample_employees": [101, 102, 103, 104, 105, 106],
        "pdf_examples": [
            "/employee/101?format=pdf",
            "/api/employee/102?format=pdf"
        ]
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

@app.get("/employee/{employee_id}")
async def employee_page(request: Request, employee_id: int, format: str = Query(default="html", pattern="^(html|pdf)$")):
    """
    Employee page - returns HTML by default, PDF if format=pdf
    """
    employee = get_employee_by_id(employee_id)
    if not employee:
        if format == "pdf":
            raise HTTPException(status_code=404, detail="Employee not found")
        return templates.TemplateResponse("employee_not_found.html.jinja", {
            "request": request,
            "employee_id": employee_id
        }, status_code=404)
    
    # Generate HTML content
    html_response = templates.TemplateResponse("employee.html.jinja", {
        "request": request,
        "employee": employee
    })
    
    if format == "pdf":
        # Get the HTML content
        html_content = html_response.body.decode('utf-8') if hasattr(html_response, 'body') else str(html_response)
        
        # If we can't get the body directly, render the template manually
        if not hasattr(html_response, 'body'):
            html_content = templates.get_template("employee.html.jinja").render(
                request=request, 
                employee=employee
            )
        
        # Generate PDF
        pdf_bytes = await generate_pdf_from_html(html_content, employee["name"])
        
        # Create filename
        safe_name = employee["name"].lower().replace(" ", "_").replace(".", "")
        filename = f"employee_{employee_id}_{safe_name}.pdf"
        
        # Return PDF response
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
    
    return html_response

# JSON API ENDPOINTS
@app.get("/api/employees")
def api_get_all_employees():
    """
    JSON API endpoint to get all employees
    """
    employees = load_employees()
    return {"employees": employees, "count": len(employees)}

@app.get("/api/employee/{employee_id}")
async def api_get_employee(employee_id: int, format: str = Query(default="json", pattern="^(json|pdf)$")):
    """
    API endpoint to get employee data - JSON by default, PDF if format=pdf
    """
    employee = get_employee_by_id(employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    if format == "pdf":
        # Create a simple request object for template rendering
        from fastapi import Request
        from fastapi.templating import Jinja2Templates
        
        # Create a mock request for template rendering
        class MockRequest:
            def __init__(self):
                self.url = f"http://localhost/api/employee/{employee_id}"
                self.base_url = "http://localhost"
        
        mock_request = MockRequest()
        
        # Render HTML template
        html_content = templates.get_template("employee.html.jinja").render(
            request=mock_request,
            employee=employee
        )
        
        # Generate PDF
        pdf_bytes = await generate_pdf_from_html(html_content, employee["name"])
        
        # Create filename
        safe_name = employee["name"].lower().replace(" ", "_").replace(".", "")
        filename = f"employee_{employee_id}_{safe_name}.pdf"
        
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
    
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