"""Builds dist/profile-dark.svg and dist/profile-light.svg: the header terminal from make_header.py with a
`gh stats` command at the end that shows your numbers, top languages and contribution heatmap.
The workflow runs this on a schedule; to try it locally:

    GITHUB_TOKEN=$(gh auth token) python make_stats.py
"""
import json
import os
import sys
import urllib.request
from datetime import date
from pathlib import Path

from make_header import THEMES, CARD_W, CARD_X, PAD_X, build

USER = os.environ.get("GITHUB_USER", "Taver-Versch")
OUT = Path(sys.argv[1] if len(sys.argv) > 1 else "dist")
TOP = 4  # languages shown
LEVELS = ["NONE", "FIRST_QUARTILE", "SECOND_QUARTILE", "THIRD_QUARTILE", "FOURTH_QUARTILE"]
CELLS = {  # coral scale to match the header prompt
    "dark": ["#21262d", "#5c2a1f", "#8f3a26", "#c9503a", "#ff9478"],
    "light": ["#ebedf0", "#ffd9cf", "#ff9478", "#e05a3a", "#c03a1e"],
}
STEP, CELL = 14, 11  # heatmap pitch and square size

# ponytail: first 100 owned repos only; paginate if you ever pass 100
QUERY = """query($login:String!){user(login:$login){
  repositories(ownerAffiliations:OWNER,isFork:false,first:100){nodes{
    languages(first:20){edges{size node{name color}}}}}
  contributionsCollection{totalCommitContributions totalPullRequestContributions totalPullRequestReviewContributions
    contributionCalendar{totalContributions weeks{contributionDays{date contributionCount contributionLevel}}}}}}"""


def fetch():
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": USER}}).encode(),
        headers={"Authorization": f"bearer {os.environ['GITHUB_TOKEN']}", "User-Agent": "profile-stats"},
    )
    data = json.load(urllib.request.urlopen(req))
    if "errors" in data:
        sys.exit(f"GitHub API error: {data['errors']}")
    return data["data"]["user"]


def streaks(days):
    """(current, longest) runs of days with at least one contribution. No contributions yet today doesn't break it."""
    counts = [d["contributionCount"] for d in days if d["date"] <= date.today().isoformat()]
    longest = run = 0
    for n in counts:
        run = run + 1 if n else 0
        longest = max(longest, run)
    if counts and not counts[-1]:
        counts.pop()
    current = 0
    for n in reversed(counts):
        if not n:
            break
        current += 1
    return current, longest


def languages(user):
    """[(name, color, share)] for the top languages by bytes across all repos, plus 'Other' for the rest."""
    sizes, colors = {}, {}
    for repo in user["repositories"]["nodes"]:
        for e in repo["languages"]["edges"]:
            name = e["node"]["name"]
            sizes[name] = sizes.get(name, 0) + e["size"]
            colors[name] = e["node"]["color"] or "#8b949e"
    total = sum(sizes.values()) or 1
    top = sorted(sizes, key=sizes.get, reverse=True)[:TOP]
    out = [(n, colors[n], sizes[n] / total) for n in top]
    rest = 1 - sum(s for *_, s in out)
    return out + ([("Other", None, rest)] if rest > 0.005 else [])


