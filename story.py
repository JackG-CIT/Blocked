"""Blocked's story text, kept apart from the level files so a voyage reshuffle can't wipe it.

Everything here is keyed by NAME (chapter title or level name), never by number, because
levels and chapters are being reorganised. The website (app.py) and the standalone build
(export_standalone.py) read it directly, so seed_levels.py doesn't need to carry any of it;
static/js/story.js draws it (cutscenes, chapter title cards, the map).

If a level or chapter is renamed, rename its key here too. Unknown keys are just ignored.
See STORY.md for the outline and the cutscene plans.
"""

# --- Chapters ---------------------------------------------------------------------------
# Keyed by chapter title (as in CHAPTERS in seed_levels.py). 'part' groups chapters for the
# map: 'ship' chapters show on the cut-away of Rook's ship, 'sea' chapters on the ocean chart.
# 'intro' goes on the chapter's title card, 'end' on its finale's "Treasure found!" popup.
# 'was' lists older titles for the same chapter, so the story still finds it before a rename.

CHAPTERS = {
    'Sea Legs': {
        'part': 'ship',
        'place': "The Castle's cargo hold",
        'intro': ("You wake in the dark, wedged between crates that smell of pepper and tar. "
                  "Somewhere above, boots stomp and Rook's crew laughs. The hold is packed to "
                  "the beams. If you want out, you'll have to make room."),
        'end': "A loose plank in the ceiling. Through it: the lower decks.",
    },
    'Pressure': {
        'part': 'ship',
        'place': "The Castle's lower decks",
        'intro': ("Bishop's pride: every door down here stays shut until something heavy sits "
                  "on the right plank. \"WEIGHT IS TRUST,\" says a chalk scrawl on the wall. "
                  "Pawn doesn't weigh much. Good thing crates do."),
        'end': "A ladder up, and a voice from above: \"Pawn? Is that you?\"",
    },
    'Locks': {
        'was': ['Locks and Keys'],
        'part': 'ship',
        'place': "The brig and the upper decks",
        'intro': ("The brig deck. Captain Knight and the crew are behind Bishop's best locks, "
                  "and every lock wants more weight than the last. Free them, then get "
                  "everyone up top before Rook wakes."),
        'end': ("The crew bursts onto the top deck, cuts loose Rook's jolly boat and rows "
                "into the fog. Knight has Rook's chart under her arm."),
    },
    'The Squeeze': {
        'part': 'sea',
        'place': "Rook's hidden harbour",
        'intro': ("Rook's chart leads to a smugglers' harbour full of docks and lock gates. "
                  "Slam a gate on a crate and it doesn't jam. It shoves. The dockhands call "
                  "it \"the squeeze.\" Pawn calls it a way in."),
        'end': ("The White Knight, chained at the far dock. Free, nearly. "
                "The fort's sea gate is still shut."),
    },
    'Gunpowder': {
        'part': 'sea',
        'place': "The harbour fort",
        'intro': ("The fort guarding the harbour mouth bristles with Rook's cannons. Knight "
                  "hands you a fuse. \"Cannons open doors too, if you aim them at the right "
                  "walls. Mind your fingers.\""),
        'end': ("The sea gate blows apart and the White Knight sails free, with shots "
                "chasing her out of the harbour."),
    },
    "Davy Jones' Locker": {
        'part': 'sea',
        'place': "The Graveyard of Ships",
        'intro': ("The X lies past the Graveyard of Ships: a fogbank full of wrecks, every "
                  "one of them someone who went looking for the Lost King's Hoard. Their guns "
                  "and powder are still aboard, and the White Knight is going to need them."),
        'end': "Out of the fog, a black sail. The Black Queen has found you.",
    },
    'Endgame': {   # name not final: the two big finale levels
        'part': 'sea',
        'place': "The X",
        'intro': ("Rook's voice rolls across the water: \"THAT'S MY TREASURE, PAWN.\" Knight "
                  "takes the wheel. \"Every gun we've got, Pawn. Make them count.\""),
        'end': None,   # the ending scene plays instead
    },
    'Expert Waters': {   # optional bonus chapter after the ending
        'part': 'sea',
        'place': "Bishop's workshop",
        'intro': ("Bishop survived. Of course he did. And he left a note: \"YOU THINK THOSE "
                  "WERE HARD?\""),
        'end': None,
    },
}


# Headings for the two halves of the voyage map.
PARTS = {
    'ship': {'title': 'Aboard the Castle', 'note': "Climb out of Rook's ship, deck by deck."},
    'sea':  {'title': 'The open sea', 'note': "Follow Rook's chart to the X."},
}


def chapter_story(titles):
    """Story details for a voyage's chapters, in order: [{title, part, place, intro, end}].
    A chapter this file doesn't know (renamed, or new) takes the part of the one before it,
    so the map keeps working while chapters are still being reshuffled."""
    out, part = [], 'ship'
    for title in titles:
        info = chapter_info(title)
        part = info.get('part', part)
        out.append({'title': title, 'part': part, 'place': info.get('place', ''),
                    'intro': info.get('intro', ''), 'end': info.get('end')})
    return out


