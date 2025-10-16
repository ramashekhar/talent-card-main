# Simple FastAPI App for Heroku

A minimal FastAPI application ready for deployment on Heroku.

## Features

- Simple REST API with multiple endpoints
- Health check endpoint
- Environment detection (local vs Heroku)
- Ready for Heroku deployment

## Endpoints

- `GET /` - Welcome message
- `GET /health` - Health check
- `GET /items/{item_id}` - Example with path parameter
- `GET /info` - Environment information

## Local Development

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the application:
   ```bash
   python main.py
   ```

3. Visit `http://localhost:8000` in your browser or use the interactive docs at `http://localhost:8000/docs`

## Heroku Deployment

### Option 1: Deploy via GitHub Integration (Recommended - No CLI needed)

1. Push your code to GitHub:
   ```bash
   git init
   git add .
   git commit -m "Initial FastAPI app for Heroku"
   git branch -M main
   git remote add origin https://github.com/yourusername/your-repo-name.git
   git push -u origin main
   ```

2. Go to [Heroku Dashboard](https://dashboard.heroku.com/)

3. Click "Create new app"

4. Choose your app name and region

5. In the "Deploy" tab:
   - Select "GitHub" as deployment method
   - Connect your GitHub account
   - Search and connect your repository
   - Enable "Automatic deploys" from main branch (optional)
   - Click "Deploy Branch" to deploy immediately

6. Once deployed, click "View" to see your app live!

### Option 2: Deploy via Heroku CLI

1. Create a Heroku app:
   ```bash
   heroku create your-app-name
   ```

2. Deploy:
   ```bash
   git add .
   git commit -m "Initial commit"
   git push heroku main
   ```

3. Open your app:
   ```bash
   heroku open
   ```

## Files

- `main.py` - FastAPI application
- `requirements.txt` - Python dependencies
- `Procfile` - Heroku process configuration
- `runtime.txt` - Python version specification