def stats_block(user):
    """Returns (block fn for make_header.build, aria label)."""
    cc = user["contributionsCollection"]
    cal = cc["contributionCalendar"]
    weeks = cal["weeks"]
    cur, best = streaks([d for w in weeks for d in w["contributionDays"]])
    langs = languages(user)

    def block(theme, c, y, t0):
        scale = CELLS[theme]
        px, inner = CARD_X + PAD_X, CARD_W - 2 * PAD_X
        muted = f'class="small" style="fill:{c["muted"]}"'
        body = []

        # big numbers
        y += 40
        stats = [
            (f'{cal["totalContributions"]:,}', "contributions, last year"),
            (f'{cc["totalCommitContributions"]:,}', "commits"),
            (f'{cc["totalPullRequestContributions"] + cc["totalPullRequestReviewContributions"]:,}', "PRs + reviews"),
            (f"{cur} day{'s' * (cur != 1)}", f"streak · best {best}"),
        ]
        for i, (big, label) in enumerate(stats):
            x = px + i * inner / len(stats)
            body.append(f'<text x="{x}" y="{y}" class="big" fill="{c["prompt"]}">{big}</text>'
                        f'<text x="{x}" y="{y + 22}" {muted}>{label}</text>')

        # top languages: one stacked bar, legend underneath
        y += 52
        body.append(f'<text x="{px}" y="{y}" class="small" fill="{c["prompt"]}">top languages, all repos</text>')
        y += 12
        x, bar = px, []
        for name, color, share in langs:
            bar.append(f'<rect class="seg" x="{x:.1f}" y="{y}" width="{share * inner:.1f}" height="10" fill="{color or c["border"]}"/>')
            x += share * inner
        body.append(f'<clipPath id="bar"><rect x="{px}" y="{y}" width="{inner}" height="10" rx="5"/></clipPath>'
                    f'<g clip-path="url(#bar)">{"".join(bar)}</g>')
        y += 30
        for i, (name, color, share) in enumerate(langs):
            x = px + i * inner / len(langs)
            body.append(f'<circle cx="{x + 5}" cy="{y - 4}" r="5" fill="{color or c["border"]}"/>'
                        f'<text x="{x + 16}" y="{y}" class="small">{name} <tspan font-weight="700" fill="{color or c["muted"]}">{share:.0%}</tspan></text>')

        # heatmap: one column per week, months labelled above
        y += 34
        gx = px + (inner - (len(weeks) * STEP - (STEP - CELL))) / 2
        months = [w["contributionDays"][0]["date"][5:7] for w in weeks]
        for i, w in enumerate(weeks):
            if 0 < i < len(weeks) - 2 and months[i] != months[i - 1]:
                body.append(f'<text x="{gx + i * STEP}" y="{y}" {muted}>{date.fromisoformat(w["contributionDays"][0]["date"]):%b}</text>')
            rects = "".join(
                f'<rect x="{gx + i * STEP}" y="{y + 10 + date.fromisoformat(d["date"]).isoweekday() % 7 * STEP}" '
                f'width="{CELL}" height="{CELL}" rx="2" fill="{scale[LEVELS.index(d["contributionLevel"])]}"/>'
                for d in w["contributionDays"]
            )
            body.append(f'<g class="wk" style="animation-delay:{t0 + i * 0.025:.3f}s">{rects}</g>')

        # footer: updated date left, legend right
        y += 10 + 7 * STEP + 22
        today = date.today()
        lx = CARD_X + CARD_W - PAD_X - 5 * STEP - 34
        body.append(f'<text x="{px}" y="{y}" {muted}>updated {today:%b} {today.day}, {today.year}</text>'
                    f'<text x="{lx - 8}" y="{y}" text-anchor="end" {muted}>less</text>'
                    + "".join(f'<rect x="{lx + k * STEP}" y="{y - 10}" width="{CELL}" height="{CELL}" rx="2" fill="{s}"/>'
                              for k, s in enumerate(scale))
                    + f'<text x="{lx + 5 * STEP + 4}" y="{y}" {muted}>more</text>')

        css = (".big{font-size:24px;font-weight:700}.small{font-size:12px}"
               ".wk{animation:in .4s ease-out both}@keyframes in{from{opacity:0;transform:translateY(4px)}}"
               f".seg{{transform-box:fill-box;transform-origin:left;animation:grow .8s ease-out {t0}s both}}"
               "@keyframes grow{from{transform:scaleX(0)}}")
        return "".join(body), css, y

    label = (f'GitHub stats: {cal["totalContributions"]} contributions in the last year, current streak {cur} days, '
             f'longest {best}. Top languages: {", ".join(f"{n} {s:.0%}" for n, _, s in langs)}.')
    return block, label


if __name__ == "__main__":
    days = [{"date": f"2000-01-0{i}", "contributionCount": n} for i, n in enumerate([1, 1, 0, 1, 1, 1, 0], 1)]
    assert streaks(days) == (3, 3), streaks(days)
    block, label = stats_block(fetch())
    OUT.mkdir(exist_ok=True)
    for theme in THEMES:
        p = OUT / f"profile-{theme}.svg"
        p.write_text(build(theme, ("gh stats", block), label), encoding="utf-8")
        print("wrote", p)
