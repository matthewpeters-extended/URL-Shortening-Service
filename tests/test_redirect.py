def _short_code_for(client, original_url):
    short_url = client.post("/shorten", json={"originalUrl": original_url}).json()["shortUrl"]
    return short_url.rsplit("/", 1)[-1]


def test_redirect_follows_to_original_url(client):
    code = _short_code_for(client, "https://example.com/destination")

    response = client.get(f"/shorten/{code}")
    assert response.status_code == 302
    assert response.headers["location"] == "https://example.com/destination"


def test_redirect_increments_usage_count(client):
    code = _short_code_for(client, "https://example.com/counted")

    client.get(f"/shorten/{code}")
    client.get(f"/shorten/{code}")
    client.get(f"/shorten/{code}")

    stats = client.get(f"/stats/{code}").json()
    assert stats["usage_count"] == 3


def test_redirect_unknown_code_is_404(client):
    response = client.get("/shorten/zzzzzzzz")
    assert response.status_code == 404


def test_redirect_garbage_code_is_404_not_500(client):
    response = client.get("/shorten/not-base62!")
    assert response.status_code == 404
