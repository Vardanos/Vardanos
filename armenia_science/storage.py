"""Deterministic gzip JSONL storage so unchanged data produces identical bytes in git."""

import gzip
import io
import json
from pathlib import Path


def write_jsonl_gz(path, records):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    buf = io.BytesIO()
    with gzip.GzipFile(filename="", mode="wb", fileobj=buf, mtime=0) as gz:
        for rec in records:
            gz.write((json.dumps(rec, ensure_ascii=False, sort_keys=True) + "\n").encode("utf-8"))
    path.write_bytes(buf.getvalue())


def read_jsonl_gz(path):
    with gzip.open(path, "rt", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                yield json.loads(line)


def iter_works(works_dir):
    for path in sorted(Path(works_dir).glob("*.jsonl.gz")):
        yield from read_jsonl_gz(path)
