"""
Talent Card Generation Endpoints

Handles talent card generation using Workday API integration.
Fetches live data from Workday and renders professional talent cards.
"""

from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse
from jinja2 import Environment, FileSystemLoader
import os
import json
import html  # Add this import for HTML entity decoding
from pathlib import Path
from typing import Dict

# Import Workday client
from src.workday_client import WorkdayClient

router = APIRouter()

# Get default tenant from environment variable (either 'csc' or 'gms'), default to 'gms'
DEFAULT_TENANT = os.getenv('WORKDAY_TENANT', 'gms').lower()

# Workday client setup
def load_workday_config(tenant: str = None) -> Dict:
    """
    Load Workday API configuration with hybrid approach:
    - Sensitive credentials (username/password) from environment variables
    - Non-sensitive config (endpoints, version) from config file
    
    Args:
        tenant: Tenant identifier ('csc' or 'gms'). If None, uses DEFAULT_TENANT.
    """
    # Use provided tenant or fall back to default
    tenant = (tenant or DEFAULT_TENANT).lower()
    
    # Validate tenant
    if tenant not in ['csc', 'gms']:
        raise ValueError(f"Invalid tenant '{tenant}'. Must be 'csc' or 'gms'")
    
    # --- Deployment Environment Detection ---
    # Heroku sets DYNO, Azure sets WEBSITE_INSTANCE_ID
    # If either is present, we treat as production.
    is_heroku = os.getenv('DYNO') is not None  # True if running on Heroku
    is_azure = os.getenv('WEBSITE_INSTANCE_ID') is not None  # True if running on Azure
    is_production = is_heroku or is_azure  # Production if either is true

    if is_production:  # Running on Heroku or Azure
        config_file = Path(f"config/workday_config_production-{tenant}.json")
    else:  # Running locally
        config_file = Path(f"config/workday_config-{tenant}.json")
        
    if not config_file.exists():
        raise FileNotFoundError(
            f"Configuration file not found: {config_file}\n"
            f"Tenant: {tenant} (from query string or WORKDAY_TENANT env variable)\n"
            f"For production: Use workday_config_production-{tenant}.json\n"
            f"For local: Create workday_config-{tenant}.json with your credentials"
        )
    
    with open(config_file, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    # Override credentials with tenant-specific environment variables if available
    username_key = f'WORKDAY_USERNAME_{tenant.upper()}'
    password_key = f'WORKDAY_PASSWORD_{tenant.upper()}'
    
    if username_key in os.environ and password_key in os.environ:
        config['username'] = os.environ[username_key]
        config['password'] = os.environ[password_key]
        print(f"✓ Using credentials from environment variables for {tenant.upper()} (Heroku/Azure)")
    else:
        print(f"✓ Using credentials from config file for {tenant.upper()} (local development)")
    
    # Validate required fields
    required_fields = ['endpoint', 'username', 'password', 'version']
    missing_fields = [field for field in required_fields if field not in config or not config[field]]
    
    if missing_fields:
        raise ValueError(
            f"Missing required configuration fields: {missing_fields}\n"
            f"Config file should have: endpoint, profile_endpoint, version\n"
            f"Environment variables needed for Heroku: WORKDAY_USERNAME, WORKDAY_PASSWORD"
        )
    
    return config

def get_workday_client(tenant: str = None) -> WorkdayClient:
    """
    Get or create a Workday client for the specified tenant.
    
    Args:
        tenant: Tenant identifier ('csc' or 'gms'). If None, uses DEFAULT_TENANT.
    
    Returns:
        WorkdayClient instance configured for the tenant
    """
    config = load_workday_config(tenant)
    return WorkdayClient(config)

def is_local_environment() -> bool:
    """Check if running locally (not Heroku or Azure)"""
    return os.getenv('DYNO') is None and os.getenv('WEBSITE_INSTANCE_ID') is None

@router.get("/talent-card/{employee_id}", response_class=HTMLResponse)
async def get_talent_card(request: Request, employee_id: str, tenant: str = None):
    """
    Talent Card page - fetches data from Workday API and renders talent card HTML
    
    This endpoint:
    1. Fetches fresh employee data from Workday REST API
    2. Renders the tenant-specific talent-card template
    3. Returns HTML response for Power Automate integration
    4. Optionally saves HTML file locally for development
    
    Args:
        employee_id: Employee ID to generate card for
        tenant: Optional tenant query parameter ('csc' or 'gms'). 
                Defaults to WORKDAY_TENANT env variable or 'gms'.
    
    Example URLs:
        - /talent-card/21103 (uses default tenant from env)
        - /talent-card/21103?tenant=gms
        - /talent-card/1000130722?tenant=csc
    """
    # Use provided tenant or fall back to default
    tenant = (tenant or DEFAULT_TENANT).lower()
    
    try:
        # Validate tenant
        if tenant not in ['csc', 'gms']:
            raise ValueError(f"Invalid tenant '{tenant}'. Must be 'csc' or 'gms'")
        
        # Get Workday client for the specified tenant
        workday_client = get_workday_client(tenant)
        
        # Fetch employee profile data from Workday API
        print(f"[{tenant.upper()}] Fetching talent card data for employee {employee_id}...")
        profile_data = workday_client.get_employee_profile(employee_id)
        
        # Render talent card template to string
        env = Environment(loader=FileSystemLoader("templates"))
        
        # Add custom filters for Power Automate HTML-to-PDF compatibility
        def decode_html_entities(text):
            """Decode HTML entities like &#39; to prevent Power Automate HTML-to-PDF issues"""
            if text and isinstance(text, str):
                return html.unescape(text)
            return text
        
        def fix_empty_paragraphs(text):
            """Replace empty <p></p> tags with <p>&nbsp;</p> for proper spacing and Power Automate compatibility"""
            if text and isinstance(text, str):
                return text.replace('<p></p>', '<p>&nbsp;</p>')
            return text
        
        env.filters['decode_entities'] = decode_html_entities
        env.filters['fix_empty_paragraphs'] = fix_empty_paragraphs
        template = env.get_template(f"talent-card-{tenant}.html.jinja")
        
        # Render template with profile data
        html_string = template.render(**profile_data)
        
        # Save to local file if running in local environment
        if is_local_environment():
            output_dir = Path("output")
            output_dir.mkdir(exist_ok=True)
            output_file = output_dir / f"talent-card-{tenant}-{employee_id}.html"
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(html_string)
            
            print(f"✓ Talent card saved locally: {output_file}")
        
        # Extract employee name for logging
        entry = profile_data.get('Report_Entry', [{}])[0]
        worker_field = entry.get('Worker', '')
        employee_name = worker_field.split('(')[0].strip() if worker_field else f"employee {employee_id}"
        
        print(f"✓ [{tenant.upper()}] Talent card generated for {employee_name}")
        
        # Return HTML response
        return HTMLResponse(content=html_string)
    
    except ValueError as e:
        # Invalid tenant error
        print(f"Invalid tenant '{tenant}': {str(e)}")
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        print(f"[{tenant.upper()}] Error generating talent card for employee {employee_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate talent card: {str(e)}"
        )