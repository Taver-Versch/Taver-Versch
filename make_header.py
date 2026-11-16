"""Builds assets/header-dark.svg and assets/header-light.svg for the profile README.

A terminal that types out who you are, like your portfolio's home page. The font is baked into the
SVG, so it never depends on an outside service. Run it again after you change the lines below:

    python make_header.py
"""
import base64
from pathlib import Path

HERE = Path(__file__).parent
FONTS = HERE / "fonts"       # JetBrains Mono 400 + 700, woff2

PROMPT = "taver@homelab:~$ "
LINES = [  # (command, output) pairs, typed in order
    ("whoami", "Taver Versch"),
    ("cat status.txt", "Software Engineering @ UNL · IT Network Infrastructure @ UNL ITS"),
    ("./now", "studying for the CCNA (Jan 2027) · shipping Break.In · PM on a WebXR lab"),
]

THEMES = {
    "dark": dict(card="#161b22", border="#30363d", bar="#0d1117", text="#e6edf3", muted="#9198a1", prompt="#ff9478"),
    "light": dict(card="#ffffff", border="#d1d9e0", bar="#f6f8fa", text="#1f2328", muted="#59636e", prompt="#c03a1e"),
}

W, CW, LH, FS = 880, 9.0, 26, 15   # svg width, char width at 15px mono (0.6em), line height, font size
CARD_X, CARD_Y, CARD_W = 40, 12, 800
PAD_X, BAR_H = 24, 34
TYPE, PAUSE, CYCLE = 0.07, 0.5, 16.0  # seconds per typed char, pause between steps, full loop


def b64(p):
    return base64.b64encode(p.read_bytes()).decode()


def pct(t):
    return f"{100 * t / CYCLE:.2f}%"


def build(theme, extra=None, label=""):
    """extra: optional (command, fn) typed after LINES; fn(theme, colors, prompt_y, reveal_time) -> (svg, css, last_y)."""
    c = THEMES[theme]
    css, body = [], []
    y = CARD_Y + BAR_H + 30
    t = 0.6
    for i, (cmd, out) in enumerate(LINES + [extra] * bool(extra)):
        # command line: the prompt shows right away, the command types out behind a sliding cover
        px = CARD_X + PAD_X
        cx = px + len(PROMPT) * CW
        n = len(cmd)
        if i:  # each prompt shows up when its turn comes, so there are no empty rows while typing
            css.append(f'.p{i}{{animation:p{i} {CYCLE}s infinite}}'
                       f'@keyframes p{i}{{0%,{pct(t - 0.01)}{{opacity:0}}{pct(t)},97%{{opacity:1}}100%{{opacity:0}}}}')
        body.append(f'<text class="p{i}" x="{px}" y="{y}" fill="{c["prompt"]}">{PROMPT}</text>'
                    f'<text x="{cx}" y="{y}">{cmd}</text>'
                    f'<rect class="k{i}" x="{cx}" y="{y - 17}" width="{n * CW + 2}" height="{LH - 2}" fill="{c["card"]}"/>')
        css.append(f'.k{i}{{transform:translateX({n * CW + 2}px);animation:k{i} {CYCLE}s infinite}}'
                   f'@keyframes k{i}{{0%,{pct(t)}{{transform:translateX(0);animation-timing-function:steps({n},end)}}'
                   f'{pct(t + n * TYPE)},97%{{transform:translateX({n * CW + 2}px)}}100%{{transform:translateX(0)}}}}')
        t += n * TYPE + PAUSE * 0.6
        y += LH
        if callable(out):  # a whole block (the stats) instead of one line of output
            svg, more_css, y = out(theme, c, y - LH, t)
            body.append(f'<g class="o{i}">{svg}</g>')
            css.append(more_css)
        else:
            weight = ' font-weight="700"' if i == 0 else ""
            body.append(f'<text class="o{i}" x="{px}" y="{y}"{weight}>{out.replace("&", "&amp;")}</text>')
        css.append(f'.o{i}{{animation:o{i} {CYCLE}s infinite}}'
                   f'@keyframes o{i}{{0%,{pct(t - 0.01)}{{opacity:0}}{pct(t)},97%{{opacity:1}}100%{{opacity:0}}}}')
        t += PAUSE
        y += LH + 6
    # last prompt with a blinking caret
    px = CARD_X + PAD_X
    body.append(f'<text class="o9" x="{px}" y="{y}" fill="{c["prompt"]}">{PROMPT}</text>'
                f'<rect class="caret" x="{px + len(PROMPT) * CW}" y="{y - 14}" width="9" height="17" fill="{c["prompt"]}"/>')
    css.append(f'.o9{{animation:o9 {CYCLE}s infinite}}@keyframes o9{{0%,{pct(t - 0.01)}{{opacity:0}}{pct(t)},97%{{opacity:1}}100%{{opacity:0}}}}'
               f'.caret{{animation:blink 1s steps(1) infinite}}@keyframes blink{{50%{{opacity:0}}}}')
    card_h = y + 22 - CARD_Y

    h = CARD_Y + card_h + 14
    fonts = "".join(f'@font-face{{font-family:JBM;font-weight:{wt};src:url(data:font/woff2;base64,{b64(FONTS / f"jetbrains-mono-latin-{wt}-normal.woff2")}) format("woff2")}}'
                    for wt in (400, 700))
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{h}" viewBox="0 0 {W} {h}" role="img" aria-label="Terminal: whoami, Taver Versch. Software Engineering at UNL, IT Network Infrastructure at UNL ITS. {label}">
<style>{fonts}
svg{{fill:{c["text"]}}}text{{font-family:JBM,ui-monospace,Menlo,Consolas,monospace;font-size:{FS}px;white-space:pre}}
{"".join(css)}
@media (prefers-reduced-motion:reduce){{*{{animation:none!important}}}}
</style>
<rect x="{CARD_X + .5}" y="{CARD_Y + .5}" width="{CARD_W - 1}" height="{card_h}" rx="10" fill="{c["card"]}" stroke="{c["border"]}"/>
<path d="M{CARD_X + .5} {CARD_Y + BAR_H}V{CARD_Y + 10.5}a10 10 0 0 1 10-10H{CARD_X + CARD_W - 10.5}a10 10 0 0 1 10 10V{CARD_Y + BAR_H}Z" fill="{c["bar"]}" stroke="{c["border"]}"/>
<circle cx="{CARD_X + 22}" cy="{CARD_Y + BAR_H / 2}" r="6" fill="#ff5f57"/><circle cx="{CARD_X + 42}" cy="{CARD_Y + BAR_H / 2}" r="6" fill="#febc2e"/><circle cx="{CARD_X + 62}" cy="{CARD_Y + BAR_H / 2}" r="6" fill="#28c840"/>
<text x="{W / 2}" y="{CARD_Y + BAR_H / 2 + 5}" text-anchor="middle" style="fill:{c["muted"]};font-size:13px">taver — bash</text>
{"".join(body)}
</svg>'''


if __name__ == "__main__":
    (HERE / "assets").mkdir(exist_ok=True)
    for theme in THEMES:
        out = HERE / "assets" / f"header-{theme}.svg"
        out.write_text(build(theme), encoding="utf-8")
        print("wrote", out, out.stat().st_size // 1024, "KB")
