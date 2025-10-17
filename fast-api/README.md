# Talent Card Generator - Enterprise FastAPI Application

A professional FastAPI application that integrates with Workday HR systems to generate A4 landscape talent cards for organizational talent management and Power Automate workflows.

## 🎯 **Core Features**

### **Enterprise Integration**
- **Workday REST API**: Live employee data retrieval from HR systems
- **Modular Architecture**: Router-based FastAPI structure for maintainability  
- **Security-First**: Environment variable credentials, no sensitive data in code
- **Professional Templates**: A4 landscape cards with embedded corporate styling

### **Production Capabilities**
- **Power Automate Ready**: HTML output optimized for OneDrive HTML→PDF conversion
- **Dual-Mode Operation**: Local development with file output + Production in-memory processing
- **Missing Photo Handling**: Graceful SVG placeholder fallback for employees without profile images
- **CORS Enabled**: Cross-origin requests for Power Automate integration
- **Health Monitoring**: Built-in health check and system monitoring endpoints

## 🚀 **Quick Start**

### **Prerequisites**
- Python 3.11.6
- Workday HR system access with custom report permissions
- Git and terminal access

### **1. Local Development Setup**

#### **Configuration (Development)**
For local development, create your configuration file with credentials:

1. **Copy the example configuration**:
   ```bash
   cp config/workday_config.example.json config/workday_config.json
   ```

2. **Edit `config/workday_config.json`** with your Workday credentials:
   ```json
   {
     "endpoint": "https://wd5-impl-services1.workday.com/ccx/service/YOUR_TENANT/Human_Resources/v44.1",
     "profile_endpoint": "https://wd5-impl-services1.workday.com/ccx/service/customreport2/YOUR_TENANT/YOUR_REPORT_ID/AI_Campbell_Talent_Card",
     "username": "YOUR_USERNAME@YOUR_TENANT",
     "password": "YOUR_PASSWORD",
     "version": "v44.1",
     "tenant": "YOUR_TENANT"
   }
   ```

   **Replace placeholders:**
   - `YOUR_TENANT` → Your Workday tenant name (e.g., "campbellsoup1")
   - `YOUR_REPORT_ID` → Your custom report ID for talent cards
   - `YOUR_USERNAME` → Your Workday username
   - `YOUR_PASSWORD` → Your Workday password

#### **⚠️ Security Note**: Never commit `workday_config.json` - it's in .gitignore

### **2. Install & Run**

#### **Install Dependencies**
```bash
# Note: Dependencies are managed at repository root level
cd ..  # Navigate to repository root
pip install -r requirements.txt
cd fast-api  # Back to project directory
```

#### **Start Development Server**
```bash
# Option 1: Direct uvicorn (recommended)
python -c "import uvicorn; from main import app; uvicorn.run(app, host='0.0.0.0', port=8001)"

# Option 2: Background server
uvicorn main:app --reload --host 0.0.0.0 --port 8001
```

#### **Access Application**
- **Main Application**: http://localhost:8001
- **API Documentation**: http://localhost:8001/docs
- **Health Check**: http://localhost:8001/health

### **3. Test Endpoints**

#### **Talent Card Generation (Live Workday Data)**
```bash
# Generate talent card for specific employee
curl http://localhost:8001/talent-card/1000130722

# Or visit in browser
http://localhost:8001/talent-card/1000130722
```

#### **Employee Testing (Local Test Data)**
```bash
# Test with sample employee data
curl http://localhost:8001/employee/101

# Or visit in browser  
http://localhost:8001/employee/101
```

### **🔧 Local Development Features**
- **File Output**: HTML files automatically saved to `output/` folder
- **Live Workday Data**: Real-time API calls for accurate testing
- **Template Debugging**: Immediate feedback on template changes
- **Hot Reload**: Server restarts automatically on code changes
- **Interactive Docs**: FastAPI auto-generated API documentation

## 📡 **API Reference**

### **Production Endpoints**

| Method | Endpoint | Description | Use Case |
|--------|----------|-------------|----------|
| `GET` | `/talent-card/{employee_id}` | Generate professional talent card HTML | **Primary**: Power Automate workflows |
| `GET` | `/health` | System health and status check | **Monitoring**: Uptime verification |
| `GET` | `/docs` | Interactive API documentation | **Development**: Endpoint testing |

### **Development Endpoints**

| Method | Endpoint | Description | Use Case |
|--------|----------|-------------|----------|
| `GET` | `/employee/{employee_id}` | Employee testing with local data | **Development**: Template testing |
| `GET` | `/` | Welcome message and system info | **Development**: Basic connectivity |

### **Response Formats**

#### **Talent Card Response**
```http
GET /talent-card/1000130722
Content-Type: text/html
Status: 200 OK

<!DOCTYPE html>
<html lang="en">
<head>
    <title>Employee Profile - Modern Layout</title>
    <style>/* A4 landscape professional styling */</style>
</head>
<body>
    <!-- Professional talent card with employee data -->
</body>
</html>
```

