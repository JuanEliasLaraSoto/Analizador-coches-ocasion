from fastapi.testclient import TestClient

from ocasion import api

cliente = TestClient(api.app)


def test_health():
    assert cliente.get("/health").json() == {"estado": "ok"}


def test_analizar_llama_al_pipeline(monkeypatch):
    def falso(anuncios, km, prov, con_opiniones):
        return {"recibidos": len(anuncios), "opiniones": con_opiniones}

    monkeypatch.setattr(api, "analizar", falso)
    r = cliente.post("/analizar", json={"anuncios": ["a", "b"], "opiniones": True})
    assert r.status_code == 200 and r.json() == {"recibidos": 2, "opiniones": True}


def test_rechaza_demasiados_anuncios():
    assert cliente.post("/analizar", json={"anuncios": ["a"] * 4}).status_code == 422


def test_limite_por_ip(monkeypatch):
    monkeypatch.setattr(api, "analizar", lambda *a, **k: {})
    monkeypatch.setattr(api, "LIMITE_POR_HORA", 2)
    api._peticiones.clear()
    codigos = [cliente.post("/analizar", json={"anuncios": ["a"]}).status_code for _ in range(3)]
    assert codigos == [200, 200, 429]
