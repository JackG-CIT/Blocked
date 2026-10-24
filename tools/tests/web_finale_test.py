"""Plays The Black Queen and The Kraken on the website (headless Edge), against a copy
of the database that has had `flask --app app seed --refresh`. Usage: web_finale_test.py <db copy>"""
import os, sys, subprocess, time
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
os.environ.update(SQLITE_PATH=sys.argv[1], DATABASE_URL='')
import app as A, db
from flask_bcrypt import generate_password_hash
from playwright.sync_api import sync_playwright

with A.app.app_context():
    if not db.query("SELECT id FROM blocked_users WHERE username='tester'", one=True):
        db.insert("INSERT INTO blocked_users (username, password, is_admin) VALUES (?, ?, 1)",
                  ('tester', generate_password_hash('testpass123').decode()))
        db.commit()
    levels = {l['name']: l for l in A.campaign()}
env = dict(os.environ, FLASK_DEBUG='0')
site = subprocess.Popen([sys.executable, '-m', 'flask', '--app', 'app', 'run', '--port', '5088'], env=env,
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(3)
fails = 0
try:
    with sync_playwright() as p:
        b = p.chromium.launch(channel='msedge')
        pg = b.new_page(viewport={'width': 1366, 'height': 768})
        errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.goto('http://127.0.0.1:5088/login'); f = pg.frames[1]
        f.fill('#username', 'tester'); f.fill('#password', 'testpass123'); f.click('button[type=submit]'); time.sleep(1.2)
        for name, kind in (('The Black Queen', 'hull'), ('The Kraken', 'kraken')):
            lv = levels[name]
            pg.frames[1].goto(f"http://127.0.0.1:5088/play/{lv['id']}"); time.sleep(1.2)
            f = pg.frames[1]
            for i in range(30):   # skip the cutscene and the chapter card
                if not f.evaluate("!!document.querySelector('.cutscene, .chapter-card')"):
                    break
                pg.keyboard.press('Escape' if i % 2 else 'Space'); time.sleep(0.4)
            time.sleep(0.5)
            bar = f.evaluate(f"(document.querySelector('.board-frame > .health .health-bar.{kind}') || {{}}).innerText || 'none'")
            geo = f.evaluate("""(() => { const w = document.querySelector('.board-wrap'), t = document.getElementById('gameBoard');
                return {camera: w.classList.contains('camera'), left: t.offsetLeft, wrapW: w.clientWidth, tableW: t.offsetWidth,
                        noScroll: document.documentElement.scrollHeight <= innerHeight + 1}; })()""")
            print(name, '| health bar:', bar, '|', geo)
            km = {'U': 'ArrowUp', 'D': 'ArrowDown', 'L': 'ArrowLeft', 'R': 'ArrowRight'}
            for ch in lv['solution']:
                pg.keyboard.press(km[ch])
                f.wait_for_function("!document.querySelector('#gameBoard td[data-fly]')", timeout=5000)
            time.sleep(1)
            won = f.is_visible('#winModal')
            print('   won:', won, '| button:', f.inner_text('#nextBtn') if f.is_visible('#nextBtn') else '-')
            fails += (not won) + (bar == 'none') + (geo['left'] != 0) + (not geo['noScroll'])
            pg.screenshot(path=os.path.join(os.path.dirname(sys.argv[1]), f'web_{kind}.png'))
        print('errors:', errs or 'none')
        fails += bool(errs)
        b.close()
finally:
    site.terminate()
print('FAILURES:', fails)
sys.exit(1 if fails else 0)
