#!/usr/bin/env python3
"""Expand compact, human-readable verified 50-game feature extract.

Source: DevinRS/Settlers_of_Catan_Analysis/Analysis1/catanstats.csv
Kaggle original: lumins/settlers-of-catan-games
Only subset of fields retained. 'winner' inferred from maximum displayed points within game.
The six original positions show resource/number exposure at two opening settlements;
port annotations and desert are not production tiles.
"""
from pathlib import Path
import csv,json,collections,statistics
ROOT=Path(__file__).resolve().parents[1]
PIPS={n:6-abs(7-n) for n in range(2,13) if n!=7}
R={'L':'wood','C':'brick','S':'sheep','W':'wheat','O':'ore'}

def decode():
    games=[];players=[]
    for line in (ROOT/'data/source_registry/observed50_compact.txt').read_text().strip().splitlines():
        g,dice,records=line.split('|');g=int(g)
        dc=[int(x,36) for x in dice.split('.')]
        assert len(dc)==11
        points=[int(x.split('-')[0].split('.')[0],36) for x in records.split(';')]
        assert len(points)==4
        games.append({'game_id':g,**{f'roll_{i+2}':n for i,n in enumerate(dc)},'total_dice_rolls':sum(dc),'winner_seat':points.index(max(points))+1})
        for seat,r in enumerate(records.split(';'),1):
            vals,tiles=r.split('-');vp,production,available=[int(v,36) for v in vals.split('.')]
            exposure=collections.defaultdict(int);nums=set();other=[]
            encoded=tiles.split('.');assert len(encoded)==6
            for token in encoded:
                if token.startswith('0'):
                    other.append(token);continue
                res=R[token[-1]];num=int(token[:-1]);w=PIPS[num];exposure[res]+=w;nums.add(num)
            row={'game_id':g,'seat':seat,'winner':int(seat==points.index(max(points))+1),
                 'final_victory_points':vp,'dice_production_total':production,'total_available_resources':available,
                 'starting_pips':sum(exposure.values()),'starting_resource_diversity':sum(exposure[k]>0 for k in R.values()),
                 'starting_number_diversity':len(nums),
                 'opening_s1_tiles':'/'.join(encoded[:3]),'opening_s2_tiles':'/'.join(encoded[3:]),
                 'nonproductive_opening_entries':'/'.join(other),
                 **{f'starting_{k}_pips':exposure[k] for k in R.values()}}
            players.append(row)
    assert len(games)==50 and len(players)==200 and sum(p['winner'] for p in players)==50
    out=ROOT/'data/derived'
    for name,rows in [('human_sample_games.csv',games),('human_sample_players.csv',players)]:
        with open(out/name,'w',newline='') as f:
            w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    return games,players
if __name__=='__main__':
    games,players=decode()
    winners=[x for x in players if x['winner']];others=[x for x in players if not x['winner']]
    print('Decoded',len(games),'games',len(players),'player-rows')
    for k in ['starting_pips','starting_resource_diversity','dice_production_total','total_available_resources']:
       print(k,round(statistics.mean(r[k] for r in winners),2),round(statistics.mean(r[k] for r in others),2))
