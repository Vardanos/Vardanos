# Armenia's scientific output

An open, regularly refreshed dataset of research by people affiliated with
Armenian institutions, plus the small Python tool (stdlib only, Python ≥ 3.10)
that builds it.

## What's in `data/`

| Path | Source | Contents |
|---|---|---|
| `institutions.csv` / `.json` | [ROR](https://ror.org) | Armenian research organisations: ROR ID, English and Armenian names, acronyms, type, city, founding year, website, Wikidata ID, parent organisations |
| `works/<year>.jsonl.gz` | [OpenAlex](https://openalex.org) | One record per publication with ≥ 1 author affiliated with an Armenian institution: DOI, title, venue, type, language, open-access status, citations, research domain/field/subfield/topic, all authors with their affiliations and affiliation type (education, facility, company, healthcare, government, nonprofit…), co-author countries, whether any affiliation is a company |
| `stats/*.csv` | derived | Works per year (incl. share with industry co-authors), field, type, venue, sector, Armenian institution (with type) and collaborating country |
| `../STATS.md` | derived | Human-readable summary of the above |

Work files are gzipped JSON Lines, sorted by OpenAlex ID and written
deterministically, so a year whose data did not change produces no git diff.

```python
from armenia_science.storage import iter_works
physics = [w for w in iter_works("data/works") if w["field"] == "Physics and Astronomy"]
```

## Running it

```bash
export OPENALEX_API_KEY=...              # free key: https://openalex.org/settings/api
python -m armenia_science institutions   # ROR → data/institutions.*
python -m armenia_science works --from-year 1991   # OpenAlex → data/works/
python -m armenia_science stats          # → data/stats/, STATS.md
python -m unittest discover -s tests
```

Without an API key, OpenAlex requests come out of a small free daily budget
shared by everyone on your IP address, and that budget can run out.

## Automatic updates

`.github/workflows/update-data.yml` runs every Monday. It refreshes the
institutions, re-harvests the current and previous publication years (whose
records and citation counts still change the most), rebuilds the statistics and
commits any changes. To set it up:

1. Add an `OPENALEX_API_KEY` repository secret (and optionally an
   `OPENALEX_MAILTO` variable).
2. Run the workflow once by hand (**Actions → Update data → Run workflow**)
   with `from_year` = `1991` to do the full back-harvest.

## Caveats

- Coverage is whatever OpenAlex indexes. Journals published in Armenian, and
  older literature without DOIs, are under-represented.
- Works are attributed by OpenAlex's affiliation matching. A paper counts when
  any author has an institution in Armenia, so diaspora researchers abroad are
  not included.
- Field classification is OpenAlex's automatically assigned *primary topic*.
- Industry is measured through papers whose authors list a company. Most
  industry R&D is never published this way (it shows up in patents and
  products instead), so this undercounts it.
