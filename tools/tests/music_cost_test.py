"""How hard is the music on the audio engine? Renders music offline (as fast as
the browser can) and reports CPU seconds per second of music. Above about 1.0
on the player's machine, audio breaks up; slow laptops and Chromebooks are
several times slower per core than a desktop.

    .venv\\Scripts\\python tools\\tests\\music_cost_test.py [audio.js path] [track ...]
"""
import pathlib, sys, json
from playwright.sync_api import sync_playwright

src = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else 'static/js/audio.js').read_text(encoding='utf-8')
tracks = sys.argv[2:] or ['set-sail', 'sea-legs', 'gunpowder', 'boss-storm']
SECONDS = 30

# audio.js makes `new AudioContext()` and schedules notes from a setInterval
# timer. Here the context is an OfflineAudioContext and the timer is driven by
# hand: render 0.1 s, run the scheduler, repeat.
HARNESS = """
async ([src, track, seconds]) => {
  const rate = 44100;
  const offline = new OfflineAudioContext(2, rate * seconds, rate);
  // audio.js schedules a little ahead of the audio clock from a timer. Here the
  // clock is faked: it reads 0 while the song starts, then the whole length
  // while the scheduler runs once, so every note is scheduled up front.
  let fakeNow = 0;
  Object.defineProperty(offline, 'currentTime', { get: () => fakeNow });
  Object.defineProperty(offline, 'state', { get: () => 'running' });
  offline.resume = () => Promise.resolve();
  window.AudioContext = function () { return offline; };
  const timers = [];
  window.setInterval = fn => { timers.push(fn); return timers.length; };
  window.clearInterval = id => { timers[id - 1] = null; };
  (0, eval)(src);
  BlockedSound.unlock();
  BlockedSound.music(track, {});
  fakeNow = seconds - 0.3;
  timers.forEach(f => f && f());
  const t0 = performance.now();
  await offline.startRendering();
  return (performance.now() - t0) / 1000;
}
"""
with sync_playwright() as p:
    b = p.chromium.launch(channel='msedge')
    pg = b.new_page()
    pg.goto('about:blank')
    for track in tracks:
        secs = pg.evaluate(HARNESS, [src, track, SECONDS])
        print(f'{track:16} {secs:5.2f} s of CPU for {SECONDS} s of music -> {secs / SECONDS:.3f} per second')
        pg.reload()
    b.close()
