"""Tests unitarios y de integración para la API Flask."""

import pytest

from app import create_app
from config import TestConfig
from models import db


@pytest.fixture
def app():
    """Crea una instancia de la app con config de test (SQLite en memoria)."""
    app = create_app(TestConfig)
    yield app


@pytest.fixture
def client(app):
    """Cliente de test Flask."""
    return app.test_client()


# ── Tests de ruta principal ──────────────────────────────

class TestIndex:
    """Tests para GET /"""

    def test_status_code(self, client):
        response = client.get("/")
        assert response.status_code == 200

    def test_content_type(self, client):
        response = client.get("/")
        assert response.content_type == "application/json"

    def test_app_name(self, client):
        response = client.get("/")
        data = response.get_json()
        assert data["app"] == "PRJ5 Backend API"

    def test_autor(self, client):
        response = client.get("/")
        data = response.get_json()
        assert data["autor"] == "Hector Garcia"

    def test_status_field(self, client):
        response = client.get("/")
        data = response.get_json()
        assert data["status"] == "ok"


# ── Tests de health check ───────────────────────────────

class TestHealth:
    """Tests para GET /health"""

    def test_health_status_code(self, client):
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_database_field(self, client):
        response = client.get("/health")
        data = response.get_json()
        assert "database" in data


# ── Tests CRUD de Items ──────────────────────────────────

class TestItems:
    """Tests para las rutas /items."""

    def test_list_items_empty(self, client):
        """GET /items devuelve lista vacía al inicio."""
        response = client.get("/items")
        assert response.status_code == 200
        assert response.get_json() == []

    def test_create_item(self, client):
        """POST /items crea un ítem correctamente."""
        response = client.post(
            "/items",
            json={"name": "Item Test", "description": "Descripción de prueba"},
        )
        assert response.status_code == 201
        data = response.get_json()
        assert data["name"] == "Item Test"
        assert data["description"] == "Descripción de prueba"
        assert "id" in data

    def test_create_item_without_name(self, client):
        """POST /items sin nombre devuelve 400."""
        response = client.post("/items", json={"description": "Sin nombre"})
        assert response.status_code == 400

    def test_create_and_list(self, client):
        """Crear un ítem y verificar que aparece en la lista."""
        client.post("/items", json={"name": "Item A"})
        response = client.get("/items")
        data = response.get_json()
        assert len(data) == 1
        assert data[0]["name"] == "Item A"

    def test_get_item_by_id(self, client):
        """GET /items/<id> devuelve el ítem correcto."""
        create_resp = client.post("/items", json={"name": "Item B"})
        item_id = create_resp.get_json()["id"]

        response = client.get(f"/items/{item_id}")
        assert response.status_code == 200
        assert response.get_json()["name"] == "Item B"

    def test_get_item_not_found(self, client):
        """GET /items/<id> con ID inexistente devuelve 404."""
        response = client.get("/items/9999")
        assert response.status_code == 404

    def test_delete_item(self, client):
        """DELETE /items/<id> elimina el ítem."""
        create_resp = client.post("/items", json={"name": "Item Borrar"})
        item_id = create_resp.get_json()["id"]

        delete_resp = client.delete(f"/items/{item_id}")
        assert delete_resp.status_code == 200

        # Verificar que ya no existe
        get_resp = client.get(f"/items/{item_id}")
        assert get_resp.status_code == 404

    def test_delete_item_not_found(self, client):
        """DELETE /items/<id> con ID inexistente devuelve 404."""
        response = client.delete("/items/9999")
        assert response.status_code == 404


# ── Tests de manejo de errores ───────────────────────────

class TestErrors:
    """Tests de manejo de errores."""

    def test_404_not_found(self, client):
        """Ruta inexistente devuelve 404."""
        response = client.get("/ruta-inexistente")
        assert response.status_code == 404
        data = response.get_json()
        assert "error" in data
