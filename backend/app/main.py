from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI(title="FastAPI Prometheus Demo")

Instrumentator().instrument(app).expose(app)


@app.get("/ping")
def ping():
    return "pong"


@app.get("/healthz")
def healthz():
    return {"status": "OK"}


@app.get("/readyz")
def readyz():
    return {"status": "READY"}


@app.get("/version")
def version():
    return {"version": "1.0.0"}
