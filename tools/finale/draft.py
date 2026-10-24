"""Finale drafts: the deck battle and the kraken. Run to check with the Java solver."""
import os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..')); sys.path.insert(0, os.path.join(HERE, '..', '..'))
import stages, fast
from seed_levels import parse

class Board:
    """Builds a map by coordinates: start all wall, carve floor, put things."""
    def __init__(self, w, h):
        self.g = [['#'] * w for _ in range(h)]
    def floor(self, x0, y0, x1, y1, ch='.'):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                self.g[y][x] = ch
        return self
    def put(self, ch, *cells):
        for x, y in cells:
            self.g[y][x] = ch
        return self
    def rows(self):
        return [''.join(r) for r in self.g]


def queen_map():
    b = Board(30, 13)
    b.put('E', (14, 0))
    b.floor(1, 1, 28, 1, 'H')                 # the Black Queen's hull, alongside
    b.put('.', (4, 2), (14, 2), (24, 2))       # gun ports
    b.floor(1, 3, 28, 4)                       # the gun deck
    b.put('^', (4, 5), (14, 5), (24, 5))       # our cannons, aimed at her hull
    b.put('F', (2, 3), (12, 3), (26, 3))       # their fuses
    b.put('_', (9, 3))                         # opens hold B's gate
    # hold A (left): its hatch is a gate, opened by a plate inside
    b.floor(1, 6, 8, 11).put('.', (7, 5)).put('_', (2, 7)).put('#', (5, 7), (6, 7), (4, 9), (5, 11))
    b.put('B', (5, 6), (3, 8), (7, 8), (2, 10)).put('P', (5, 9))
    b.put('.', (1, 5))                         # hold A's ladder
    # hold B (middle): a two-wide shaft up to the deck; its pen opens from the deck plate
    b.put('.', (16, 5), (17, 5), (16, 6), (17, 6))
    b.floor(10, 8, 18, 11).put('.', (17, 7)).put('#', (12, 10))
    b.put('B', (13, 8), (11, 9), (15, 9))
    # hold C (right): its hatch is a gate, opened by a plate inside; a crawlway joins it to B
    b.floor(20, 6, 28, 11).put('.', (20, 5)).put('_', (21, 8)).put('#', (20, 8), (22, 8), (22, 10), (23, 10))
    b.put('B', (23, 6), (21, 7), (24, 8), (23, 9)).put('.', (28, 5))   # hold C's ladder
    return b.rows()


QUEEN = {
    'name': 'The Black Queen',
    'map': queen_map(),
    'links': {(2, 3): (4, 5), (12, 3): (14, 5), (26, 3): (24, 5), (2, 7): (7, 5), (9, 3): (17, 7), (21, 8): (20, 5)},
    'health': {'hull': 6},
}


def check(lv, mode='greedy3', cap=8_000_000, xmx='8g'):
    W, H, tiles = stages.level_tiles(lv['map'], lv['links'], lv.get('health'))
    t = time.time()
    steps, head = stages.run_java(W, H, tiles, mode, cap, xmx)
    print(lv['name'], mode, ' '.join(head[1:]), f'{time.time() - t:.0f}s')
    if steps is None:
        return None
    F = fast.Fast(W, H, tiles)
    M = fast.Macro(F)
    s, moves = F.start, []
    for src, di in steps:
        moves += fast.walk(F, M, s, src)
        s = F.move((src, s[1], s[2]), di)
        moves.append('UDLR'[di])
    print('  moves', len(moves), 'won', bool(F.exits >> s[0] & 1))
    return ''.join(moves)


if __name__ == '__main__':
    which = sys.argv[1] if len(sys.argv) > 1 else 'queen'
    lv = {'queen': QUEEN}[which]
    for row in lv['map']:
        assert len(row) == len(lv['map'][0]), row
    print(check(lv, *(sys.argv[2:3] or ['greedy3'])))


def staged(lv, plan, mode='macro', cap=12_000_000, xmx='6g'):
    return stages.solve_stages(lv['map'], lv['links'], plan, mode=mode, cap=cap, xmx=xmx, health=lv.get('health'))


QUEEN_PLAN = [{'need': [(2, 7)]}, {'need': [(2, 7), (9, 3)]}] + [{'hp': h, 'mode': 'greedy3'} for h in (5, 4, 3, 2, 1, 0)] + [{}]


