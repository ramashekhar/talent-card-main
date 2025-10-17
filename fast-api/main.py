from fastapi import FastAPI, Request, HTTPException, Query
from fastapi.responses import HTMLResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
import json
from typing import List, Dict, Optional
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
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
    """Generate PDF from employee data using ReportLab"""
    try:
        # Create a BytesIO buffer to hold PDF data
        buffer = BytesIO()
        
        # Create PDF document
        doc = SimpleDocTemplate(buffer, pagesize=A4, 
                              rightMargin=72, leftMargin=72,
                              topMargin=72, bottomMargin=18)
        
        # Get styles
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            textColor=colors.HexColor('#007bff'),
            alignment=1  # Center alignment
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            spaceBefore=12,
            spaceAfter=6,
            textColor=colors.HexColor('#495057')
        )
        
        normal_style = ParagraphStyle(
            'CustomNormal',
            parent=styles['Normal'],
            fontSize=12,
            spaceBefore=6,
            spaceAfter=6
        )
        
        # Build PDF content
        story = []
        
        # Title
        story.append(Paragraph("Employee Profile", title_style))
        story.append(Spacer(1, 12))
        
        # Employee name
        story.append(Paragraph(f"<b>{employee['name']}</b>", heading_style))
        story.append(Spacer(1, 12))
        
        # Employee details table
        data = [
            ['Employee ID:', str(employee['employee_id'])],
            ['Position:', employee['position']],
            ['Department:', employee['department']],
            ['Manager:', employee['manager']],
            ['Email:', employee['email']]
        ]
        
        table = Table(data, colWidths=[2*inch, 4*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f8f9fa')),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#495057')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('TOPPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#dee2e6'))
        ]))
        
        story.append(table)
        story.append(Spacer(1, 20))
        
        # Footer
        import datetime
        footer_text = f"Generated on {datetime.datetime.now().strftime('%B %d, %Y')}"
        story.append(Paragraph(footer_text, normal_style))
        
        # Build PDF
        doc.build(story)
        
        # Get PDF bytes
        pdf_bytes = buffer.getvalue()
        buffer.close()
        
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