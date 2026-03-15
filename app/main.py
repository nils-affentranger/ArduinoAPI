from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.api import endpoints

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Connect to Arduino
    try:
        endpoints.arduino.connect()
    except Exception as e:
        print(f"Warning: Could not connect to Arduino on startup: {e}")
    yield
    # Shutdown: Disconnect from Arduino
    endpoints.arduino.disconnect()

app = FastAPI(title="Arduino Serial API", lifespan=lifespan)

# Include API router
app.include_router(endpoints.router, prefix="/arduino", tags=["arduino"])

@app.get("/")
async def root():
    """Health check endpoint."""
    return {"status": "ok", "message": "Arduino API is running."}
