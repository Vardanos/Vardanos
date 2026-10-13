"""Armenian research organisations from the Research Organization Registry (ROR)."""

import csv
import re
import json
from pathlib import Path

from .http import get_json

ROR_API = "https://api.ror.org/v2/organizations"


def _name(org):
    for n in org.get("names", []):
        if "ror_display" in n.get("types", []):
            return n["value"]
    return org["names"][0]["value"] if org.get("names") else ""


def _clean(value):
    # Some ROR records carry a stray language tag glued to Armenian text, e.g. "...ինստիտուտhy".
    return re.sub(r"(?<=[\u0530-\u058F])hy$", "", value)


def _names_of_type(org, kind, lang=None):
    return [_clean(n["value"]) for n in org.get("names", [])
            if kind in n.get("types", []) and (lang is None or n.get("lang") == lang)]


def slim_org(org):
    loc = (org.get("locations") or [{}])[0].get("geonames_details", {})
    ext = {e["type"]: e.get("preferred") or (e.get("all") or [None])[0] for e in org.get("external_ids", [])}
    website = next((l["value"] for l in org.get("links", []) if l.get("type") == "website"), "")
    parents = [r["id"] for r in org.get("relationships", []) if r.get("type") == "parent"]
    return {
        "ror": org["id"],
        "name": _name(org),
        "name_hy": "; ".join(_names_of_type(org, "label", "hy")),
        "acronyms": "; ".join(_names_of_type(org, "acronym")),
        "types": "; ".join(org.get("types", [])),
        "status": org.get("status", ""),
        "city": loc.get("name", ""),
        "established": org.get("established") or "",
        "website": website,
        "wikidata": ext.get("wikidata") or "",
        "grid": ext.get("grid") or "",
        "parent_ror": "; ".join(parents),
    }


ORG_TYPES = ["education", "facility", "government", "healthcare", "nonprofit", "funder", "archive", "company", "other"]


def _fetch(filter_):
    orgs, page = [], 1
    while True:
        data = get_json(ROR_API, {"filter": filter_, "page": page})
        items = data.get("items", [])
        orgs.extend(items)
        if not items or len(orgs) >= data.get("number_of_results", 0):
            return orgs
        page += 1


def fetch_armenian_orgs():
    # Paging through one large result set skips records, so query each type separately and merge.
    base = "locations.geonames_details.country_code:AM"
    orgs = {}
    for t in ORG_TYPES:
        for o in _fetch(f"{base},types:{t}"):
            orgs[o["id"]] = o
    return list(orgs.values())


def harvest(out_dir):
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    rows = sorted(map(slim_org, fetch_armenian_orgs()), key=lambda r: (r["name"].lower(), r["ror"]))
    with open(out / "institutions.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    (out / "institutions.json").write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return rows
