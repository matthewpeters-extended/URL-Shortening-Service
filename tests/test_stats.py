def _short_code_for(client, original_url):
    short_url = client.post("/shorten", json={"originalUrl": original_url}).json()["shortUrl"]
    return short_url.rsplit("/", 1)[-1]


def test_stats_returns_zero_usage_before_any_redirect(client):
    code = _short_code_for(client, "https://example.com/fresh")

    response = client.get(f"/stats/{code}")
    assert response.status_code == 200
    body = response.json()
    assert body["original_url"] == "https://example.com/fresh"
    assert body["usage_count"] == 0


def test_stats_does_not_itself_count_as_usage(client):
    code = _short_code_for(client, "https://example.com/not-counted")

    client.get(f"/stats/{code}")
    client.get(f"/stats/{code}")

    assert client.get(f"/stats/{code}").json()["usage_count"] == 0


def test_stats_unknown_code_is_404(client):
    response = client.get("/stats/zzzzzzzz")
    assert response.status_code == 404
