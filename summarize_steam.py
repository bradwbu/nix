import json
with open('/home/brad/.openclaw/workspace/steam-library.json') as f:\n    lib = json.load(f)\ntotal_min = sum(g.get('playtime', 0) for g in lib)\nprint(f'TOTAL_GAMES:{len(lib)}')
print(f'TOTAL_HRS:{total_min/60:.1f}')
print('TOP20:')
for g in lib[:20]:
    hrs = g.get('playtime', 0) / 60
    recent = g.get('playtimeLastTwoWeeks', 0) / 60
    print(f"{g['name']} | {hrs:.1f}h total | {recent:.1f}h last2w")
print('UNPLAYED:', sum(1 for g in lib if g.get('playtime', 0) == 0))
over100 = [g for g in lib if g.get('playtime', 0) / 60 >= 100]
print(f'GAMES_OVER_100H:{len(over100)}')
