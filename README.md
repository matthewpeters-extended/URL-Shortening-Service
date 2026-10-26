# URL Shortening Service

A small REST API that turns a long URL into a short one, redirects visitors who follow it, and
tracks how many times it has been followed.

Stack: **FastAPI** + **SQLAlchemy** + **SQLite**, rate limiting via `slowapi`. There is no
authentication anywhere in this one; the spec does not call for users at all, and this is the
only one of the five practice APIs where that is true.

## Quickstart

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

python scripts/seed_demo_data.py    # shortens two sample URLs so there is something to try

uvicorn app.main:app --reload --reload-dir app
```

Interactive docs (Swagger UI) at `http://127.0.0.1:8000/docs` once it is running.

Run the test suite with:

```bash
pytest
```

## The main components

**`app/models.py` holds the one table this service needs.** `Url` has `id`, `original_url`,
`created_at`, and `usage_count`, exactly as the spec lists, with one deliberate omission: there
is no stored `short_url` column. The short code is computed from `id` on every request instead
of written to the row at creation time, which is explained fully below.

**`app/short_code.py` is the entire idea behind this service.** `encode(number)` turns a plain
integer into a base62 string using the sixty two characters `0` through `9`, `a` through `z`,
and `A` through `Z`; `decode(code)` is its exact inverse. Nothing here talks to a database, and
nothing here is random. Given the same integer, `encode` always returns the same string, and
`decode` always recovers the original integer from it. That one fact is what the whole service
is built around.

**`app/routers/shorten.py` is the write side and the redirect.** `POST /shorten` looks for an
existing row with the same `original_url` first and returns its short URL if found, so
shortening the same link twice never creates two different codes for it. Otherwise it inserts a
new row and calls `encode(url.id)` on whatever primary key SQLite just assigned it, which is
also the only place a short code is ever produced. `GET /shorten/{short_code}` reverses that:
`decode()` the code back into an id, look the row up by primary key, bump `usage_count`, and
send back a `302` redirect to `original_url`. A code that fails to decode, because it contains
a character outside the base62 alphabet, is treated exactly like a code that decoded fine but
matched no row: both come back as a plain `404`, never a `500`.

**`app/routers/stats.py` is read only and does not count as a visit.** `GET /stats/{short_code}`
decodes the same way the redirect does, but only to look the row up and report `original_url`,
`short_url`, `created_at`, and `usage_count`; it never touches `usage_count` itself. Checking a
link's stats a hundred times should not make it look a hundred times more popular than it is.

**`app/schemas.py` uses the exact field names the spec's JSON bodies ask for.** `ShortenRequest`
and `ShortenResponse` use `originalUrl` and `shortUrl` in camelCase rather than Python's usual
snake_case, because that is the literal wire contract the task spec gives for `POST /shorten`.
`UrlStatsOut`, which the spec leaves unspecified, follows normal snake_case instead.

**`tests/`** has 21 pytest tests: pure unit tests for `encode`/`decode` round tripping and its
error cases, and feature tests for shortening, deduplication, redirecting, usage counting, and
the two different 404 cases, all against an in memory SQLite database.

## Decisions worth knowing about

* **The short code is derived from the row's id, not generated and stored separately.** A more
  typical implementation picks a random string, checks whether it already exists, and retries
  on collision. Deriving the code from a primary key that SQLite already guarantees is unique
  removes the collision case entirely: there is nothing to retry, and nothing to keep in sync
  between two columns that are really describing the same fact.
* **Shortening the same URL twice returns the same short URL.** The alternative, a fresh row
  and a fresh code every time, would mean the same destination could be reachable by many
  different short links at once, and `usage_count` for that destination would be split across
  all of them instead of telling the whole story in one place.
* **This service will happily shorten a link to anywhere, including somewhere malicious, and
  will redirect anyone who visits the short link without warning.** That is inherent to what a
  URL shortener is, not a bug particular to this implementation; a production version would
  need abuse detection and a warning page for unfamiliar destinations, which is out of scope for
  a practice project with no authentication at all.
* **There are no users and no login**, unlike the other four practice APIs in this series,
  because the spec for this one never introduces any. Everything here is anonymous and public
  by design, not by omission.