def queen2_map():
    b = Board(26, 12)
    b.put('E', (13, 0))
    b.floor(1, 1, 24, 1, 'H')                  # the Black Queen's hull, alongside
    b.put('.', (4, 2), (13, 2), (22, 2))        # gun ports
    b.floor(1, 3, 24, 4)                        # our gun deck
    b.put('^', (4, 5), (13, 5), (22, 5))        # cannons, aimed at her hull
    b.put('F', (2, 3), (11, 3), (24, 3))
    b.put('_', (8, 3))                          # opens hold B's pen
    # hold A: ladder (1,5); hatch (6,5) is a gate, its plate (2,7) is inside
    b.floor(1, 6, 7, 10).put('.', (1, 5), (6, 5)).put('_', (2, 7))
    b.put('#', (4, 7), (5, 7), (3, 9), (6, 10))
    b.put('B', (4, 6), (3, 8), (6, 8), (2, 9)).put('P', (5, 9))
    # hold B: a two-wide shaft; its pen (gate (16,7)) opens from the deck plate
    b.put('.', (15, 5), (16, 5), (15, 6), (16, 6), (16, 7))
    b.floor(9, 8, 16, 10).put('#', (12, 9))
    b.put('B', (11, 8), (14, 9))
    # hold C: ladder (24,5); hatch (19,5) is a gate, its plate (20,7) is inside
    b.floor(18, 6, 24, 10).put('.', (19, 5), (24, 5)).put('_', (20, 7))
    b.put('#', (21, 7), (22, 7), (20, 9), (23, 9))
    b.put('B', (22, 6), (19, 8), (22, 9) if False else (21, 9), (23, 8))
    return b.rows()


QUEEN2 = {
    'name': 'The Black Queen',
    'map': queen2_map(),
    'links': {(2, 3): (4, 5), (11, 3): (13, 5), (24, 3): (22, 5), (2, 7): (6, 5), (8, 3): (16, 7), (20, 7): (19, 5)},
    'health': {'hull': 5},
}
QUEEN2_PLAN = [{'need': [(2, 7)]}, {'need': [(2, 7), (8, 3)]}] + [{'hp': h, 'mode': 'greedy3'} for h in (4, 3, 2, 1, 0)] + [{}]


def kraken_map():
    b = Board(30, 13)
    # the powder room (hub), the cannon and the long tunnel to the kraken
    b.floor(2, 4, 8, 8).put('>', (1, 6)).put('F', (8, 4)).put('P', (5, 8))
    b.put('#', (6, 4))
    b.floor(9, 6, 21, 6)
    # the kraken, and the treasure behind it
    b.floor(22, 4, 24, 8, 'K').floor(25, 6, 27, 6).put('E', (28, 6))
    # north room: its door (3,3) is a gate, opened by a plate at the far end; a ladder at (8,3)
    b.floor(2, 1, 12, 2).put('.', (3, 3), (8, 3)).put('_', (12, 1))
    b.put('#', (9, 2))
    b.put('B', (10, 1), (5, 2), (7, 2))
    # south room: its door (5,9) is a gate, opened by a plate inside; a ladder at (8,9)
    b.floor(2, 10, 12, 11).put('.', (5, 9), (8, 9)).put('_', (11, 11))
    b.put('#', (3, 11))
    b.put('B', (4, 10), (7, 11), (10, 10))
    b.put('B', (4, 5), (3, 7))
    return b.rows()


KRAKEN = {
    'name': 'The Kraken',
    'map': kraken_map(),
    'links': {(8, 4): (1, 6), (12, 1): (3, 3), (11, 11): (5, 9)},
    'health': {'kraken': 5},
}
KRAKEN_PLAN = [{'hp': h, 'mode': 'greedy3'} for h in (4, 3, 2, 1, 0)] + [{}]


def broadside_map():
    b = Board(35, 9)
    # room 1, the brig: its door (9,4) is a gate, opened by a plate inside
    b.floor(1, 1, 8, 7).put('_', (2, 2)).put('.', (9, 4)).put('P', (2, 5))
    b.put('#', (5, 2), (5, 6), (7, 2))
    b.put('B', (4, 3), (4, 5), (6, 4), (3, 6))
    # room 2, the powder store: blast the wall (19,6) through to room 3
    b.floor(10, 1, 18, 7).put('>', (11, 6)).put('F', (13, 1))
    b.put('#', (15, 3), (15, 4))
    b.put('B', (16, 2))
    # room 3, the gun deck: a gate in the lane (26,4) eats shots unless its plate is held
    b.floor(20, 1, 31, 7).put('>', (21, 4)).put('F', (23, 1)).put('_', (24, 7)).put('E', (34, 4))
    b.put('#', (28, 2), (28, 6))
    return b.rows()


BROADSIDE = {
    'name': 'The Last Broadside',
    'map': broadside_map(),
    'links': {(2, 2): (9, 4), (13, 1): (11, 6), (23, 1): (21, 4), (24, 7): (26, 4)},
}


