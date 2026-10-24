"""Tests the story features (intro cutscene, voyage map, Map/List switch) on the website and the
standalone build, in headless Edge. The website runs against a COPY of blocked.db.

Usage: story_test.py <scratch dir>     (screenshots are saved there too)
Build the standalone version first: flask --app app export-standalone
"""
import functools, http.server, json, os, re, shutil, sqlite3, subprocess, sys, threading, time
from playwright.sync_api import sync_playwright

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
OUT = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else '.')
os.makedirs(OUT, exist_ok=True)
DB = os.path.join(OUT, 'story_test.db')
shutil.copy(os.path.join(ROOT, 'blocked.db'), DB)
failures = []


def check(ok, what):
    print(('  ok   ' if ok else '  FAIL ') + what)
    if not ok:
        failures.append(what)


# ---------- 1. Flask test client ----------
print('Flask test client')
os.environ.update(SQLITE_PATH=DB, DATABASE_URL='')
sys.path.insert(0, ROOT)
import app as site   # noqa: E402
c = site.app.test_client()
r = c.get('/')
check(r.status_code == 200 and b'storyData' in r.data and b'data-story-scene="intro"' in r.data, 'guest home page has the story data and intro button')
user = 'story%d' % (int(time.time()) % 1000000)
r = c.post('/register', data={'username': user, 'email': '', 'password': 'testpass123', 'confirm': 'testpass123'})
r = c.get('/')
check(r.status_code == 200 and b'id="voyageMap"' in r.data and b'id="voyageList"' in r.data, 'logged-in home page has the map and the list')
with site.app.app_context():
    voyage = site.campaign()
first = voyage[0]['id']
check(c.get(f'/play/{first}').status_code == 200, f'/play/{first} loads')

