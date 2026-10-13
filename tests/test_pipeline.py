import tempfile
import unittest
from pathlib import Path

from armenia_science import openalex, stats
from armenia_science.storage import read_jsonl_gz, write_jsonl_gz

RAW = {
    "id": "https://openalex.org/W1",
    "doi": "https://doi.org/10.1/abc",
    "title": "Cosmic rays at Aragats",
    "publication_year": 2023,
    "publication_date": "2023-05-01",
    "type": "article",
    "language": "en",
    "primary_location": {"source": {"display_name": "Physical Review D", "issn_l": "2470-0010"}},
    "open_access": {"is_oa": True, "oa_status": "gold"},
    "cited_by_count": 7,
    "primary_topic": {"display_name": "Cosmic rays", "field": {"display_name": "Physics and Astronomy"},
                      "subfield": {"display_name": "Nuclear and High Energy Physics"},
                      "domain": {"display_name": "Physical Sciences"}},
    "authorships": [
        {"author": {"id": "https://openalex.org/A1", "display_name": "A. Chilingarian", "orcid": None},
         "countries": ["AM"],
         "institutions": [{"id": "https://openalex.org/I1", "display_name": "AANL", "country_code": "AM",
                           "ror": "https://ror.org/00ad27c73"}]},
        {"author": {"id": "https://openalex.org/A2", "display_name": "J. Doe", "orcid": None},
         "countries": ["DE"],
         "institutions": [{"id": "https://openalex.org/I2", "display_name": "DESY", "country_code": "DE",
                           "ror": None}]},
    ],
}


class PipelineTest(unittest.TestCase):
    def test_slim_work(self):
        w = openalex.slim_work(RAW)
        self.assertEqual(w["id"], "W1")
        self.assertEqual(w["doi"], "10.1/abc")
        self.assertEqual(w["countries"], ["AM", "DE"])
        self.assertEqual(w["armenian_institutions"], [{"id": "I1", "name": "AANL"}])
        self.assertEqual(w["field"], "Physics and Astronomy")

    def test_storage_roundtrip_is_deterministic(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "x.jsonl.gz"
            write_jsonl_gz(p, [{"b": 1, "a": "Հայ"}])
            first = p.read_bytes()
            write_jsonl_gz(p, [{"a": "Հայ", "b": 1}])
            self.assertEqual(first, p.read_bytes())
            self.assertEqual(list(read_jsonl_gz(p)), [{"a": "Հայ", "b": 1}])

    def test_stats(self):
        w = openalex.slim_work(RAW)
        s = stats.compute([w, {**w, "id": "W2", "is_oa": False, "countries": ["AM"]}])
        self.assertEqual(s["by_year"][2023], {"works": 2, "oa_works": 1, "citations": 14, "international": 1})
        self.assertEqual(s["by_country"]["DE"], 1)
        self.assertNotIn("AM", s["by_country"])
        self.assertEqual(s["by_institution"]["I1"], 2)
        with tempfile.TemporaryDirectory() as d:
            stats.write(s, Path(d) / "stats", Path(d) / "STATS.md")
            self.assertIn("| 2023 | 2 | 50.0% | 50.0% | 14 |", (Path(d) / "STATS.md").read_text())


if __name__ == "__main__":
    unittest.main()
