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

# Workday client setup
def load_workday_config() -> Dict:
    """
    Load Workday API configuration with hybrid approach:
    - Sensitive credentials (username/password) from environment variables
    - Non-sensitive config (endpoints, version) from config file
    """
    
    # Always load base config from file (use production config for Heroku, local for dev)
    if os.getenv('DYNO'):  # Running on Heroku
        config_file = Path("config/workday_config_production.json")
    else:  # Running locally
        config_file = Path("config/workday_config.json")
        
    if not config_file.exists():
        raise FileNotFoundError(
            f"Configuration file not found: {config_file}\n"
            f"For Heroku: Use workday_config_production.json (safe for GitHub)\n"
            f"For local: Create workday_config.json with your credentials"
        )
    
    with open(config_file, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    # Override credentials with environment variables if available (Heroku deployment)
    if 'WORKDAY_USERNAME' in os.environ and 'WORKDAY_PASSWORD' in os.environ:
        config['username'] = os.environ['WORKDAY_USERNAME']
        config['password'] = os.environ['WORKDAY_PASSWORD']
        print("✓ Using credentials from environment variables (Heroku)")
    else:
        print("✓ Using credentials from config file (local development)")
    
    # Validate required fields
    required_fields = ['endpoint', 'profile_endpoint', 'username', 'password', 'version']
    missing_fields = [field for field in required_fields if field not in config or not config[field]]
    
    if missing_fields:
        raise ValueError(
            f"Missing required configuration fields: {missing_fields}\n"
            f"Config file should have: endpoint, profile_endpoint, version\n"
            f"Environment variables needed for Heroku: WORKDAY_USERNAME, WORKDAY_PASSWORD"
        )
    
    return config

# Initialize Workday client
try:
    workday_config = load_workday_config()
    workday_client = WorkdayClient(workday_config)
except Exception as e:
    print(f"Warning: Could not initialize Workday client: {e}")
    workday_client = None

def is_local_environment() -> bool:
    """Check if running locally (not Heroku)"""
    return os.getenv('DYNO') is None

@router.get("/talent-card/{employee_id}", response_class=HTMLResponse)
async def get_talent_card(request: Request, employee_id: str):
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