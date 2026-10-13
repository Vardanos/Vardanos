# Grant sources for Denovo Sciences — an autoresearch-style search

**Result:** [`SHORTLIST.md`](SHORTLIST.md) / [`shortlist.csv`](shortlist.csv) list the
100 most relevant non-dilutive funding sources for
[Denovo Sciences](profile.md) (AI drug discovery, Yerevan), ranked after 100 experiments.

## Method

This adapts [karpathy/autoresearch](https://github.com/karpathy/autoresearch).
There, an agent edits `train.py`, trains for 5 minutes and keeps the change only
if `val_bpb` improves. Here ([`program.md`](program.md) has the full rules):

- [`evaluate.py`](evaluate.py) is the fixed rubric. It scores each candidate on
  whether an Armenian LLC can receive the money, topic fit, instrument (grant >
  prize > credits > in-kind), applicant stage, award size, geography and status,
  and penalises unverified records. The metric, **relevance@100**, is the mean
  score of the best 100 candidates.
- [`pool.jsonl`](pool.jsonl) is what the agent edits. Every record carries an
  evidence URL.
- Each of the 100 [`experiments/`](experiments) tests one hypothesis about where
  relevant money is (for example "Armenia's Horizon Europe association opens the
  EIC" or "rare-disease foundations fund companies abroad"). Each was checked
  with web searches and applied with `python run.py experiments/NNN.json`.
- An `add` experiment is kept only if relevance@100 rises. Rejected candidates
  are in [`rejected.jsonl`](rejected.jsonl). A `verify` experiment corrects facts
  and is always kept, even when the metric falls.
- Run `python run.py --replay` to rebuild the pool and [`results.tsv`](results.tsv)
  from the experiment files alone. Run `python run.py --report` to regenerate the
  list.

Outcome: 88 experiments kept, 11 discarded and 1 fix. Relevance@100 went from
0.000 to 0.438. Examples of discards: Neruzh (diaspora founders only), EU4Innovation
pre-seed, Wellcome Discovery (Armenia drops out from 29 Oct 2026), Global
Innovation Fund, Hevolution, the REPAIR Impact Fund, NIAID AViDD, USAID and EIC
Transition (it needs a precursor project).

## Time-sensitive (as of 13 Oct 2026)

| Deadline | Programme | Note |
|---|---|---|
| 28 Oct 2026 | EIC Pathfinder Challenges | Single applicants allowed; check topic fit first |
| ~2 Nov 2026 | MIT Solve 2027 challenges | Small prize; weak topic fit |
| 4 Nov 2026 (unconfirmed) | EIC Accelerator full-proposal cut-off | Short proposals accepted any time |
| 15 Nov 2026 | NATO SPS 2027-1 multi-year projects | Needs a NATO-country co-director |
| 4 Mar 2027 | Horizon Europe Excellence Hubs | Armenia is a widening country |
| ~Feb–Apr 2027 | MMV call, Worldwide Cancer Research, PCF, CARB-X round, EIT Health Catapult, MSCA Staff Exchanges | Annual cycles |

## Caveats

- The ranking is only as good as the rubric. The rubric rewards programmes that
  Denovo can apply to directly over better-fitting programmes that need an
  academic lead. Some disease funders outside Denovo's areas (Alzheimer's, T1D,
  IBD) therefore rank above, for example, the homocystinuria-specific HCU Network.
  Read the score together with the notes.
- Records marked `verified: false` (about a third) come from prior knowledge.
  They were not checked against a 2026 source in this run. Confirm eligibility
  and dates before applying.
- The company profile comes from public sources (Gust, CB Insights, press). It
  found no US, EU or Qatari subsidiary. If one exists, the "needs foreign entity"
  programmes (NIH SBIR, Innovate UK, QSTP, BIRAC, CPRIT) move up.
