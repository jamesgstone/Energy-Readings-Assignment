import asyncio
import os
import json
import redis.asyncio as redis 
from fastapi import FastAPI

app = FastAPI()

# environment variables
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
STREAM_NAME = "energy_readings"
GROUP_NAME = "processing_group"

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

@app.on_event("startup")
async def startup_event():
    try:
        await r.xgroup_create(STREAM_NAME, GROUP_NAME, id="0", mkstream=True)
    except Exception:
        pass 
    
    asyncio.create_task(consume_messages())

async def consume_messages():
    consumer_name = "processor-1"
    while True:
        try:
            response = await r.xreadgroup(GROUP_NAME, consumer_name, {STREAM_NAME: ">"}, count=1, block=5000)
            
            if response:
                for stream, messages in response:
                    for message_id, data in messages:
                        site_id = data.get("site id")
                        if site_id:
                            await r.rpush(f"site:{site_id}:readings", json.dumps(data))
                            await r.xack(STREAM_NAME, GROUP_NAME, message_id)
        except Exception as e:
            print(f"Consumer Error: {e}")
            await asyncio.sleep(2)

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.get("/sites/{site_id}/readings")
async def get_readings(site_id: str):
    data = await r.lrange(f"site:{site_id}:readings", 0, -1)
    return [json.loads(item) for item in data]