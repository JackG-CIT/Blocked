"""Writes BlockedV2/seed_levels.py: the voyage, its chapters, and their ratings.

    cd tools
    ..\\.venv\\Scripts\\python assemble.py

Levels come from the current seed_levels.py (by name), the hard levels in
hard_levels.py, and new designs in new_levels.py. Edit CHAPTERS below to change
the order; chapters can be any length. Every level is rated again (rating.py)
except the hard levels, whose ratings and proven-shortest solutions are kept.
"""
import os
import sys
import pprint
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import seed_levels as old
import rating
import fast
import hard_levels
import new_levels

HERE = os.path.dirname(os.path.abspath(__file__))
OLD = {lv['name']: lv for lv in old.LEVELS}
for lv in old.LEVELS:
    for was in lv.get('was', ()):
        OLD.setdefault(was, lv)
NEW = {lv['name']: lv for lv in new_levels.LEVELS}
HARD = {lv['name']: {k: lv[k] for k in ('name', 'notes', 'map', 'links', 'difficulty', 'par', 'solution')}
        for lv in hard_levels.HARD}


# The old Last Broadside (the user's Level 12, rebuilt) is kept as an expert level.
_brig = [lv for lv in old.LEVELS if lv['name'] in ('The Last Broadside', 'Brig Break') and len(lv['map'][0]) == 25]
OLD['Brig Break'] = dict(_brig[0], name='Brig Break', was=[],
                         notes='Break out of the brig, blast the hold open, and give her a broadside to remember.')


def level(name):
    """A level by name: a new design first, then the current voyage, then the hard pile."""
    for pool in (NEW, OLD, HARD):
        if name in pool:
            return dict(pool[name])
    raise KeyError(name)


# (title, idea, level names). Chapter titles match story.py's keys.
CHAPTERS = [
    ('Sea Legs', 'pushing crates', [
        'Shore Leave', 'Heave Ho', 'Wedged', 'One at a Time', 'Stowaway Shuffle']),
    ('Pressure', 'plates and gates', [
        'Dead Weight', 'Two Locks', 'Hold the Door', 'Tangled Rigging']),
    ('Locks', 'bigger plate puzzles', [
        'Cargo Hold', 'The Brig', 'Deadbolt', 'Nine Locks', 'Seven Seals']),
    ('The Squeeze', 'squeezing crates out of shutting gates', [
        'Squeeze Play', 'Shove Off', 'Lock Gate', 'Dry Dock', 'Pinch Point']),
    ('Gunpowder', 'cannons and fuses', [
        'Load and Light', 'Clear the Way', 'Open Fire', 'Broadside', 'Powder Monkey', 'Powder Keg',
        'Run the Gauntlet', 'Crossfire']),
    ("Davy Jones' Locker", 'loaded fuses, and everything at once', [
        "Davy Jones' Locker", 'Hair Trigger', 'The Long Shot', 'The Last Broadside']),
    ('Endgame', 'the deck battle and the kraken', [
        'The Black Queen', 'The Kraken']),
    ('Expert Waters', 'bonus levels for experts, after the ending', [
        'Stomp', 'Fire in the Hole',
        'Crossed Lines', 'Through the Gates', 'Pinch and Tuck', 'Back to Back', 'Four Bells', 'Long Haul',
        'The Long Way Round', 'Relay', 'Conveyor', 'Backfire', 'Down the Hatch', 'The Chimney',
        'Powder Room', 'Brig Break']),
]
# Chapters whose levels each stand alone (a chest at the end of every level, no walking on).
LOOSE = ['Endgame', 'Expert Waters']
# Chapters after the story's ending.
BONUS = ['Expert Waters']


# Levels too big to rate with a full search use a known solution (from the stage solver).
_sol = lambda f: open(os.path.join(HERE, 'solutions', f)).read().strip()
KNOWN_SOLUTIONS = {'Seven Seals': _sol('l6_solution.txt'), 'Nine Locks': _sol('l7_solution.txt'),
                   'Pinch Point': _sol('l9_solution.txt'), 'Powder Room': _sol('l11_solution.txt'),
                   'Brig Break': _sol('l12_solution.txt')}
KNOWN_SOLUTIONS.update(getattr(new_levels, 'SOLUTIONS', {}))
GIANTS = {'Seven Seals', 'Nine Locks', 'Pinch Point', 'Powder Room', 'Brig Break'}
GIANTS |= set(getattr(new_levels, 'GIANTS', ()))
EXACT_PAR = {'Seven Seals': 44}
EXACT_PAR.update(getattr(new_levels, 'EXACT_PAR', {}))


def rate_offline(lv):
    """Same formula as rating.py, but with the fast solver so big levels can be rated."""
    if lv['name'] in HARD:
        print(f"  {lv['name']}: {lv['difficulty'] / 2:g} skulls (kept), par {lv['par']}")
        return
    spec = {'map': [r.replace('D', '.') for r in lv['map']], 'links': lv['links'], 'health': lv.get('health', {})}
    W, H, tiles = old.parse(spec)
    F = fast.Fast(W, H, tiles)
    r = {'solvable': False} if lv['name'] in GIANTS else fast.solve(F, max_states=1_500_000, stats=True)
    exact = r['solvable']
    if exact:
        sol, states, ruin = r['solution'], r['states'], r['push_ruin']
    else:
        sol = KNOWN_SOLUTIONS.get(lv['name']) or lv['solution']
        states, ruin = 30_000_000, 0.35      # too big to count: assume a typical trap rate
    s, pushes = F.start, 0
    for ch in sol:
        n = F.move(s, 'UDLR'.index(ch))
        assert n is not None, lv['name']
        pushes += n[1] != s[1]
        s = n
    assert F.exits >> s[0] & 1, lv['name'] + ' solution does not win'
    kinds = {t['type'] for t in tiles}
    value = rating.score(len(sol), pushes, states, ruin, ('pressureplate' in kinds) + ('fuse' in kinds))
    lv['difficulty'] = rating.halves(value)   # half-skull steps, 1-10
    lv['par'] = len(sol) if exact else EXACT_PAR.get(lv['name'])
    lv['solution'] = sol
    print(f"  {lv['name']}: {lv['difficulty'] / 2:g} skulls ({rating.name(lv['difficulty'])}), "
          f"score {value:.1f}, {'par ' + str(len(sol)) if exact else 'best known ' + str(len(sol))}")


