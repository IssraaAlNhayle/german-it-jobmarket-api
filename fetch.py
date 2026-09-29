import json
import time
from datetime import date, datetime, timezone
from pathlib import Path

import requests

#defining fetching constants
URL = "https://rest.arbeitsagentur.de/jobboerse/jobsuche-service/pc/v6/jobs"
HEADERS = {"X-API-Key": "jobboerse-jobsuche"}
SIZE = 500
MAX_PAGES = 100

BERUFSFELDER = [
    "Informatik",
    "Softwareentwicklung und Programmierung",
    "IT-Netzwerktechnik, -Administration, -Organisation",
    "IT-Systemanalyse, -Anwendungsberatung und -Vertrieb",
]

def fetch_berufsfeld(name):
    collected = []
    page = 1

    while page <= MAX_PAGES:
        params = {
            "berufsfeld": name,
            "angebotsart": 1,
            "size": SIZE,
            "page": page,
        }
        response = requests.get(URL, headers=HEADERS, params=params, timeout=30)
        response.raise_for_status()
        records = response.json().get("ergebnisliste", [])
        collected.extend(records)
        print(f"page {page}: {len(records)} (running total: {len(collected)})")

        if len(records) < SIZE:
            break
        page += 1
        time.sleep(0.5)
    else:
        raise RuntimeError(f"{name}: hit MAX_PAGES limit — data is incomplete")
    return collected
all_records = []
counts = {}
for name in BERUFSFELDER:
    print(f"\n{name}")
    records = fetch_berufsfeld(name)
    counts[name] = len(records)
    all_records.extend(records)

out_dir = Path("data/raw")
out_dir.mkdir(parents=True, exist_ok=True)
out_file = out_dir / f"{date.today().isoformat()}.json"

payload = {
    "fetched_at": datetime.now(timezone.utc).isoformat(),
    "query": {"angebotsart": 1, "size": SIZE, "berufsfelder": BERUFSFELDER},
    "counts_per_berufsfeld": counts,
    "count": len(all_records),
    "records": all_records,
}

with open(out_file, "w", encoding="utf-8") as f:
    json.dump(payload, f, ensure_ascii=False)

print(f"\nsaved {len(all_records)} records to {out_file}")



