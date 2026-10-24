"""Renders a track with two versions of audio.js (randomness fixed) and compares
the waveforms: correlation 1.0 and a tiny difference mean they sound the same.

    .venv\Scripts\python tools\tests\music_compare.py old_audio.js new_audio.js [track ...]
"""
import math, pathlib, sys
from playwright.sync_api import sync_playwright

old, new = (pathlib.Path(p).read_text(encoding='utf-8') for p in sys.argv[1:3])
tracks = sys.argv[3:] or ['set-sail', 'boss-storm']
SECONDS = 10
HARNESS = """
async ([src, track, seconds]) => {
  let seed = 1; Math.random = () => { seed = (seed * 16807) % 2147483647; return (seed - 1) / 2147483646; };
  const offline = new OfflineAudioContext(2, 44100 * seconds, 44100);
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
  const buf = await offline.startRendering();
  return Array.from(buf.getChannelData(0).filter((_, i) => i % 4 === 0));
}
"""
with sync_playwright() as p:
    b = p.chromium.launch(channel='msedge')
    pg = b.new_page()
    for track in tracks:
        pg.goto('about:blank'); a = pg.evaluate(HARNESS, [old, track, SECONDS])
        pg.goto('about:blank'); c = pg.evaluate(HARNESS, [new, track, SECONDS])
        n = min(len(a), len(c))
        dot = sum(a[i] * c[i] for i in range(n)); na = math.sqrt(sum(x * x for x in a[:n])); nc = math.sqrt(sum(x * x for x in c[:n]))
        diff = math.sqrt(sum((a[i] - c[i]) ** 2 for i in range(n)) / n); rms = na / math.sqrt(n)
        print(f'{track:14} correlation {dot / (na * nc):.4f}, difference {20 * math.log10(diff / rms):.1f} dB below the music')
    b.close()
