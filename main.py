from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from uvicorn.config import LOGGING_CONFIG
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from api.main import api_router
from exception.exception_handler import add_exception_handler
from core.database import Base, engine
from opentelemetry import trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.exporter.zipkin.json import ZipkinExporter
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.propagators.b3 import B3Format
from opentelemetry.propagate import set_global_textmap
import py_eureka_client.eureka_client as eureka_client
import uvicorn
import os
import models

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    await eureka_client.init_async(eureka_server=os.getenv('EUREKA_SERVER'),
                                   app_name="analysis-service",
                                   instance_host=os.getenv('INSTANCE_HOST'),
                                   instance_port=int(os.getenv('INSTANCE_NON_SECURE_PORT')))
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await eureka_client.stop_async()


app = FastAPI(lifespan=lifespan,
              openapi_url="/v3/api-docs")

# OpenTelemetry 설정
resource = Resource.create({"service.name": "analysis-service"})
trace.set_tracer_provider(TracerProvider(resource=resource))

# Zipkin Exporter 설정
zipkin_exporter = ZipkinExporter(
    endpoint=os.getenv('ZIPKIN_TRACING_ENDPOINT')
)

# Span Processor 추가
trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(zipkin_exporter))

# FastAPI에 OpenTelemetry Instrumentation 추가
FastAPIInstrumentor.instrument_app(app)

# Requests 모듈에 대한 Trace 설정 (외부 API 호출 시)
RequestsInstrumentor().instrument()

# B3 전파 방식 사용
set_global_textmap(B3Format())

app.include_router(api_router)

add_exception_handler(app)

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="API Document",
        version="v1.0.0",
        description="ANALYSIS SERVICE 명세서",
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "bearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "in": "header",
            "name": "Authorization"
        }
    }
    openapi_schema["security"] = [{"bearerAuth": []}]
    openapi_schema["servers"] = [
        {"url": os.getenv('DEVELOPMENT_SERVER_URL'), "description": "개발 서버"},
        {"url": os.getenv('LOCAL_SERVER_URL'), "description": "로컬 서버"}
    ]
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


@app.get("/health_check", tags=["Health Check"], summary=" ")
def health_check_handler():
    return {"status": "It's Working in " + os.getenv('APPLICATION_NAME')}


if __name__ == "__main__":
    try:
        LOGGING_CONFIG["formatters"]["default"]["fmt"] = "%(asctime)s [%(name)s] %(levelprefix)s %(message)s"
        LOGGING_CONFIG["formatters"]["access"]["fmt"] = '%(asctime)s [%(name)s] %(levelprefix)s %(client_addr)s - "%(request_line)s" %(status_code)s'
        uvicorn.run(app, host="0.0.0.0", port=int(os.getenv('INSTANCE_PORT')))
    except KeyboardInterrupt:
        pass
