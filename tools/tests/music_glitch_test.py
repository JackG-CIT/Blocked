"""Measures music scheduling glitches on the standalone build's level screen.

Every note's start time is compared with the audio clock at the moment it's
scheduled; a note scheduled after its start time is an audible glitch. The CPU
is throttled to imitate slower laptops/Chromebooks.

    .venv\Scripts\python tools\tests\music_glitch_test.py [variant]
variants: none (as built), notide (sea animation off), look1 (1s lookahead), both
"""
import functools, http.server, os, sys, threading, time
from playwright.sync_api import sync_playwright

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'dist', 'standalone')
handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=ROOT)
handler.log_message = lambda self, *a: None
srv = http.server.ThreadingHTTPServer(('127.0.0.1', 5091), handler)
threading.Thread(target=srv.serve_forever, daemon=True).start()

PROBE = """
(() => {
  window.__late = []; window.__notes = 0;
  const start = AudioScheduledSourceNode.prototype.start;
  AudioScheduledSourceNode.prototype.start = function (when = 0, ...rest) {
    if (this.context && this.context.state === 'running' && when > 0) {
      window.__notes++;
      const margin = when - this.context.currentTime;
      if (margin < 0) window.__late.push(margin);
    }
    return start.call(this, when, ...rest);
  };
})();
"""

def run(variant, throttle, seconds=20):
    with sync_playwright() as p:
        b = p.chromium.launch(channel='msedge', args=['--autoplay-policy=no-user-gesture-required'])
        ctx = b.new_context(viewport={'width': 1366, 'height': 768})
        pg = ctx.new_page()
        pg.add_init_script(PROBE)
        if variant in ('notide', 'both'):
            pg.add_init_script("document.addEventListener('DOMContentLoaded', () => { const s = document.createElement('style'); s.textContent = 'body { animation: none !important; }'; document.head.appendChild(s); });")
        cdp = ctx.new_cdp_session(pg)
        pg.goto('http://127.0.0.1:5091/index.html')
        if variant in ('look1', 'both'):
            pass   # lookahead is patched in the file under test (see the fix)
        pg.mouse.click(5, 300)
        pg.evaluate("BlockedStandalone.show('chapters')")
        time.sleep(2)
        pg.evaluate("window.__late = []; window.__notes = 0")
        cdp.send('Emulation.setCPUThrottlingRate', {'rate': throttle})
        time.sleep(seconds)
        late, notes = pg.evaluate("[window.__late, window.__notes]")
        b.close()
        worst = min(late) if late else 0
        print(f'{variant:7} cpu x{throttle}: {notes} notes, {len(late)} late ({100 * len(late) / max(notes, 1):.1f}%), worst {worst * 1000:.0f} ms late')

variant = sys.argv[1] if len(sys.argv) > 1 else 'none'
for rate in (1, 4, 6):
    run(variant, rate)
srv.shutdown()
