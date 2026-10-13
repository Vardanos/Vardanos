"""Works with at least one Armenia-affiliated author, harvested from OpenAlex."""

import datetime
import os
import sys
from pathlib import Path

from .http import get_json
from .storage import write_jsonl_gz

OPENALEX_API = "https://api.openalex.org/works"
COUNTRY = "AM"
SELECT = ",".join([
    "id", "doi", "title", "publication_year", "publication_date", "type", "language",
    "primary_location", "open_access", "cited_by_count", "primary_topic", "authorships",
])


def _short(openalex_id):
    return (openalex_id or "").rsplit("/", 1)[-1]


def slim_work(w):
    source = ((w.get("primary_location") or {}).get("source")) or {}
    topic = w.get("primary_topic") or {}
    authors, am_insts, countries = [], {}, set()
    for a in w.get("authorships") or []:
        insts = []
        for i in a.get("institutions") or []:
            iid = _short(i.get("id"))
            insts.append({"id": iid, "name": i.get("display_name"), "country": i.get("country_code"), "ror": i.get("ror")})
            if i.get("country_code") == COUNTRY:
                am_insts[iid] = i.get("display_name")
        countries.update(c for c in a.get("countries") or [] if c)
        author = a.get("author") or {}
        authors.append({
            "name": author.get("display_name"),
            "id": _short(author.get("id")),
            "orcid": author.get("orcid"),
            "institutions": insts,
        })
    oa = w.get("open_access") or {}
    return {
        "id": _short(w.get("id")),
        "doi": (w.get("doi") or "").replace("https://doi.org/", "") or None,
        "title": w.get("title"),
        "year": w.get("publication_year"),
        "date": w.get("publication_date"),
        "type": w.get("type"),
        "language": w.get("language"),
        "venue": source.get("display_name"),
        "issn_l": source.get("issn_l"),
        "is_oa": oa.get("is_oa"),
        "oa_status": oa.get("oa_status"),
        "cited_by_count": w.get("cited_by_count") or 0,
        "domain": (topic.get("domain") or {}).get("display_name"),
        "field": (topic.get("field") or {}).get("display_name"),
        "subfield": (topic.get("subfield") or {}).get("display_name"),
        "topic": topic.get("display_name"),
        "countries": sorted(countries),
        "armenian_institutions": [{"id": k, "name": v} for k, v in sorted(am_insts.items())],
        "authors": authors,
    }


def _auth_params():
    params = {}
    if os.environ.get("OPENALEX_API_KEY"):
        params["api_key"] = os.environ["OPENALEX_API_KEY"]
    if os.environ.get("OPENALEX_MAILTO"):
        params["mailto"] = os.environ["OPENALEX_MAILTO"]
    return params


def fetch_year(year):
    cursor, works = "*", []
    while cursor:
        data = get_json(OPENALEX_API, {
            "filter": f"authorships.institutions.country_code:{COUNTRY},publication_year:{year}",
            "select": SELECT,
            "per-page": 200,
            "cursor": cursor,
            **_auth_params(),
        })
        works.extend(slim_work(w) for w in data.get("results", []))
        cursor = data.get("meta", {}).get("next_cursor") if data.get("results") else None
    return works


def harvest(out_dir, from_year=1991, to_year=None):
    to_year = to_year or datetime.date.today().year
    works_dir = Path(out_dir) / "works"
    for year in range(from_year, to_year + 1):
        works = sorted(fetch_year(year), key=lambda r: r["id"])
        if works:
            write_jsonl_gz(works_dir / f"{year}.jsonl.gz", works)
        print(f"{year}: {len(works)} works", file=sys.stderr)