# ---------- 2. Website in Edge ----------
print('Website')
env = dict(os.environ, SQLITE_PATH=DB, DATABASE_URL='', FLASK_DEBUG='0')
srv = subprocess.Popen([os.path.join(ROOT, '.venv', 'Scripts', 'python'), '-m', 'flask', '--app', 'app', 'run', '--port', '5091'],
                       cwd=ROOT, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(3)
BASE = 'http://127.0.0.1:5091'
KEYS = {'U': 'ArrowUp', 'D': 'ArrowDown', 'L': 'ArrowLeft', 'R': 'ArrowRight'}


def visible(fr, sel):
    return fr.evaluate(f"(() => {{ const e = document.querySelector('{sel}'); return !!e && !e.closest('.hidden') && e.getClientRects().length > 0; }})()")


try:
    with sync_playwright() as p:
        b = p.chromium.launch(channel='msedge', args=['--autoplay-policy=no-user-gesture-required'])
        pg = b.new_page(viewport={'width': 1280, 'height': 800})
        errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.on('console', lambda m: errs.append('console: ' + m.text) if m.type == 'error' else None)
        frame = lambda: pg.frames[1]

        pg.goto(BASE + '/')
        time.sleep(1.2)
        fr = frame()
        check(fr.locator('.cutscene').count() == 1, 'intro plays on the first visit (guest)')
        size = fr.evaluate("(() => { const c = document.querySelector('.cutscene canvas').getBoundingClientRect(); return [c.width, c.height, innerWidth, innerHeight]; })()")
        check(size[0] >= size[2] - 8 and size[1] >= size[3] * 0.9, f'intro fills the screen (canvas {size[0]:.0f}x{size[1]:.0f} in {size[2]}x{size[3]})')
        check(fr.locator('.cutscene-hint').inner_text().lower() == 'press any key to skip', 'dim "press any key to skip" hint')
        check(fr.locator('.cutscene-caption, .cutscene-text').count() == 0, 'no narration captions')
        # let it play straight through, screenshotting along the way (the shots are 5.5, 7.5, 9, 8.5 and 3.5s)
        t0 = time.time()
        for n, at in enumerate((4, 10.5, 17.5, 22.5, 26.5, 31, 33.5)):
            time.sleep(max(0, at - (time.time() - t0)))
            pg.screenshot(path=os.path.join(OUT, f'site_intro_{n + 1}.png'))
        time.sleep(max(0, 36 - (time.time() - t0)))
        check(frame().locator('.cutscene').count() == 0, 'the intro plays through and closes by itself')

        pg.goto(BASE + '/'); time.sleep(1.2)
        check(frame().locator('.cutscene').count() == 0, 'intro does not replay on the next visit')

        frame().goto(BASE + '/login'); time.sleep(1)
        fr = frame()
        fr.fill('#username', user); fr.fill('#password', 'testpass123'); fr.click('button[type=submit]')
        time.sleep(1.5)
        fr = frame()
        n_map = fr.locator('#voyageMapBody .map-node').count()
        check(n_map == len(voyage), f'map shows every voyage room ({n_map} of {len(voyage)})')
        check(visible(fr, '#voyageMapBody') and not visible(fr, '#voyageList'), 'map is the default view')
        check(fr.locator('.map-node.current').count() == 1 and fr.locator('.map-pawn').count() == 1, 'Pawn stands on the current room')
        parts = fr.evaluate("[...document.querySelectorAll('.map-part-head h3')].map(h => h.textContent)")
        check(parts == ['Aboard the Castle', 'The open sea'], f'map has both parts: {parts}')
        pg.screenshot(path=os.path.join(OUT, 'site_map.png'), full_page=True)
        fr.locator('#voyageMap').screenshot(path=os.path.join(OUT, 'site_map_full.png'))

        fr.click('.view-toggle [data-view=list]'); time.sleep(0.3)
        check(visible(fr, '#voyageList') and not visible(fr, '#voyageMapBody'), 'List button shows the old list')
        pg.goto(BASE + '/'); time.sleep(1.5)
        check(visible(frame(), '#voyageList'), 'the List choice is remembered')
        frame().click('.view-toggle [data-view=map]'); time.sleep(0.3)

        frame().click('[data-story-scene=intro] >> visible=true'); time.sleep(0.8)
        check(frame().locator('.cutscene').count() == 1, 'Watch the intro replays it')
        frame().press('body', 'q'); time.sleep(0.6)
        check(frame().locator('.cutscene').count() == 0, 'any key skips the intro')

        frame().click('a.map-node.current')
        where = ''
        for _ in range(40):
            time.sleep(0.2)
            try:
                where = frame().evaluate('location.pathname')
            except Exception:
                continue
            if where.endswith(f'/play/{first}'):
                break
        check(where.endswith(f'/play/{first}'), f'clicking the current room plays it ({where})')

        pg.set_viewport_size({'width': 390, 'height': 760})
        frame().goto(BASE + '/'); time.sleep(1.5)
        wide = frame().evaluate('document.documentElement.scrollWidth - document.documentElement.clientWidth')
        check(wide <= 0, f'no sideways scroll on a phone ({wide}px)')
        frame().locator('#voyageMap').screenshot(path=os.path.join(OUT, 'site_map_phone.png'))
        pg.set_viewport_size({'width': 1280, 'height': 800})

        # --- the story around the rooms ---
        import story
        payload = lambda lid: json.loads(re.search(r'id="levelData">(.*?)</script>', c.get(f'/play/{lid}').get_data(as_text=True), re.S).group(1))
        with site.app.app_context():
            chapters = site.chapters_of(voyage)
        con = sqlite3.connect(DB)   # clear the whole voyage, so every room is open
        uid = con.execute('SELECT id FROM blocked_users WHERE username = ?', (user,)).fetchone()[0]
        con.executemany('INSERT INTO blocked_completions (user_id, level_id, finish_ms, total_moves) VALUES (?, ?, 1000, 999)',
                        [(uid, lv['id']) for lv in voyage])
        con.commit(); con.close()
        p1 = payload(first)
        check(p1['storyBefore']['chapter']['title'] == chapters[0][1] and p1['storyBefore']['chapter']['intro'],
              f"room 1 starts chapter 1 with its title card ({p1['storyBefore']['chapter']['title']})")
        check(p1['transitionLine'] == story.transition(voyage[0]['name'], p1['transitionLine']), 'room lines come from story.py')
        fin = chapters[0][3][-1]['id']
        check(payload(fin)['chestLine'] == story.chapter_story([chapters[0][1]])[0]['end'], 'chapter 1 finale has its chest line')
        esc = next((ch for ch in chapters[1:] if chapters[ch[0] - 2][1] in story.after_names('Locks')), None)
        check(esc is not None, 'a chapter follows Locks, so the escape scene has a place to play')
        # the room whose popup plays the ending (the Endgame's last room, or the voyage's last)
        last = next((lv['id'] for lv in reversed(voyage) if payload(lv['id']).get('ending')), None)
        check(last is not None, f'one room ends the story (level {last})')
        if last:
            con = sqlite3.connect(DB)
            con.execute('DELETE FROM blocked_tiles WHERE level_id = ?', (last,))
            con.execute('INSERT INTO blocked_tiles (level_id, tile_type, x, y, direction, ax, ay) '
                        'SELECT ?, tile_type, x, y, direction, ax, ay FROM blocked_tiles WHERE level_id = ?', (last, first))
            w, h, sol = con.execute('SELECT width, height, solution FROM blocked_levels WHERE id = ?', (first,)).fetchone()
            con.execute('UPDATE blocked_levels SET width = ?, height = ?, solution = ? WHERE id = ?', (w, h, sol, last))
            con.commit(); con.close()

        frame().goto(BASE + f'/play/{first}'); time.sleep(1.5)
        fr = frame()
        check(fr.locator('.chapter-card').count() == 1 and chapters[0][1] in fr.inner_text('.chapter-card'), 'chapter title card shows on the first room')
        pg.screenshot(path=os.path.join(OUT, 'site_card.png'))
        fr.press('body', 'ArrowLeft'); time.sleep(0.2)
        check(fr.locator('.chapter-card').count() == 1 and fr.inner_text('#moveCount') == '0', 'arrow keys do nothing while the card is up')
        fr.press('body', 'Space'); time.sleep(0.6)
        check(fr.locator('.chapter-card').count() == 0, 'Space sets sail')
        frame().goto(BASE + f'/play/{first}'); time.sleep(1.5)
        check(frame().locator('.chapter-card').count() == 0, 'the card shows once')

        if esc:
            frame().goto(BASE + f"/play/{esc[3][0]['id']}"); time.sleep(1.5)
            check(frame().locator('.cutscene').count() == 1, f'the escape scene plays before chapter {esc[0]}')
            time.sleep(3); pg.screenshot(path=os.path.join(OUT, 'site_escape.png'))
            frame().press('body', 'x'); time.sleep(1)
            check(frame().locator('.chapter-card').count() == 1 and esc[1] in frame().inner_text('.chapter-card'),
                  f'then the {esc[1]} title card')
            frame().press('body', 'Enter'); time.sleep(0.6)
            check(frame().locator('.chapter-card, .cutscene').count() == 0, 'then the room')

        frame().goto(BASE + f'/play/{last or first}'); time.sleep(1.5)
        fr = frame()
        while fr.locator('.chapter-card, .cutscene').count():
            fr.press('body', 'Escape'); time.sleep(0.6)
        fr.click('h1')
        for ch in payload(last)['route']:
            fr.press('body', KEYS[ch]); time.sleep(0.02)
        time.sleep(1)
        pg.screenshot(path=os.path.join(OUT, 'site_last_popup.png'))
        check(visible(fr, '#winModal') and fr.inner_text('#nextBtn').startswith('The end'), "the last room's popup offers The end")
        fr.press('body', 'Space'); time.sleep(1)
        check(fr.locator('.cutscene').count() == 1, 'Space plays the ending')
        time.sleep(1.5); pg.screenshot(path=os.path.join(OUT, 'site_ending.png'))
        fr.press('body', 'x')
        where = ''
        for _ in range(40):
            time.sleep(0.2)
            try:
                where = frame().evaluate('location.pathname')
            except Exception:
                continue
            if where == '/':
                break
        check(where == '/', 'after the ending, back to the map')
        time.sleep(1)
        buttons = frame().evaluate("[...document.querySelectorAll('#sceneButtons [data-story-scene]')].map(b => b.textContent)")
        check('The end' in buttons and 'The escape' in buttons, f'watch-again buttons for the scenes seen: {buttons}')
        check(not errs, f'no page errors: {errs or "none"}')
        b.close()
finally:
    srv.terminate()

# ---------- 3. Standalone build ----------
print('Standalone')
DIST = os.path.join(ROOT, 'dist', 'standalone')
handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=DIST)
handler.log_message = lambda *a: None
web = http.server.ThreadingHTTPServer(('127.0.0.1', 5092), handler)
threading.Thread(target=web.serve_forever, daemon=True).start()
SA = 'http://127.0.0.1:5092/index.html'
with sync_playwright() as p:
    b = p.chromium.launch(channel='msedge', args=['--autoplay-policy=no-user-gesture-required'])
    pg = b.new_page(viewport={'width': 1280, 'height': 800})
    errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.on('console', lambda m: errs.append('console: ' + m.text) if m.type == 'error' else None)
    pg.goto(SA); time.sleep(1.5)
    check(pg.locator('.cutscene').count() == 1, 'intro plays the first time the game opens')
    pg.keyboard.press('Space'); time.sleep(0.6)
    check(pg.locator('.cutscene').count() == 0 and pg.is_visible('#screen-title') and not pg.is_visible('#infoModal'),
          'Space skips to the title screen, and the key does nothing else')
    pg.reload(); time.sleep(1.2)
    check(pg.locator('.cutscene').count() == 0, 'intro does not replay after a reload')
    count = pg.evaluate('BLOCKED_DATA.levels.length')
    pg.click('.topbar [data-go=chapters]'); time.sleep(0.5)
    check(pg.locator('#voyageMapBody .map-node').count() == count, f'map shows all {count} rooms')
    check(pg.is_visible('#voyageMapBody') and not pg.is_visible('#chapterList'), 'map is the default view')
    pg.locator('#voyageMap').screenshot(path=os.path.join(OUT, 'sa_map.png'))
    pg.click('.view-toggle [data-view=list]'); time.sleep(0.3)
    check(pg.is_visible('#chapterList') and not pg.is_visible('#voyageMapBody'), 'List button shows the chapter list')
    pg.click('.view-toggle [data-view=map]'); time.sleep(0.3)
    pg.click('a.map-node.current'); time.sleep(0.8)
    while pg.is_visible('#infoModal'):
        pg.keyboard.press('Space'); time.sleep(0.3)
    check(pg.is_visible('#screen-play') and pg.inner_text('#pName') == pg.evaluate('BLOCKED_DATA.levels[0].name'), 'clicking the current room plays it')
    while pg.locator('.chapter-card, .cutscene').count() or pg.is_visible('#infoModal'):   # room 1's title card, then the tutorial
        pg.keyboard.press('Space'); time.sleep(0.5)
    pg.click('#pBack'); time.sleep(0.6)
    check(pg.is_visible('#voyageMapBody'), 'All levels goes back to the map')
    pg.click('[data-go=title]'); time.sleep(0.3)
    pg.click('#screen-title [data-story-scene=intro]'); time.sleep(0.6)
    check(pg.locator('.cutscene').count() == 1, 'Watch the intro replays it')
    pg.mouse.click(400, 300); time.sleep(0.6)
    check(pg.locator('.cutscene').count() == 0, 'a click or tap skips it')
    # --- the story around the rooms ---
    pg.evaluate("""() => { const p = {}; BLOCKED_DATA.levels.forEach(l => p[l.id] = {count: 1, best_ms: 1000, best_moves: 999});
                     localStorage.setItem('blocked-sa-progress', JSON.stringify(p));
                     localStorage.setItem('blocked-sa-story-seen', JSON.stringify({intro: 1}));
                     localStorage.setItem('blocked-sa-seen', JSON.stringify({controls:1,plates:1,squeeze:1,cannons:1,loaded:1,doors:1,kraken:1,hull:1})); }""")
    pg.reload(); time.sleep(1)
    info = pg.evaluate("""() => { const L = BLOCKED_DATA.levels, C = BLOCKED_DATA.chapters, S = BLOCKED_DATA.story;
        const esc = L.findIndex((l, i) => i > 0 && L[i - 1].chapter !== l.chapter && S.cutscenes.escape.after.includes('chapter:' + C[L[i - 1].chapter - 1]));
        const fin = L.findIndex((l, i) => L[i + 1] && L[i + 1].chapter !== l.chapter);
        return { esc, escTitle: esc >= 0 ? C[L[esc].chapter - 1] : null, fin, finSol: L[fin].solution, finLine: S.chapters[L[fin].chapter - 1].end,
                 last: BLOCKED_DATA.ending ?? L.length - 1, lastSol: L[BLOCKED_DATA.ending ?? L.length - 1].solution }; }""")

    def clear_overlays():
        while pg.locator('.chapter-card, .cutscene').count() or pg.is_visible('#infoModal'):
            pg.keyboard.press('Escape'); time.sleep(0.5)

    def solve(sol):
        for ch in sol:
            pg.keyboard.press(KEYS[ch]); time.sleep(0.02)
        time.sleep(1)

    pg.evaluate('BlockedStandalone.playVoyage(0, {flow: true})'); time.sleep(0.8)
    check(pg.locator('.chapter-card').count() == 1, 'chapter 1 title card on the first room')
    pg.keyboard.press('Space'); time.sleep(0.6)
    check(pg.locator('.chapter-card').count() == 0 and pg.is_visible('#screen-play'), 'Space sets sail')
    if info['esc'] >= 0:
        pg.evaluate(f"BlockedStandalone.playVoyage({info['esc']}, {{flow: true}})"); time.sleep(0.8)
        check(pg.locator('.cutscene').count() == 1, f"the escape scene plays before {info['escTitle']}")
        pg.keyboard.press('x'); time.sleep(1)
        check(pg.locator('.chapter-card').count() == 1, f"then the {info['escTitle']} title card")
        pg.keyboard.press('Enter'); time.sleep(0.6)
    clear_overlays()
    pg.evaluate(f"BlockedStandalone.playVoyage({info['fin']}, {{}})"); time.sleep(0.8)
    clear_overlays()
    solve(info['finSol'])
    check(pg.is_visible('#winStory') and pg.inner_text('#winStory') == info['finLine'], f"chapter finale popup shows its chest line: {pg.inner_text('#winStory')!r}")
    pg.evaluate(f"""() => {{ const L = BLOCKED_DATA.levels, f = L[0];   // the ending room gets room 1's layout (this page only)
        Object.assign(L[{info['last']}], {{ width: f.width, height: f.height, tiles: f.tiles, solution: f.solution }}); }}""")
    info['lastSol'] = pg.evaluate('BLOCKED_DATA.levels[0].solution')
    pg.evaluate(f"BlockedStandalone.playVoyage({info['last']}, {{}})"); time.sleep(0.8)
    clear_overlays()
    solve(info['lastSol'])
    check(pg.is_visible('#winModal') and pg.inner_text('#nextBtn').startswith('The end'), "the last room's popup offers The end")
    pg.keyboard.press('Space'); time.sleep(1)
    check(pg.locator('.cutscene').count() == 1, 'Space plays the ending')
    pg.keyboard.press('x'); time.sleep(1.5)
    check(pg.is_visible('#screen-chapters'), 'after the ending, back to the map')
    buttons = pg.evaluate("[...document.querySelectorAll('#sceneButtons [data-story-scene]')].map(b => b.textContent)")
    check('The end' in buttons, f'watch-again buttons: {buttons}')

    pg.set_viewport_size({'width': 390, 'height': 760})
    pg.click('.topbar [data-go=chapters]'); time.sleep(0.5)
    wide = pg.evaluate('document.documentElement.scrollWidth - document.documentElement.clientWidth')
    check(wide <= 0, f'no sideways scroll on a phone ({wide}px)')
    check(not errs, f'no page errors: {errs or "none"}')
    b.close()
web.shutdown()

print('\nALL PASSED' if not failures else f'\n{len(failures)} FAILED: {failures}')
sys.exit(1 if failures else 0)