def fmt_level(lv):
    out = ['    {']
    out.append(f"        'name': {lv['name']!r},")
    if lv.get('was'):
        out.append(f"        'was': {lv['was']!r},")
    out.append(f"        'notes': {lv['notes']!r},")
    out.append(f"        'difficulty': {lv['difficulty']}, 'par': {lv['par']!r},")
    if lv.get('transition'):
        out.append(f"        'transition': {lv['transition']!r},")
    out.append("        'map': [")
    for r in lv['map']:
        out.append(f"            {r!r},")
    out.append('        ],')
    links = ', '.join(f'{a}: {b}' for a, b in lv['links'].items())
    out.append(f"        'links': {{{links}}},")
    if lv.get('health'):
        out.append(f"        'health': {lv['health']!r},")
    out.append(f"        'solution': {lv['solution']!r},")
    out.append('    },')
    return '\n'.join(out)


HEADER = '''"""The main voyage for `flask --app app seed`, written by tools/assemble.py
(edit the chapter list there, not here).

Each chapter adds a new idea and ends with a harder test of it (its last level
is the chapter's "boss", and gets the boss music). Chapters can be any length
(CHAPTER_LENGTHS). In most chapters the rooms join up: you walk out through a
door into the next room, and the chest waits in the last room. The chapters in
LOOSE_CHAPTERS (the finale, and the Expert Waters bonus) are separate levels,
each with its own chest. BONUS_CHAPTERS come after the story's ending.
Every level has been checked with the solvers: it can be beaten, and it needs
the mechanic it's built around.

Optional per level:
  'transition'  a line shown on the room tally as you walk on to the next room
                (story text lives in story.py; this is the fallback)
  'difficulty'  rating in half skulls (1-10) and 'par' (fewest moves, or None),
                worked out offline by the solver; rating.py has the formula
  'solution'    a known winning route (U/D/L/R); hints follow it on big levels
  'was'         old names, if a level is renamed (so --refresh still finds it)

Map key:  # wall   P pirate (start)   B crate   E treasure (exit)
          _ pressure plate   F fuse   ^ v < > cannon facing that way
          = a crate that starts on a pressure plate
          K kraken   H enemy hull: blocks like a wall; every crate shot into it
            costs it one health, and at 0 all of its squares vanish
            ('health' sets how much each has: {'kraken': 4, 'hull': 3})
          D marks a gate (an empty tile a plate opens). It's only a reminder;
            the link itself is set in "links" as (plate or fuse) -> target.
"""

'''


def main():
    src = open(old.__file__, encoding='utf-8').read()
    tail = src[src.index("SYMBOLS = {"):]
    chapters = [(title, idea, [level(n) for n in names]) for title, idea, names in CHAPTERS]
    seen = set()
    for _, _, levels in chapters:
        for lv in levels:
            assert lv['name'] not in seen, 'twice: ' + lv['name']
            seen.add(lv['name'])
            rate_offline(lv)
    left_out = sorted(set(OLD) - seen - {w for lv in old.LEVELS for w in lv.get('was', ())})
    if left_out:
        print('note: not in the voyage any more:', ', '.join(left_out))
    body = ['LEVELS = [']
    n = 0
    chapters = [c for c in chapters if c[2]]
    for c, (title, idea, levels) in enumerate(chapters, 1):
        body.append(f'    # ===== Chapter {c}: {title} ({idea}) =====')
        for k, lv in enumerate(levels, 1):
            n += 1
            test = k == len(levels) and title not in LOOSE and len(levels) > 1
            body.append(f'    # {n}' + ('  (chapter test)' if test else ''))
            body.append(fmt_level(lv))
    body.append(']')
    body.append('')
    body.append('# Chapter titles, in order, and how many levels each one has.')
    body.append('CHAPTERS = ' + pprint.pformat([t for t, _, _ in chapters]))
    body.append('CHAPTER_LENGTHS = ' + repr([len(l) for _, _, l in chapters]))
    body.append('# Chapters whose levels each stand alone (every level ends at its own chest).')
    body.append('LOOSE_CHAPTERS = ' + repr([t for t in LOOSE if any(t == c[0] for c in chapters)]))
    body.append("# Chapters after the story's ending.")
    body.append('BONUS_CHAPTERS = ' + repr([t for t in BONUS if any(t == c[0] for c in chapters)]))
    body.append('')
    body.append('')
    text = HEADER + '\n'.join(body) + '\n' + tail
    open(old.__file__, 'w', encoding='utf-8', newline='\n').write(text)
    print('wrote', n, 'levels in', len(chapters), 'chapters')


if __name__ == '__main__':
    main()
