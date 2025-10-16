# Heroku Examples Collection

A collection of various Python web application examples ready for Heroku deployment.

## Projects

### 1. FastAPI Example (`fast-api/`)
A simple FastAPI application with basic endpoints.

**Endpoints:**
- `GET /` - Welcome message
- `GET /health` - Health check
- `GET /items/{item_id}` - Example with parameters
- `GET /info` - Environment information

**Deploy to Heroku:**
1. Create new Heroku app
2. Connect to this GitHub repo
3. Set the app root directory to `fast-api` in Heroku settings
4. Deploy from the main branch

### Future Projects
- Django example
- Flask example  
- Streamlit dashboard
- API with database integration

## Deployment Instructions

Each project folder contains its own:
- `requirements.txt` - Dependencies
- `Procfile` - Heroku process configuration
- `runtime.txt` - Python version
- `README.md` - Project-specific instructions

## Local Development

Navigate to any project folder and run:
```bash
cd project-name
pip install -r requirements.txt
python main.py  # or the appropriate entry point
```

## Heroku Deployment via GitHub

1. Push this repo to GitHub
2. Create a new Heroku app
3. Connect the app to this GitHub repository
4. **Important**: Set the app root directory to the specific project folder (e.g., `fast-api`)
5. Deploy from main branch

## Structure
```
heroku/
├── fast-api/          # FastAPI example
├── django-app/        # Django example (coming soon)
├── flask-app/         # Flask example (coming soon)
└── README.md          # This file
```