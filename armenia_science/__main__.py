"""Build an open dataset of Armenia's scientific output."""

import argparse
import sys

from . import openalex, ror, stats


def main(argv=None):
    p = argparse.ArgumentParser(prog="armenia_science", description=__doc__)
    p.add_argument("--data-dir", default="data")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("institutions", help="Fetch Armenian research organisations from ROR")
    h = sub.add_parser("works", help="Harvest Armenia-affiliated works from OpenAlex")
    h.add_argument("--from-year", type=int, default=1991)
    h.add_argument("--to-year", type=int)
    s = sub.add_parser("stats", help="Build CSV tables and the Markdown summary")
    s.add_argument("--summary", default="STATS.md")
    args = p.parse_args(argv)

    if args.cmd == "institutions":
        print(f"{len(ror.harvest(args.data_dir))} institutions")
    elif args.cmd == "works":
        try:
            openalex.harvest(args.data_dir, args.from_year, args.to_year)
        except RuntimeError as e:
            sys.exit(f"OpenAlex harvest failed: {e}\nSet OPENALEX_API_KEY (free at https://openalex.org/settings/api).")
    elif args.cmd == "stats":
        stats.run(args.data_dir, args.summary)


if __name__ == "__main__":
    main()
