#!/usr/bin/env python3
"""Reproducible opening-board enumeration + dice-exposure experiments.

Not a full Catan game simulator. No output here estimates win probability.
Standard 19-hex resource/number inventory; random layouts can include adjacent red numbers.
"""
import csv, json, random, math, argparse, statistics, collections
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
RESOURCES=['wood']*4+['brick']*3+['sheep']*4+['wheat']*4+['ore']*3+['desert']
NUMBERS=[2,3,3,4,4,5,5,6,6,8,8,9,9,10,10,11,11,12]
PIPS={n:(6-abs(7-n)) for n in range(2,13) if n!=7}
DICE=[a+b for a in range(1,7) for b in range(1,7)]
AXIAL=sorted([(q,r) for q in range(-2,3) for r in range(-2,3) if max(abs(q),abs(r),abs(q+r))<=2],key=lambda t:(t[1],t[0]))
assert len(AXIAL)==19

def geometry():
    vertices={}; hex_centers=[]; hex_vertices=[]
    for q,r in AXIAL:
        x=math.sqrt(3)*(q+r/2);y=1.5*r
        hex_centers.append([round(x,5),round(y,5)])
        vi=[]
        for k in range(6):
            a=math.radians(-90+60*k); px=round(x+math.cos(a),5);py=round(y+math.sin(a),5)
            vertices.setdefault((px,py),set()).add(len(hex_vertices));vi.append((px,py))
        hex_vertices.append(vi)
    keys=sorted(vertices,key=lambda x:(x[1],x[0])); index={k:i for i,k in enumerate(keys)}
    neighbor_sets=[set() for _ in keys]
    hex_vids=[]
    for h in hex_vertices:
        ix=[index[v] for v in h];hex_vids.append(ix)
        for i in range(6):
            a,b=ix[i],ix[(i+1)%6];neighbor_sets[a].add(b);neighbor_sets[b].add(a)
    out=[{'id':i,'x':v[0],'y':v[1],'hexes':sorted(vertices[v]),'neighbors':sorted(neighbor_sets[i])} for i,v in enumerate(keys)]
    assert len(out)==54 and all(len(v['hexes']) in (1,2,3) for v in out)
    return hex_centers,out,hex_vids
CENTERS, VERTICES, HEX_VIDS = geometry()

def make_board(seed):
    rng=random.Random(seed)
    rs=RESOURCES[:];rng.shuffle(rs)
    ns=NUMBERS[:];rng.shuffle(ns)
    tiles=[]
    for i,(res,(q,r)) in enumerate(zip(rs,AXIAL)):
        t={'id':i,'q':q,'r':r,'x':CENTERS[i][0],'y':CENTERS[i][1], 'resource':res,'number':None if res=='desert' else ns.pop(), 'vertices':HEX_VIDS[i]}
        tiles.append(t)
    return {'seed':seed,'tiles':tiles,'vertices':VERTICES,'rules':'base-game-resource-counts; randomized-tokens; ports-not-modeled'}

def feature(board,vertex_id):
    v=VERTICES[vertex_id];tilelist=[board['tiles'][h] for h in v['hexes']]
    t=[x for x in tilelist if x['resource']!='desert']
    pips=sum(PIPS[x['number']] for x in t)
    rp={r:0 for r in ['wood','brick','sheep','wheat','ore']}
    numbers=[]
    for x in t:
        rp[x['resource']]+=PIPS[x['number']]
        numbers.append(x['number'])
    return {'vertex_id':vertex_id,'pips':pips,'resource_diversity':sum(a>0 for a in rp.values()),
            'number_diversity':len(set(numbers)), **{r+'_pips':p for r,p in rp.items()},
            'coastal':int(len(v['hexes'])<3)}

def pair_feature(fa,fb):
    return {
        'total_pips':fa['pips']+fb['pips'],
        'resource_diversity':sum((fa[r+'_pips']+fb[r+'_pips'])>0 for r in ['wood','brick','sheep','wheat','ore']),
        'wood_pips':fa['wood_pips']+fb['wood_pips'],
        'brick_pips':fa['brick_pips']+fb['brick_pips'],
        'sheep_pips':fa['sheep_pips']+fb['sheep_pips'],
        'wheat_pips':fa['wheat_pips']+fb['wheat_pips'],
        'ore_pips':fa['ore_pips']+fb['ore_pips'],
        'covered_hexes':len(set(VERTICES[fa['vertex_id']]['hexes'])|set(VERTICES[fb['vertex_id']]['hexes'])),
        'legal_pair':int(fb['vertex_id'] not in VERTICES[fa['vertex_id']]['neighbors'] and fa['vertex_id']!=fb['vertex_id'])
    }

