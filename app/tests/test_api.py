def test_healthz(client):
    r = client.get("/healthz")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_readyz(client):
    r = client.get("/readyz")
    assert r.status_code == 200
    assert r.json()["status"] == "ready"


def test_shorten_returns_code(client):
    r = client.post("/api/shorten", json={"url": "https://example.com"})
    assert r.status_code == 201
    body = r.json()
    assert len(body["code"]) == 6
    assert body["short_url"].endswith(body["code"])


def test_shorten_rejects_bad_url(client):
    r = client.post("/api/shorten", json={"url": "not-a-url"})
    assert r.status_code == 422


def test_redirect_works_and_counts_clicks(client):
    code = client.post("/api/shorten", json={"url": "https://example.com"}).json()["code"]

    r = client.get(f"/{code}", follow_redirects=False)
    assert r.status_code == 302
    assert "example.com" in r.headers["location"]

    stats = client.get(f"/api/stats/{code}").json()
    assert stats["clicks"] == 1


def test_unknown_code_is_404(client):
    assert client.get("/doesnotexist").status_code == 404
    assert client.get("/api/stats/nope").status_code == 404


def test_metrics_endpoint_exposes_counters(client):
    client.get("/healthz")
    r = client.get("/metrics")
    assert r.status_code == 200
    assert "http_requests_total" in r.text
