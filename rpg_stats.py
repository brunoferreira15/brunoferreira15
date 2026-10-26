#!/usr/bin/env python3
# Gera assets/registro.svg e assets/minigame.svg no estilo RPG com os dados do GitHub.
import os, json, math, urllib.request, datetime

USER = os.environ.get("GH_USER", "brunoferreira15")
OUT = os.environ.get("OUT_DIR", "assets")
MONO = "Consolas, 'Courier New', monospace"
FONT = " 0000000|0ehjlphe|14c4444e|2eh1248v|3u11e11u|426aiv22|5vgu11he|668guhhe|7v124888|8ehhehhe|9ehhf12c|Aehhvhhh|Buhhuhhu|Cehggghe|Duhhhhhu|Evgguggv|Fvgguggg|Gehgnhhe|Hhhhvhhh|Ie44444e|J72222ic|Khikokih|Lggggggv|Mhrllhhh|Nhhpljhh|Oehhhhhe|Puhhuggg|Qehhhlid|Ruhhukih|Sfgge11u|Tv444444|Uhhhhhhe|Vhhhhha4|Whhhllla|Xhha4ahh|Yhha4444|Zv1248gv"
GLYPH = {g[0]: [int(c, 32) for c in g[1:]] for g in FONT.split("|")}

def tw(s, px): return (len(s) * 6 - 1) * px

def ptext(s, x, y, px, fill="#fff", anchor="start"):
    s = s.upper()
    if anchor == "middle": x -= tw(s, px) / 2
    elif anchor == "end": x -= tw(s, px)
    d = []
    for i, ch in enumerate(s):
        for r, bits in enumerate(GLYPH.get(ch, GLYPH[" "])):
            c = 0
            while c < 5:
                if bits >> (4 - c) & 1:
                    a = c
                    while c < 5 and bits >> (4 - c) & 1: c += 1
                    d.append(f"M{x+(i*6+a)*px:g} {y+r*px:g}h{(c-a)*px:g}v{px:g}h-{(c-a)*px:g}z")
                else: c += 1
    return f'<path fill="{fill}" d="{"".join(d)}"/>'

def svg(w, h, body, css=""):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h:g}" width="{w}" height="{h:g}" shape-rendering="crispEdges">'
            f'<style>{css}</style><rect width="{w}" height="{h:g}" fill="#000"/>{body}</svg>')

def header(title):
    lx = 44 + tw(title, 2)
    return (f'<rect x="8" y="7" width="8" height="8" fill="#fff" transform="rotate(45 12 11)"/>{ptext(title, 30, 4, 2)}'
            f'<rect x="{lx}" y="9" width="{796-lx}" height="2" fill="#fff"/><rect x="{lx}" y="13" width="{796-lx}" height="2" fill="#555"/>')

def window(x, y, w, h):
    return (f'<rect x="{x+1.5:g}" y="{y+1.5:g}" width="{w-3:g}" height="{h-3:g}" fill="#000" stroke="#fff" stroke-width="3"/>'
            f'<rect x="{x+7:g}" y="{y+7:g}" width="{w-14:g}" height="{h-14:g}" fill="none" stroke="#555" stroke-width="1.5"/>')

def txt(x, y, s, fill="#aaa", size=15, anchor="start"):
    return f'<text x="{x:.1f}" y="{y}" text-anchor="{anchor}" fill="{fill}" font-family="{MONO}" font-size="{size}">{s}</text>'

def dash(x1, x2, y):
    return f'<line x1="{x1:.1f}" y1="{y}" x2="{x2:.1f}" y2="{y}" stroke="#333" stroke-width="1.5" stroke-dasharray="3 4"/>'

QUERY = """query($login:String!){ user(login:$login){
  contributionsCollection{ totalCommitContributions totalPullRequestContributions totalIssueContributions
    contributionCalendar{ weeks{ contributionDays{ date contributionCount contributionLevel } } } }
  repositories(first:100, ownerAffiliations:OWNER, isFork:false){ nodes{ stargazerCount
    languages(first:10, orderBy:{field:SIZE, direction:DESC}){ edges{ size node{ name } } } } }
  repositoriesContributedTo(first:100, includeUserRepositories:false, contributionTypes:[COMMIT, PULL_REQUEST, REPOSITORY]){ nodes{
    languages(first:10, orderBy:{field:SIZE, direction:DESC}){ edges{ size node{ name } } } } }
}}"""

def fetch():
    if os.environ.get("MOCK_FILE"): return json.load(open(os.environ["MOCK_FILE"], encoding="utf-8"))
    req = urllib.request.Request("https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": USER}}).encode(),
        headers={"Authorization": "bearer " + os.environ["GITHUB_TOKEN"], "Content-Type": "application/json", "User-Agent": "rpg"})
    d = json.load(urllib.request.urlopen(req))
    if "errors" in d: raise SystemExit(json.dumps(d["errors"]))
    return d["data"]["user"]

