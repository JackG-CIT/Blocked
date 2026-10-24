"""How the voyage splits into chapters, shared by the website (app.py), the
standalone build (export_standalone.py) and the line-up check (flow.py).

Chapters can be any length: seed_levels.py lists the titles (CHAPTERS), how many
levels each one has (CHAPTER_LENGTHS), and the "loose" chapters (LOOSE_CHAPTERS),
whose levels each stand alone. In a normal chapter the rooms join up: you walk
out of each room through a door or trapdoor into the next one, and the chest
waits in the chapter's last room (its boss room). In a loose chapter (the
finale's two big levels, and the Expert Waters bonus) every level ends at its
own chest. Bonus chapters (BONUS_CHAPTERS, e.g. Expert Waters) come after the
story's ending, so the ending plays after the last level before them.

Levels past the end of the listed chapters (an admin added more) fall into
extra chapters of five called "Uncharted Waters".
"""
EXTRA_TITLE = 'Uncharted Waters'
EXTRA_SIZE = 5


def settings():
    """CHAPTERS, CHAPTER_LENGTHS and LOOSE_CHAPTERS from seed_levels.py."""
    try:
        import seed_levels
    except ImportError:
        return [], [], set()
    titles = list(getattr(seed_levels, 'CHAPTERS', []))
    lengths = list(getattr(seed_levels, 'CHAPTER_LENGTHS', [EXTRA_SIZE] * len(titles)))
    return titles, lengths, set(getattr(seed_levels, 'LOOSE_CHAPTERS', ()))


def bonus_titles():
    try:
        import seed_levels
    except ImportError:
        return set()
    return set(getattr(seed_levels, 'BONUS_CHAPTERS', ()))


def layout(total, titles=None, lengths=None, loose=None):
    """The chapters for a voyage of `total` levels:
    [{number, title, start, size, rooms}], where `rooms` is False for a loose chapter."""
    if titles is None:
        titles, lengths, loose = settings()
    lengths, loose = lengths or [], loose or set()
    out, start = [], 0
    while start < total:
        n = len(out)
        title = titles[n] if n < len(titles) else EXTRA_TITLE
        size = lengths[n] if n < len(lengths) else EXTRA_SIZE
        size = max(1, min(size, total - start))
        out.append({'number': n + 1, 'title': title, 'start': start, 'size': size, 'rooms': title not in loose})
        start += size
    return out


def ending_index(chapters):
    """The level after which the story's ending plays: the last level before the bonus chapters."""
    bonus = bonus_titles()
    story = [ch for ch in chapters if ch['title'] not in bonus] or chapters
    return story[-1]['start'] + story[-1]['size'] - 1 if story else -1


def locate(chapters, index):
    """(chapter, room) for the level at `index`; rooms count from 1."""
    for ch in chapters:
        if ch['start'] <= index < ch['start'] + ch['size']:
            return ch, index - ch['start'] + 1
    raise IndexError(index)


def walks_on(chapter, room):
    """Whether this room ends at a door into the next room (not a chest)."""
    return chapter['rooms'] and room < chapter['size']


def is_boss(chapter, room):
    """A chapter's last room is its test (the boss room)."""
    return room == chapter['size']


def music_slot(chapter, room):
    """The music slot (static/js/audio.js PLAYLIST) for a voyage room. Chapters 1-6
    play their own track, with the grand boss version in the last room. The finale
    chapter plays the storm, then the kraken's theme for its last level; anything
    after that (Expert Waters) has its own slot."""
    n = chapter['number']
    if n <= 6:
        return f'boss{n}' if is_boss(chapter, room) else f'chapter{n}'
    if n == 7:
        return 'kraken' if is_boss(chapter, room) else 'finale'
    return 'expert'
