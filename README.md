# German IT Job Market API

A REST API over the German IT job market, built on the Bundesagentur für Arbeit
Jobsuche API — answering questions the original source cannot, because it only
ever shows what is live right now.

**Status:** in development. Daily ingestion works; cleaning, storage and the API
layer are in progress. See [Roadmap](#roadmap).

---

## Why this exists

The Bundesagentur's own job board can already count and filter postings — its API
returns aggregations via a `facetten` field. So counting is not the contribution
here. Three things are:

**Time.** The source is a snapshot. Ask it how demand for IT roles in Berlin
changed over the last three months and it has no answer — it keeps no history.
This project records every posting's `first_seen` and `last_seen` and never
deletes, so change over time becomes measurable.

**Deduplication.** The same vacancy is frequently advertised by the employer
*and* by several staffing agencies, each as a separate posting. The source counts
all of them. This project collapses them, so a count of open positions means
something closer to the number of actual jobs.

**Technology.** There is no "Python", "Java" or "Kubernetes" dimension in the
source data — the axis does not exist. It is derived here from posting titles,
and reported honestly as *"postings whose title mentions X"*, never as
*"jobs requiring X"*.

A fourth dimension emerged from the data itself: **remote work**. 60% of postings
carry a `homeofficemoeglich` flag, and some specify a percentage. Remote share of
IT postings over time, by city, is not something the source charts.

## Scope

IT is not one occupational field in this taxonomy — it is four. 

| Berufsfeld | Postings (2026-09-29) |
|---|---|
| IT-Netzwerktechnik, -Administration, -Organisation | 7,867 |
| Informatik | 6,989 |
| Softwareentwicklung und Programmierung | 4,652 |
| IT-Systemanalyse, -Anwendungsberatung und -Vertrieb | 4,439 |
| **Total** | **23,947** |


Also filtered: `angebotsart=1`, which restricts results to regular job vacancies
and excludes Ausbildung (177,076 nationally), Praktika/Trainee (14,393) and
self-employment offers (3,492).

## Planned endpoints

| Endpoint | Answers | Available on arbeitsagentur.de? |
|---|---|---|
| `GET /postings` | Filtered search: city, field, technology, employer, date range | Yes — baseline, not the contribution |
| `GET /postings/{referenznummer}` | One posting, with first and last observation dates | Partly — no "first seen" there |
| `GET /stats/trends` | Postings per day, by city / field / technology | **No** |
| `GET /stats/technologies` | Postings mentioning each technology in the title | **No — the dimension does not exist** |
| `GET /stats/employers` | Top employers, deduplicated | **No — agencies are double-counted** |
| `GET /stats/cities` | Cities ranked by IT postings | Yes, via facets — convenience only |
| `GET /health` | Status, row count, last successful ingest | — |

The API is read-only. Writes happen only in the ingestion process, which is not
reachable from any endpoint.

## Data quality findings

Measured against the live API, not taken from documentation. These shape the
cleaning layer.

**Documented field names do not match the response.** The names in the OpenAPI
specification differ from what the API actually returns. All field names used
here were read from live responses. (Related: bundesAPI/jobsuche-api issue #69.)

**API version matters.** `v4` returns `403 Forbidden`; `v6` returns `200`, with
the same public key `jobboerse-jobsuche`.

## Architecture

```
Arbeitsagentur API  →  fetch/ingest  →  PostgreSQL  →  FastAPI  →  consumer
                       (daily)          (cleaned)      (read-only)
```

## Stack

Python · PostgreSQL · FastAPI · SQLAlchemy · `requests`

## Running it

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

python fetch.py
```

Writes `data/raw/YYYY-MM-DD.json` (~24,000 records, tens of MB). Raw data is
gitignored.

## Roadmap

- Paginating fetch across all four IT Berufsfelder
- Dating raw archive with provenance
- Cleaning layer: flatten locations, normalise employer names, extract technologies
- PostgreSQL schema with `first_seen` / `last_seen`
- Idempotent daily ingest
- FastAPI endpoints
- Scheduled daily run
- Deployment

**Definition of done:** ingest runs daily unattended, survives a malformed record,
produces no duplicates on re-run; all endpoints documented and deployed; the
README states the limitations plainly.

## Data source

[Bundesagentur für Arbeit Jobsuche API](https://github.com/bundesAPI/jobsuche-api)
v6. Public, no registration. Data belongs to the Bundesagentur für Arbeit.