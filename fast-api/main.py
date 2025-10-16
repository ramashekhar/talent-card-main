from fastapi import FastAPI
import os

# Create FastAPI instance
app = FastAPI(title="Simple FastAPI App", version="1.0.0")

@app.get("/")
def read_root():
    """
    Root endpoint that returns a welcome message
    """
    return {"message": "Hello World! This is a simple FastAPI app running on Heroku!"}

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