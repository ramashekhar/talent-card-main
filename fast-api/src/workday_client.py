"""
Workday SOAP API Client Module

This module provides a client for interacting with Workday's SOAP-based Human Resources API.
It handles SOAP envelope construction, WS-Security authentication, and XML response parsing.

Classes:
    WorkdayClient: SOAP client for fetching person photos from Workday

Usage:
    client = WorkdayClient(config)
    base64_photo = client.get_person_photo(employee_id)
"""

import requests
import xml.etree.ElementTree as ET
from pathlib import Path
from jinja2 import Template
from typing import Optional, Dict


class WorkdayClient:
    """
    SOAP client for Workday Human Resources API.
    
    This client handles authentication, request construction, and response parsing
    for Workday's Get_Person_Photos operation.
    
    Attributes:
        endpoint (str): Workday API endpoint URL
        username (str): Workday username for WS-Security authentication
        password (str): Workday password for WS-Security authentication
        version (str): Workday API version (e.g., "v44.1")
    """
    
    # XML namespaces used in SOAP requests/responses
    NAMESPACES = {
        'env': 'http://schemas.xmlsoap.org/soap/envelope/',
        'wsse': 'http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd',
        'wd': 'urn:com.workday/bsvc'
    }
    
    def __init__(self, config: Dict[str, str]):
        """
        Initialize Workday client with configuration.
        
        Args:
            config (dict): Configuration dictionary containing:
                - endpoint: Workday API endpoint URL (SOAP for photos)
                - profile_endpoint: REST API endpoint URL (for profile data)
                - username: Authentication username
                - password: Authentication password
                - version: API version (e.g., "v44.1")
        """
        self.endpoint = config['endpoint']
        self.profile_endpoint = config.get('profile_endpoint')
        self.username = config['username']
        self.password = config['password']
        self.version = config['version']
        
        # Load SOAP request template (optional - only needed for SOAP photo calls)
        template_path = Path(__file__).parent.parent / "api" / "Get_Person_Photos_Request_Template.jinja"
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                self.request_template = Template(f.read())
        except FileNotFoundError:
            # SOAP template not found - SOAP functionality will be disabled
            self.request_template = None
    
    def build_soap_request(self, employee_id: str) -> str:
        """
        Build SOAP XML request for Get_Person_Photos operation using Jinja2 template.
        
        Constructs a complete SOAP envelope with WS-Security authentication header
        and Get_Person_Photos_Request body by rendering the template with provided values.
        
        Args:
            employee_id (str): Employee ID to fetch photo for
            
        Returns:
            str: Complete SOAP XML request as string
            
        Raises:
            Exception: If SOAP template is not available
        """
        if not self.request_template:
            raise Exception("SOAP template not available. SOAP functionality disabled.")
            
        soap_request = self.request_template.render(
            username=self.username,
            password=self.password,
            version=self.version,
            employee_id=employee_id
        )
        return soap_request
    
    def call_api(self, soap_request: str) -> str:
        """
        Make HTTP POST request to Workday API.
        
        Sends SOAP request to Workday endpoint with appropriate headers.
        
        Args:
            soap_request (str): SOAP XML request body
            
        Returns:
            str: XML response from Workday API
            
        Raises:
            requests.exceptions.RequestException: If HTTP request fails
            Exception: If API returns error status code
        """
        headers = {
            'Content-Type': 'text/xml; charset=utf-8',
            'SOAPAction': ''
        }
        
        try:
            response = requests.post(
                self.endpoint,
                data=soap_request.encode('utf-8'),
                headers=headers,
                timeout=30
            )
            
            # Raise exception for 4xx/5xx status codes
            response.raise_for_status()
            
            return response.text
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"API request failed: {str(e)}")
    
    def parse_response(self, xml_response: str) -> Optional[str]:
        """
        Parse Workday XML response and extract Base64 photo data.
        
        Extracts the Base64-encoded image data from the <wd:File> tag
        in the SOAP response.
        
        Args:
            xml_response (str): XML response from Workday API
            
        Returns:
            str: Base64-encoded photo data, or None if not found
            
        Raises:
            Exception: If XML parsing fails or response contains SOAP fault
        """
        try:
            # Parse XML response
            root = ET.fromstring(xml_response)
            
            # Check for SOAP Fault (error response)
            fault = root.find('.//env:Fault', self.NAMESPACES)
            if fault is not None:
                fault_string = fault.find('.//faultstring')
                error_msg = fault_string.text if fault_string is not None else "Unknown SOAP fault"
                raise Exception(f"Workday API returned error: {error_msg}")
            
            # Extract Base64 data from <wd:File> tag
            file_element = root.find('.//wd:File', self.NAMESPACES)
            
            if file_element is not None and file_element.text:
                return file_element.text.strip()
            else:
                return None
                
        except ET.ParseError as e:
            raise Exception(f"Failed to parse XML response: {str(e)}")
    
    def get_person_photo(self, employee_id: str) -> Optional[str]:
        """
        Fetch person photo from Workday API.
        
        High-level method that orchestrates the complete workflow:
        1. Build SOAP request
        2. Call Workday API
        3. Parse response and extract Base64 photo
        
        Args:
            employee_id (str): Employee ID to fetch photo for
            
        Returns:
            str: Base64-encoded photo data, or None if not found
            
        Raises:
            Exception: If any step in the workflow fails
        """
        # Build SOAP request
        soap_request = self.build_soap_request(employee_id)
        
        # Call API
        xml_response = self.call_api(soap_request)
        
        # Parse response and extract Base64
        base64_data = self.parse_response(xml_response)
        
        return base64_data
    
    def get_employee_profile(self, employee_id: str) -> Dict:
        """
        Fetch complete employee profile from Workday REST API.
        
        Makes GET request to custom report endpoint with HTTP Basic Auth.
        Returns complete JSON response including Report_Entry with base64 photo.
        
        This is a REST API call (not SOAP) that returns the full v4 JSON structure
        including employee data, performance history, and embedded Base64 photo.
        
        Args:
            employee_id (str): Employee ID to fetch profile for
            
        Returns:
            dict: Complete profile JSON (v4 structure with Report_Entry[])
            
        Raises:
            Exception: If API request fails, authentication fails, or response is invalid
        """
        if not self.profile_endpoint:
            raise Exception("Profile endpoint not configured in workday_config.json")
        
        # Build URL with query parameters
        url = f"{self.profile_endpoint}?format=JSON&Employee_ID={employee_id}"
        
        # Extract username without @tenant suffix for REST API
        # REST API uses just the numeric ID, not the full SOAP username
        rest_username = self.username.split('@')[0] if '@' in self.username else self.username
        
        try:
            # Make GET request with HTTP Basic Auth (using username without @tenant)
            response = requests.get(
                url,
                auth=(rest_username, self.password),
                timeout=30
            )
            
            # Raise exception for 4xx/5xx status codes
            response.raise_for_status()
            
            # Parse JSON response
            profile_data = response.json()
            
            # Validate response has Report_Entry
            if 'Report_Entry' not in profile_data:
                raise Exception("Invalid response: missing 'Report_Entry' in JSON")
            
            if not profile_data['Report_Entry']:
                raise Exception(f"No profile data found for employee {employee_id}")
            
            return profile_data
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                raise Exception("Authentication failed: Invalid credentials")
            elif e.response.status_code == 404:
                raise Exception(f"Employee {employee_id} not found")
            else:
                raise Exception(f"HTTP error: {str(e)}")
                
        except requests.exceptions.RequestException as e:
            raise Exception(f"API request failed: {str(e)}")
            
        except ValueError as e:
            raise Exception(f"Invalid JSON response: {str(e)}")
