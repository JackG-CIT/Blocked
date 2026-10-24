import os
import json, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
from seed_levels import LEVELS, parse
TOOLS = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')
import fast, levels_user as U, l12

def health_of(F, walls):
    """Each monster's health left in a fast.py state."""
    return {kind: bin((walls >> (F.token0 + 64 * m)) & ((1 << 64) - 1)).count('1')
            for m, kind in enumerate(fast.MONSTERS)}


# Small levels that exercise the kraken and hull rule (solver.py MONSTERS).
KRAKEN_CASES = [
    ('Kraken test: three shots', [
        '##########',
        '#.......K#',
        '#>......KE',
        '#.......K#',
        '#..F....K#',
        '#.BBB..PK#',
        '#.......K#',
        '##########',
    ], {(3, 4): (1, 2)}, {'kraken': 3}),
    ('Hull test: sink her, then walk the wreck', [
        '#########',
        '#P.....H#',
        '#..B.F.H#',
        '#....B.HE',
        '#>.....H#',
        '#......H#',
        '#########',
    ], {(5, 2): (1, 4)}, {'hull': 2}),
    ('Water test: shots fly over, the pirate cannot', [
        '#########',
        '#P.....H#',
        '#..B.F.H#',
        '#....B.HE',
        '#>...~~H#',
        '#....~~H#',
        '#########',
    ], {(5, 2): (1, 4)}, {'hull': 2}),
]


def case(name, rows, links, moves, health=None):
    spec = {'map': [r.replace('D', '.') for r in rows], 'links': links, 'health': health or {}}
    W, H, tiles = parse(spec)
    F = fast.Fast(W, H, tiles)
    s = F.start
    states = []
    for ch in moves:
        s = F.move(s, 'UDLR'.index(ch))
        p, b, w = s
        states.append([[p % W, p // W], sorted([i % W, i // W] for i in range(W * H) if b >> i & 1), health_of(F, w)])
    # hint-solver checkpoints: exact remaining distance from a few late positions
    checks = []
    for k in (len(moves) - 25, len(moves) - 12, len(moves) - 5):
        if k <= 0: continue
        s = F.start
        for ch in moves[:k]:
            s = F.move(s, 'UDLR'.index(ch))
        G = fast.Fast(W, H, tiles); G.start = s
        r = fast.solve(G, max_states=250000)
        if r['solvable']:
            checks.append({'at': k, 'moves': r['moves']})
    return {'name': name, 'level': {'width': W, 'height': H, 'tiles': tiles}, 'moves': moves,
            'states': states, 'won': bool(F.exits >> s[0] & 1) or None, 'checks': checks}

def main():
    """Every voyage level (with its stored solution) plus the hard extra levels."""
    import hard_levels
    skip = set(sys.argv[1:])   # levels whose stored solution is known to be out of date
    cases = [case(spec['name'], spec['map'], spec['links'], spec['solution']) for spec in LEVELS if spec['name'] not in skip]
    cases += [case(lv['name'], lv['map'], lv['links'], lv['solution']) for lv in hard_levels.HARD
              if lv['name'] not in {spec['name'] for spec in LEVELS}]
    for name, rows, links, health in KRAKEN_CASES:
        spec = {'map': rows, 'links': links, 'health': health}
        W, H, tiles = parse(spec)
        r = fast.solve(fast.Fast(W, H, tiles), max_states=3_000_000)
        assert r['solvable'], name
        # The other two rule files must agree on the shortest solution.
        import solver
        r2 = solver.solve(solver.Level(W, H, tiles), max_states=3_000_000)
        assert r2['solvable'] and r2['moves'] == r['moves'], (name, r2.get('moves'), r['moves'])
        # One less health makes it easier; one more makes it impossible (or longer).
        hard = dict(health, **{k: v + 1 for k, v in health.items()})
        W, H, t2 = parse({'map': rows, 'links': links, 'health': hard})
        r3 = fast.solve(fast.Fast(W, H, t2), max_states=3_000_000)
        print(f"{name}: {r['moves']} moves; with one more health: {r3.get('moves', 'unsolvable')}")
        cases.append(case(name, rows, links, r['solution'], health))
    json.dump(cases, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cases.json'), 'w'))
    print(len(cases), 'cases', sum(len(c['checks']) for c in cases), 'hint checks')


if __name__ == '__main__':
    main()
