# Blocked: story outline

Outline v3, matched to the reorganised voyage (7 chapters plus an optional Expert Waters chapter). The shape is set, and names and wording are still open.

**All story text now lives in `story.py`**, keyed by chapter title and level name rather than by number, so it survives the reshuffle. Both versions of the game read it directly (nothing goes in `seed_levels.py`): room lines on the tally, chapter title cards, chest lines on each finale's popup, the cutscenes and the map.

## The shape

| Part | Chapter | Where | Mechanic |
| --- | --- | --- | --- |
| **1. Escape** | Sea Legs | The *Castle*'s cargo hold | crates |
| | Pressure | The *Castle*'s lower decks | pressure plates |
| | Locks | The brig and upper decks: free the crew, steal Rook's jolly boat | advanced plates |
| **2. Get your ship back** | The Squeeze | Rook's hidden harbour, with lock gates on the docks | the squeeze |
| | Gunpowder | The harbour fort: blast the sea gate, sail the *White Knight* out | cannons |
| **3. The voyage** | Davy Jones' Locker | The Graveyard of Ships: salvage powder from wrecks on the way to the X | carried resources |
| | Endgame *(name TBD)* | The X: **deck battle** with the *Black Queen*, then the **kraken** guarding the Hoard | finale |
| *Bonus* | Expert Waters | Bishop's workshop: "YOU THINK THOSE WERE HARD?" | expert levels |

The ending comes after the kraken, when the crew reaches the Lost King's Hoard.

## The premise

You're **Pawn**, the smallest deckhand aboard the *White Knight*, the smallest piece on the board. One foggy night Captain **Rook** and his iron-plated ship, the *Castle*, come out of the fog. Rook's crew throws Captain Knight and the crew into the *Castle*'s brig, and tows the *White Knight* off to his hidden harbour.

They forgot about you. You were asleep in a crate.

## The cast (chess theme)

**Black pieces:**
- **Captain Rook:** big, blunt, only moves in straight lines. "A shut door never lies."
- **Bishop:** Rook's engineer. Never comes at anything straight, and rigged every trap. *(The level notes could be his chalk scrawls.)*
- ***Castle*:** Rook's ship (Part 1).
- ***Black Queen*:** Rook's flagship (the finale).

**White pieces:**
- **Pawn:** you. At the end Pawn crosses the board and is *promoted* to captain.
- **Captain Knight:** your captain. Moves in strange, clever ways. *(The draft calls Knight "she"; change it if you like.)*
- ***White Knight*:** your ship.
- **The crew:** names to come.

**The prize:** the **Lost King's Hoard**, guarded by a kraken. The last word of the game is **"Checkmate."**

## The map

The map is the default level select, with a **Map / List** toggle.
- **Part 1** (Sea Legs, Pressure, Locks): a cut-away side view of the *Castle*, one deck per chapter, climbing upward.
- **Parts 2–3:** after the escape cutscene, the view pulls out to an **ocean chart**: the harbour, the fort, the Graveyard of Ships, then the X. Your marker starts as the jolly boat and becomes the *White Knight* after Gunpowder. The *Black Queen*'s sail appears after Davy Jones' Locker.
- Each chapter's `'part'` in `story.py` (`ship` / `sea`) says which map it goes on.

## Cutscenes (animated pixel scenes)

**All six are built.** They play full screen with no narration, just the characters' lines in speech bubbles. Any key or a tap skips them. Each plays once, and the map has "Watch again" buttons for the ones you've seen. What happens in each shot (`plan`) and the words on screen (`lines`) are in `story.py` → `CUTSCENES`. A scene plays before the first room of the next chapter, then that chapter's title card. The ending plays from the "The end ▶" button on the Endgame's last room.

| Plays | Scene |
| --- | --- |
| First time the game opens | **Intro:** the *White Knight* at night, the *Castle* from the fog, crew captured, Pawn asleep in a crate |
| After Locks | **Escape:** onto the top deck, steal the jolly boat, row into the fog. Rook in his nightshirt: "PAWN!" |
| After Gunpowder | **Ship free:** the sea gate blows, the *White Knight* sails out |
| After Davy Jones' Locker | **The *Black Queen*:** the crown-shaped island ahead, a black sail behind |
| After the deck battle | **Kraken:** the *Black Queen* sinks ("Check."), then the water boils |
| After the kraken | **Ending:** the Hoard, the oversized captain's hat, "CHECKMATE." |

Smaller scenes could go at other chapter ends or mid-chapter later. Each chapter also gets a short **intro** on its title card and an **end line** on its "Treasure found!" popup (both in `story.py` → `CHAPTERS`).

## Per-room lines

These are in `story.py` → `TRANSITIONS`, one line per level name, written so they don't depend on exact order. There are none yet for:
- the new levels in Locks, The Squeeze and Davy Jones' Locker (no names yet)
- the finale levels (each chapter finale shows its chapter-end line instead)
- cut levels (Stomp, Fire in the Hole)

## Still to decide (later)
1. Final level names and chapter names (e.g. "Endgame" for the finale chapter).
2. Crew names. Does the good side have a Queen, King and so on?
3. Level notes as Bishop's chalk?
4. Any extra cutscenes, and where.
5. Exact wording everywhere.
6. Finale level designs (deck battle and kraken).
