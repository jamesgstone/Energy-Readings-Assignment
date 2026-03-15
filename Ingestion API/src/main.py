from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
import redis
import os

app = FastAPI()

# envierment variabels
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = os.getenv("REDIS_PORT", 6379)
r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

class EnergyReading(BaseModel):
    site_id: str = Field(..., alias="site id")
    device_id: str = Field(..., alias="device id")
    power_reading: float
    timestamp: str

    class Config:
        populate_by_name = True

@app.get("/health")
def health_check():
    return {"status": "healthy"} 

@app.post("/readings", status_code=201)
def post_reading(reading: EnergyReading):
    try:
        stream_id = r.xadd("energy_readings", reading.dict(by_alias=True))
        return {"status": "accepted", "stream id": stream_id} 
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))