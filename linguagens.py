import json, os, urllib.request

USER = os.environ.get("USERNAME", "brunoferreira15")
TOKEN = os.environ.get("GITHUB_TOKEN", "")

QUERY = """
query($login: String!) {
  user(login: $login) {
    repositories(first: 100, ownerAffiliations: OWNER, isFork: false, privacy: PUBLIC) {
      nodes { nameWithOwner languages(first: 20) { edges { size node { name color } } } }
    }
    repositoriesContributedTo(first: 100, includeUserRepositories: false,
                              contributionTypes: [COMMIT, PULL_REQUEST], privacy: PUBLIC) {
      nodes { nameWithOwner languages(first: 20) { edges { size node { name color } } } }
    }
  }
}
"""

def buscar():
    if os.environ.get("MOCK"):
        return json.loads(os.environ["MOCK"])
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": USER}}).encode(),
        headers={"Authorization": f"bearer {TOKEN}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req) as r:
        dados = json.load(r)
    if "errors" in dados:
        raise SystemExit(f"Erro da API do GitHub: {dados['errors']}")
    return dados["data"]["user"]

user = buscar()
vistos, totais, cor_ling = set(), {}, {}
for grupo in ("repositories", "repositoriesContributedTo"):
    for repo in user[grupo]["nodes"]:
        if repo["nameWithOwner"] in vistos:
            continue
        vistos.add(repo["nameWithOwner"])
        for e in repo["languages"]["edges"]:
            nome = e["node"]["name"]
            totais[nome] = totais.get(nome, 0) + e["size"]
            cor_ling[nome] = e["node"].get("color") or "#8a8a8a"

soma = sum(totais.values()) or 1
ranking = sorted(totais.items(), key=lambda x: -x[1])[:8]

# Cor oficial de cada linguagem no GitHub (cinza se a linguagem não tiver cor)
cores = [cor_ling[nome] for nome, _ in ranking]

def pct(v):
    return f"{v / soma * 100:.1f}".replace(".", ",") + "%"

largura, barra_x, barra_w = 400, 25, 350
linhas = (len(ranking) + 1) // 2
altura = 95 + linhas * 26

partes = []
x = barra_x
for i, (nome, v) in enumerate(ranking):
    w = v / soma * barra_w
    partes.append(f'<rect x="{x:.2f}" y="52" width="{w:.2f}" height="10" fill="{cores[i]}"/>')
    x += w

legenda = []
for i, (nome, v) in enumerate(ranking):
    col, lin = i % 2, i // 2
    lx, ly = 30 + col * 180, 92 + lin * 26
    legenda.append(
        f'<circle cx="{lx}" cy="{ly - 4}" r="5" fill="{cores[i]}" stroke="#666" stroke-width="0.5"/>'
        f'<text x="{lx + 12}" y="{ly}" class="t">{nome} <tspan class="p">{pct(v)}</tspan></text>'
    )

if not ranking:
    legenda.append('<text x="30" y="92" class="t">Nenhuma linguagem encontrada ainda</text>')

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{largura}" height="{altura}" viewBox="0 0 {largura} {altura}">
  <style>
    .titulo {{ font: 600 18px 'Segoe UI', Ubuntu, Arial, sans-serif; fill: #ffffff; }}
    .t {{ font: 400 13px 'Segoe UI', Ubuntu, Arial, sans-serif; fill: #ffffff; }}
    .p {{ fill: #a8a8a8; }}
  </style>
  <rect width="{largura}" height="{altura}" rx="6" fill="#000000"/>
  <text x="25" y="35" class="titulo">Linguagens mais usadas</text>
  <clipPath id="arredonda"><rect x="{barra_x}" y="52" width="{barra_w}" height="10" rx="5"/></clipPath>
  <rect x="{barra_x}" y="52" width="{barra_w}" height="10" rx="5" fill="#222"/>
  <g clip-path="url(#arredonda)">{"".join(partes)}</g>
  {"".join(legenda)}
</svg>
'''

with open("linguagens.svg", "w", encoding="utf-8") as f:
    f.write(svg)
print("Linguagens:", ", ".join(f"{n} {pct(v)}" for n, v in ranking))
