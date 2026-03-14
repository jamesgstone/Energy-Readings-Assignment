from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
import redis
import os

app = FastAPI()

# חיבור ל-Redis לפי משתני סביבה (חשוב ל-Helm מאוחר יותר) [cite: 62]
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = os.getenv("REDIS_PORT", 6379)
r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

# מודל נתונים עם ולידציה [cite: 32, 33, 34, 35, 36, 37]
class EnergyReading(BaseModel):
    site_id: str = Field(..., alias="site id")
    device_id: str = Field(..., alias="device id")
    power_reading: float
    timestamp: str

    class Config:
        populate_by_name = True

@app.get("/health")
def health_check():
    return {"status": "healthy"} [cite: 31]

@app.post("/readings", status_code=201)
def post_reading(reading: EnergyReading):
    # ולידציה בסיסית (Pydantic מטפל ברוב השדות החסרים ומחזיר 422 אוטומטית) [cite: 38]
    try:
        # פרסום ל-Redis Stream [cite: 21, 22]
        stream_id = r.xadd("energy_readings", reading.dict(by_alias=True))
        return {"status": "accepted", "stream id": stream_id} [cite: 39, 40, 41]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))