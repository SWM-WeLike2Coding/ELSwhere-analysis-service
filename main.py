from fastapi import FastAPI
from contextlib import asynccontextmanager
from dotenv import load_dotenv
import py_eureka_client.eureka_client as eureka_client
import uvicorn
import random
import os

load_dotenv()
port = random.randint(1024, 65535)

@asynccontextmanager
async def lifespan(app: FastAPI):
    await eureka_client.init_async(eureka_server=os.getenv('EUREKA_SERVER'),
                                   app_name="analysis-service",
                                   instance_host=os.getenv('INSTANCE_HOST'),
                                   instance_port=port)
    yield
    await eureka_client.stop_async()

app = FastAPI(lifespan=lifespan,
              title = "API Document",
              description = "ANALYSIS SERVICE 명세서",
              version = "v1.0.0",
              openapi_url = "/v3/api-docs",
              servers=[
                  {"url": os.getenv('DEVELOPMENT_SERVER_URL'), "description": "개발 서버"},
                  {"url": os.getenv('LOCAL_SERVER_URL'), "description": "로컬 서버"}
              ]
)

@app.get("/")
def health_check_handler():
    return {"status": "It's Working in " + os.getenv('APPLICATION_NAME')}

if __name__ == "__main__":
    try:
        uvicorn.run(app, host="0.0.0.0", port=port)
    except KeyboardInterrupt:
        pass
