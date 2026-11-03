"""Generate the animated profile banner (light & dark) into profile/."""

from html import escape
from pathlib import Path

W, H = 840, 220
PHRASES = [
    "Machine Learning Systems",
    "Efficient LLM Serving",
    "SLO-aware Scheduling",
    "KV-cache Management",
    "Anime, Light Novels & Games",
]
STEP = 3.2  # seconds each phrase occupies
FONT = 20
CHAR_W = FONT * 0.6  # monospace advance width
SANS = "'Segoe UI', Ubuntu, 'Helvetica Neue', Helvetica, Arial, sans-serif"
MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, 'Liberation Mono', monospace"

THEMES = {
    "light": dict(bg1="#fff7fb", bg2="#f5f3ff", border="#f3d5e6", text="#1f2328",
                  muted="#6e7781", g1="#ec4899", g2="#8b5cf6", g3="#3b82f6", cell="#e9d5ff"),
    "dark": dict(bg1="#1a1220", bg2="#11131c", border="#2f2638", text="#e6edf3",
                 muted="#8b949e", g1="#f472b6", g2="#a78bfa", g3="#60a5fa", cell="#2d2440"),
}


def typing(t):
    x0, y = 78, 158
    total = STEP * len(PHRASES)
    out = []
    for i, p in enumerate(PHRASES):
        w = len(p) * CHAR_W
        # type in, hold, delete, stay empty until the next cycle
        kt = [0, 1.4 / total, 2.6 / total, 3.0 / total, 1]
        kts = ";".join(f"{k:.4f}" for k in kt)
        vals = f"0;{w:.1f};{w:.1f};0;0"
        begin = f"{i * STEP:.1f}s"
        out.append(f'''
    <clipPath id="c{i}"><rect x="{x0}" y="{y - FONT}" width="0" height="{FONT + 8}">
      <animate attributeName="width" values="{vals}" keyTimes="{kts}" dur="{total}s" begin="{begin}" repeatCount="indefinite" calcMode="spline"
        keySplines="0.4 0 0.6 1;0 0 1 1;0.4 0 0.6 1;0 0 1 1"/>
    </rect></clipPath>
    <text x="{x0}" y="{y}" clip-path="url(#c{i})" class="mono" fill="{t['text']}">{escape(p)}</text>
    <rect x="{x0 + 2}" y="{y - FONT + 3}" width="2.5" height="{FONT + 2}" fill="{t['g1']}" class="cursor" opacity="0">
      <animate attributeName="x" values="{x0 + 2};{x0 + w + 2:.1f};{x0 + w + 2:.1f};{x0 + 2};{x0 + 2}" keyTimes="{kts}" dur="{total}s" begin="{begin}" repeatCount="indefinite" calcMode="spline"
        keySplines="0.4 0 0.6 1;0 0 1 1;0.4 0 0.6 1;0 0 1 1"/>
      <animate attributeName="opacity" values="1;1;1;0;0" keyTimes="{kts}" dur="{total}s" begin="{begin}" repeatCount="indefinite" calcMode="discrete"/>
    </rect>''')
    return f'<text x="54" y="{y}" class="mono" fill="{t["g1"]}">&gt;</text>' + "".join(out)


def kv_grid(t):
    """A little KV cache: blocks fill up token by token, then get evicted."""
    cols, rows, size, gap = 7, 4, 22, 7
    x0 = W - 56 - cols * size - (cols - 1) * gap
    y0 = 56
    dur, n = 7.0, cols * rows
    colors = [t["g1"], t["g2"], t["g2"], t["g3"]]
    out = []
    for k in range(n):
        r, c = divmod(k, cols)
        on = 0.05 + 0.7 * k / n
        kts = f"0;{on:.3f};{on + 0.02:.3f};0.86;0.93;1"
        out.append(
            f'<rect x="{x0 + c * (size + gap)}" y="{y0 + r * (size + gap)}" width="{size}" height="{size}" rx="5" fill="{t["cell"]}"/>'
            f'<rect x="{x0 + c * (size + gap)}" y="{y0 + r * (size + gap)}" width="{size}" height="{size}" rx="5" fill="{colors[r]}" opacity="0">'
            f'<animate attributeName="opacity" values="0;0;0.95;0.95;0;0" keyTimes="{kts}" dur="{dur}s" repeatCount="indefinite"/></rect>'
        )
    label_y = y0 + rows * (size + gap) + 14
    out.append(f'<text x="{x0}" y="{label_y}" class="mono small" fill="{t["muted"]}">kv_cache.fill()</text>')
    return "\n    ".join(out)


def banner(t):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Hi, I'm Smiling. Machine Learning Systems, LLM inference.">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="{t['bg1']}"/><stop offset="1" stop-color="{t['bg2']}"/>
    </linearGradient>
    <linearGradient id="title" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="{t['g1']}"/><stop offset="0.55" stop-color="{t['g2']}"/><stop offset="1" stop-color="{t['g3']}"/>
    </linearGradient>
    <style>
      .sans {{ font-family: {SANS}; }}
      .mono {{ font-family: {MONO}; font-size: {FONT}px; }}
      .small {{ font-size: 13px; }}
      .cursor {{ animation: blink 1s steps(1) infinite; }}
      @keyframes blink {{ 50% {{ fill-opacity: 0; }} }}
    </style>
  </defs>
  <rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="18" fill="url(#bg)" stroke="{t['border']}"/>
  <text x="54" y="58" class="mono small" fill="{t['muted']}">smiling689 · SJTU · John Class</text>
  <text x="52" y="112" class="sans" font-size="46" font-weight="700" fill="url(#title)">Hi, I'm Smiling</text>
  {typing(t)}
  <rect x="54" y="180" width="64" height="4" rx="2" fill="url(#title)"/>
  {kv_grid(t)}
</svg>
'''


out = Path(__file__).resolve().parent.parent / "profile"
out.mkdir(exist_ok=True)
for name, t in THEMES.items():
    suffix = "" if name == "light" else "-dark"
    (out / f"banner{suffix}.svg").write_text(banner(t))
