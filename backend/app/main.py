from fastapi import FastAPI
from app.routes import api_router

app = FastAPI(title="My Laravel-style FastAPI Project")

# Register Router
app.include_router(api_router, prefix="/api")

@app.get("/")
def root():
    return {"message": "Server is running properly!"}