#### **Health Check Response**  
```json
{
  "status": "healthy",
  "timestamp": "2025-10-17T10:30:00Z",
  "environment": "development",
  "workday_client": "configured"
}
```## 🚀 **Production Deployment**

### **Heroku Deployment (Recommended)**

#### **Environment Detection**
The application automatically detects Heroku environment (`DYNO` environment variable) and switches to secure production mode:

- **🔒 No File Storage**: All HTML processing in memory only
- **📊 Fresh Data**: Direct API calls to Workday for live employee data  
- **🌐 CORS Enabled**: Cross-origin requests for Power Automate integration
- **📁 Production Config**: Uses `config/workday_config_production.json` (GitHub-safe)
- **🔐 Environment Variables**: Credentials from Heroku Config Vars

#### **Deployment Steps**

1. **Set Heroku Config Variables** (credentials):
   ```bash
   heroku config:set WORKDAY_USERNAME=your_username@your_tenant
   heroku config:set WORKDAY_PASSWORD=your_password
   ```

2. **Deploy via GitHub Integration** (recommended):
   - Connect your GitHub repository in Heroku Dashboard
   - Enable automatic deploys from main branch
   - Deploy immediately or push to trigger deployment

3. **Or deploy via Git**:
   ```bash
   git push heroku main
   ```

#### **Production Configuration**
- **Config File**: Uses `workday_config_production.json` (safe for GitHub)
- **Credentials**: Retrieved from `WORKDAY_USERNAME` and `WORKDAY_PASSWORD` environment variables
- **Endpoints**: Production endpoints and API version settings
- **Security**: No sensitive data in repository

### **🔐 Security Architecture**

#### **Development vs Production**
| Environment | Config File | Credentials | File Output |
|-------------|-------------|-------------|-------------|
| **Local** | `workday_config.json` | In config file | `output/` folder |
| **Heroku** | `workday_config_production.json` | Environment variables | In-memory only |

#### **Security Best Practices**
- ⚠️ **Never commit** `config/workday_config.json` (contains credentials)
- ✅ **Safe config** `workday_config_production.json` can be committed (no credentials)
- 🔒 **Environment variables** for all sensitive data in production
- 🚫 **No persistent storage** of personal data on production servers
- � **Local file generation** only in development mode

## 🤖 **Power Automate Integration**

### **Workflow Setup**

#### **Step 1: HTTP Request Action**
```
Action: HTTP
Method: GET
URI: https://your-heroku-app.herokuapp.com/talent-card/{employee_id}
Headers: 
  Accept: text/html
```

#### **Step 2: Create HTML File**  
```
Action: OneDrive - Create file
File name: talent-card-{employee_id}.html
File content: {body from HTTP action}
```

#### **Step 3: Convert to PDF**
```
Action: OneDrive - Convert file
Source file: talent-card-{employee_id}.html
Output format: PDF
```

### **Integration Benefits**
- **🚀 High Performance**: FastAPI async processing
- **🔄 Live Data**: Always current employee information from Workday
- **📱 Professional Output**: A4 landscape cards optimized for printing
- **🛡️ Secure**: No data persistence, processing in memory
- **📊 Reliable**: Health monitoring and error handling

### **Example Power Automate Flow**
```json
{
  "trigger": "Manual trigger with employee ID input",
  "actions": [
    {
      "name": "Get Talent Card HTML",
      "type": "HTTP",
      "inputs": {
        "method": "GET", 
        "uri": "https://your-app.herokuapp.com/talent-card/@{triggerBody()['employee_id']}"
      }
    },
    {
      "name": "Create HTML File",
      "type": "OneDrive - Create file",
      "inputs": {
        "fileName": "talent-card-@{triggerBody()['employee_id']}.html",
        "content": "@{body('Get_Talent_Card_HTML')}"
      }
    },
    {
      "name": "Convert to PDF", 
      "type": "OneDrive - Convert file",
      "inputs": {
        "sourceFile": "@{outputs('Create_HTML_File')['body']['id']}",
        "format": "PDF"
      }
    }
  ]
}
```## 🏗️ **Architecture & File Structure**

### **Modular Application Architecture**
```
fast-api/
├── main.py                          ← FastAPI app entry point
├── routers/                         ← Modular endpoint organization
│   ├── talent_cards.py              ← Main: Workday API integration & talent card generation
│   ├── employee.py                  ← Development: Local employee testing
│   └── health.py                    ← System: Health monitoring endpoints
├── src/                             ← Core business logic
│   └── workday_client.py            ← Workday REST API client with authentication
├── config/                          ← Configuration management
│   ├── workday_config_production.json ← Production config (GitHub-safe, no credentials)
│   └── workday_config.example.json    ← Template for local development
├── templates/                       ← Jinja2 template system
│   ├── talent-card.html.jinja       ← A4 landscape professional talent cards
│   └── employee.html.jinja          ← Development testing template
├── static/                          ← CSS and static assets
├── output/                          ← Local development HTML generation (gitignored)
└── README.md                        ← This documentation
```

