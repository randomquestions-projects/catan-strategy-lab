# Catan Strategy Lab — dataset schemas

Reproducible synthetic files use `board_seed` as the board join key. The `board_topology.json` file maps a `vertex_id` to its adjacent hexes and neighboring settlement vertices. All vertex IDs are zero-based; the website displays `vertex_id + 1`.

| File | Rows | Columns |
|---|---:|---|
| `board_tiles.csv` | 4,750 | `board_seed`, `hex_id`, `q`, `r`, `resource`, `number`, `pips` |
| `board_vertices.csv` | 13,500 | `board_seed`, `vertex_id`, `pips`, `resource_diversity`, `number_diversity`, `wood_pips`, `brick_pips`, `sheep_pips`, `wheat_pips`, `ore_pips`, `coastal` |
| `opening_pairs.csv` | 339,750 | `board_seed`, `first_vertex`, `second_vertex`, `total_pips`, `resource_diversity`, `wood_pips`, `brick_pips`, `sheep_pips`, `wheat_pips`, `ore_pips`, `covered_hexes` |
| `dice_exposure_trials.csv` | 20,000 | `board_seed`, `first_vertex`, `second_vertex`, `rolls`, `expected_production`, `observed_production`, `luck_delta`, `received_wood`, `received_brick`, `received_sheep`, `received_wheat`, `received_ore` |
| `human_sample_games.csv` | 50 | `game_id`, `roll_2`, `roll_3`, `roll_4`, `roll_5`, `roll_6`, `roll_7`, `roll_8`, `roll_9`, `roll_10`, `roll_11`, `roll_12`, `total_dice_rolls`, `winner_seat` |
| `human_sample_players.csv` | 200 | `game_id`, `seat`, `winner`, `final_victory_points`, `dice_production_total`, `total_available_resources`, `starting_pips`, `starting_resource_diversity`, `starting_number_diversity`, `opening_s1_tiles`, `opening_s2_tiles`, `nonproductive_opening_entries`, `starting_wood_pips`, `starting_brick_pips`, `starting_sheep_pips`, `starting_wheat_pips`, `starting_ore_pips` |

## Keys and joining

- `board_tiles.csv`: `(board_seed, hex_id)`; `hex_id` indexes the `hex_vertices` in `board_topology.json`.
- `board_vertices.csv`: `(board_seed, vertex_id)`; includes opening pip-weight exposure by resource.
- `opening_pairs.csv`: `(board_seed, first_vertex, second_vertex)`; vertex IDs always ascending and adjacent vertices excluded.
- `dice_exposure_trials.csv`: `(board_seed, first_vertex, second_vertex)` is **not unique**: trials may sample an opening repeatedly; each row independently samples a 72-roll dice sequence.
- `human_sample_players.csv`: `(game_id, seat)` uniquely identifies one player from the 50-game observational pilot. These rows must not be joined to synthetic boards.
- `human_sample_games.csv`: one row per `game_id` (50 total); includes observed dice histogram.
- `human_sample_analysis.json`: within-game summary derived from `human_sample_players.csv` with game-cluster bootstrap.
- `observed_4player_random.json`: aggregate **not per-game rows**. Cannot be joined to raw human pilot or synthetic data by game ID.

## Known limitations

- Pip scores are dice-outcome weights (2 and 12 = 1; 6 and 8 = 5); units differ from true win probabilities.
- `board_tiles.csv` uses independently shuffled numbers/resource tiles; the layout generation is *not* the guided official 6/8-separated number-token placement.
- No ports, robber, road building, opponent blocking, player trades, strategy or final outcome is generated for synthetic data.
- The historical 50-game pilot does not include complete turn-level event logs or opponent ratings, and its opening-pip definition is not harmonized with the 40k-game aggregate.
- Generated data is designed for reproducible experiments and frontend exploration, **not** supervised win-probability training with invented labels.