def chapter_info(title):
    """A chapter's story by its title, or by a title it 'was'."""
    if title in CHAPTERS:
        return CHAPTERS[title]
    return next((info for info in CHAPTERS.values() if title in info.get('was', [])), {})


def after_names(name):
    """A chapter title plus its older titles: what a cutscene's 'after' can match."""
    info = CHAPTERS.get(name)
    return [name] + (info.get('was', []) if info else [])


def after_keys(cut):
    """When a cutscene plays, as the pages match it: 'chapter:<title>' after a chapter,
    'level:<name>' after a level ('after_level'), or 'start' / 'ending'. Tagging them keeps a
    chapter and a level with the same name (Davy Jones' Locker) apart."""
    if 'after_level' in cut:
        return ['level:' + cut['after_level']]
    if cut['after'] in ('start', 'ending'):
        return [cut['after']]
    return ['chapter:' + n for n in after_names(cut['after'])]


def payload(titles):
    """Everything the pages need, as plain JSON: the chapters' story and the cutscenes."""
    return {'chapters': chapter_story(titles), 'parts': PARTS,
            'cutscenes': {c['id']: {'title': c['title'], 'order': n, 'after': after_keys(c), 'lines': c.get('lines', [])}
                          for n, c in enumerate(CUTSCENES)}}


def transition(name, fallback=None):
    """The line on a room's tally: this file's line for the level, else the level's own."""
    return TRANSITIONS.get(name) or fallback


# --- Per-room lines ---------------------------------------------------------------------
# Shown on the room tally as you walk on to the next room. Keyed by level name. Lines try not
# to depend on the exact order, so they survive the reshuffle. New levels get lines later.

TRANSITIONS = {
    # Sea Legs: the hold
    'Shore Leave':       "The crates creak behind you. Nobody heard. Probably.",
    'Heave Ho':          "Pepper sacks, rum casks, someone's spare boots. Rook steals everything.",
    'Wedged':            "That crate's not going anywhere now. Neither are you, if you're careless.",
    'One at a Time':     "Light through the planks above. Not far now.",

    # Pressure: the lower decks
    'Dead Weight':       "So that's how Rook's doors work. Bishop, you crooked menace.",
    'Two Locks':         "Chalked on the wall: \"NO, YOU CAN'T BE IN TWO PLACES AT ONCE. TRIED IT.\"",
    'Hold the Door':     "Snoring overhead. Rook's crew sleeps like cannons.",

    # Locks: the brig and upper decks
    'Cargo Hold':        "Your crew's stolen cargo, stacked to the beams. You'll be back for that.",
    'The Brig':          "The cell doors swing open. Knight: \"Good work, deckhand. Now get us off this tub.\"",
    'Deadbolt':          "Boots pass right overhead. Everyone freezes until they're gone.",
    'Nine Locks':        "Nine locks on one hatch. Rook really doesn't like visitors.",
    'Seven Seals':       "Seven plates for one door. Rook really doesn't like visitors.",   # the chapter test for now: a popup, not a line

    # The Squeeze: the harbour
    'Squeeze Play':      "The gate spat the crate clean into the sealed pocket. Bishop would be proud. Or furious.",
    'Shove Off':         "The dock gates groan open. Somewhere in this harbour is your ship.",
    'Lock Gate':         "Through a gap in the warehouse wall: the White Knight's masts.",
    'Dry Dock':          "Empty dry docks, all but one. You can hear the White Knight creaking against her chains.",

    # Gunpowder: the fort
    'Load and Light':    "That's one way to knock. Your ears are ringing.",
    'Clear the Way':     "The fort's guards are shouting now. They know someone's here.",
    'Powder Keg':        "Powder monkeys scatter. One salutes you on his way out.",
    'Broadside':         "Somewhere below, the White Knight's chains rattle.",
    'Open Fire':         "A shot from the walls punches through the dock behind you. Close one.",
    'Run the Gauntlet':  "Knight, from the harbour: \"Keep moving, Pawn! We're nearly loose!\"",
    'Powder Monkey':     "No going back now. The fort's on fire. Only a little.",

    # Davy Jones' Locker: the Graveyard of Ships
    'Hair Trigger':      "A wreck with her guns still loaded, and one still firing. Don't stand in front of it.",
    "Davy Jones' Locker": "Water sloshes round your ankles. This wreck won't stay up much longer.",
    'The Long Shot':     "Every barrel of powder you can carry. The White Knight's guns are hungry.",

    # Expert Waters: Bishop's workshop
    'Brig Break':        "Chalked on the cell door: \"THIS ONE'S HARDER. YOU'RE WELCOME.\"",
}
# The Last Broadside, The Black Queen and The Kraken end their chapters (or end at their own
# chest), so they show a popup rather than a tally line: their story is the chapter's 'end'
# and the cutscenes.


