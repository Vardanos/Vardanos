"""Fixed scoring harness (the `prepare.py` of this loop). Do not modify.

Scores every candidate funding source in `pool.jsonl` for relevance to the
company described in `profile.md` and reports relevance@100: the mean score of
the 100 best candidates, with empty slots counting as zero. Higher is better.
"""

import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).parent
POOL = HERE / "pool.jsonl"
TOP_K = 100

# Can an Armenian LLC (Denovo Sciences) actually receive the money?
ELIGIBILITY = {
    "direct": 1.0,                # Armenian company may apply as lead/sole applicant
    "as_partner": 0.6,            # only inside a consortium or with a lead elsewhere
    "via_founder": 0.4,           # an individual (founder/scientist) applies, not the company
    "needs_foreign_entity": 0.25, # needs a subsidiary in the funder's country
    "ineligible": 0.0,
}
# How close is the funder's scope to what Denovo does?
TOPIC = {
    "ai_drug_discovery": 1.0,     # AI / computational drug discovery explicitly in scope
    "therapeutic_area": 0.85,     # drug discovery in Denovo's areas: rare/metabolic, infectious, oncology
    "life_sciences": 0.65,        # health / biotech broadly
    "deep_tech_ai": 0.5,          # AI or deep tech, any sector
    "general": 0.3,               # any innovation
}
INSTRUMENT = {
    "grant": 1.0,
    "grant_equity": 0.9,          # blended grant + equity (e.g. EIC Accelerator)
    "prize": 0.75,
    "compute_credits": 0.6,       # in-kind cloud / GPU credits
    "fellowship_mobility": 0.5,   # people / mobility funding only
    "other": 0.2,
}
STAGE = {"startup_sme": 1.0, "any_org": 0.8, "academic_led": 0.5}
GEO = {
    "armenia": 1.0,               # programme specific to Armenia
    "regional": 0.8,              # Eastern Partnership / Horizon-associated / EU neighbourhood
    "partner_country": 0.7,       # country of an existing Denovo partner (Qatar, India, US)
    "global": 0.6,
}
STATUS = {"open": 1.0, "recurring": 1.0, "rolling": 1.0, "intermittent": 0.6, "closed": 0.0}
VERIFIED = {True: 1.0, False: 0.7}

REQUIRED = {
    "id": str, "funder": str, "program": str, "url": str, "eligibility": str,
    "topic": str, "instrument": str, "stage": str, "geo": str, "status": str,
    "verified": bool, "notes": str,
}
VOCAB = {"eligibility": ELIGIBILITY, "topic": TOPIC, "instrument": INSTRUMENT,
         "stage": STAGE, "geo": GEO, "status": STATUS}


def validate(rec):
    for key, typ in REQUIRED.items():
        if not isinstance(rec.get(key), typ):
            raise ValueError(f"{rec.get('id')}: field {key!r} must be {typ.__name__}")
    for key, table in VOCAB.items():
        if rec[key] not in table:
            raise ValueError(f"{rec['id']}: {key}={rec[key]!r} not in {sorted(table)}")
    if not rec["url"].startswith("https://"):
        raise ValueError(f"{rec['id']}: url must be an https evidence link")
    award = rec.get("max_award_usd")
    if award is not None and not (isinstance(award, (int, float)) and award > 0):
        raise ValueError(f"{rec['id']}: max_award_usd must be positive or null")


def size_score(award):
    if award is None:
        return 0.3
    return min(max(math.log10(award) - 3, 0.0), 4.0) / 4  # $1k→0 … $10M+→1


def score(rec):
    fit = (0.35 * TOPIC[rec["topic"]] + 0.15 * INSTRUMENT[rec["instrument"]]
           + 0.15 * STAGE[rec["stage"]] + 0.15 * size_score(rec.get("max_award_usd"))
           + 0.20 * GEO[rec["geo"]])
    return ELIGIBILITY[rec["eligibility"]] * STATUS[rec["status"]] * VERIFIED[rec["verified"]] * fit


def load(path=POOL):
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def rank(pool):
    ids = [r["id"] for r in pool]
    dupes = {i for i in ids if ids.count(i) > 1}
    if dupes:
        raise ValueError(f"duplicate ids: {sorted(dupes)}")
    for rec in pool:
        validate(rec)
    return sorted(pool, key=lambda r: (-score(r), r["id"]))


def relevance_at_k(pool, k=TOP_K):
    return sum(score(r) for r in rank(pool)[:k]) / k


if __name__ == "__main__":
    pool = load(Path(sys.argv[1]) if len(sys.argv) > 1 else POOL)
    print(f"pool_size:       {len(pool)}")
    print(f"relevance@{TOP_K}:  {relevance_at_k(pool):.6f}")
