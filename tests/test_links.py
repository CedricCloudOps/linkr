def _create(client, url="https://example.com/page", alias=None):
    body = {"url": url}
    if alias:
        body["custom_alias"] = alias
    return client.post("/api/v1/links", json=body)


def test_create_link(client):
    resp = _create(client)
    assert resp.status_code == 201
    data = resp.json()
    assert data["target_url"].startswith("https://example.com")
    assert data["code"] in data["short_url"]
    assert data["total_clicks"] == 0


def test_create_rejects_invalid_url(client):
    resp = client.post("/api/v1/links", json={"url": "not-a-url"})
    assert resp.status_code == 422


def test_custom_alias(client):
    resp = _create(client, alias="promo-2026")
    assert resp.status_code == 201
    assert resp.json()["code"] == "promo-2026"


def test_reserved_alias_rejected(client):
    resp = _create(client, alias="api")
    assert resp.status_code == 422


def test_duplicate_alias_conflicts(client):
    assert _create(client, alias="launch").status_code == 201
    assert _create(client, alias="launch").status_code == 409


def test_get_link_metadata(client):
    code = _create(client).json()["code"]
    resp = client.get(f"/api/v1/links/{code}")
    assert resp.status_code == 200
    assert resp.json()["code"] == code


def test_get_missing_link(client):
    assert client.get("/api/v1/links/missing").status_code == 404


def test_delete_link(client):
    code = _create(client).json()["code"]
    assert client.delete(f"/api/v1/links/{code}").status_code == 204
    assert client.get(f"/api/v1/links/{code}").status_code == 404
