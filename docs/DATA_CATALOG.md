# Data catalog and lineage — Catan Strategy Lab (2026-11-09)

## Evidence tiers

**Tier A — observed games, published aggregates.** Third-party `sousa16/catan-analyzer` contains `data/stats.json` (Git blob SHA `ef209a88c23c47a530824aa375ce9a7b2eb07d0c`, 111,746 bytes). It reports **43,700** parsed games across player counts and dice modes, **40,740** four-player random-dice games, and 572 four-player balanced-dice games. The upstream README claims 43,947 original files. Those are **not equal denominators**. We embedded a sourced extract of the four-player random-dice aggregate in `data/derived/observed_4player_random.json`. This is not an independently verified reprocessing of the source log.

**Tier B — observed player-level pilot.** Kaggle's `lumins/settlers-of-catan-games` is mirrored at `DevinRS/Settlers_of_Catan_Analysis/Analysis1/catanstats.csv` (Git blob SHA `1969909bcecd8fb4b3b7b9ceb293dd8be497e922`, 16,689 bytes). We manually encoded a verified subset of the values in `data/source_registry/observed50_compact.txt`, and generated `human_sample_games.csv` (50 game rows) and `human_sample_players.csv` (200 player rows). Derived fields include turn-order/seat, winner (highest displayed points), starting resource/pip exposures, dice production, final score, and per-game dice rolls. We also generate `human_sample_analysis.json` via `analyze_pilot.py`: winners have +1.007 opening pips compared with the within-game average of other players (game-cluster bootstrap 95% interval +0.360 to +1.653), and 24 of 50 winners were tied for top opening-pip score (48%). This small and potentially unrepresentative sample does **not** reconcile with the large sample's opening-pip result; no pooling or independent validation has been attempted. The game mode, underlying sampling method, skill level, and license are not established; use pilot evidence cautiously. Port and desert positions encoded as 0-prefixed tokens are excluded from pip exposure. This derived sample does not preserve every original source column; `fetch_external_sources.py` can download the full original CSV on an internet-enabled machine. **Do not compare the pilot starting-pip totals directly with the large aggregate until starting-feature definitions and extraction logic have been reconciled.**

**Tier C — board enumeration.** `generate_openings.py` uses the standard 19-hex island, 54 settlement vertices, the standard resource tile counts (wood 4, brick 3, sheep 4, wheat 4, ore 3, desert 1), and token multiset (2 and 12 once, 3–6 and 8–11 twice). 250 independently shuffled layouts (seed 20261109 through 20261358). For each board, all 54 possible first intersections and all **1,359** two-intersection combinations obeying the distance rule are enumerated, for **339,750** total legal pairs. (Unoccupied-board pairs only; nothing here guarantees a pair is obtainable in real snake draft.) Exports: `board_tiles.csv` (all 4,750 hexes), `board_topology.json` (54 vertices / 72 edges / 19 axial hex coordinates), `board_vertices.csv`, `opening_pairs.csv`, `example_board.json`, `example_boards.json`. No robber, ports, player blocking, or actual strategy play is modeled. Token placements are randomly shuffled and may place 6 and 8 adjacent, unlike many guided setups.

**Tier D — dice-only Monte Carlo.** `dice_exposure_trials.csv` runs 20,000 independently seeded 72-roll 2d6 sequences over randomly selected *legal starting pairs* in those boards. It counts only static starting-settlement resource production; no robber, settlements/cities gained later, discarded cards, bank shortages, development cards, trading, or strategic decisions. Expectation per 72 rolls is `72 * pair_total_pips / 36`. Positive/negative deviations are **resource production luck**, NOT percent of wins due to luck, and NOT player skill estimates.

**Tier E — reproducible full-game simulator (runner, not run).** `scripts/run_catanatron_baseline.py` imports Catanatron, version-stamps results, and starts a random-policy game baseline. Its output is not bundled and was not executed in this offline build. Future controlled comparisons should use matched boards, seats, opponent policy mixes, and common-random-number experiments where the engine supports them. Catanatron itself is GPL-3.0; no simulator code is copied into this project.

## Eight research modules and the required data

| Module | Currently available | Next data / method |
|---|---|---|
| 1. Optimal openings | 13.5k locations; 339.75k legal pairs; 50 human-game pilot; 40k game aggregate | ports, snake draft, opponent blocking, fitted held-out win model |
| 2. Skill vs. luck | 20k dice-only resource simulations | replicate complete games with matched random seeds and different policies |
| 3. Strategy Index | Opening feature strategies defined in website | full-game policy assignments and winner outcomes; randomized balanced experiments |
| 4. Development-card analytics | Observed winner versus other-player aggregate | event-level purchase/action, game state, development-card mix and opportunity costs |
| 5. Trading economics | Published trade-income aggregates | bilateral trade offers/acceptance, resource inventory, immediate and downstream game value |
| 6. Win predictor | Game-level final outcomes; no complete turn snapshots locally | timestamped game states and calibrated out-of-game holdout |
| 7. Robber strategy | Published robber summaries | actions, targets, resource block, game standings and placement alternatives |
| 8. AI tournament | Catanatron integration runner | registered agents, seeds, cross-play Elo, reproducible logs and policy identifiers |

## Compliance and distribution

- Colonist-origin raw data is described as **research/educational** by an upstream repository, not an automatically sublicensable public-domain data resource.
- Verify permissions and ownership of original raw logs and the Kaggle sample before republishing rows or derived downloadable datasets. The source URLs are included for transparency; external files downloaded into `data/external/` are excluded by `.gitignore`.
- Only **our newly generated synthetic geometry and dice-trial tables** plus curated attributed aggregate/pilot features are included in the ZIP. Before publishing the ZIP in a public GitHub repository, perform an independent license review of the pilot-derived rows.
- **Do not scrape Colonist or use undocumented APIs**. The project does not use them.

## Critical statistical cautions

- Winner/loser resource income and cities built are **post-treatment/post-game variables** with reverse causality potential and game-length confounding. Never claim they are independent causal drivers just because the winner/loser differences are large.
- Starting pip numbers in source datasets are not guaranteed to be identically computed. Derived opening-pip comparisons require validation on a common definition.
- A strategy score calculated on a board is **not** a calibrated win probability. For estimated win probabilities, collect policy-attributed full-game outcomes, train out-of-fold, test across random boards and bot-policy mixtures, and check calibration.
- Rows from a shared game are dependent; uncertainty intervals for player-level analyses must cluster at the game level or resample entire games.
- Some data are from 2-, 3-, 5-, 6-, 7- or 8-player games or balanced dice; filter mode and player count appropriately.

## Data dictionaries

See `docs/SCHEMAS.md` for all file columns, sample records, common keys and valid joins.

## Verifiable upstream links

- Large aggregates and engineered Parquet: https://github.com/sousa16/catan-analyzer
- The large dataset's original description: https://github.com/OrgadYron/catan_43k_games_dataset
- 50-game source mirror: https://github.com/DevinRS/Settlers_of_Catan_Analysis/tree/main/Analysis1
- Original pilot listing: https://www.kaggle.com/datasets/lumins/settlers-of-catan-games
- Full game simulation library: https://github.com/bcollazo/catanatron
