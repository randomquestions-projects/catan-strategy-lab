#!/usr/bin/env python3
"""Within-game observed opening comparisons in the tiny 50-game pilot.

Cluster bootstrap resamples games, not independent player rows. Not causal effects.
"""
from pathlib import Path
import csv,random,statistics,collections,json
ROOT=Path(__file__).resolve().parents[1]
rows=list(csv.DictReader(open(ROOT/'data/derived/human_sample_players.csv')))
games=collections.defaultdict(list)
for r in rows:
 for k in ['starting_pips','starting_resource_diversity','dice_production_total','starting_ore_pips','starting_wheat_pips','starting_sheep_pips','starting_wood_pips','starting_brick_pips']:r[k]=int(r[k])
 r['winner']=int(r['winner']);games[r['game_id']].append(r)
assert len(games)==50
rng=random.Random(20261109)
features=['starting_pips','starting_resource_diversity','dice_production_total','starting_ore_pips','starting_wheat_pips','starting_sheep_pips']
results={}
for k in features:
 ds=[next(r[k] for r in a if r['winner']==1)-statistics.mean(r[k] for r in a if r['winner']==0) for a in games.values()]
 draws=sorted(statistics.mean(rng.choices(ds,k=len(ds))) for i in range(4000))
 results[k]={'mean_within_game_winner_vs_other_delta':round(statistics.mean(ds),3),'bootstrap_ci_95_game_cluster':[round(draws[100],3),round(draws[3900],3)]}
# Proportion of games won by one of players tied for highest opening pips
highest=sum(any(r['winner']==1 and r['starting_pips']==max(x['starting_pips'] for x in a) for r in a) for a in games.values())
result={'evidence':'small human-game pilot; descriptive, not causal','games':50,'player_rows':200,'analysis_seed':20261109,'bootstrap_resamples':4000,'within_game_comparisons':results,'winner_was_tied_for_highest_starting_pips_games':highest,'winner_was_tied_for_highest_starting_pips_pct':round(100*highest/50,1),'warning':'Source opening fields and large aggregated starting-pip definition have not been reconciled. Do not pool. Historical sample may be biased.'}
(ROOT/'data/derived/human_sample_analysis.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result,indent=2))
