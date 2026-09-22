from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(
    title="Water Quality Monitoring API",
    description="API for Edge-Cloud Collaborative Water Quality Monitoring System",
    version="1.0.0"
)

class StatusResponse(BaseModel):
    status: str
    message: str

@app.get("/", response_model=StatusResponse)
async def root():
    return {"status": "ok", "message": "Backend is running!"}

@app.get("/health", response_model=StatusResponse)
async def health_check():
    return {"status": "ok", "message": "Healthy"}

# TODO: Add MQTT client connection here
# TODO: Add database connection and endpoints here