### **Key Components**

#### **FastAPI Application (`main.py`)**
- Modular router-based architecture
- CORS middleware for Power Automate
- Environment detection (local vs Heroku)
- Health monitoring integration

#### **Workday Integration (`src/workday_client.py`)**
- REST API client with HTTP Basic Auth
- Error handling and response parsing
- Support for custom report endpoints
- Secure credential management

#### **Professional Templates (`templates/`)**
- A4 landscape format (297mm x 210mm)
- Embedded CSS for consistent rendering
- Corporate styling with red theme
- Missing photo handling with SVG placeholders
- Print-optimized for PDF conversion

### **Technology Stack**
- **FastAPI 2.0.0**: Modern async web framework
- **Jinja2**: Professional template engine  
- **Uvicorn/Gunicorn**: Production ASGI server
- **Requests**: HTTP client for Workday API
- **Python 3.11.6**: Latest stable Python version

### **Deployment Files (Repository Root)**
- **`Procfile`**: Heroku process configuration (`cd fast-api && gunicorn main:app...`)
- **`requirements.txt`**: Python dependencies (Heroku uses root-level)
- **`runtime.txt`**: Python version specification (`python-3.11.6`)

---

## � **Power Automate Integration**

### **HTML-to-PDF Compatibility**

This application is specifically optimized for **Microsoft Power Automate HTML-to-PDF conversion** workflows. The following compatibility features ensure reliable PDF generation:

#### **Template Optimizations**
- **Empty Paragraph Handling**: Automatically converts `<p></p>` to `<p>&nbsp;</p>` to prevent sandbox exceptions
- **Consistent Font Sizing**: CSS rules ensure uniform 12px font across all content types (`<p>`, `<ul>`, `<li>`)
- **Mixed Format Support**: Handles rich text data from Workday (HTML lists, paragraphs, plain text)
- **HTML Entity Decoding**: Processes special characters (`&#39;` → `'`) for clean PDF output

#### **Power Automate Workflow Steps**
1. **HTTP Request**: Call `/talent-card/{employee_id}` endpoint
2. **Get Response**: Receive clean HTML optimized for PDF conversion
3. **OneDrive Action**: Use "Convert HTML to PDF" with the response body
4. **Result**: Professional A4 landscape PDF talent card

#### **Known Compatibility Issues Resolved**
- ✅ **Empty `<p></p>` tags**: Replaced with `<p>&nbsp;</p>` for proper spacing
- ✅ **Font size inconsistencies**: Added CSS for `<ul><li>` elements to match paragraph styling  
- ✅ **HTML entity encoding**: Automatic decoding prevents conversion errors
- ✅ **Mixed content formats**: Unified handling of HTML and plain text from Workday

#### **Testing Power Automate Integration**
```http
# Test with known working employee
GET /talent-card/1000212306

# Test with previously problematic employee (now fixed)  
GET /talent-card/1000130722
```

#### **Troubleshooting Power Automate Issues**
- **Sandbox Exception**: Check for empty paragraph tags (now auto-fixed)
- **Font Size Problems**: Verify CSS loads properly in Power Automate preview
- **Encoding Issues**: HTML entities are automatically decoded by template filters

---

## �🔧 **Troubleshooting**

### **Common Issues**

#### **Configuration Errors**
- **Problem**: `Configuration file not found`
- **Solution**: Create `config/workday_config.json` from example file
- **Development**: Use local config with credentials
- **Production**: Ensure Heroku Config Vars are set

#### **Missing Profile Photos**
- **Problem**: `'dict object' has no attribute 'base64'`
- **Solution**: ✅ **Fixed** - Template now handles missing photos gracefully
- **Result**: SVG placeholder avatar displays for employees without photos

#### **Port Conflicts**
- **Problem**: `Address already in use`  
- **Solution**: Use port 8001 for local development instead of 8000
- **Command**: `uvicorn main:app --port 8001`

#### **Workday API Issues**
- **Problem**: Authentication failures or API errors
- **Solution**: Verify credentials in config/environment variables
- **Check**: Ensure custom report permissions in Workday

### **Development Tips**
- **Local Testing**: Use `/employee/{id}` endpoints with sample data
- **Template Changes**: Server auto-reloads with `--reload` flag  
- **File Output**: Check `output/` folder for generated HTML files
- **API Documentation**: Visit `/docs` for interactive testing

---

**Project Type**: Enterprise FastAPI Application  
**Integration**: Workday HR Systems  
**Output Format**: A4 Landscape HTML (Power Automate → PDF)  
**Last Updated**: October 2025