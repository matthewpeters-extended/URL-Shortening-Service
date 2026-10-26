def test_shorten_creates_short_url(client):
    response = client.post("/shorten", json={"originalUrl": "https://example.com/some/long/path"})
    assert response.status_code == 201, response.text
    body = response.json()
    assert body["shortUrl"].startswith("http://127.0.0.1:8000/shorten/")


def test_shorten_rejects_invalid_url(client):
    response = client.post("/shorten", json={"originalUrl": "not a url"})
    assert response.status_code == 422


def test_shorten_same_url_twice_returns_same_short_url(client):
    first = client.post("/shorten", json={"originalUrl": "https://example.com/repeat"}).json()
    second = client.post("/shorten", json={"originalUrl": "https://example.com/repeat"}).json()
    assert first["shortUrl"] == second["shortUrl"]


def test_shorten_different_urls_return_different_short_urls(client):
    first = client.post("/shorten", json={"originalUrl": "https://example.com/a"}).json()
    second = client.post("/shorten", json={"originalUrl": "https://example.com/b"}).json()
    assert first["shortUrl"] != second["shortUrl"]
