# autoresearch for grant sources

Adapted from karpathy/autoresearch. There, an agent edits `train.py`, trains for
5 minutes, and keeps the change only if `val_bpb` improves. Here:

| autoresearch | this loop |
|---|---|
| `prepare.py` (fixed eval) | `evaluate.py` — fixed rubric, metric **relevance@100** (higher is better) |
| `train.py` (agent edits) | `pool.jsonl` — candidate funding sources with structured attributes |
| one 5-minute training run | one research experiment: a single hypothesis about where relevant money is, checked with web search |
| `results.tsv` | `results.tsv` (+ `rejected.jsonl` for discarded candidates) |

## Rules

1. Read `profile.md`. Never edit `evaluate.py` or the profile mid-run.
2. Each experiment tests **one hypothesis** ("Horizon-associated status opens
   EIC programmes", "rare-disease foundations fund companies abroad", …),
   written to `experiments/NNN.json` and applied with `python run.py`.
3. Every record needs an https evidence URL for the programme. Attributes are
   set from what the funder publishes, not from what would score well. Set
   `verified: true` only if the eligibility/status was checked against a
   source during this run.
4. `add` experiments are kept only when relevance@100 strictly increases.
   Discarded candidates go to `rejected.jsonl` and are not retried.
5. `verify` experiments correct facts (eligibility, status, closed programmes)
   and are **always kept**, even when the metric falls — gaming the metric
   with stale data is the one thing this loop must not do.
6. Prefer simplicity: one programme per record; a funder with many unrelated
   calls gets one record per call family, not per deadline.
7. Stop after 100 experiments and run `python run.py --report`.
