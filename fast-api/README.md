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
---

## 📁 Folder Structure

```
talent-card-main/
├── Procfile                  # Heroku process configuration
├── requirements.txt          # Python dependencies
├── runtime.txt               # Python version specification
├── README.md                 # Project documentation
└── fast-api/
    ├── main.py               # FastAPI app entry point
    ├── routers/
    │   ├── talent_cards.py   # Workday API integration & talent card generation
    │   ├── employee.py       # Local employee testing
    │   └── health.py         # Health monitoring endpoints
    ├── src/
    │   └── workday_client.py # Workday REST API client
    ├── config/
    │   ├── workday_config_production-gms.json # Production config (GMS)
    │   ├── workday_config_production-csc.json # Production config (CSC)
    │   ├── workday_config-gms.json            # Local config (GMS)
    │   ├── workday_config-csc.json            # Local config (CSC)
    │   └── workday_config.example.json        # Example config
    ├── templates/
    │   ├── talent-card-gms.html.jinja        # GMS talent card template
    │   ├── talent-card-csc.html.jinja        # CSC talent card template
    │   └── employee_not_found.html.jinja     # Not found template
    ├── static/
    │   └── style.css                        # CSS and static assets
    ├── output/                              # Local HTML output (gitignored)
    └── DEVELOPMENT_LOG.md                   # Development log
```

## 🆕 November 27, 2025: Major Enhancements

### Tenant Selection via Query String
- You can now select tenant ("csc" or "gms") using a query string:
  - `/talent-card/21103?tenant=gms` (GMS)
  - `/talent-card/1000130722?tenant=csc` (CSC)
- If not provided, defaults to `WORKDAY_TENANT` environment variable (or "gms").
- Config and template loading are now dynamic per request.

### Repository Migration
- Project migrated from Heroku repo to new GitHub repo `talent-card-main`.
- All git operations should be run from the project root.

### Azure Deployment Support
- Added instructions for Azure App Service deployment (see below).

---
### **Prerequisites**
- Python 3.11.6
- Workday HR system access with custom report permissions
- Git and terminal access
---

## 🚀 Deployment Guide

### Local Development


1. Clone the repo:
  ```powershell
  git clone https://github.com/ramashekhar/talent-card-main.git
  cd talent-card-main
  pip install -r requirements.txt
  ```
2. Change directory to the FastAPI app folder:
  ```powershell
  cd fast-api
  ```
3. Create and edit your config files for both tenants:
  ```powershell
  copy config\workday_config.example.json config\workday_config-gms.json
  copy config\workday_config.example.json config\workday_config-csc.json
  # Edit config\workday_config-gms.json and config\workday_config-csc.json with your credentials and endpoints
  ```
4. Run the server (from inside fast-api):
  ```powershell
  python main.py
  # or
  uvicorn main:app --port 8001
  ```
5. Access endpoints:
  - http://localhost:8001/talent-card/21103?tenant=gms
  - http://localhost:8001/talent-card/1000130722?tenant=csc
  - http://localhost:8001/docs

### Heroku Deployment
1. Set config variables in Heroku:
  ```bash
  heroku config:set WORKDAY_USERNAME=your_username@your_tenant
  heroku config:set WORKDAY_PASSWORD=your_password
  heroku config:set WORKDAY_TENANT=gms # or csc
  ```
2. Deploy to Heroku using one of these methods:
  - **Recommended:** Use Heroku GitHub integration (connect your repo in the Heroku dashboard and enable automatic deploys).
  - Or use the Heroku CLI to trigger a manual deployment:
    ```bash
    heroku git:remote -a your-app-name
    git push heroku main  # Only if you want to use Heroku's git remote
    ```
3. Heroku will use root-level Procfile and requirements.txt. No changes needed for subfolder structure.
4. Endpoints:
  - https://your-app.herokuapp.com/talent-card/21103?tenant=gms
  - https://your-app.herokuapp.com/talent-card/1000130722?tenant=csc

### Azure App Service Deployment
1. Set up your App Service for Python 3.11+.
2. In Azure Portal, go to Configuration > General settings > Startup Command and set:
  ```bash
  cd fast-api && gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:$PORT
  ```
3. Set environment variables in Azure:
  - WORKDAY_USERNAME
  - WORKDAY_PASSWORD
  - WORKDAY_TENANT (gms or csc)
  - SCM_DO_BUILD_DURING_DEPLOYMENT=true
4. Endpoints:
  - https://your-app.azurewebsites.net/talent-card/21103?tenant=gms
  - https://your-app.azurewebsites.net/talent-card/1000130722?tenant=csc
  - https://your-app.azurewebsites.net/docs

---
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
uvicorn main:app --port 8001
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

## 🏗️ **Architecture & File Structure**

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