def registro(u):
    cc = u["contributionsCollection"]
    stars = sum(r["stargazerCount"] for r in u["repositories"]["nodes"])
    langs = {}
    for g in ("repositories", "repositoriesContributedTo"):
        for r in u[g]["nodes"]:
            for e in r["languages"]["edges"]:
                langs[e["node"]["name"]] = langs.get(e["node"]["name"], 0) + e["size"]
    total = sum(langs.values()) or 1
    top = sorted(langs.items(), key=lambda t: -t[1])[:4]
    days = sorted((d for w in cc["contributionCalendar"]["weeks"] for d in w["contributionDays"]), key=lambda d: d["date"])
    cur, i = 0, len(days) - 1
    if i >= 0 and days[i]["contributionCount"] == 0: i -= 1
    while i >= 0 and days[i]["contributionCount"] > 0: cur += 1; i -= 1
    best = run = 0
    for d in days:
        run = run + 1 if d["contributionCount"] > 0 else 0
        best = max(best, run)

    W = (800 - 24) / 3
    xs = [0, W + 12, 2 * W + 24]
    b = header("REGISTRO DE AVENTURA") + "".join(window(x, 30, W, 196) for x in xs)
    x = xs[0]
    b += ptext("STATUS", x + 22, 52, 2)
    rows = [("Commits", cc["totalCommitContributions"]), ("Pull requests", cc["totalPullRequestContributions"]),
            ("Issues", cc["totalIssueContributions"]), ("Estrelas", stars)]
    for k, (lab, v) in enumerate(rows):
        y = 88 + k * 32
        b += txt(x + 22, y + 11, lab) + ptext(str(v), x + W - 22, y, 2, "#fff", "end")
        if k < 3: b += dash(x + 22, x + W - 22, y + 21)
    x = xs[1]
    b += ptext("MAGIAS", x + 22, 52, 2)
    tones = ["#ffffff", "#aaaaaa", "#666666", "#3a3a3a"]
    bx, bw, acc = x + 22, W - 44, 0
    for k, (name, size) in enumerate(top):
        seg = bw * size / total if k < len(top) - 1 else bw - acc
        b += f'<rect x="{bx+acc:.1f}" y="84" width="{max(seg,0):.1f}" height="12" fill="{tones[k]}"/>'
        acc += seg
        y = 118 + k * 24
        b += f'<rect x="{bx:.1f}" y="{y}" width="10" height="10" fill="{tones[k]}" stroke="#555" stroke-width="1"/>'
        b += txt(bx + 18, y + 10, name, "#ddd", 14) + txt(x + W - 22, y + 10, f"{size/total*100:.1f}%".replace(".", ","), "#aaa", 14, "end")
    b += f'<rect x="{bx:.1f}" y="84" width="{bw:.1f}" height="12" fill="none" stroke="#555" stroke-width="1"/>'
    x = xs[2]
    b += ptext("COMBO", x + 22, 52, 2) + ptext(str(cur), x + W / 2, 86, 6, "#fff", "middle")
    b += txt(x + W / 2, 148, "dia seguido" if cur == 1 else "dias seguidos", "#aaa", 15, "middle")
    b += dash(x + 22, x + W - 22, 166) + txt(x + 22, 192, "Recorde", "#aaa", 14)
    b += ptext(f"{best} " + ("DIA" if best == 1 else "DIAS"), x + W - 22, 182, 1.6, "#fff", "end")
    return svg(800, 226, b)

