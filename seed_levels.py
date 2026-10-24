"""The main voyage for `flask --app app seed`, written by tools/assemble.py
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

LEVELS = [
    # ===== Chapter 1: Sea Legs (pushing crates) =====
    # 1
    {
        'name': 'Shore Leave',
        'notes': "Find your sea legs. The treasure won't dig itself up.",
        'difficulty': 1, 'par': 24,
        'map': [
            '##########',
            '#P...#...#',
            '####.#.#.#',
            '#....#.#.#',
            '#.####.#E#',
            '#......###',
            '##########',
        ],
        'links': {},
        'solution': 'RRRDDLLLDDRRRRRUUUURRDDD',
    },
    # 2
    {
        'name': 'Heave Ho',
        'notes': "Something's in the way. Lean into it.",
        'difficulty': 2, 'par': 12,
        'map': [
            '##########',
            '#P..B...##',
            '######.###',
            '#E.....###',
            '##########',
        ],
        'links': {},
        'solution': 'RRRRRDDLLLLL',
    },
    # 3
    {
        'name': 'Wedged',
        'notes': "Crates go where they're shoved, and they never come back.",
        'difficulty': 2, 'par': 8,
        'map': [
            '#########',
            '#P..#####',
            '#..B....#',
            '#...###E#',
            '#########',
        ],
        'links': {},
        'solution': 'RRDRRRRD',
    },
    # 4
    {
        'name': 'One at a Time',
        'notes': "Even the burliest pirate can't shift two at once.",
        'difficulty': 2, 'par': 10,
        'map': [
            '#########',
            '#...#...#',
            '#P.BB..E#',
            '#...#...#',
            '#########',
        ],
        'links': {},
        'solution': 'URRDRRURDR',
    },
    # 5  (chapter test)
    {
        'name': 'Stowaway Shuffle',
        'notes': "Every crate's in the way, and every corner's a grave. Shove with care.",
        'difficulty': 4, 'par': 35,
        'map': [
            '################',
            '#PB.####..######',
            '#.B###....B#.B.E',
            '##.##.B.#.##.B.#',
            '##.####B#.##B..#',
            '#..##.B......###',
            '#......##.######',
            '################',
        ],
        'links': {},
        'solution': 'RDDDDLDRRRRURRUULURRURDDDDRRRURRUUR',
    },
    # ===== Chapter 2: Pressure (plates and gates) =====
    # 6
    {
        'name': 'Dead Weight',
        'notes': "You can't stand in two places at once.",
        'difficulty': 3, 'par': 10,
        'map': [
            '#########',
            '#P....#E#',
            '#.B._.D.#',
            '#.....#.#',
            '#########',
        ],
        'links': {(4, 2): (6, 2)},
        'solution': 'DRRURRDRRU',
    },
    # 7
    {
        'name': 'Two Locks',
        'notes': 'Every lock wants its own weight.',
        'difficulty': 3, 'par': 20,
        'map': [
            '#############',
            '#P...#._..###',
            '#.B..D..B.D.#',
            '#.._##....#E#',
            '#############',
        ],
        'links': {(3, 3): (5, 2), (7, 1): (10, 2)},
        'solution': 'DRURDRRRDRRURULDRRRD',
    },
    # 8
    {
        'name': 'Hold the Door',
        'notes': 'One to hold, one to carry.',
        'difficulty': 4, 'par': 17,
        'map': [
            '#############',
            '#P....#.....#',
            '#.B.B.D..._.#',
            '#..._.#.....#',
            '########D####',
            '########E####',
            '#############',
        ],
        'links': {(4, 3): (6, 2), (10, 2): (8, 4)},
        'solution': 'RDLDRRURRRRRRDLDD',
    },
    # 9  (chapter test)
    {
        'name': 'Tangled Rigging',
        'notes': 'Every plate pulls a rope to some other door. Trace the rigging.',
        'difficulty': 5, 'par': 74,
        'map': [
            '############',
            '#..........#',
            '#.BB.......#',
            '#.....######',
            '#.....#_...#',
            '#..P.D....DE',
            '#.....#....#',
            '#.#.#.######',
            '#.#_#......#',
            '#.#.#....###',
            '#........D_#',
            '############',
        ],
        'links': {(3, 8): (9, 10), (10, 10): (5, 5), (7, 4): (10, 5)},
        'solution': 'UURUULDDDDDDDDUUUUUULLURURDDDDDDULLDDDDRRRRRRRRLLLLLLUUUULURRRRRDRURULDRRR',
    },
    # ===== Chapter 3: Locks (bigger plate puzzles) =====
    # 10
    {
        'name': 'Cargo Hold',
        'notes': 'Three locks, three crates. Every crate has one good home.',
        'difficulty': 4, 'par': 35,
        'map': [
            '###########',
            '#...#..####',
            '#.B..B.####',
            '##.#_._####',
            '#P.B...DDDE',
            '#...#_.####',
            '###########',
        ],
        'links': {(4, 3): (7, 4), (6, 3): (8, 4), (5, 5): (9, 4)},
        'solution': 'RRRURRUULDRDLULLULLDRRRRURDLDDRRRRR',
    },
    # 11
    {
        'name': 'The Brig',
        'notes': 'No room to spare and no second chances. Think three pushes ahead.',
        'difficulty': 4, 'par': 42,
        'map': [
            '##############',
            '#._B.#..DDDE##',
            '#..B....######',
            '#._#..B.######',
            '#.P_...#######',
            '#...##########',
            '#..###########',
            '##############',
        ],
        'links': {(2, 1): (8, 1), (2, 3): (9, 1), (3, 4): (10, 1)},
        'solution': 'RRUULRRRRDLLDLLLULUURDRRULDRDRDLUURRURRRRR',
    },
    # 12
    {
        'name': 'Deadbolt',
        'notes': 'Four plates, four bolts, and you only brought three crates. Something has to give.',
        'difficulty': 6, 'par': 91,
        'map': [
            '#########',
            '#...#..##',
            '#B=P.D..#',
            '#..B#...#',
            '#..B.#D.#',
            '#..#._._#',
            '#_###DD##',
            '#####E###',
        ],
        'links': {(2, 2): (5, 2), (5, 5): (5, 6), (7, 5): (6, 6), (1, 6): (6, 4)},
        'solution': 'ULLDDUURRDRRDRRDDLLLULULLUURDRLLDDDURURURRURDLDRDDLLULULLURRDLLDDRUURURRURDDDRDLUUURDDLDDLD',
    },
    # 13
    {
        'name': 'Nine Locks',
        'notes': 'Five crates, nine locks. Not every door has to stay open forever.',
        'difficulty': 6, 'par': None,
        'map': [
            '############',
            '#P_B.#__...#',
            '#....#.....#',
            '#..B.#.....#',
            '##.##__#D.##',
            '##.B..D#B.DE',
            '#.D##.DD..##',
            '#.....##...#',
            '#.B...#...D#',
            '#.___.D..#D#',
            '#.....#..#_#',
            '############',
        ],
        'links': {(2, 1): (2, 6), (2, 9): (6, 5), (3, 9): (6, 6), (4, 9): (7, 6), (5, 4): (6, 9), (6, 4): (8, 4), (6, 1): (10, 8), (7, 1): (10, 9), (10, 10): (10, 5)},
        'solution': 'DRRRULDLDDDDDDUUUUUURRDLULDDDDDLDRURDULUURRRDRULDDDDDLLUULURRDRUUUDDDDRRURUUUUURULDLUDRRDDDDDLDLLLUUUURUUUDRRRDDDDDLDLLLULLLLDRRRRRRDRULURRURDDUULUURR',
    },
    # 14  (chapter test)
    {
        'name': 'Seven Seals',
        'notes': 'Seven locks between you and the sea, and every one wants a crate.',
        'difficulty': 5, 'par': 44,
        'map': [
            '#########E#',
            '######_.#D#',
            '#.._..B.#D#',
            '#..BB_B_#D#',
            '#.B.#.=.#D#',
            '##P###..#D#',
            '##_#_.B.DD#',
            '###########',
        ],
        'links': {(2, 6): (8, 6), (3, 2): (9, 6), (4, 6): (9, 5), (5, 3): (9, 4), (6, 4): (9, 3), (6, 1): (9, 2), (7, 3): (9, 1)},
        'solution': 'ULUURRRRDRULLLLDDDURURURRDDRDDLUDLRRRRUUUUUU',
    },
    # ===== Chapter 4: The Squeeze (squeezing crates out of shutting gates) =====
    # 15
    {
        'name': 'Squeeze Play',
        'notes': "A shut door don't argue. Whatever's in the doorway gets shoved aside.",
        'difficulty': 3, 'par': 24,
        'map': [
            '########',
            '#....###',
            '#PB.B###',
            '#.##.###',
            '#.=.D###',
            '#D###_##',
            '#E######',
        ],
        'links': {(2, 4): (4, 4), (5, 5): (1, 5)},
        'solution': 'RURRDDUULLDRURDLLLDDRLDD',
    },
    # 16
    {
        'name': 'Shove Off',
        'notes': "The dock gate won't hold a crate. It shoves it somewhere else. Make it somewhere useful.",
        'difficulty': 4, 'par': 49,
        'map': [
            '###########',
            '#######P#.#',
            '##....._D_#',
            '##..B.#####',
            '##.B.######',
            '###......DE',
            '###########',
        ],
        'links': {(7, 2): (8, 2), (9, 2): (9, 5)},
        'solution': 'DLLDLULLDDRULURRRRRLLDLLDDRUULURRRRUDLLDLDDRRRRRR',
    },
    # 17
    {
        'name': 'Lock Gate',
        'notes': 'Two gates, three crates, one way out. The harbourmaster would like a word.',
        'difficulty': 4, 'par': 41,
        'map': [
            '#########',
            '#P..D_.DE',
            '##B#.#.##',
            '##_B.#.##',
            '#......##',
            '#.B#..###',
            '#..######',
            '#########',
        ],
        'links': {(5, 1): (7, 1), (2, 3): (4, 1)},
        'solution': 'RDURRDDDLLUUDRDLLDDRUURRUUDDLLUDRRRRUUURR',
    },
    # 18
    {
        'name': 'Dry Dock',
        'notes': 'Every gate in the dry dock slams shut sooner or later. Be standing somewhere else when it does.',
        'difficulty': 5, 'par': 79,
        'map': [
            '##########',
            '#P.##..###',
            '##.B...B.#',
            '#_###....#',
            '#.##...###',
            '#D..._...#',
            '##...##.DE',
            '##########',
        ],
        'links': {(1, 3): (8, 6), (5, 5): (1, 5)},
        'solution': 'RDRRRURDDRRULLDLDDRULURUULDDDRDLLURUURRRDLLULDDLDLLRRURRDLLDLLURRLLLUDRRRRRRDRR',
    },
    # 19  (chapter test)
    {
        'name': 'Pinch Point',
        'notes': 'A shutting gate spits its crate out somewhere. Make it somewhere useful.',
        'difficulty': 6, 'par': None,
        'map': [
            '############',
            '#..#.......#',
            '#._#...BBB.#',
            '###D.......#',
            '#...B....###',
            '#....B...DDE',
            '#..P..B..###',
            '#......B...#',
            '#.......D###',
            '#..##...#_.#',
            '#.._=...#..#',
            '############',
        ],
        'links': {(4, 10): (3, 3), (3, 10): (8, 8), (2, 2): (9, 5), (9, 9): (10, 5)},
        'solution': 'URURULUURRRRDLLLDDLDDDDRDDLLRRUULLLDLDRUUUUUURRRRDRDDLDRUUULDLDRRRUUULUURDDDDUULLLDDLDRRUUUUUURRRDLDDDDLDUUUUURRRDLLULDDDDLDDLLLLDDRLUUUUURRRRRRRRR',
    },
    # ===== Chapter 5: Gunpowder (cannons and fuses) =====
    # 20
    {
        'name': 'Load and Light',
        'notes': "A cannon's only as good as what's in front of it.",
        'difficulty': 3, 'par': 15,
        'map': [
            '##########',
            '#P...F..##',
            '#..B....##',
            '#>.....#E#',
            '#......#.#',
            '##########',
        ],
        'links': {(5, 1): (1, 3)},
        'solution': 'RRDRDLUURRDDRRR',
    },
    # 21
    {
        'name': 'Clear the Way',
        'notes': "When a wall of crates won't budge, try something louder.",
        'difficulty': 2, 'par': 10,
        'map': [
            '###########',
            '#P..F######',
            '#....###E##',
            '#>B..BB...#',
            '###########',
        ],
        'links': {(4, 1): (1, 3)},
        'solution': 'RRRDDRRRRU',
    },
    # 22
    {
        'name': 'Open Fire',
        'notes': 'A shut gate stops a cannonball as well as a pirate.',
        'difficulty': 3, 'par': 18,
        'map': [
            '#############',
            '#P...F#######',
            '#..B._#######',
            '#.....#######',
            '#>B.......D#E',
            '#############',
        ],
        'links': {(5, 2): (10, 4), (5, 1): (1, 4)},
        'solution': 'DRRRURLDDDRRRRRRRR',
    },
    # 23
    {
        'name': 'Broadside',
        'notes': 'Count your shots before you take them.',
        'difficulty': 4, 'par': 32,
        'map': [
            '#############',
            '#P.#.F#######',
            '#..B..#######',
            '#.#.B.#######',
            '#>....#..#..E',
            '#..B..#######',
            '#.....#######',
            '#############',
        ],
        'links': {(5, 1): (1, 4)},
        'solution': 'DRRRDRDLLURRUDDDLLDLUURRRRRRRRRR',
    },
    # 24
    {
        'name': 'Powder Monkey',
        'notes': "Once you're through, there's no going back to light it.",
        'difficulty': 5, 'par': 77,
        'map': [
            '############',
            '#####...####',
            '##....v.####',
            '##.###.....#',
            '#.B##..BB..#',
            '#.......####',
            '###.#..#####',
            '##.F..######',
            '##P#########',
            '############',
            '######.....E',
            '############',
        ],
        'links': {(3, 7): (6, 2)},
        'solution': 'URUURRRRURULUULLDLLLDDLDRRDDUURRURURRRRDLLLDLUDDDLLLUURRDRUUDDDLLLRRRDDDRRRRR',
    },
    # 25
    {
        'name': 'Powder Keg',
        'notes': "A fuse doesn't care who's standing on it.",
        'difficulty': 5, 'par': 62,
        'map': [
            '#########',
            'E..######',
            '##...####',
            '####...##',
            '######.##',
            '##P>.####',
            '#.F..####',
            '#.......#',
            '##.##.B.#',
            '##...B.##',
            '##..#####',
            '#########',
        ],
        'links': {(2, 6): (3, 5)},
        'solution': 'DDRRRRRDLDLLLDLUUULURRDRUDRDRDLLLDLUUULURRDRULLRRURRUULLULLULL',
    },
    # 26
    {
        'name': 'Run the Gauntlet',
        'notes': "Your powder's on the wrong side of the gate.",
        'difficulty': 5, 'par': 62,
        'map': [
            '########',
            '########',
            '###F_.P#',
            '###.B###',
            '##..B.##',
            '##...B.#',
            '###....#',
            '###.#.##',
            '###...##',
            '#.#.#.<#',
            '#D######',
            '#E######',
        ],
        'links': {(4, 2): (1, 10), (3, 2): (6, 9)},
        'solution': 'LLLDDDDRRRULULDLDRURDDDUUUULULUDDLDRRURDDDDUUUULULUDDDDDDDLLDD',
    },
    # 27  (chapter test)
    {
        'name': 'Crossfire',
        'notes': "Today's obstacle is tomorrow's ammunition.",
        'difficulty': 5, 'par': 99,
        'map': [
            '##############',
            '#P.#########v#',
            '##..F#######.#',
            '#>.B..B..#...#',
            '##.....#.#...#',
            '##F.##..B..###',
            '######..#####E',
            '##############',
        ],
        'links': {(4, 2): (1, 3), (2, 5): (12, 1)},
        'solution': 'RDRDRDRRDRRUULLLLLURDLLDDRULURRRRRRRRRDRUDLLDLLLDLUULLLDLUURRRRRRRRRDRULLLLLLDLLLDLUURRRRRRRRDRRDDR',
    },
    # ===== Chapter 6: Davy Jones' Locker (loaded fuses, and everything at once) =====
    # 28
    {
        'name': "Davy Jones' Locker",
        'notes': "Everything you've learned. Nothing to spare.",
        'difficulty': 5, 'par': 86,
        'map': [
            '#################',
            '#P...F###.#######',
            '#.#B.####..######',
            '##..#.####..#..##',
            '#>.....BB...D..#E',
            '#..#.####...#..##',
            '#.B#..####_######',
            '#.....###..######',
            '#################',
        ],
        'links': {(10, 6): (12, 4), (5, 1): (1, 4)},
        'solution': 'RRDDLDDLDDRRRUUULUUURRLDLDDLDLDDRUUDDRRUUURRRRRDRRUULDDULLLLLLLUUURRLDLDDRRRRRRRRRRRRR',
    },
    # 29
    {
        'name': 'Hair Trigger',
        'notes': 'Sit a crate on the fuse and the cannon never sleeps. Feed it.',
        'difficulty': 5, 'par': 50,
        'map': [
            '##########',
            '#...#v..##',
            '#.B.....##',
            '#.B.B##F##',
            '#P.B.#####',
            '#....#####',
            '#####E####',
        ],
        'links': {(7, 3): (5, 1)},
        'solution': 'UURRRRRURDLLLLLLDDRULURRRLDLDDRUULURRLDDRULURDDDRD',
    },
    # 30
    {
        'name': 'The Long Shot',
        'notes': "Load the gun, feed the gun, and mind where you're standing when it fires.",
        'difficulty': 6, 'par': None,
        'map': [
            '################',
            '#.....#...#..#_#',
            '#.B...DB..#.BD##',
            '#.##.##.B.#...DE',
            '#.=_D##._P#.#.##',
            '##D##F>.#D#.=###',
            '#....#...#######',
            '#..B...B._######',
            '#.B....B.#######',
            '#........#######',
            '################',
        ],
        'links': {(8, 4): (6, 2), (2, 4): (4, 4), (3, 4): (2, 5), (5, 5): (6, 5), (9, 7): (9, 5), (12, 5): (13, 2), (14, 1): (14, 3)},
        'solution': 'UULDULLLULDDUULLLDRRURDLLLDDRDDRDRRRRRDDLUUUURRULULDDRRRRUUURDLDDLLLDDLLLLLLDRRRRDRUUUURRRRUURRRR',
    },
    # 31  (chapter test)
    {
        'name': 'The Last Broadside',
        'notes': "Three rooms and five crates, with not one to spare. A crate you waste in the brig is a shot you won't have on the gun deck.",
        'difficulty': 7, 'par': None,
        'map': [
            '###################################',
            '#........#...F.....#...F........###',
            '#._..#.#.#......B..#........#...###',
            '#...B....#.....#...#............###',
            '#.....B........#...#.>..........##E',
            '#.P.B....#.........#............###',
            '#..B.#...#.>.......#........#...###',
            '#........#.........#...._.......###',
            '###################################',
        ],
        'links': {(2, 2): (9, 4), (13, 1): (11, 6), (23, 1): (21, 4), (24, 7): (26, 4)},
        'solution': 'URRRULDLURULDDRRRRRRRRURDDUUUURDRRRRURDDDDLDRRRRRRURDLLLLLLULLLLULLLLLLLLLLLDRRRRDRULURRRRRRURDLDRRRRURDLDRRRRDRUURUUULURDDDDDLLLLLULLLLULLLLLLDLLLLLLDRDRULURRRRDRULURRRRRRURDLDRRRRURDLDRRRRDRUURUUULURDDRRRRDRRRRRRR',
    },
    # ===== Chapter 7: Endgame (the deck battle and the kraken) =====
    # 32
    {
        'name': 'The Black Queen',
        'notes': "Rook's flagship, alongside and closing. Haul the crates up from the holds, feed the guns, and sink her.",
        'difficulty': 7, 'par': None,
        'map': [
            '#############E############',
            '#HHHHHHHHHHHHHHHHHHHHHHHH#',
            '####.########.########.###',
            '#.F....._..F............F#',
            '#........................#',
            '#.##^#.######^#..##.##^#.#',
            '#...B...#######..#....B..#',
            '#._.##..########.#.._##..#',
            '#..B..B.#..B.....#.B...B.#',
            '#.B#.P..#...#.B..#..#B.#.#',
            '#.....#.#........#.......#',
            '##########################',
        ],
        'links': {(2, 3): (4, 5), (11, 3): (13, 5), (24, 3): (22, 5), (2, 7): (6, 5), (8, 3): (16, 7), (20, 7): (19, 5)},
        'health': {'hull': 5},
        'solution': 'DLLLUULUURRRRLLLLDDDDRRRURRRUULUUULURRDRRRRRRRRRRRRRRRRRDDDDDDLLLLLUULURDDDRRRRRUUUUUULLLLLLLLLLLLLLLLLLLLLLLDDDDDDRRRURRUUUUDLLLLLUURRURRRRDLLULLLDRRRRRRRRRRRRRRRRRRRRRRDDLLLLRRRDRDDDLLUULLLUUUDRRRRRUULULLLLLDRRRURRRDLLLLLLLLLLLLLLLLLLLLLLLDDDDRRRRDRUUUUDLLLLLUURRURRRRDLLULLLDRRRRRRRRRRRRRRRRRRRRRRDDDDDDLLLURULLRDDLLUUUUUDRRRRRUULULLLLLDRRRURRRDDDDDLLLLRDDLLUUUUUDRRRRRUULULLLLLDRRRURRRDLULUULLLLLLLLLU',
    },
    # 33
    {
        'name': 'The Kraken',
        'notes': 'Something big lies between you and the Hoard. One gun, one lane, and every crate you can find.',
        'difficulty': 7, 'par': None,
        'map': [
            '##############################',
            '##........B._#################',
            '##...B.B.#...#################',
            '###.####.#####################',
            '##....#.F#############KKK#####',
            '##..B....#############KKK#####',
            '#>....................KKK...E#',
            '##.B.....#############KKK#####',
            '##...P...#############KKK#####',
            '#####.##.#####################',
            '##..B.....B..#################',
            '##.#...B..._.#################',
            '##############################',
        ],
        'links': {(8, 4): (1, 6), (12, 1): (3, 3), (11, 11): (5, 9)},
        'health': {'kraken': 5},
        'solution': 'UUUULDRDLLRDLUURRRRURDDDDLLLLLLURUURRRRURUUULLDLLURRRRDLLLURRRRRRLLLLLLLLDDDDRDLURRRRURUULLLLULDDDDRDLURRRRURDDDDDDDRRRULDLLULLDRRRRULLLLDLUUUURULLLURRRRURDDRRRRRRRRRRRRRRRRRRRR',
    },
    # ===== Chapter 8: Expert Waters (bonus levels for experts, after the ending) =====
    # 34
    {
        'name': 'Stomp',
        'notes': 'Some planks are more than they seem.',
        'difficulty': 2, 'par': 9,
        'map': [
            '###########',
            '#P.B_...###',
            '#......D.E#',
            '###########',
        ],
        'links': {(4, 1): (7, 2)},
        'solution': 'RRDRRRRRR',
    },
    # 35
    {
        'name': 'Fire in the Hole',
        'notes': 'Mind the fuse.',
        'difficulty': 2, 'par': 8,
        'map': [
            '#########',
            '#P..F..##',
            '#......##',
            '#.>B..#E#',
            '#.....#.#',
            '#########',
        ],
        'links': {(4, 1): (2, 3)},
        'solution': 'RRRDDRRR',
    },
    # 36
    {
        'name': 'Crossed Lines',
        'notes': 'Every plate opens a door on the far side. Mind the wiring.',
        'difficulty': 6, 'par': 204,
        'map': [
            '##############',
            '##...D.##..#DE',
            '#.B#.........#',
            '#_.#._.##...##',
            '#..B.#..##..##',
            '#.#BB.D###.P_#',
            '#....#########',
            '##############',
        ],
        'links': {(1, 3): (6, 5), (5, 3): (12, 1), (12, 5): (5, 1)},
        'solution': 'UUULLLLLLLULLDLDDDDRRRUULLRRDDLLLUUDDRRURRRUUULLDDLDRRLUUUULLDLDDRRDDLLUURRDRRRUULLDLDRRLUUUULLDDULDDRRDDLLUURRDRRRUULURRRRURDLDRULLLLDLLDLDRRLULLUULDDRRDDLLUURRDRRRUULURRRRURDRDDLUDDRUUULLLLLULDRRRRRRRUR',
    },
    # 37
    {
        'name': 'Through the Gates',
        'notes': 'A shut gate stops a cannonball. Two of them stop it twice.',
        'difficulty': 7, 'par': 179,
        'map': [
            '###########',
            '#._.#.P.###',
            '#FB.B.#..##',
            '#..#B##.B##',
            '#...D.B..##',
            '#.>.D..#_##',
            '#....####.#',
            '#########E#',
        ],
        'links': {(2, 1): (4, 5), (1, 2): (2, 5), (8, 5): (4, 4)},
        'solution': 'RDRDDLLLLLDDLLUUUUURDLDDDDRRUURRRRUUULLDLLULLDDDRRRRRLLLLLUUURRDRDULULLDRDLDDDRRUURUULULDLDDRRLUURRDDRDLUUULLLDDRRDRRRRULLDLULLUURRDDRDLUUULLLRRRRURRDDDRDLLLLDLLLUUUUDDRRDRRRRRRDD',
    },
    # 38
    {
        'name': 'Pinch and Tuck',
        'notes': "Same gate, same slam, different landing. It's all in what's in the way.",
        'difficulty': 7, 'par': 218,
        'map': [
            '##########',
            '#........#',
            'ED####...#',
            '#.##.BB..#',
            '##D_.#..##',
            '#..####..#',
            '#....._..#',
            '#..B.D..##',
            '#..##_P###',
            '##########',
        ],
        'links': {(3, 4): (5, 7), (6, 6): (2, 4), (5, 8): (1, 2)},
        'solution': 'UURUULUDRDDLLLDLULLDDRULURRRRLLLUURRURRDRDDLLLLRRRRUUURUULDULDRDDDRDLLLLDLLURRRLLLUDRRRRDRUUUULUURDDDDRDLLLLDLLURRRLLLUURRURRDRDDLLLLRRRRUULUURDDDRDLLLLDLLURRRLLLUDRRRRDRUUULUURDDDRDLLLLLDLLUURDLDRRRURDURRUUUUULLLLLLDL',
    },
    # 39
    {
        'name': 'Back to Back',
        'notes': "Two guns, a fuse you can't reach in time, and treasure behind the wall.",
        'difficulty': 7, 'par': 247,
        'map': [
            '#############',
            '###.#>.<#####',
            'E#FB.#...P..#',
            '#..##.F###..#',
            '#....B......#',
            '#.B#.##B##..#',
            '##......#####',
            '#############',
        ],
        'links': {(2, 2): (7, 1), (6, 3): (5, 1)},
        'solution': 'LLLDDLLDDLLULUURDRRRRRRRLLLUURRRRDRDDLUURULLLLRRRDDLLLLLLDDRRRUDLLLUURRRRRLLLUURRRRDRDDLUURULLLLRRRDDLLLDDLLLLLULURUUDDRRRRRRRLLLUURRRRDRDDLUURULLLLRRRDDLLLLLLLLUUURRDLULDDLDRRRRRRRRLLLUURRRRDRDDLUURULLLLRRRDDLLLLLLLLUUDDRRRURURRRRDDLLLLLLLLUUULLD',
    },
    # 40
    {
        'name': 'Four Bells',
        'notes': "Ring the cannon four times and the treasure's yours.",
        'difficulty': 7, 'par': 258,
        'map': [
            '############',
            '#####_#####E',
            '#.FB..>D#.##',
            '#P#BB.....##',
            '#.B...#.#BD#',
            '#####._....#',
            '############',
        ],
        'links': {(5, 1): (10, 4), (2, 2): (6, 2), (6, 5): (7, 2)},
        'solution': 'DRRRLLLUURRRDRRRDDLLUDRRUULLULLLLDDRRRLLLUURRDURRDRRDDLLULLUURDRDDRRUURRDRDLLLUULLULLDRRRRDDRRUULRDDLLUULLULLLRDRRDDRRUULLLLDRURRRDDLLUDRRUURRDDLLUULLULLDRRRRURRDLRDDLLUULLULLLLDDRRURRDDRRUULLLLDRURRRDDLLUDRRUURRDDLLUULLULLDRRRRURRDLRDDLLUULLULLLRDRRRRURRRRU',
    },
    # 41
    {
        'name': 'Long Haul',
        'notes': 'Every shot means hauling a crate the length of the hold.',
        'difficulty': 7, 'par': 260,
        'map': [
            '##############',
            '#..#F.#>.##.##',
            '#.B#..##.B.#.#',
            '#.B....#.###.E',
            '#...#..#.#####',
            '#P#.##.#.....#',
            '##...........#',
            '##.....####..#',
            '##############',
        ],
        'links': {(4, 1): (7, 1)},
        'solution': 'UURLUURDDRRLDDDRRRUULULLLLDRURDDUURRDRDDDLLLLURUUURUURDLDLDDDRRRRRRRURRDDLURULLLDLUUUUDDDDLLUUULLUUDDLDLLUURDLDRURDDUURRDRDDDLLLLURRRRRRRRURRDDLURULLLDLUUUUDDDDLLUUULUULDDRDRDDRRUUUUURRDLULDDDDRDLLLDLLURRRRRRURRDDLURULLLDLUUUUDDDDLLUUULUULDDRDRDDRRUUUUURRRRDDR',
    },
    # 42
    {
        'name': 'The Long Way Round',
        'notes': 'Three crates. Two hundred and ninety-six moves. No pressure.',
        'difficulty': 7, 'par': 296,
        'map': [
            '####E######',
            '###.D#._#.#',
            '#...#..._.#',
            '#.#.#..#..#',
            '#.B.#..##.#',
            '#.#.##.#..#',
            '#.#.....B.#',
            '#PBD...#^F#',
            '###########',
        ],
        'links': {(7, 1): (4, 1), (8, 2): (3, 7), (9, 7): (8, 7)},
        'solution': 'UUUUURRDDDDRRRUUUURRDRDDDLLLDLLURDRUUUULURRLDDDDLLLUUUULLDDRLUURRDDDDRRRRRURUUULDRDDDLLLUUUURLDDDDDLLLURDRRURRURUUULLULDLDDRDDDLLURRRLUULUURRRDRDDDDULLLUUULURRLDDDDLLLUULLDDDRRURRDLURRRRUUURULDDDDLLUUUURLDDDDDLLLURDRRURRUUURULLULDLDDRDDDLLURRRLUULUURRRDDDRDDULLLUUULURRURRDDLURULDDDDDLLLLLUUUUURU',
    },
    # 43
    {
        'name': 'Relay',
        'notes': 'Hand the crates along. Every plate takes a turn holding the door.',
        'difficulty': 7, 'par': 320,
        'map': [
            '#########E###',
            '######..#D.##',
            '#....B_.##.##',
            '#..###_.#..##',
            '#...#P#BBD###',
            '##._......###',
            '##D.###...###',
            '#############',
        ],
        'links': {(6, 2): (9, 4), (6, 3): (9, 1), (3, 5): (2, 6)},
        'solution': 'DLLULUURRRRDRDULULLLLDDDRRRRRDRRULLLLLLULUURRRRURDDDUULLLLLDDRDRRRRDRRULLLLLRRRUUULLLLLDDDUUURRRRDRDDLLLLDLUUULURRRRLLLDDDRRRRRDRRUULRDLLLLLLULUURRRRDRDRDLLLLRRRUULULLLLDDDUUURRRRDRDDLLLLDLUUDRRRRRDRRULLLLLLRRRRUULUURDDDUULLLLLLDDRULURRRRLLLDDRDRRRRURRDLLLLLRRRUUUULDLLLLDDDUUURRRRRDDDLLLLDLUUULURRRRLLLDDDRRRRRURRURUULU',
    },
    # 44
    {
        'name': 'Conveyor',
        'notes': 'Doors that slam shut move crates better than you do.',
        'difficulty': 7, 'par': 321,
        'map': [
            '#########E#',
            '#..##...#.#',
            '#B.B....D.#',
            '#D.#B.#####',
            '##..B.#_###',
            '#.._##...P#',
            '#._.....D##',
            '###########',
        ],
        'links': {(7, 4): (8, 2), (3, 5): (8, 6), (2, 6): (1, 3)},
        'solution': 'LLDLLLLUULUURRRDDLLRRUULLLDDUURRDRDLLDDLLURURRUURURRDLULDLLLDDDUUUULDRDDDLDRRRRRURRDLLLLLULUULURRRDDLDLLDRRUURUULLDDRDDLLURDRRRRRLLLLULUUURRDDLRUULLDDUURRRURRDLLLLRDDLLDUULUURDRRDDLDLLDRRUURUULLDDRDDLLURDRRRRRLLLLULUUURRDDLRUULLDDDURRRULURURRDLLLLRDDLLULUURDRRDDLDLLDRRUURUULLDDRDDLLURDRRRRRLLLLUDRRRRUDLLLLULUUURRRRRRRUU',
    },
    # 45
    {
        'name': 'Backfire',
        'notes': 'Load it from behind. Mind your fingers.',
        'difficulty': 7, 'par': 336,
        'map': [
            '##E#######',
            '#..#..F###',
            '#.##.#_###',
            '####.<.###',
            '#.B..#P###',
            '#_.#.#B###',
            '#......D##',
            '#.B.DB..##',
            '##########',
        ],
        'links': {(6, 1): (5, 3), (6, 2): (4, 7), (1, 5): (7, 6)},
        'solution': 'UUULLDDDDDLLLDRURRRRUUUDDDDLULUUUUURRDDDDDLLLLULURRLDDDLURRRRRUUUUULLDDDDULLDDRRRRLLUULLLDRDDLURRRRRUUUDDDRDLLULUUUUURRDULLDDDDDRDRRULUUUDDDLDLULLDRULUURRUUURRDDDDDLLUULLDDRRRRUUUUULLDDDLLLDRDDLURRRRRUUUDDDRDLLULUUUUURRDULLDDDDDRDRRULUUUDDDLDLULLUURURUURRDDDDUUUULLDDDLLDDRRRDRRULLLLDLURRUUUDLLLDDRULURRLDDRRUUDDRRUUUUULLDURRLLDDLLLUURU',
    },
    # 46
    {
        'name': 'Down the Hatch',
        'notes': 'The cannon points the right way. Getting crates in front of it is the hard part.',
        'difficulty': 7, 'par': 356,
        'map': [
            '###########',
            '#...####v##',
            '#..=..._F.#',
            '#.#####.#.#',
            '#.B.....D.#',
            '#.##...#..#',
            '#.BD.B.B#.#',
            '####P######',
            '#########E#',
        ],
        'links': {(3, 2): (3, 6), (7, 2): (8, 4), (8, 2): (8, 1)},
        'solution': 'UURRDLLUURRRUULLLLULLDRLDDRRRRRLLLLLDDRRRUDLLLUUUURRRRRLLLLLDDRRRDRRURRDRULLLDLLURRRLLLLLLUURRRRRRRRDLULLLLLLLDDRRRRRRURULLLLRRRDDLDDLLUURRRUULLLLULLDRLDDDDRRRUDLLLUUUURRRRRLLLLLDDRRRRRRURRDDLURULULLLLLULLDRRRRRRRDRDDLDLLUURURULLLLRRRDDLDDLLUURRRUULLLLULLDRLDDDDRRRUDLLLUUUURRRRRLLLLLDDRRRRRRURRDDLURULULLLLLULLDRRRRRRRDRDDLDLLUURUDLLLLLLUURRRRRRDDLDDRRDDR',
    },
    # 47
    {
        'name': 'The Chimney',
        'notes': 'Four crates, four walls, and one very long walk to the fuse.',
        'difficulty': 8, 'par': 386,
        'map': [
            '#####E##',
            '#F..#.##',
            '#.D..###',
            '#..BB###',
            '##..BP##',
            '##_###.#',
            '#._#..B#',
            '#.B.D#^#',
            '#...####',
            '########',
        ],
        'links': {(1, 1): (6, 7), (2, 5): (4, 7), (2, 6): (2, 2)},
        'solution': 'LLULLUUDDRDRRRRDDLLDLDLLUURUUDDLDDRUUDRRURRUULLLLDUULUURRDRDLDRUULULLDRURDRDDLLDDLDRUUURRUULDRDLUUULLDDRDDDLDDRUUDRLUUURRUULDRDLUUULLDDRDDDLDDRUUDRRURLDLLUUURRUULDRDLUUULLDDRDDDLDRUUURRUULDRDLULDDDLDDRUUDRLUUURUUULLDDRDRRUULDRDLULDDDLDDRUUDRRURLDLLUUURUUULLDDRDRRUULDRDLULDDDLDDRUUDRRURRUULLULLDDDLDRUUUURRDLULDDDLDDRUUDRLUUURUUULLDDRDRRUULDRDLULDDDLDDRUUDRRURLDLLUUURUUULLDDRDRRRRUUULU',
    },
    # 48
    {
        'name': 'Powder Room',
        'notes': 'Eleven crates and not one to spare. Count before you shoot.',
        'difficulty': 8, 'par': None,
        'map': [
            '############',
            '#_#...D___.#',
            '#D...#######',
            '#....B.._F.#',
            '#####B######',
            '#>...#DDDD#E',
            '#####B######',
            '#.....#....#',
            '#FB=P.#BBB.#',
            '#>.B....BB.#',
            '##^F..#....#',
            '############',
        ],
        'links': {(3, 8): (1, 2), (8, 3): (6, 1), (1, 1): (6, 5), (7, 1): (7, 5), (8, 1): (8, 5), (9, 1): (9, 5), (9, 3): (1, 5), (1, 8): (1, 9), (3, 10): (2, 10)},
        'solution': 'ULLDURRDDDLRULRDLULUUUUUURRRRRLLLLLDDDDRRDLULDLURDDRRRRRDRRRUUULLLDURRRDDDLLULLLDLURULDRRRDRRRULLLLLDLUURULLRDDLLUUUUUULURRDRULURRRRRLLLLDDLLDDDDDDRRRRRUURDURRDDLLLLLDLUURULLRDDLLUUUUUULURRDRULURRRRLLLDDLLDDDDDDRRRRRUURRDRDLLLLLDLUURULLRDDLLUUUUUULURRDRULURRRLLDDLLDDDDDDRUDLUUUUUURRRRRRLLLLLLDDDDDDRRUULRDDLLUUUURRRDDDLDRRRURRDLLLLDLURULULLUUUURRRDDDDDLDRRRURRDLLLLDLUURULLRDDLLUURRRUUUURRRRLLLLDDDDLLLUUUURULDLUDRDDDDRRDLURDDLLUUUDRRRUUUURRRRLLLLDDRRRRRR',
    },
    # 49
    {
        'name': 'Brig Break',
        'notes': 'Break out of the brig, blast the hold open, and give her a broadside to remember.',
        'difficulty': 7, 'par': None,
        'map': [
            '#########################',
            '############_#...########',
            '######_...F##D...########',
            '######.BBB.#.....#.....##',
            '#>...D.BPB.D..BB.D....D#E',
            '######.BBB.#..BB.#..._.##',
            '######...._#....=########',
            '############.....########',
            '#########################',
        ],
        'links': {(6, 2): (5, 4), (10, 6): (11, 4), (12, 1): (17, 4), (16, 6): (13, 2), (10, 2): (1, 4), (21, 5): (22, 4)},
        'solution': 'DLDRRLLLUUUDDRRULLLLLRRRRRRURDUUDDRRDDRRUUUUDRRDLLDLUUDDDDRRRUUULDLDRUUUURDLDRRRRRURDLLLLLLLLLLLLLUDDDRULUURRDLLLLLLLRRRRRURRUDDRRRRRRRRRRRRRR',
    },
]

# Chapter titles, in order, and how many levels each one has.
CHAPTERS = ['Sea Legs',
 'Pressure',
 'Locks',
 'The Squeeze',
 'Gunpowder',
 "Davy Jones' Locker",
 'Endgame',
 'Expert Waters']
CHAPTER_LENGTHS = [5, 4, 5, 5, 8, 4, 2, 16]
# Chapters whose levels each stand alone (every level ends at its own chest).
LOOSE_CHAPTERS = ['Endgame', 'Expert Waters']
# Chapters after the story's ending.
BONUS_CHAPTERS = ['Expert Waters']


SYMBOLS = {'#': 'wall', 'P': 'player', 'B': 'box', 'E': 'exit', '_': 'pressureplate', 'F': 'fuse',
           'K': 'kraken', 'H': 'hull'}
CANNONS = {'^': 'up', 'v': 'down', '<': 'left', '>': 'right'}
STACKED = {'=': ('pressureplate', 'box')}   # a crate that starts on a plate


def parse(spec):
    rows = spec['map']
    tiles = []
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            if ch in SYMBOLS or ch in CANNONS or ch in STACKED:
                for kind in STACKED.get(ch, (SYMBOLS.get(ch, 'cannon'),)):
                    tile = {'type': kind, 'x': x, 'y': y,
                            'direction': CANNONS.get(ch), 'aX': None, 'aY': None}
                    if kind in ('pressureplate', 'fuse') and (x, y) in spec['links']:
                        tile['aX'], tile['aY'] = spec['links'][(x, y)]
                    if kind in ('kraken', 'hull'):   # aX holds its health
                        tile['aX'] = spec.get('health', {}).get(kind, 3)
                    tiles.append(tile)
    return len(rows[0]), len(rows), tiles
