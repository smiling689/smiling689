"""Generate the animated profile banner (light & dark) into profile/."""

from html import escape
from pathlib import Path

W, H = 840, 160
PHRASES = [
    "Machine Learning Systems",
    "LLM Inference & Serving",
    "Curious about Kernels & Training",
    "Anime, Light Novels & Games",
]
STEP = 3.2  # seconds each phrase occupies
FONT = 14
CHAR_W = FONT * 0.6  # monospace advance width
SANS = "'Segoe UI', Ubuntu, 'Helvetica Neue', Helvetica, Arial, sans-serif"
MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, 'Liberation Mono', monospace"

THEMES = {
    "light": dict(paper="#fbf9f6", ink="#1d1b26", muted="#8a8597", grid="#e9e4ee", line="#d9d3e2",
                  accent="#d9467a", c2="#6d5df5", grain=0.07),
    "dark": dict(paper="#13121a", ink="#ecebf3", muted="#8d89a0", grid="#211f2c", line="#34304a",
                 accent="#f06ba0", c2="#9b8cff", grain=0.09),
}


def typing(t, x0, y):
    total = STEP * len(PHRASES)
    kt = ";".join(f"{k:.4f}" for k in (0, 1.4 / total, 2.6 / total, 3.0 / total, 1))
    spline = 'calcMode="spline" keySplines="0.4 0 0.6 1;0 0 1 1;0.4 0 0.6 1;0 0 1 1"'
    out = []
    for i, p in enumerate(PHRASES):
        w = len(p) * CHAR_W
        begin = f"{i * STEP:.1f}s"
        timing = f'keyTimes="{kt}" dur="{total}s" begin="{begin}" repeatCount="indefinite"'
        out.append(f'''
  <clipPath id="c{i}"><rect x="{x0}" y="{y - FONT}" width="0" height="{FONT + 6}">
    <animate attributeName="width" values="0;{w:.1f};{w:.1f};0;0" {timing} {spline}/>
  </rect></clipPath>
  <text x="{x0}" y="{y}" clip-path="url(#c{i})" class="mono" fill="{t['ink']}">{escape(p)}</text>
  <g class="cursor"><rect x="{x0 + 1}" y="{y - FONT + 2}" width="7" height="{FONT + 1}" fill="url(#hatch)" stroke="{t['accent']}" stroke-width="0.8" opacity="0">
    <animate attributeName="x" values="{x0 + 1};{x0 + w + 2:.1f};{x0 + w + 2:.1f};{x0 + 1};{x0 + 1}" {timing} {spline}/>
    <animate attributeName="opacity" values="1;1;1;0;0" {timing} calcMode="discrete"/>
  </rect></g>''')
    return "".join(out)


def terminal(t):
    x, y, w, h = 44, 104, 340, 30
    return f'''
  <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="2" fill="{t['paper']}" stroke="{t['line']}"/>
  <rect x="{x}" y="{y}" width="22" height="{h}" fill="url(#hatch)" stroke="{t['line']}"/>
  <text x="{x + 32}" y="{y + 20}" class="mono" fill="{t['accent']}">$</text>''' + typing(t, x + 48, y + 20)


def diagram(t):
    """Isometric line-art of a transformer stack; the forward pass lights up layer by layer."""
    cx, top, s, gap, depth, layers = 676, 26, 62, 10, 4, 5
    hx, hy = 0.866 * s, 0.5 * s
    dur = 5.0

    def face(y):
        return [(cx, y), (cx + hx, y + hy), (cx, y + s), (cx - hx, y + hy)]

    def pts(ps):
        return " ".join(f"{x:.1f},{y:.1f}" for x, y in ps)

    out = []
    for k in range(layers):  # bottom to top so upper plates occlude lower ones
        y = top + (layers - 1 - k) * gap
        T, R, B, L = face(y)
        sides = [[L, B, (B[0], B[1] + depth), (L[0], L[1] + depth)],
                 [B, R, (R[0], R[1] + depth), (B[0], B[1] + depth)]]
        for side in sides:
            out.append(f'<polygon points="{pts(side)}" fill="url(#hatch)" stroke="{t["ink"]}" stroke-width="0.8"/>')
        out.append(f'<polygon points="{pts([T, R, B, L])}" fill="{t["paper"]}" stroke="{t["ink"]}" stroke-width="0.8"/>')
        on = 0.05 + 0.1 * k
        out.append(
            f'<polygon points="{pts([T, R, B, L])}" fill="none" stroke="{t["accent"]}" stroke-width="1.6" opacity="0">'
            f'<animate attributeName="opacity" values="0;0;1;0;0" keyTimes="0;{on:.2f};{on + 0.06:.2f};{on + 0.2:.2f};1" dur="{dur}s" repeatCount="indefinite"/></polygon>'
        )

    # top plate: a causal attention mask, filled row by row
    T = (cx, top)
    u, v = (hx / 4, hy / 4), (-hx / 4, hy / 4)

    def cell(i, j):
        o = (T[0] + i * u[0] + j * v[0], T[1] + i * u[1] + j * v[1])
        return [o, (o[0] + u[0], o[1] + u[1]), (o[0] + u[0] + v[0], o[1] + u[1] + v[1]), (o[0] + v[0], o[1] + v[1])]

    for n in range(1, 4):
        a, b = (T[0] + n * u[0], T[1] + n * u[1]), (T[0] + n * u[0] + 4 * v[0], T[1] + n * u[1] + 4 * v[1])
        c, d = (T[0] + n * v[0], T[1] + n * v[1]), (T[0] + n * v[0] + 4 * u[0], T[1] + n * v[1] + 4 * u[1])
        out.append(f'<path d="M {a[0]:.1f} {a[1]:.1f} L {b[0]:.1f} {b[1]:.1f} M {c[0]:.1f} {c[1]:.1f} L {d[0]:.1f} {d[1]:.1f}" stroke="{t["line"]}" stroke-width="0.8"/>')
    order = [(q, k) for q in range(4) for k in range(q + 1)]
    for idx, (q, k) in enumerate(order):
        on = 0.55 + 0.035 * idx
        out.append(
            f'<polygon points="{pts(cell(k, q))}" fill="url(#hatch)" stroke="{t["accent"]}" stroke-width="0.6" opacity="0">'
            f'<animate attributeName="opacity" values="0;0;1;1;0;0" keyTimes="0;{on:.3f};{on + 0.01:.3f};0.93;0.97;1" dur="{dur}s" repeatCount="indefinite"/></polygon>'
        )

    # dimension line for the layer count, leader for the attention plate
    dx = cx - hx - 16
    y0, y1 = top + hy, top + (layers - 1) * gap + hy + depth
    out.append(f'<path d="M {dx:.1f} {y0:.1f} V {y1:.1f} M {dx - 4:.1f} {y0:.1f} H {dx + 4:.1f} M {dx - 4:.1f} {y1:.1f} H {dx + 4:.1f}" stroke="{t["muted"]}" stroke-width="0.8"/>')
    out.append(f'<text x="{dx - 8:.1f}" y="{(y0 + y1) / 2 + 4:.1f}" class="mono xs" fill="{t["muted"]}" text-anchor="end">×L</text>')
    lx, ly = cx + hx * 0.75, top + hy * 0.75
    out.append(f'<path d="M {lx:.1f} {ly:.1f} L {lx + 16:.1f} {top + 6} H {lx + 30:.1f}" stroke="{t["muted"]}" stroke-width="0.8" fill="none"/>')
    out.append(f'<circle cx="{lx:.1f}" cy="{ly:.1f}" r="1.6" fill="{t["muted"]}"/>')
    out.append(f'<text x="{lx + 34:.1f}" y="{top + 10}" class="mono xs" fill="{t["muted"]}">attn</text>')
    out.append(f'<text x="{W - 44}" y="{H - 14}" class="mono xxs" fill="{t["muted"]}" text-anchor="end">fig.1 — forward pass</text>')
    return "\n  ".join(out)


