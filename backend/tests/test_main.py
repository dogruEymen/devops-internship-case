from pathlib import Path
import sys

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.main import app  # noqa: E402


client = TestClient(app)


def test_ping_returns_pong():
    response = client.get("/ping")

    assert response.status_code == 200
    assert response.json() == "pong"


def test_healthz_returns_ok_status():
    response = client.get("/healthz")

    assert response.status_code == 200
    assert response.json() == {"status": "OK"}


def test_readyz_returns_ready_status():
    response = client.get("/readyz")

    assert response.status_code == 200
    assert response.json() == {"status": "READY"}


def test_version_returns_current_version():
    response = client.get("/version")

    assert response.status_code == 200
    assert response.json() == {"version": "1.0.0"}
