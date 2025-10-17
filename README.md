# Python Web Applications Portfolio

A professional collection of production-ready Python web applications with Heroku deployment examples.

## 🚀 **Live Applications**

### **Talent Card Generator** - FastAPI Enterprise Application
**🔗 Production URL:** `[To be deployed]`  
**📂 Project Folder:** [`fast-api/`](./fast-api/)  
**🏢 Enterprise Integration:** Workday API + Power Automate

Professional talent card generation system that integrates with Workday HR systems to create A4 landscape talent cards for organizational use.

**Key Features:**
- **Workday REST API Integration**: Fetches live employee data
- **Professional Template Engine**: A4 landscape cards with embedded CSS
- **Power Automate Ready**: HTML→PDF conversion workflow
- **Dual-Mode Operation**: Local development + Production deployment
- **Security**: Environment-based credential management
- **Missing Photo Handling**: Graceful fallback with SVG placeholders

**Architecture:**
- **Framework**: FastAPI 2.0.0 with modular router architecture
- **Template Engine**: Jinja2 with professional corporate styling
- **API Client**: Custom Workday REST client with HTTP Basic Auth
- **Deployment**: Heroku with Config Vars for security
- **Development**: Local server with file output for testing

**API Endpoints:**
- `GET /talent-card/{employee_id}` - Generate talent card HTML
- `GET /employee/{employee_id}` - Individual employee testing
- `GET /health` - System health monitoring
- `GET /docs` - Interactive API documentation

---

## 📁 **Project Structure**

```
heroku/                              ← Repository root & Heroku deployment
├── Procfile                         ← Heroku: "cd fast-api && gunicorn..."
├── requirements.txt                 ← Root dependencies (Heroku uses this)
├── runtime.txt                      ← Python version specification
├── README.md                        ← This portfolio overview
└── fast-api/                        ← Talent Card Generator Application
    ├── main.py                      ← FastAPI modular entry point
    ├── routers/                     ← Modular endpoint architecture
    │   ├── talent_cards.py          ← Main Workday API integration
    │   ├── employee.py              ← Development testing endpoints  
    │   └── health.py                ← System monitoring
    ├── src/                         ← Core business logic
    │   └── workday_client.py        ← Workday REST API client
    ├── config/                      ← Configuration management
    │   ├── workday_config_production.json ← Safe config (GitHub-safe)
    │   └── workday_config.example.json    ← Template for local dev
    ├── templates/                   ← Jinja2 template system
    │   ├── talent-card.html.jinja   ← A4 professional talent cards
    │   └── employee.html.jinja      ← Development testing template
    ├── static/                      ← CSS and static assets
    ├── output/                      ← Local development HTML generation
    └── README.md                    ← Detailed project documentation
```

---

## 🔧 **Technology Stack**

### **Backend Frameworks**
- **FastAPI 2.0.0**: High-performance async web framework
- **Uvicorn/Gunicorn**: ASGI server with worker processes
- **Jinja2**: Professional template rendering engine

### **Integration & APIs**
- **Workday REST API**: Enterprise HR system integration
- **HTTP Basic Auth**: Secure API authentication
- **CORS Middleware**: Cross-origin resource sharing for Power Automate

### **Deployment & DevOps**
- **Heroku**: Cloud platform with git-based deployment
- **Environment Variables**: Secure credential management
- **Dual-Mode Config**: Development vs Production configuration

### **Development Tools**
- **Modular Architecture**: Router-based endpoint organization
- **Local Development**: File-based output for testing
- **Interactive Documentation**: Auto-generated API docs

---

## 🚀 **Deployment Guide**

### **Production Deployment (Heroku)**

1. **Repository Setup**: This repository is ready for Heroku deployment
2. **Environment Variables**: Set secure credentials in Heroku Config Vars
3. **Automatic Detection**: Heroku uses root-level `Procfile`, `requirements.txt`, `runtime.txt`
4. **Subdirectory Execution**: Procfile navigates to project folder automatically

### **Quick Deploy to Heroku**

```bash
# 1. Create Heroku app
heroku create your-talent-card-app

# 2. Set environment variables
heroku config:set WORKDAY_USERNAME=your_username@tenant
heroku config:set WORKDAY_PASSWORD=your_password

# 3. Deploy from GitHub (recommended)
# Connect your GitHub repository in Heroku Dashboard
# Or deploy via git:
git push heroku main

# 4. Open application
heroku open
```

### **Local Development**

Each project includes detailed setup instructions in its README.md file.

---

## 📋 **Future Applications**

This repository is designed to showcase multiple Python web applications:

- **✅ Talent Card Generator** (FastAPI) - Production ready
- **🔄 Django Dashboard** - Coming soon
- **🔄 Flask API** - Coming soon  
- **🔄 Streamlit Analytics** - Coming soon

---

## 🏗️ **Architecture Highlights**

### **Enterprise Integration Pattern**
- External API integration (Workday)
- Secure credential management
- Professional template rendering
- Cross-platform compatibility (Power Automate)

### **Deployment Best Practices**
- Environment-based configuration
- Security-first approach (no credentials in code)
- Modular architecture for maintainability
- Comprehensive error handling

### **Development Workflow**
- Local development with file output
- Production deployment with in-memory processing
- Interactive API documentation
- Modular router-based architecture

---

**Portfolio maintained by**: [Your Organization]  
**Last Updated**: October 2025  
**Repository**: `talent-card-agent`  
**License**: [Your License]