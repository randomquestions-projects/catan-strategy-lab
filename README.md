# Catan Strategy Lab · Project 03

A working GitHub Pages-ready website and a reproducible Catan data research package.

**Important: this is an actual interactive prototype and generated dataset, not a full Catan game simulator or validated win-probability product.** The first two research tracks—opening placements and dice-production luck—are activated. The other six have research designs, but unrun experiments are not represented as facts.

## What is delivered

- Interactive, responsive static site with four tabs: **Insights**, **Opening Optimizer**, **Strategy Simulator**, and **Methodology & Data**.
- 18 interactive sample boards with 54 selectable intersections, number tokens, actual distance-rule checks, two-settlement pairing, live strategy-specific rankings, and a clearly labeled heuristic score.
- Dice-production Monte Carlo engine in the browser with configurable roll counts and 2,000 sequences per run; no server or API key.
- Embedded, attributed aggregated results from 40,740 published four-player random-dice games.
- 250 randomized boards, **4,750** tile-layout rows, **13,500** opening intersection rows, **339,750** legal two-settlement pair feature rows, and a 54-vertex / 72-edge board-topology definition.
- 20,000 reproducible 72-roll dice-only trials; all have source and methodology metadata.
- 50 historical pilot games decoded into 200 player rows and 50 game rows from a publicly published CSV subset, with source attribution and license warnings. A reproducible within-game comparison and 4,000-game-cluster-resample uncertainty analysis is included in `human_sample_analysis.json`.
- A public-source download script for the original 50-game CSV and separately published engineered 43k-game Parquet and JSON aggregates. The **large Parquet/raw game logs are not included in the ZIP**, as they were not successfully retrieved in this isolated build.
- An optional Catanatron full-game baseline runner, not yet executed, so no synthetic win rates are claimed.

## Preview or publish

Option A: extract the ZIP and run from the project folder:

```bash
python3 -m http.server 8000
# open http://localhost:8000
```

Option B: create a **public GitHub Pages repository named `catan-strategy-lab`** under the `randomquestions-projects` account, upload the files from this folder to the repo root, then enable Pages → Deploy from branch → `main` / `(root)`. The resulting default site URL should be `https://randomquestions-projects.github.io/catan-strategy-lab/`. Add that URL to your existing analytics home page.

*Privacy note:* On GitHub Pages, the website's HTML/CSS/JavaScript, embedded aggregates, and any CSVs uploaded into the public repo are public. If you want to keep code, analysis methodology, and underlying data private, **publish only `index.html` and the `assets/` directory, plus `.nojekyll`**, not the entire research ZIP; move `scripts/`, `docs/`, `data/`, and `tests/` into a separate private repository. The frontend's rankings necessarily reveal some client-side heuristic logic, so genuinely proprietary scoring or trained models will eventually need a server/API—GitHub Pages alone cannot hide it.

## Reproduce datasets

Python 3.10+ standard library; no pip dependencies for opening generation and validation:

```bash
python3 scripts/generate_openings.py --boards 250 --dice-trials 20000 --seed 20261109
python3 scripts/decode_human_sample.py
python3 scripts/analyze_pilot.py
python3 scripts/validate_datasets.py
```

With internet access (download to ignored `data/external/`):

```bash
python3 scripts/fetch_external_sources.py --sources all
```

To run true full Catan games locally (separate from this opening/dice-only simulator):

```bash
pip install catanatron
python3 scripts/run_catanatron_baseline.py --games 500 --seed 20261109
```

Catanatron may require Python 3.11+ depending on the installed release. Check its installation and GPL-3.0 terms. The runner is an all-random baseline; a sound skill/luck study needs better policies and controlled replications.

## Research and licensing

Read `docs/DATA_CATALOG.md` for source-specific sample sizes, transformation details, common data traps, limitations and rights considerations. The public small dataset and third-party aggregates were read from upstream GitHub research projects. Those do not imply unrestricted rights to reuse original game logs. Before public redistribution of the 50-game-derived data rows, check the original Kaggle data's license. Do not attempt unauthorized scraping of Colonist.

The new site's charts are *observational* or *dice/geometry simulations* as indicated. No reported number is an estimated game-win probability.

## Roadmap

1. Reconcile the pilot and large dataset feature definitions, independently reproduce the large aggregate from its downloadable Parquet when possible, and build opening win-probability models with within-game and time-aware validation.
2. Add harbors, blocked intersections, actual snake draft, guided red-number constraints, and scenario-driven board input to the optimizer.
3. Design a policy tournament in Catanatron: balanced, city engine, roads, dev cards, robber, and trade agents with matched board/seeds; run enough games to reach useful confidence intervals.
4. Add full-game state logging, calibrated win predictor and counterfactual action value. Finally, train and evaluate an AI advisor against held-out agents.

_Catan Strategy Lab is an independent, unofficial analytics project; not affiliated with rights holders._
