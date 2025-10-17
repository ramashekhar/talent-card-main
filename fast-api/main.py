from fastapi import FastAPI, Request, HTTPException, Query
from fastapi.responses import HTMLResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
import json
from typing import List, Dict, Optional
import pdfkit
from io import BytesIO

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

async def generate_pdf_from_employee_data(employee: Dict) -> bytes:
    """Generate PDF from employee data using pdfkit (pixel-perfect HTML→PDF)"""
    try:
        # Build HTML content that matches our template styling
        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Employee Details - {employee['name']}</title>
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    line-height: 1.6;
                    margin: 0;
                    padding: 20px;
                    background-color: #f5f5f5;
                    color: #333;
                }}
                .container {{
                    max-width: 800px;
                    margin: 0 auto;
                    background: white;
                    padding: 30px;
                    border-radius: 10px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }}
                .header {{
                    text-align: center;
                    margin-bottom: 30px;
                    padding-bottom: 20px;
                    border-bottom: 2px solid #e9ecef;
                }}
                .employee-card {{
                    background: #f8f9fa;
                    padding: 25px;
                    border-radius: 8px;
                    border-left: 5px solid #007bff;
                    margin: 20px 0;
                }}
                .employee-name {{
                    color: #007bff;
                    font-size: 2em;
                    margin-bottom: 10px;
                    font-weight: 600;
                }}
                .employee-info {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                    gap: 15px;
                    margin: 20px 0;
                }}
                .info-item {{
                    background: white;
                    padding: 15px;
                    border-radius: 5px;
                    border: 1px solid #dee2e6;
                }}
                .info-label {{
                    font-weight: bold;
                    color: #495057;
                    font-size: 0.9em;
                    text-transform: uppercase;
                    letter-spacing: 0.5px;
                }}
                .info-value {{
                    margin-top: 5px;
                    font-size: 1.1em;
                    color: #212529;
                }}
                .footer {{
                    margin-top: 30px;
                    padding-top: 20px;
                    border-top: 1px solid #e9ecef;
                    text-align: center;
                    font-size: 0.9em;
                    color: #6c757d;
                }}
            </style>
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
                            <div class="info-value">{employee['email']}</div>
                        </div>
                    </div>
                </div>

                <div class="footer">
                    Generated on {__import__('datetime').datetime.now().strftime('%B %d, %Y')}
                </div>
            </div>
        </body>
        </html>
        """
        
        # Configure pdfkit options for better quality
        options = {
            'page-size': 'A4',
            'margin-top': '0.75in',
            'margin-right': '0.75in',
            'margin-bottom': '0.75in',
            'margin-left': '0.75in',
            'encoding': "UTF-8",
            'no-outline': None,
            'enable-local-file-access': None
        }
        
        # Generate PDF from HTML
        try:
            pdf_bytes = pdfkit.from_string(html_content, False, options=options)
        except (OSError, IOError) as e:
            if "wkhtmltopdf" in str(e):
                # On local development without wkhtmltopdf, provide helpful error
                raise HTTPException(
                    status_code=503, 
                    detail={
                        "error": "PDF generation unavailable",
                        "reason": "wkhtmltopdf binary not found",
                        "local_development": "Install wkhtmltopdf from https://wkhtmltopdf.org/downloads.html",
                        "heroku_deployment": "PDF generation will work on Heroku with configured buildpacks",
                        "html_alternative": f"View HTML version at /employee/{employee['employee_id']}"
                    }
                )
            raise
        
        return pdf_bytes
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")



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
        # Generate PDF directly from employee data
        pdf_bytes = await generate_pdf_from_employee_data(employee)
        
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
        # Generate PDF directly from employee data
        pdf_bytes = await generate_pdf_from_employee_data(employee)
        
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