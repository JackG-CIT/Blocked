"""Tests the level rework in the standalone build (run `flask --app app export-standalone` first):
chapters of any length, the finale's health bars and camera, the ending's place, and the editor's
new tiles. Headless Edge; zero page errors expected."""
import functools, http.server, json, threading, time, pathlib, sys
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parents[2]
handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(ROOT / 'dist' / 'standalone'))
handler.log_message = lambda self, *a: None
srv = http.server.ThreadingHTTPServer(('127.0.0.1', 5094), handler)
threading.Thread(target=srv.serve_forever, daemon=True).start()
fails = []
def check(ok, what):
    print(('ok   ' if ok else 'FAIL ') + what)
    if not ok:
        fails.append(what)

with sync_playwright() as p:
    b = p.chromium.launch(channel='msedge', args=['--autoplay-policy=no-user-gesture-required'])
    pg = b.new_page(viewport={'width': 1366, 'height': 768})
    errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)))
    # Unlock everything and skip the story scenes and first-time popups.
    pg.add_init_script("""
        localStorage.setItem('blocked-sa-story-seen', JSON.stringify({intro: true}));
    """)
    pg.goto('http://127.0.0.1:5094/index.html'); time.sleep(1)
    data = pg.evaluate('window.BLOCKED_DATA')
    lv = data['levels']
    check(data['chapters'][:8] == ['Sea Legs', 'Pressure', 'Locks', 'The Squeeze', 'Gunpowder', "Davy Jones' Locker", 'Endgame', 'Expert Waters'],
          'eight chapters in order: ' + ', '.join(data['chapters']))
    sizes = {}
    for l in lv:
        sizes[l['chapter']] = l['size']
    check(sizes == {1: 5, 2: 4, 3: 5, 4: 5, 5: 8, 6: 4, 7: 2, 8: 16}, f'chapter sizes {sizes}')
    names = [l['name'] for l in lv]
    check(lv[names.index('Tangled Rigging')]['mid'] is False and lv[names.index('Hold the Door')]['mid'] is True,
          "chapter 2's 4th room is its chest room; its 3rd walks on")
    check(not lv[names.index('The Black Queen')]['mid'] and not lv[names.index('Stomp')]['mid'], 'finale and Expert Waters levels stand alone')
    check(data['ending'] == names.index('The Kraken'), f"the ending plays after The Kraken (index {data['ending']})")
    check([l['music'] for l in lv if l['name'] in ('The Black Queen', 'The Kraken', 'Relay', 'Seven Seals', 'Pinch Point')]
          == ['boss3', 'boss4', 'finale', 'kraken', 'expert'], 'music slots for the new chapters')
    # Unlock every level, then open the finale levels.
    pg.evaluate("""() => { const pr = {}; BLOCKED_DATA.levels.forEach(l => pr[l.id] = {best_ms: 1000, best_moves: 10, runs: 1});
                           localStorage.setItem('blocked-sa-progress', JSON.stringify(pr)); }""")
    keys = pg.evaluate('Object.keys(localStorage)')
    print('   storage keys:', keys)
    for name, kind, vp in (('The Black Queen', 'hull', (1366, 768)), ('The Kraken', 'kraken', (1280, 650))):
        pg.set_viewport_size({'width': vp[0], 'height': vp[1]})
        pg.goto('http://127.0.0.1:5094/index.html'); time.sleep(0.8)
        pg.mouse.click(5, 300)
        pg.click('[data-go=chapters]'); time.sleep(0.3)
        pg.evaluate("document.querySelector('[data-view=list]') && document.querySelector('[data-view=list]').click()")
        time.sleep(0.3)
        pg.evaluate('''name => { const card = [...document.querySelectorAll('#chapterList .level-card')]
                                 .find(c => c.querySelector('h3').textContent === name);
                                 card.querySelector('button.stretched').click(); }''', name)
        time.sleep(1.2)
        for _ in range(30):   # skip the story scenes, the chapter card and first-time popups
            if pg.evaluate("!!document.querySelector('#gameBoard td.player')") and not pg.is_visible('#infoModal'):
                break
            pg.keyboard.press('Escape' if _ % 2 else 'Space'); time.sleep(0.4)
        time.sleep(0.5)
        cap = pg.locator('#screen-play .board-frame > .health .health-bar.' + kind)
        check(cap.count() == 1, f'{name}: health bar shows ({pg.inner_text("#screen-play .board-frame > .health") if cap.count() else "none"})')
        cam = pg.evaluate("document.querySelector('#screen-play .board-wrap').classList.contains('camera')")
        scroll_h = pg.evaluate("document.documentElement.scrollHeight <= innerHeight + 1")
        check(scroll_h, f'{name} at {vp[0]}x{vp[1]}: page does not scroll (camera={cam})')
        # Play the stored solution through the keyboard and wait out the shots.
        sol = lv[names.index(name)]['solution']
        keymap = {'U': 'ArrowUp', 'D': 'ArrowDown', 'L': 'ArrowLeft', 'R': 'ArrowRight'}
        for ch in sol:
            pg.keyboard.press(keymap[ch])
            pg.wait_for_function("!document.querySelector('#gameBoard td[data-fly]')", timeout=5000)
            if pg.is_visible('#winModal') or pg.is_visible('#infoModal'):
                break
        time.sleep(0.6)
        won = pg.is_visible('#winModal')
        check(won, f'{name}: the stored solution wins in the game ({len(sol)} moves)')
        if cam:
            check(True, f'{name}: camera window used at {vp[0]}x{vp[1]}')
        pg.screenshot(path=str(ROOT / 'dist' / f'{kind}.png'))
        if pg.is_visible('#winModal'):
            pg.keyboard.press('Escape')
    # The editor has the new tools.
    pg.set_viewport_size({'width': 1366, 'height': 768})
    pg.goto('http://127.0.0.1:5094/index.html'); time.sleep(0.8)
    pg.click('[data-go=workshop]'); time.sleep(0.3)
    pg.click('#newLevelBtn'); time.sleep(0.5)
    tools = pg.evaluate("Array.from(document.querySelectorAll('#tools [data-tool], #tools button')).map(b => b.textContent.trim())")
    check(any('Kraken' in t for t in tools) and any('hull' in t.lower() for t in tools), 'editor has Kraken and Enemy hull tools')
    check(not errs, 'no page errors ' + str(errs))
    b.close()
srv.shutdown()
print('FAILURES:', len(fails))
sys.exit(1 if fails else 0)