def corners(t):
    m, s = 10, 10
    out = []
    for cx, sx in ((m, 1), (W - m, -1)):
        for cy, sy in ((m, 1), (H - m, -1)):
            out.append(f'<path d="M {cx} {cy + sy * s} V {cy} H {cx + sx * s}" stroke="{t["accent"]}" stroke-width="1.2" fill="none"/>')
    return "\n  ".join(out)


def banner(t):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Hi, I'm Smiling. Machine Learning Systems, LLM inference.">
  <defs>
    <pattern id="minor" width="8" height="8" patternUnits="userSpaceOnUse"><path d="M 8 0 H 0 V 8" fill="none" stroke="{t['grid']}" stroke-width="0.5"/></pattern>
    <pattern id="major" width="40" height="40" patternUnits="userSpaceOnUse"><rect width="40" height="40" fill="url(#minor)"/><path d="M 40 0 H 0 V 40" fill="none" stroke="{t['grid']}" stroke-width="1"/></pattern>
    <pattern id="hatch" width="4" height="4" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><line x1="0" y1="0" x2="0" y2="4" stroke="{t['accent']}" stroke-width="1"/></pattern>
    <linearGradient id="fade" x1="0" y1="0" x2="1" y2="0"><stop offset="0.3" stop-color="#fff" stop-opacity="0.15"/><stop offset="0.6" stop-color="#fff" stop-opacity="1"/></linearGradient>
    <mask id="gridmask"><rect width="{W}" height="{H}" fill="url(#fade)"/></mask>
    <filter id="grain" x="0" y="0" width="100%" height="100%">
      <feTurbulence type="fractalNoise" baseFrequency="0.85" numOctaves="2" stitchTiles="stitch"/>
      <feColorMatrix type="saturate" values="0"/>
    </filter>
    <style>
      .sans {{ font-family: {SANS}; }}
      .mono {{ font-family: {MONO}; font-size: {FONT}px; }}
      .xs {{ font-size: 11px; }}
      .xxs {{ font-size: 10px; letter-spacing: 0.5px; }}
      .cursor {{ animation: blink 1s steps(1) infinite; }}
      @keyframes blink {{ 50% {{ opacity: 0; }} }}
    </style>
  </defs>
  <rect width="{W}" height="{H}" fill="{t['paper']}"/>
  <rect width="{W}" height="{H}" fill="url(#major)" mask="url(#gridmask)"/>
  <rect width="{W}" height="{H}" filter="url(#grain)" opacity="{t['grain']}"/>
  <rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" fill="none" stroke="{t['line']}"/>
  {corners(t)}
  <path d="M 44 36 H 60" stroke="{t['accent']}" stroke-width="1.5"/>
  <text x="68" y="40" class="mono xs" fill="{t['muted']}">smiling689 · SJTU · John Class</text>
  <text x="42" y="84" class="sans" font-size="32" font-weight="700" fill="{t['ink']}">Hi, I'm <tspan fill="{t['accent']}">Smiling</tspan></text>
  {terminal(t)}
  {diagram(t)}
</svg>
'''


out = Path(__file__).resolve().parent.parent / "profile"
out.mkdir(exist_ok=True)
for name, t in THEMES.items():
    suffix = "" if name == "light" else "-dark"
    (out / f"banner{suffix}.svg").write_text(banner(t))
