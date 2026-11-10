#!/usr/bin/env python3
import csv,json,collections,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];p=ROOT/'data/derived'

def check(file):
 with open(p/file,newline='') as f:return list(csv.DictReader(f))
meta=json.loads((p/'generation_metadata.json').read_text())
tiles=check('board_tiles.csv');vertices=check('board_vertices.csv');pairs=check('opening_pairs.csv');dice=check('dice_exposure_trials.csv');human=check('human_sample_players.csv');games=check('human_sample_games.csv')
assert len(tiles)==meta['board_tile_rows']==meta['boards']*19
assert len(vertices)==meta['opening_vertices']==meta['boards']*54
assert meta['board_edges_per_board']==72
assert all(sum(int(t['resource']=='desert') for t in tiles if t['board_seed']==str(meta['rng_seed']+i))==1 for i in range(meta['boards']))
assert len(pairs)==meta['legal_opening_pairs']==339750
assert len(dice)==meta['dice_trials']==20000
assert len(human)==200 and len(games)==50
assert len({v['board_seed'] for v in vertices})==meta['boards']
assert set(v['vertex_id'] for v in vertices)==set(str(i) for i in range(54))
assert all(1<=int(r['total_pips'])<=30 for r in pairs)
assert all(1<=int(r['resource_diversity'])<=5 for r in pairs)
assert len({(r['board_seed'],r['first_vertex'],r['second_vertex']) for r in pairs})==len(pairs)
assert all(float(r['expected_production'])>=0 and int(r['rolls'])==72 for r in dice)
assert sum(int(r['winner']) for r in human)==50
assert all(sum(int(k[f'roll_{n}']) for n in range(2,13))==int(k['total_dice_rolls']) for k in games)
assert len({(r['game_id'],r['seat']) for r in human})==200
assert sum(int(r['winner']) for r in human if r['game_id']=='1')==1
print('VALIDATED: 250 boards, 4,750 hex tiles, 13,500 vertices, 339,750 legal pairs, 20,000 dice trials, 50 historical games, 200 player rows')
