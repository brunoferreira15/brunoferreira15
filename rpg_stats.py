#!/usr/bin/env python3
# Gera assets/registro.svg e assets/minigame.svg (Caça aos bugs) no estilo RPG com os dados do GitHub.
import os, json, math, urllib.request, datetime

USER = os.environ.get("GH_USER", "brunoferreira15")
OUT = os.environ.get("OUT_DIR", "assets")
MONO = "Consolas, 'Courier New', monospace"
FONT = " 0000000|0ehjlphe|14c4444e|2eh1248v|3u11e11u|426aiv22|5vgu11he|668guhhe|7v124888|8ehhehhe|9ehhf12c|Aehhvhhh|Buhhuhhu|Cehggghe|Duhhhhhu|Evgguggv|Fvgguggg|Gehgnhhe|Hhhhvhhh|Ie44444e|J72222ic|Khikokih|Lggggggv|Mhrllhhh|Nhhpljhh|Oehhhhhe|Puhhuggg|Qehhhlid|Ruhhukih|Sfgge11u|Tv444444|Uhhhhhhe|Vhhhhha4|Whhhllla|Xhha4ahh|Yhha4444|Zv1248gv|:0440440|;0440448|!4444404|{688g886|}c22122c|·0004000|★4eveah0|☆4ahaah0"
GLYPH = {g[0]: [int(c, 32) for c in g[1:]] for g in FONT.split("|")}
ACCENT = {"Á": ("A", [2, 4]), "É": ("E", [2, 4]), "Í": ("I", [2, 4]), "Ó": ("O", [2, 4]), "Ú": ("U", [2, 4]),
          "Ã": ("A", [13, 22]), "Õ": ("O", [13, 22]), "Â": ("A", [4, 10]), "Ê": ("E", [4, 10]), "Ô": ("O", [4, 10]), "Ç": ("C", None)}

def tw(s, px): return (len(s) * 6 - 1) * px

