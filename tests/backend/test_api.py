"""Backend tests for Drusti API."""
import pytest
from fastapi.testclient import TestClient
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))


def get_client():
    from app.main import app
    return TestClient(app)


def test_health():
    client = get_client()
    r = client.get("/api/health")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "ok"


def test_login_success():
    client = get_client()
    r = client.post("/api/auth/login", json={"email": "worker@drusti.local", "password": "drusti123"})
    assert r.status_code == 200
    assert "access_token" in r.json()


def test_login_fail():
    client = get_client()
    r = client.post("/api/auth/login", json={"email": "wrong@example.com", "password": "bad"})
    assert r.status_code == 401


def test_create_patient():
    client = get_client()
    r = client.post("/api/patients", json={"name": "Test Patient", "age": 50, "sex": "Male"})
    assert r.status_code == 200
    assert r.json()["success"]


def test_list_patients():
    client = get_client()
    r = client.get("/api/patients")
    assert r.status_code == 200
    assert r.json()["success"]


def test_dashboard():
    client = get_client()
    r = client.get("/api/dashboard")
    assert r.status_code == 200


def test_analytics():
    client = get_client()
    r = client.get("/api/analytics")
    assert r.status_code == 200


def test_facilities_empty():
    client = get_client()
    r = client.get("/api/facilities")
    assert r.status_code == 200


def test_system_status():
    client = get_client()
    r = client.get("/api/settings/status")
    assert r.status_code == 200
    assert r.json()["data"]["mode"] in ("demo", "live")