def queen3_map():
    """The Black Queen pulled up alongside: her hull (two rows), two rows of open water,
    then our deck. Shots fly over the water; a gangplank (18,3)-(18,4) lets you board
    once she's sunk and her treasure is all that's left."""
    b = Board(26, 14)
    D = 2   # everything on our ship sits two rows lower than in queen2_map
    b.put('E', (13, 0))
    b.floor(1, 1, 24, 2, 'H')                   # the Black Queen's hull
    b.floor(1, 3, 24, 4, '~').put('.', (18, 3), (18, 4))   # the water between, and the gangplank
    b.floor(1, 3 + D, 24, 4 + D)                # our gun deck
    b.put('^', (4, 5 + D), (13, 5 + D), (22, 5 + D))
    b.put('F', (2, 3 + D), (11, 3 + D), (24, 3 + D))
    b.put('_', (8, 3 + D))
    b.floor(1, 6 + D, 7, 10 + D).put('.', (1, 5 + D), (6, 5 + D)).put('_', (2, 7 + D))
    b.put('#', (4, 7 + D), (5, 7 + D), (3, 9 + D), (6, 10 + D))
    b.put('B', (4, 6 + D), (3, 8 + D), (6, 8 + D), (2, 9 + D)).put('P', (5, 9 + D))
    b.put('.', (15, 5 + D), (16, 5 + D), (15, 6 + D), (16, 6 + D), (16, 7 + D))
    b.floor(9, 8 + D, 16, 10 + D).put('#', (12, 9 + D))
    b.put('B', (11, 8 + D), (14, 9 + D))
    b.floor(18, 6 + D, 24, 10 + D).put('.', (19, 5 + D), (24, 5 + D)).put('_', (20, 7 + D))
    b.put('#', (21, 7 + D), (22, 7 + D), (20, 9 + D), (23, 9 + D))
    b.put('B', (22, 6 + D), (19, 8 + D), (21, 9 + D), (23, 8 + D))
    return b.rows()


QUEEN3 = {
    'name': 'The Black Queen',
    'map': queen3_map(),
    'links': {(2, 5): (4, 7), (11, 5): (13, 7), (24, 5): (22, 7), (2, 9): (6, 7), (8, 5): (16, 9), (20, 9): (19, 7)},
    'health': {'hull': 5},
}


def kraken2_map():
    """The user's Level 11 (Powder Room), exactly as it was, then three side puzzles that
    feed a new cannon on the ship's rail, which fires across the water at the kraken
    sitting on the landing to the treasure island. A gangplank crosses the water."""
    import levels_user as U
    l11 = U.L11[0]
    b = Board(39, 13)
    for y, row in enumerate(l11):
        for x, ch in enumerate(row):
            b.g[y][x] = ch
    b.put('.', (11, 5), (12, 5))                    # Level 11's treasure square is now the way out
    # the powder room (hub): the new cannon and its fuse
    b.floor(13, 4, 19, 8).put('>', (12, 6)).put('F', (19, 4)).put('#', (17, 4))
    b.put('B', (15, 5), (14, 7))
    # north store: its door (14,3) is a gate, opened by a plate at the far end; a ladder at (19,3)
    b.floor(13, 1, 23, 2).put('.', (14, 3), (19, 3)).put('_', (23, 1)).put('#', (20, 2))
    b.put('B', (21, 1), (16, 2), (18, 2))
    # south store: its door (16,9) is a gate, opened by a plate inside; a ladder at (19,9)
    b.floor(13, 10, 23, 11).put('.', (16, 9), (19, 9)).put('_', (22, 11)).put('#', (14, 11))
    b.put('B', (15, 10), (18, 11), (21, 10))
    # the ship's rail, the open sea, the gangplank (row 4) and the gun's lane (row 6)
    b.floor(21, 3, 29, 9, '~').floor(20, 4, 29, 4).floor(20, 6, 23, 6)
    # the kraken on the landing, and the treasure island behind it
    b.floor(30, 4, 32, 8, 'K').floor(33, 3, 37, 9).put('E', (36, 6))
    return b.rows()


KRAKEN2 = {
    'name': 'The Kraken',
    'map': kraken2_map(),
    'links': {(3, 8): (1, 2), (8, 3): (6, 1), (1, 1): (6, 5), (7, 1): (7, 5), (8, 1): (8, 5), (9, 1): (9, 5),
              (9, 3): (1, 5), (1, 8): (1, 9), (3, 10): (2, 10),           # Level 11's wiring, unchanged
              (19, 4): (12, 6), (23, 1): (14, 3), (22, 11): (16, 9)},     # the new cannon and gates
    'health': {'kraken': 5},
}