def ptext(s, x, y, px, fill="#fff", anchor="start", cls=""):
    s = s.upper()
    if anchor == "middle": x -= tw(s, px) / 2
    elif anchor == "end": x -= tw(s, px)
    d = []
    def row(i, r, bits):
        c = 0
        while c < 5:
            if bits >> (4 - c) & 1:
                a = c
                while c < 5 and bits >> (4 - c) & 1: c += 1
                d.append(f"M{x+(i*6+a)*px:g} {y+r*px:g}h{(c-a)*px:g}v{px:g}h-{(c-a)*px:g}z")
            else: c += 1
    for i, ch in enumerate(s):
        base, acc = ch, None
        if ch in ACCENT: base, acc = ACCENT[ch]
        for r, bits in enumerate(GLYPH.get(base, GLYPH[" "])): row(i, r, bits)
        if acc: row(i, -3, acc[0]); row(i, -2, acc[1])
        if ch == "Ç": row(i, 7, 4); row(i, 8, 12)
    c = f' class="{cls}"' if cls else ""
    return f'<path{c} fill="{fill}" d="{"".join(d)}"/>'

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
    import random
    LEVEL = {"NONE": 0, "FIRST_QUARTILE": 1, "SECOND_QUARTILE": 2, "THIRD_QUARTILE": 3, "FOURTH_QUARTILE": 4}
    SH = ["#111111", "#3a3a3a", "#666666", "#999999", "#dddddd"]
    weeks = u["contributionsCollection"]["contributionCalendar"]["weeks"]
    COLS, ROWS, cs, TOP = len(weeks), 7, 13, 34
    GW, GH = COLS * cs + 12, TOP + ROWS * cs + 12
    grid = [[0] * ROWS for _ in range(COLS)]
    months = []
    for c, w in enumerate(weeks):
        for d in w["contributionDays"]:
            dt = datetime.date.fromisoformat(d["date"])
            grid[c][dt.isoweekday() % 7] = LEVEL.get(d["contributionLevel"], 0)
            if dt.day == 1: months.append((c, "JAN FEV MAR ABR MAI JUN JUL AGO SET OUT NOV DEZ".split()[dt.month - 1]))
    today = weeks[-1]["contributionDays"][-1]["date"]
    rnd = random.Random(today)
    cx = lambda c: 6 + c * cs + cs / 2
    cy = lambda r: TOP + r * cs + cs / 2

    # ------------------------------------------------------------ simulação
    TYPES = {"syntax": ("SYNTAX", "FIX: SYNTAXERROR CORRIGIDO"), "e404": ("404", "FIX: PÁGINA 404 ENCONTRADA"),
             "loop": ("LOOP", "FIX: LOOP INFINITO QUEBRADO"), "nul": ("NULL", "FIX: NULLPOINTER TRATADO")}
    KEYS = list(TYPES)
    g = [col[:] for col in grid]
    crystals = {}                       # (c,r) -> frame coletado
    mage_kf = []                        # (f, x, y, op)
    bugs, alive = [], []
    bolts, bursts, rings, msgs, flashes, shots, shields = [], [], [], [], [], [], []
    mana_ev, kill_ev, storm_ev = [(0, 0)], [(0, 0)], [(0, 0)]
    mana = kills = 0
    st = {"t": 0, "last_msg": -99, "charge": 0, "storm": 0}
    mage = {"c": 0, "r": 3, "x": cx(0), "y": cy(3), "tx": None, "wait": 0}
    mage_kf.append((0, mage["x"], mage["y"], 1))

    def say(text, x, y, big=False):
        if not big and st["t"] - st["last_msg"] < 10: return
        st["last_msg"] = st["t"]
        if big:
            near = [m for m in msgs if m[4] and st["t"] - m[0] < 36 and abs(m[3] - y) < 30]
            y += 15 * len(near)
        msgs.append((st["t"], text, x, max(14, y), big))

    def empty_cell():
        for _ in range(80):
            c, r = rnd.randrange(COLS), rnd.randrange(ROWS)
            if not g[c][r] and abs(c - mage["c"]) > 4: return c, r
        return COLS - 1, 3

    def spawn(kind=None, x=0, y=0, size=1.0, ry=None):
        b = {"id": len(bugs), "type": kind or rnd.choice(KEYS), "x": x, "y": y, "ry": y if ry is None else ry, "size": size,
             "vx": -(0.35 + rnd.random() * 0.3), "born": st["t"], "a": rnd.random() * 6.28, "ccx": x, "ccy": y,
             "vis": True, "child": size < 1, "kf": [(st["t"], x, y)], "vis_ev": [(st["t"], 1)], "death": None}
        bugs.append(b); alive.append(b); return b

    def spawn_at():
        c, r = empty_cell(); b = spawn(None, cx(c), cy(r)); rings.append((st["t"], b["x"], b["y"]))

    def bolt(a, b, w=2):
        pts = [a] + [(a[0] + (b[0] - a[0]) * i / 6 + rnd.uniform(-4, 4), a[1] + (b[1] - a[1]) * i / 6 + rnd.uniform(-4, 4)) for i in range(1, 6)] + [b]
        bolts.append((st["t"], pts, w))

    def kill(b, why=""):
        nonlocal kills
        if b not in alive: return
        alive.remove(b); b["death"] = st["t"]; b["kf"].append((st["t"], b["x"], b["y"]))
        bursts.append((st["t"], b["x"], b["y"], "#bbbbbb", 8, 16 * b["size"]))
        kills += 1; kill_ev.append((st["t"], kills))
        if b["type"] == "syntax" and not b["child"] and why != "storm":
            spawn("syntax", b["x"], b["y"], 0.7, max(cy(0), b["y"] - cs)); spawn("syntax", b["x"], b["y"], 0.7, min(cy(6), b["y"] + cs))
            say("SYNTAXERROR SE DIVIDIU!", b["x"], b["y"] - 10)
        elif why != "storm":
            say("FIX: ; ADICIONADO" if b["child"] else TYPES[b["type"]][1], b["x"], b["y"] - 10)

    def next_target():
        best, bd = None, 1e18
        for c in range(COLS):
            for r in range(ROWS):
                if g[c][r]:
                    d = (c - mage["c"]) ** 2 * (40 if c < mage["c"] else 1) + (r - mage["r"]) ** 2 * 2
                    if d < bd: bd, best = d, (c, r)
        return best

    def orb(): return (mage["x"] + 5, mage["y"] - 13)

    for _ in range(8): spawn_at()
    phase, boss, clear_t, spawn_t, cd = "play", None, 0, 0, 10
    hop = None
    MAXF = 3000
    while st["t"] < MAXF:
        st["t"] += 1; t = st["t"]
        if phase == "play":
            if mage["tx"] is None:
                if mage["wait"] > 0: mage["wait"] -= 1
                else:
                    n = next_target() if t < MAXF - 400 else None
                    if not n:
                        phase = "boss"
                        for b in alive[:]:
                            bursts.append((t, b["x"], b["y"], "#777777", 6, 12)); b["death"] = t; b["kf"].append((t, b["x"], b["y"]))
                        alive.clear()
                        boss = {"x": GW + 30, "y": cy(3), "hp": 14, "start": t, "arrive": None, "hits": [], "death": None}
                        say("UM BUG LENDÁRIO APARECEU!", GW / 2, TOP + 16, True)
                    else:
                        far = abs(n[0] - mage["c"]) > 3
                        hop = {"from": (mage["x"], mage["y"]), "to": (cx(n[0]), cy(n[1])), "cell": n, "k": 0, "tp": far, "start": t}
                        mage["tx"] = hop["to"][0]
                        if far:
                            rings.append((t, mage["x"], mage["y"])); bursts.append((t, mage["x"], mage["y"], "#ffffff", 8, 14))
                            mage_kf.append((t, mage["x"], mage["y"], 1)); mage_kf.append((t + 1, mage["x"], mage["y"], 0)); mage_kf.append((t + 2, hop["to"][0], hop["to"][1], 0))
                        else:
                            mage_kf.append((t, mage["x"], mage["y"], 1))
                            mx, my = (hop["from"][0] + hop["to"][0]) / 2, (hop["from"][1] + hop["to"][1]) / 2 - 8
                            mage_kf.append((t + 3.5, mx, my, 1))
            else:
                hop["k"] += 1
                D = 8 if hop["tp"] else 7
                if hop["k"] >= D:
                    mage["x"], mage["y"] = hop["to"]
                    mage_kf.append((t, mage["x"], mage["y"], 1))
                    if hop["tp"]: rings.append((t, mage["x"], mage["y"]))
                    c, r = hop["cell"]; v = g[c][r]
                    if v:
                        g[c][r] = 0; crystals[(c, r)] = t; mana += v; mana_ev.append((t, mana))
                        bursts.append((t, mage["x"], mage["y"], SH[v], 8, 14))
                        if v == 4 and not st["charge"] and st.get("storms", 0) < 2:
                            st["charge"] = 1; storm_ev.append((t, 1)); say("TEMPESTADE CARREGADA ★", mage["x"], mage["y"] - 20, True)
                    mage["c"], mage["r"], mage["tx"], mage["wait"] = c, r, None, 2
            if phase == "play" and st["charge"] and len(alive) >= 8:
                st["charge"] = 0; st["storms"] = st.get("storms", 0) + 1; storm_ev.append((t, 0)); st["storm"] = 14; st["wave"] = 0; flashes.append(t); say("TEMPESTADE DE RAIOS!", GW / 2, TOP + 16, True)
            spawn_t += 1
            if phase == "play" and spawn_t >= 12 and len(alive) < 14:
                spawn_t = 0; spawn_at()
                if rnd.random() < 0.4 and len(alive) < 14: spawn_at()
        # movimento dos bugs
        for b in alive:
            if b["type"] == "loop":
                b["a"] += 0.12; b["ccx"] -= 0.35; b["x"] = b["ccx"] + math.cos(b["a"]) * 14; b["y"] = b["ccy"] + math.sin(b["a"]) * 9
                if (t - b["born"]) % 3 == 0: b["kf"].append((t, b["x"], b["y"]))
            else:
                b["x"] += b["vx"]; b["y"] += (b["ry"] - b["y"]) * 0.15
                if t - b["born"] in (4, 12): b["kf"].append((t, b["x"], b["y"]))
            if b["type"] == "e404" and (t - b["born"]) % 70 == 69:
                b["kf"].append((t, b["x"], b["y"])); bursts.append((t, b["x"], b["y"], "#666666", 6, 12))
                b["x"] = 90 + rnd.random() * (GW - 120); b["ry"] = b["y"] = cy(rnd.randrange(ROWS))
                b["kf"].append((t + 0.01, b["x"], b["y"])); bursts.append((t, b["x"], b["y"], "#ffffff", 6, 10))
                if rnd.random() < 0.4: say("404: NÃO ENCONTRADO", b["x"], b["y"] - 10)
            if b["type"] == "nul":
                vis = ((t + int(b["born"])) % 44) < 24
                if vis != b["vis"]: b["vis"] = vis; b["vis_ev"].append((t, 1 if vis else 0.15))
            if b["x"] < -10:
                b["kf"].append((t, b["x"], b["y"])); b["x"] = GW + 6; b["ccx"] = GW + 6; b["kf"].append((t + 0.01, b["x"], b["y"]))
        # tempestade
        if st["storm"] > 0:
            st["storm"] -= 1
            if st["storm"] == 10:
                n = len(alive)
                for b in alive[:]: bolt((b["x"] + rnd.uniform(-5, 5), 0), (b["x"], b["y"]), 3); kill(b, "storm")
                if n: say(f"FIX: {n} BUGS CORRIGIDOS DE UMA VEZ" if n > 1 else "FIX: 1 BUG CORRIGIDO", GW / 2, TOP + 30, True)
            if st["storm"] % 4 == 2 and boss and boss["death"] is None:
                boss["hp"] -= 2; boss["hits"].append((t, boss["hp"])); bolt((boss["x"], 0), (boss["x"], boss["y"]), 3)
        cd = max(0, cd - 1)
        if phase == "play" and cd == 0 and not (hop and mage["tx"] is not None and hop["tp"]):
            o = orb()
            vis = [b for b in alive if b["vis"]]
            if vis:
                tg = min(vis, key=lambda b: math.hypot(b["x"] - o[0], b["y"] - o[1]))
                if math.hypot(tg["x"] - o[0], tg["y"] - o[1]) < 110:
                    bolt(o, (tg["x"], tg["y"])); kill(tg); cd = 22
        if phase == "boss" and boss:
            bt = t - boss["start"]
            if boss["x"] > GW - 80: boss["x"] -= 3
            elif boss["arrive"] is None: boss["arrive"] = t
            if bt % 40 == 0 and bt > 0:
                for k in (-1, 0, 1):
                    dx, dy = mage["x"] - boss["x"], mage["y"] - boss["y"]; L = math.hypot(dx, dy) or 1
                    vx, vy = dx / L * 4.5, dy / L * 4.5 + k * 0.6
                    sx, sy, f = boss["x"] - 14, boss["y"], 0
                    while math.hypot(sx - mage["x"], sy - (mage["y"] - 6)) >= 16 and f < 200: sx += vx; sy += vy; f += 1
                    shots.append((t, boss["x"] - 14, boss["y"], sx, sy, t + f)); shields.append(t + f)
            if bt == 60 and st["charge"]:
                st["charge"] = 0; storm_ev.append((t, 0)); st["storm"] = 11; flashes.append(t); say("TEMPESTADE DE RAIOS!", GW / 2, TOP + 16, True)
            if cd == 0 and boss["arrive"] is not None:
                bolt(orb(), (boss["x"] - 8, boss["y"])); boss["hp"] -= 1; boss["hits"].append((t, boss["hp"])); cd = 14
                bursts.append((t, boss["x"] - 10, boss["y"], "#ffffff", 6, 12))
            if boss["hp"] <= 0:
                boss["death"] = t
                for i in range(4): bursts.append((t + i * 3, boss["x"] + rnd.uniform(-15, 15), boss["y"] + rnd.uniform(-10, 10), "#ffffff" if i % 2 else "#999999", 10, 26))
                say("FIX: BUG LENDÁRIO DERROTADO", boss["x"] - 60, boss["y"] - 22, True)
                kills += 1; kill_ev.append((t, kills)); phase = "clear"; clear_t = t
        if phase == "clear" and t - clear_t >= 55: break
    N = st["t"] + 1
    mage_kf.append((N, mage["x"], mage["y"], 1))
    for b in alive: b["kf"].append((N, b["x"], b["y"]))

    # ------------------------------------------------------------ SVG
    DT = 0.06
    P = N * DT
    css = [".o{opacity:0}"]
    pc = lambda f: f"{max(0.0, min(100.0, f / N * 100)):.3f}"
    q = lambda fr: f"{min(99.9, fr / N * 100):.3f}"
    def kf(name, frames, timing="linear"):
        seen, out = set(), []
        for f, decl in frames:
            p = pc(f)
            while p in seen and float(p) < 100: p = f"{float(p) + 0.001:.3f}"
            if p in seen: continue
            seen.add(p); out.append(f"{p}%{{{decl}}}")
        css.append(f"@keyframes {name}{{{''.join(out)}}}.{name}{{animation:{name} {P:.2f}s {timing} infinite}}")
    def shared(name, body_kf, timing="linear"):
        css.append(f"@keyframes {name}{{{body_kf}}}.{name}{{animation:{name} {P:.2f}s {timing} infinite}}")
    dl = lambda f: f' style="animation-delay:{f*DT:.2f}s"'
    # letras reaproveitadas
    used = set()
    def T(s_, x, y, px, fill="#fff", anchor="start", cls="", extra=""):
        s_ = s_.upper()
        if anchor == "middle": x -= tw(s_, px) / 2
        elif anchor == "end": x -= tw(s_, px)
        uses = []
        for i, ch in enumerate(s_):
            if ch == " ": continue
            used.add(ch); uses.append(f'<use href="#g{ord(ch):x}" x="{i*6}"/>')
        c = f' class="{cls}"' if cls else ""
        return f'<g{c}{extra} transform="translate({x:.1f},{y:.1f}) scale({px:g})" fill="{fill}">{"".join(uses)}</g>'
    shared("w6", f"0%{{opacity:1}}{q(6)}%{{opacity:0}}100%{{opacity:0}}", "steps(1,end)")
    shared("w4", f"0%{{opacity:1}}{q(4)}%{{opacity:0}}100%{{opacity:0}}", "steps(1,end)")
    shared("rg", f"0%{{opacity:1;transform:scale(1)}}{q(10)}%{{opacity:0;transform:scale(7)}}100%{{opacity:0;transform:scale(7)}}")
    shared("fl", f"0%{{opacity:.6}}{q(2)}%{{opacity:.3}}{q(6)}%{{opacity:0}}100%{{opacity:0}}")
    for life, nm in ((36, "mb"), (40, "mm")):
        shared(nm, f"0%{{opacity:1;transform:translateY(0)}}{q(life)}%{{opacity:1;transform:translateY(-{life*0.4:.0f}px)}}{float(q(life))+0.001:.3f}%{{opacity:0}}100%{{opacity:0}}")
    radii = sorted({round(R) for *_, R in bursts})
    for R in radii:
        shared(f"p{R}", f"0%{{opacity:1;transform:translateX(0)}}{q(14)}%{{opacity:0;transform:translateX({R}px)}}100%{{opacity:0;transform:translateX({R}px)}}")
    body = []
    for c, m in months: body.append(T(m, 6 + c * cs, TOP - 11, 1, "#555555"))
    cells = "".join(f"M{6+c*cs+1} {TOP+r*cs+1}h{cs-3}v{cs-3}h-{cs-3}z" for c in range(COLS) for r in range(ROWS))
    body.append(f'<path fill="#111" d="{cells}"/>')
    css.append("@keyframes tw{0%,88%{opacity:0}92%{opacity:1}100%{opacity:0}}.tw{animation:tw 4s steps(1,end) infinite}")
    dia = lambda X, Y: f"M{X+cs/2-1:g} {Y+2}L{X+cs-3} {Y+cs/2-1:g}L{X+cs/2-1:g} {Y+cs-4}L{X+2} {Y+cs/2-1:g}Z"
    for (c, r), f in sorted(crystals.items(), key=lambda a: a[1]):
        v = grid[c][r]; X, Y = 6 + c * cs, TOP + r * cs; name = f"c{c}_{r}"
        kf(name, [(0, "opacity:1"), (f, "opacity:1"), (f + 0.01, "opacity:0"), (N - 0.02, "opacity:0"), (N, "opacity:1")], "steps(1,end)")
        body.append(f'<g class="{name}"><path fill="{SH[v]}" d="{dia(X, Y)}"/><rect class="tw" style="animation-delay:-{rnd.random()*4:.1f}s" x="{X+cs/2-2:g}" y="{Y+4}" width="2" height="2" fill="#fff"/></g>')
    for c in range(COLS):
        for r in range(ROWS):
            if grid[c][r] and (c, r) not in crystals:
                body.append(f'<path fill="{SH[grid[c][r]]}" d="{dia(6 + c * cs, TOP + r * cs)}"/>')
    BUG = ["..#....#..", "...#..#...", ".########.", "##.####.##", ".########.", "##########", ".#.#..#.#.", "#........#"]
    bd = "".join(f"M{i-5} {j-4}h1v1h-1z" for j, row in enumerate(BUG) for i, ch in enumerate(row) if ch == "#")
    defs = [f'<path id="bug" d="{bd}"/>']
    def bug_use(s, col):
        return f'<g transform="scale({s:g})"><use href="#bug" fill="{col}"/><rect x="-2" y="-1" width="1" height="1" fill="#000"/><rect x="1" y="-1" width="1" height="1" fill="#000"/></g>'
    css.append("@keyframes bob{50%{transform:translateY(1px)}}.bob{animation:bob .48s steps(1,end) infinite}")
    for b in bugs:
        name = f"b{b['id']}"
        end = b["death"] if b["death"] is not None else N
        k0 = b["kf"][0]
        tr = lambda X, Y: f"transform:translate({X:.0f}px,{Y:.0f}px)"
        fr = [(0, tr(k0[1], k0[2]) + ";opacity:0"), (b["born"] - 0.01, tr(k0[1], k0[2]) + ";opacity:0")]
        for f, X, Y in b["kf"]: fr.append((f, tr(X, Y) + ";opacity:1"))
        lx, ly = b["kf"][-1][1], b["kf"][-1][2]
        if end < N: fr += [(end + 0.01, tr(lx, ly) + ";opacity:0"), (N, tr(lx, ly) + ";opacity:0")]
        kf(name, fr)
        inner = ""
        if len(b["vis_ev"]) > 1:
            kf(name + "v", [(0, "opacity:1")] + [(f, f"opacity:{o}") for f, o in b["vis_ev"]] + [(N, "opacity:1")], "steps(1,end)")
            inner = f' class="{name}v"'
        tag = "{;}" if b["child"] else TYPES[b["type"]][0]
        col = "#888" if b["type"] == "nul" else "#bbb"
        body.append(f'<g class="{name}"><g{inner}><g class="bob">{bug_use(b["size"], col)}</g>{T(tag, 0, round(-4 * b["size"] - 9), 1, "#888", "middle")}</g></g>')
    WZ = [[14,0,6,4,'#fff'],[12,4,10,4,'#fff'],[10,8,14,4,'#fff'],[8,12,18,4,'#fff'],[2,16,30,4,'#fff'],[16,9,3,3,'#000'],[8,20,18,8,'#ddd'],[12,22,3,3,'#000'],[19,22,3,3,'#000'],[6,28,22,24,'#fff'],[10,28,14,12,'#999'],[13,40,8,4,'#999'],[6,44,22,3,'#666'],[8,52,7,4,'#fff'],[19,52,7,4,'#fff'],[28,32,6,4,'#fff'],[34,12,3,44,'#888'],[31,4,9,9,'#fff']]
    byc = {}
    for a_, b_, w, h, f in WZ: byc.setdefault(f, []).append(f"M{a_} {b_}h{w}v{h}h-{w}z")
    wiz = "".join(f'<path fill="{f}" d="{"".join(p)}"/>' for f, p in byc.items())
    css.append("@keyframes orb{50%{opacity:0}}.orb{animation:orb .6s steps(1,end) infinite}")
    kf("mg", [(f, f"transform:translate({X:.0f}px,{Y:.0f}px);opacity:{o}") for f, X, Y, o in mage_kf])
    body.append(f'<g class="mg"><g transform="translate(-6,{-56*0.3+cs*0.45:.2f}) scale(0.3)">{wiz}<rect class="orb" x="29" y="2" width="13" height="13" fill="#fff"/></g></g>')
    for f in shields:
        body.append(f'<path class="o w6"{dl(f)} fill="none" stroke="#fff" stroke-width="1.5" d="M{mage["x"]+1:.0f} {mage["y"]-20:.0f}A14 14 0 0 1 {mage["x"]+1:.0f} {mage["y"]+8:.0f}"/>')
    if boss:
        bx0, by0 = GW + 30, boss["y"]
        arrive = boss["arrive"] or boss["start"] + 37
        kf("bs", [(0, f"transform:translate({bx0}px,{by0:.0f}px);opacity:0"), (boss["start"], f"transform:translate({bx0}px,{by0:.0f}px);opacity:0"),
                  (boss["start"] + 0.01, f"transform:translate({bx0}px,{by0:.0f}px);opacity:1"), (arrive, f"transform:translate({GW-80}px,{by0:.0f}px);opacity:1"),
                  (boss["death"], f"transform:translate({GW-80}px,{by0:.0f}px);opacity:1"), (boss["death"] + 0.01, f"transform:translate({GW-80}px,{by0:.0f}px);opacity:0"),
                  (N, f"transform:translate({GW-80}px,{by0:.0f}px);opacity:0")])
        css.append("@keyframes bb{50%{transform:translateY(-3px)}}.bb{animation:bb 1s steps(2,end) infinite}")
        fr = [(0, "transform:scaleX(1)")] + [(f, f"transform:scaleX({max(0, hp)/14:.3f})") for f, hp in boss["hits"]] + [(N, "transform:scaleX(0)")]
        kf("hp", fr, "steps(1,end)")
        crown = "".join(f"M{a_} {b_}h5v5h-5z" for a_, b_ in ((-8, -20), (-3, -24), (2, -20))) + "M-8 -17h15v3h-15z"
        flashes_b = "".join(f'<g class="o w4"{dl(f)}>{bug_use(3.2, "#fff")}</g>' for f, _ in boss["hits"])
        body.append(f'<g class="bs"><g class="bb">{bug_use(3.2, "#bbb")}{flashes_b}<path fill="#fff" d="{crown}"/></g>'
                    f'<g transform="translate(-36,{TOP-14-by0:.0f})"><rect width="72" height="5" fill="#333"/><rect class="hp" width="72" height="5" fill="#fff"/></g>'
                    f'{T("BUG LENDÁRIO", 0, TOP - 26 - by0, 1, "#ccc", "middle")}</g>')
        for i, (f0, x0, y0, x1, y1, f1) in enumerate(shots):
            kf(f"s{i}", [(0, f"transform:translate({x0:.0f}px,{y0:.0f}px);opacity:0"), (f0, f"transform:translate({x0:.0f}px,{y0:.0f}px);opacity:0"),
                         (f0 + 0.01, f"transform:translate({x0:.0f}px,{y0:.0f}px);opacity:1"), (f1, f"transform:translate({x1:.0f}px,{y1:.0f}px);opacity:1"),
                         (f1 + 0.01, f"transform:translate({x1:.0f}px,{y1:.0f}px);opacity:0"), (N, f"transform:translate({x1:.0f}px,{y1:.0f}px);opacity:0")])
            body.append(f'<g class="s{i}"><rect x="-2" y="-2" width="4" height="4" fill="#999"/><rect x="-1" y="-1" width="2" height="2" fill="#fff"/></g>')
    for f, pts, w in bolts:
        pp = " ".join(f"{a_:.0f},{b_:.0f}" for a_, b_ in pts)
        body.append(f'<g class="o w6"{dl(f)} fill="none" stroke-linejoin="round"><polyline points="{pp}" stroke="#666" stroke-width="{w+2}"/><polyline points="{pp}" stroke="#fff" stroke-width="{w}"/></g>')
    for f, X, Y in rings:
        body.append(f'<g transform="translate({X:.0f},{Y:.0f})"><rect class="o rg"{dl(f)} x="-2" y="-2" width="4" height="4" fill="none" stroke="#fff" vector-effect="non-scaling-stroke"/></g>')
    for f, X, Y, col, n, R in bursts:
        n = min(n, 6)
        parts = "".join(f'<g transform="rotate({k*360/n+rnd.uniform(-15,15):.0f})"><rect class="o p{round(R)}"{dl(f)} width="2" height="2"/></g>' for k in range(n))
        body.append(f'<g transform="translate({X:.0f},{Y:.0f})" fill="{col}">{parts}</g>')
    for f in flashes:
        body.append(f'<rect class="o fl"{dl(f)} width="{GW}" height="{GH}" fill="#fff"/>')
    for f, text, X, Y, big in msgs:
        w = tw(text, 1); fx = max(4, min(GW - w - 4, X - w / 2))
        body.append(f'<g class="o {"mb" if big else "mm"}"{dl(f)}><rect x="{fx-4:.0f}" y="{Y-10:.0f}" width="{w+8:.0f}" height="13" fill="#000" stroke="{"#fff" if big else "#444"}"/>{T(text, round(fx), round(Y - 7), 1)}</g>')
    if boss and boss["death"]:
        fr = [(0, "opacity:0")]
        a_ = boss["death"] + 15
        while a_ < N - 2: fr += [(a_, "opacity:1"), (a_ + 8, "opacity:0")]; a_ += 12
        kf("fz", fr + [(N, "opacity:0")], "steps(1,end)")
        w = tw("FASE LIMPA!", 1.6) + 22
        body.append(f'<g class="fz"><rect x="{GW/2-w/2:.0f}" y="{TOP+ROWS*cs/2-12:.0f}" width="{w:.0f}" height="22" fill="#000" stroke="#fff" stroke-width="2"/>{T("FASE LIMPA!", GW/2, TOP+ROWS*cs/2-5.6, 1.6, "#fff", "middle")}</g>')

    sc = 776 / GW
    H = round(44 + GH * sc + 34)
    hy = round(44 + GH * sc + 6)
    hud = []
    def counter(prefix, events, x, anchor="start"):
        res = ""
        for k, (f, v) in enumerate(events):
            f2 = events[k + 1][0] if k + 1 < len(events) else N
            name = f"{prefix}{k}"
            kf(name, [(0, f"opacity:{1 if f == 0 else 0}"), (f, "opacity:1"), (f2, "opacity:0"), (N, f"opacity:{1 if f == 0 else 0}")], "steps(1,end)")
            res += T(str(v) if prefix != "st" else ("★" if v else "☆"), x, hy, 1.6, "#fff", anchor, name)
        return res
    hud.append(T("MANA", 24, hy, 1.6) + counter("mn", mana_ev, 24 + tw("MANA ", 1.6)))
    hud.append(T("BUGS CORRIGIDOS", 290, hy, 1.6) + counter("kl", kill_ev, 290 + tw("BUGS CORRIGIDOS ", 1.6)))
    hud.append(T("TEMPESTADE", 776 - tw("TEMPESTADE ☆", 1.6), hy, 1.6, "#888") + counter("st", storm_ev, 776, "end"))
    for ch in sorted(used):
        base, acc = ACCENT.get(ch, (ch, None))
        d = []
        for r, bits in enumerate(GLYPH.get(base, GLYPH[" "])):
            for c_ in range(5):
                if bits >> (4 - c_) & 1: d.append(f"M{c_} {r}h1v1h-1z")
        if acc:
            for r, bits in ((-3, acc[0]), (-2, acc[1])):
                for c_ in range(5):
                    if bits >> (4 - c_) & 1: d.append(f"M{c_} {r}h1v1h-1z")
        if ch == "Ç": d.append("M2 7h1v1h-1zM1 8h2v1h-2z")
        defs.append(f'<path id="g{ord(ch):x}" d="{"".join(d)}"/>')
    out = header("MINIGAME · CAÇA AOS BUGS") + window_frame(0, 30, 800, H - 30)
    out += f'<defs>{"".join(defs)}</defs><g transform="translate(12,44) scale({sc:.4f})">{"".join(body)}</g>{"".join(hud)}'
    return svg(800, H, out, "".join(css))

def window_frame(x, y, w, h):
    return window(x, y, w, h)

if __name__ == "__main__":
    u = fetch()
    os.makedirs(OUT, exist_ok=True)
    for name, fn in (("registro.svg", registro), ("minigame.svg", minigame)):
        open(os.path.join(OUT, name), "w", encoding="utf-8").write(fn(u))
        print("ok", name)
