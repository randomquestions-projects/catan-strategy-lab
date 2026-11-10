#!/usr/bin/env python3
"""Run genuine full-game self-play once Catanatron has been installed locally.

Install `pip install catanatron`. This baseline uses four random agents, not strong
policies; no self-play runs from this file are included or claimed in the initial site.
"""
import argparse,csv,json,random,datetime,importlib.metadata
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def main():
  ap=argparse.ArgumentParser();ap.add_argument('--games',type=int,default=500);ap.add_argument('--seed',type=int,default=20261109);args=ap.parse_args()
  try:from catanatron import Game,RandomPlayer,Color
  except ImportError:raise SystemExit('Install simulator first: pip install catanatron')
  colors=(Color.RED,Color.BLUE,Color.WHITE,Color.ORANGE)
  out=ROOT/'data'/'external';out.mkdir(exist_ok=True)
  dest=out/'catanatron_random_baseline.csv'
  with open(dest,'w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=['trial','seed','winner','agent_policy','player_count','engine']);w.writeheader()
    for i in range(args.games):
      seed=args.seed+i;random.seed(seed)
      players=[RandomPlayer(color) for color in colors]
      game=Game(players)
      winner=game.play()
      w.writerow({'trial':i,'seed':seed,'winner':str(winner),'agent_policy':'random-player','player_count':4,'engine':'catanatron'})
      if (i+1)%100==0:print('Completed',i+1,'full games')
  version=importlib.metadata.version('catanatron')
  (out/'catanatron_random_baseline_metadata.json').write_text(json.dumps({'engine_version':version,'game_count':args.games,'first_seed':args.seed,'policy':'all-random; not a useful strong-strategy benchmark','generated_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()},indent=2))
  print('Wrote',dest)
if __name__=='__main__':main()
