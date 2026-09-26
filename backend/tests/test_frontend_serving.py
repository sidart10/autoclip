from fastapi.testclient import TestClient

from backend.app_factory import create_app


def _frontend_fixture(tmp_path, monkeypatch):
    frontend_dir = tmp_path / "dist"
    frontend_dir.mkdir()
    (frontend_dir / "index.html").write_text(
        "<html><body>AutoClip frontend</body></html>", encoding="utf-8"
    )
    assets_dir = frontend_dir / "assets"
    assets_dir.mkdir()
    (assets_dir / "app.js").write_text("window.autoclip = true", encoding="utf-8")
    monkeypatch.setenv("AUTOCLIP_FRONTEND_DIR", str(frontend_dir))


def test_web_app_serves_bundled_frontend(tmp_path, monkeypatch):
    _frontend_fixture(tmp_path, monkeypatch)

    response = TestClient(create_app(mode="web")).get("/")

    assert response.status_code == 200
    assert "AutoClip frontend" in response.text


def test_frontend_mount_does_not_shadow_api_routes(tmp_path, monkeypatch):
    _frontend_fixture(tmp_path, monkeypatch)

    response = TestClient(create_app(mode="web")).get("/api/v1/health/")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_web_app_falls_back_to_index_for_client_routes(tmp_path, monkeypatch):
    _frontend_fixture(tmp_path, monkeypatch)

    response = TestClient(create_app(mode="web")).get("/projects/example")

    assert response.status_code == 200
    assert "AutoClip frontend" in response.text