# --- Cutscenes --------------------------------------------------------------------------
# Animated pixel scenes that play full screen with no narration (static/js/story.js draws
# them). 'after' says when one plays: 'start' (the first time the game opens), a chapter
# title (before the next chapter's first room), or 'ending' (after the Endgame's last room).
# 'after_level' instead names a level: the scene plays before the room after it.
# Each plays once; the map has "watch again".
#   'title'  its name on the map's "watch again" buttons.
#   'plan'   what happens in each shot. Notes for us; never shown in the game.
#   'lines'  the words that do appear, one dict per shot: speech bubbles (and sounds like
#            BOOM), keyed by who says them. Leave a line out and its bubble just doesn't show.

CUTSCENES = [
    {'id': 'intro', 'title': 'The capture', 'after': 'start',
     'plan': [
        "Night. The White Knight sails home, lanterns low, a sailor singing on deck.",
        "Out of the fog: the Castle, Captain Rook's iron-plated ship. Rook orders them to surrender, then fires.",
        "Rook's crew drags Captain Knight and the crew across, under a red alarm glow, then tows the White Knight away.",
        "In the Castle's hold, one crate is snoring. Pawn wakes up and pops out.",
        "The BLOCKED logo.",
     ],
     'lines': [
        {'sailor': "Yo ho, yo ho..."},
        {'lookout': "SHIP! OUT OF THE FOG!", 'rook': "STRIKE YOUR COLOURS!", 'boom': "BOOM!"},
        {'crew': "HELP!", 'crew2': "NOT THE BRIG!", 'knight': "UNHAND ME, ROOK!",
         'rook': "TAKE THE SHIP TOO!", 'rook2': "HAR HAR HAR!"},
        {'pawn': "...uh oh."},
        {},
     ]},
    {'id': 'escape', 'title': 'The escape', 'after': 'Locks',
     'plan': [
        "The Castle at night. Pawn, Knight and the crew sneak out of a hatch and along the deck to Rook's jolly boat.",
        "The boat drops into the sea and they row for the fog. Rook bursts on deck in his nightshirt and fires after them. Missed.",
        "Rook's stolen chart unrolls: a dotted line from the boat to his hidden harbour, and beyond it, an X.",
     ],
     'lines': [
        {'knight': "QUIET NOW...", 'pawn': "THE BOAT!"},
        {'crew': "ROW! ROW!", 'rook': "PAAAWN!", 'boom': "BOOM!"},
        {'chart': "ROOK'S CHART", 'harbour': "HIS HARBOUR", 'x': "THE KING'S HOARD"},
     ]},
    {'id': 'ship-free', 'title': 'The White Knight sails', 'after': 'Gunpowder',
     'plan': [
        "Dawn at Rook's harbour. The White Knight is chained behind the fort's sea gate. Pawn lights a cannon.",
        "The sea gate blows apart, and the White Knight sails out through the smoke into the sunrise.",
     ],
     'lines': [
        {'pawn': "FIRE IN THE HOLE!", 'boom': "KA-BOOM!"},
        {'crew': "WE'RE FREE!", 'knight': "HOIST THE SAILS! TO THE X!"},
     ]},
    {'id': 'black-queen', 'title': 'The Black Queen', 'after': "Davy Jones' Locker",
     'plan': [
        "The fog of the Graveyard of Ships thins. Ahead, an island shaped like a crown.",
        "Behind: a black sail. The Black Queen, Rook's flagship, bigger than the Castle, under a red sky.",
     ],
     'lines': [
        {'lookout': "LAND HO! THE CROWN!"},
        {'rook': "THAT TREASURE IS MINE!", 'knight': "BATTLE STATIONS!"},
     ]},
    {'id': 'kraken', 'title': 'The kraken', 'after_level': 'The Black Queen',   # after the deck-battle level
     'plan': [
        "The Black Queen goes down by the bow, Rook shaking his fist all the way. Knight: \"Check.\"",
        "The water ahead boils, and tentacles rise between the White Knight and the island.",
     ],
     'lines': [
        {'rook': "CURSE YOU, PAWN!", 'knight': "CHECK."},
        {'crew': "KRAKEN!!!"},
     ]},
    {'id': 'ending', 'title': 'The end', 'after': 'ending',
     'plan': [
        "Dawn. The White Knight sails into the crown island's lagoon. The sea is calm.",
        "The Lost King's Hoard: a great chest bursting with gold.",
        "Knight drops a captain's hat three sizes too big onto Pawn's head.",
        "CHECKMATE. The end.",
     ],
     'lines': [
        {'lookout': "THE CROWN ISLAND!"},
        {'crew': "TREASURE!!!"},
        {'knight': "A PAWN THAT CROSSES THE BOARD...", 'knight2': "...GETS PROMOTED.", 'pawn': "CAPTAIN PAWN?!"},
        {'checkmate': "CHECKMATE.", 'end': "THE END", 'after': "...unless Bishop left more doors."},
     ]},
]
