def _create(client, url="https://example.com/dest"):
    return client.post("/api/v1/links", json={"url": url}).json()["code"]


def test_redirect_and_click_count(client):
    code = _create(client)
    resp = client.get(f"/{code}", follow_redirects=False)
    assert resp.status_code == 302
    assert resp.headers["location"] == "https://example.com/dest"

    # Second hit is served from cache; both hits are recorded as clicks.
    client.get(f"/{code}", follow_redirects=False)
    stats = client.get(f"/api/v1/links/{code}/stats").json()
    assert stats["total_clicks"] == 2
    assert sum(day["clicks"] for day in stats["by_day"]) == 2


def test_redirect_unknown_code(client):
    assert client.get("/nonexist", follow_redirects=False).status_code == 404


def test_cache_metrics_recorded(client):
    code = _create(client)
    client.get(f"/{code}", follow_redirects=False)  # miss
    client.get(f"/{code}", follow_redirects=False)  # hit
    metrics = client.get("/metrics").text
    assert "linkr_cache_hits_total" in metrics
    assert "linkr_cache_misses_total" in metrics