def minigame(u):
    LEVEL = {"NONE": 0, "FIRST_QUARTILE": 1, "SECOND_QUARTILE": 2, "THIRD_QUARTILE": 3, "FOURTH_QUARTILE": 4}
    SH = ["#161616", "#3a3a3a", "#666666", "#999999", "#dddddd"]
    weeks = u["contributionsCollection"]["contributionCalendar"]["weeks"]
    W = len(weeks)
    grid = [[0] * 7 for _ in range(W)]
    for c, w in enumerate(weeks):
        for d in w["contributionDays"]:
            grid[c][datetime.date.fromisoformat(d["date"]).isoweekday() % 7] = LEVEL.get(d["contributionLevel"], 0)
    p = 752 / W
    cell = p * 0.72
    gx, gy = 24, 54
    path = [(c, r) for c in range(W) for r in (range(7) if c % 2 == 0 else range(6, -1, -1))]
    N, DT = len(path), 0.12
    P = N * DT
    pct = lambda k: f"{k / N * 100:.3f}%"
    H = 30 + 24 + 7 * p + 44
    css, b = [], header("MINIGAME") + window(0, 30, 800, H - 30)
    sq = lambda c, r, f, cls="": f'<rect{cls} x="{gx+c*p+(p-cell)/2:.1f}" y="{gy+r*p+(p-cell)/2:.1f}" width="{cell:.1f}" height="{cell:.1f}" fill="{f}"/>'
    b += "".join(sq(c, r, SH[0]) for c in range(W) for r in range(7))
    eat = []
    for k, (c, r) in enumerate(path):
        if grid[c][r]:
            eat.append(k)
            css.append(f"@keyframes e{k}{{0%{{opacity:1}}{pct(k)}{{opacity:0}}100%{{opacity:0}}}}.e{k}{{animation:e{k} {P:.2f}s steps(1,end) infinite}}")
            b += sq(c, r, SH[grid[c][r]], f' class="e{k}"')
    pm, gh = [], []
    for k, (c, r) in enumerate(path + [path[-1]]):
        x, y = gx + c * p + p / 2, gy + r * p + p / 2
        nr = path[(k + 1) % N][1] if k < N else r
        ang = 90 if nr > r else (-90 if nr < r else 0)
        at = pct(k) if k < N else "100%"
        pm.append(f"{at}{{transform:translate({x:.1f}px,{y:.1f}px) rotate({ang}deg)}}")
        gh.append(f"{at}{{transform:translate({x:.1f}px,{y:.1f}px)}}")
    css += ["@keyframes pm{" + "".join(pm) + "}", "@keyframes gh{" + "".join(gh) + "}",
            f".pm{{animation:pm {P:.2f}s steps(1,end) infinite}}",
            f".g1{{animation:gh {P:.2f}s steps(1,end) -{(N-16)*DT:.2f}s infinite}}",
            f".g2{{animation:gh {P:.2f}s steps(1,end) -{(N-28)*DT:.2f}s infinite}}",
            "@keyframes mo{50%{opacity:0}}.mo{animation:mo .24s steps(1) infinite}"]
    rr = p * 0.45
    s = rr * 0.95
    for cls, col in (("g2", "#777777"), ("g1", "#bbbbbb")):
        b += (f'<g class="{cls}"><path fill="{col}" d="M{-s:.1f} 0A{s:.1f} {s:.1f} 0 0 1 {s:.1f} 0L{s:.1f} {s:.1f}L{-s:.1f} {s:.1f}Z"/>'
              f'<rect x="{-s*.55:.1f}" y="{-s*.35:.1f}" width="{s*.35:.1f}" height="{s*.35:.1f}" fill="#000"/>'
              f'<rect x="{s*.2:.1f}" y="{-s*.35:.1f}" width="{s*.35:.1f}" height="{s*.35:.1f}" fill="#000"/></g>')
    cx, cy = rr * math.cos(0.05 * math.pi), rr * math.sin(0.05 * math.pi)
    ox, oy = rr * math.cos(0.25 * math.pi), rr * math.sin(0.25 * math.pi)
    b += (f'<g class="pm"><path fill="#fff" d="M0 0L{cx:.2f} {-cy:.2f}A{rr:.2f} {rr:.2f} 0 1 0 {cx:.2f} {cy:.2f}Z"/>'
          f'<path class="mo" fill="#000" d="M0 0L{ox:.2f} {-oy:.2f}L{rr*1.05:.2f} 0L{ox:.2f} {oy:.2f}Z"/></g>')
    ly = gy + 7 * p + 14
    b += ptext("SCORE", 30, ly, 1.6) + ptext("1 UP", 770, ly, 1.6, "#fff", "end")
    sx = 30 + tw("SCORE ", 1.6)
    bounds = [0] + eat + [N]
    for n in range(len(eat) + 1):
        a, z = bounds[n], bounds[n + 1]
        css.append(f"@keyframes s{n}{{0%{{opacity:{1 if n == 0 else 0}}}{pct(a)}{{opacity:1}}{pct(z)}{{opacity:0}}100%{{opacity:0}}}}"
                   f".s{n}{{animation:s{n} {P:.2f}s steps(1,end) infinite}}")
        b += f'<g class="s{n}">{ptext(str(n), sx, ly, 1.6)}</g>'
    return svg(800, round(H), b, "".join(css))

if __name__ == "__main__":
    u = fetch()
    os.makedirs(OUT, exist_ok=True)
    for name, fn in (("registro.svg", registro), ("minigame.svg", minigame)):
        open(os.path.join(OUT, name), "w", encoding="utf-8").write(fn(u))
        print("ok", name)
