import os
from opentelemetry import trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.exporter.zipkin.json import ZipkinExporter
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.propagators.b3 import B3MultiFormat
from opentelemetry.propagate import set_global_textmap

def setup_opentelemetry(app):

    # OpenTelemetry 설정
    resource = Resource.create({"service.name": os.getenv("APPLICATION_NAME")})
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
    set_global_textmap(B3MultiFormat())