def write_csv(path, rows, columns):
    with open(path,'w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=columns,extrasaction='ignore');w.writeheader();w.writerows(rows)

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--boards',type=int,default=250);parser.add_argument('--dice-trials',type=int,default=20000);parser.add_argument('--seed',type=int,default=20261109);args=parser.parse_args()
    out=ROOT/'data'/'derived';out.mkdir(parents=True,exist_ok=True)
    first_board=make_board(args.seed)
    (out/'example_board.json').write_text(json.dumps(first_board,separators=(',',':')))
    vr=[];pairs=[]; samples=[];tile_rows=[];rng=random.Random(args.seed+10)
    for k in range(args.boards):
        seed=args.seed+k;board=make_board(seed);fs=[feature(board,i) for i in range(54)]
        for t in board['tiles']:tile_rows.append({'board_seed':seed,'hex_id':t['id'],'q':t['q'],'r':t['r'],'resource':t['resource'],'number':t['number'] or '', 'pips':PIPS.get(t['number'],0)})
        for f in fs:vr.append({'board_seed':seed,**f})
        legal=[]
        for i in range(54):
            for j in range(i+1,54):
                pf=pair_feature(fs[i],fs[j])
                if not pf['legal_pair']:continue
                legal.append((i,j,pf))
                pairs.append({'board_seed':seed,'first_vertex':i,'second_vertex':j,**{x:y for x,y in pf.items() if x!='legal_pair'}})
        # Sample board-opening pair independently of performance.
        for z in range(args.dice_trials//args.boards+(1 if k<args.dice_trials%args.boards else 0)):
            i,j,pf=rng.choice(legal)
            hist=collections.Counter(rng.choice(DICE) for _ in range(72))
            # Production count from the *two starting settlements only*, before robber/discard/city.
            actual=0; by_res={r:0 for r in ['wood','brick','sheep','wheat','ore']}
            for vid in (i,j):
                for h in VERTICES[vid]['hexes']:
                    t=board['tiles'][h]
                    if t['number'] is None:continue
                    by_res[t['resource']]+=hist[t['number']]
                    actual+=hist[t['number']]
            expected=72*pf['total_pips']/36
            samples.append({'board_seed':seed,'first_vertex':i,'second_vertex':j,'rolls':72,
                'expected_production':round(expected,4),'observed_production':actual,
                'luck_delta':round(actual-expected,4),**{'received_'+r:by_res[r] for r in by_res}})
    write_csv(out/'board_tiles.csv',tile_rows,['board_seed','hex_id','q','r','resource','number','pips'])
    edge_pairs=sorted((a,b) for a,v in enumerate(VERTICES) for b in v['neighbors'] if a<b)
    assert len(edge_pairs)==72
    (out/'board_topology.json').write_text(json.dumps({'hex_axial_coordinates':AXIAL,'hex_vertices':HEX_VIDS,'vertices':VERTICES,'edges':edge_pairs},separators=(',',':')))
    write_csv(out/'board_vertices.csv',vr,['board_seed','vertex_id','pips','resource_diversity','number_diversity','wood_pips','brick_pips','sheep_pips','wheat_pips','ore_pips','coastal'])
    write_csv(out/'opening_pairs.csv',pairs,['board_seed','first_vertex','second_vertex','total_pips','resource_diversity','wood_pips','brick_pips','sheep_pips','wheat_pips','ore_pips','covered_hexes'])
    write_csv(out/'dice_exposure_trials.csv',samples,['board_seed','first_vertex','second_vertex','rolls','expected_production','observed_production','luck_delta','received_wood','received_brick','received_sheep','received_wheat','received_ore'])
    deltas=[s['luck_delta'] for s in samples]
    metadata={'generated_utc':'2026-11-09','generator':'scripts/generate_openings.py','rng_seed':args.seed,'boards':args.boards,
       'board_tile_rows':len(tile_rows),'board_edges_per_board':len(edge_pairs),'opening_vertices':len(vr),'legal_opening_pairs':len(pairs),'dice_trials':len(samples),
       'dice_trial_roll_count':72,'dice_trial_mean_delta':round(statistics.mean(deltas),3),
       'dice_trial_p05_delta':round(sorted(deltas)[int(.05*len(deltas))],2),
       'dice_trial_p95_delta':round(sorted(deltas)[int(.95*len(deltas))],2),
       'evidence':'synthetic, base-game board geometry plus theoretical 2d6 rolls; not human outcomes or a win model',
       'limitations':['Ports and opponent blocking are not included','Number token positions randomized, not constrained against adjacent 6/8','Dice experiment assumes static two-settlement opening; no expansion, robber, discard, or city production','Does not estimate probability of winning']}
    (out/'generation_metadata.json').write_text(json.dumps(metadata,indent=2))
    print(json.dumps(metadata,indent=2))

if __name__=='__main__':main()
