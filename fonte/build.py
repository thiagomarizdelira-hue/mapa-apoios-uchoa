import json, math, sys, csv, re, os
from urllib.parse import quote
D = sys.argv[1]; TPL = sys.argv[2]; OUT = sys.argv[3]; CSVOUT = sys.argv[4]
d = json.load(open(os.path.join(D, 'dados.json')))
g = json.load(open(os.path.join(D, 'malha_pe.json')))
NORONHA = '2605459'

def fixname(s):
    s = re.sub(r'\s+', ' ', s).strip()
    return ' '.join(w.lower() if w.lower() in ('da','de','do','das','dos','e') and i > 0 else w for i, w in enumerate(s.split(' ')))

for m in d['municipios']:
    for k in ('prefeito', 'vice', 'prefeitoNome'):
        if m.get(k): m[k] = fixname(m[k])
for x in d['deputados']:
    x['nome'] = fixname(x['nome']); x['nomeCompleto'] = fixname(x['nomeCompleto'])

def rings(geom):
    if geom['type'] == 'Polygon': return [geom['coordinates']]
    return geom['coordinates']

# bounds of mainland
mn = [999, 999]; mx = [-999, -999]
for f in g['features']:
    if f['properties']['codarea'] == NORONHA: continue
    for poly in rings(f['geometry']):
        for ring in poly:
            for lng, lat in ring:
                mn[0] = min(mn[0], lng); mn[1] = min(mn[1], lat); mx[0] = max(mx[0], lng); mx[1] = max(mx[1], lat)
k = math.cos(math.radians((mn[1] + mx[1]) / 2))
W = 1000.0
sc = W / ((mx[0] - mn[0]) * k)
H = (mx[1] - mn[1]) * sc
PAD = 10
def proj(lng, lat): return (PAD + (lng - mn[0]) * k * sc, PAD + (mx[1] - lat) * sc)

# Noronha inset: placed at top right, scaled up
nb = None
for f in g['features']:
    if f['properties']['codarea'] == NORONHA:
        pts = [p for poly in rings(f['geometry']) for ring in poly for p in ring]
        nb = (min(p[0] for p in pts), min(p[1] for p in pts), max(p[0] for p in pts), max(p[1] for p in pts))
INS = (W - 120, PAD + 8, 110, 50)  # x,y,w,h
nsc = min(INS[2] / ((nb[2] - nb[0]) * k), INS[3] / (nb[3] - nb[1])) * 0.8
def projN(lng, lat): return (INS[0] + 10 + (lng - nb[0]) * k * nsc, INS[1] + 8 + (nb[3] - lat) * nsc)

def path(geom, pf):
    out = []
    for poly in rings(geom):
        for ring in poly:
            pts = [pf(*p) for p in ring]
            s = 'M' + 'L'.join(f'{x:.1f},{y:.1f}' for x, y in pts) + 'Z'
            out.append(s)
    return ''.join(out)

paths = {f['properties']['codarea']: path(f['geometry'], projN if f['properties']['codarea'] == NORONHA else proj) for f in g['features']}
for m in d['municipios']:
    m['d'] = paths[m['id']]
    pf = projN if m['id'] == NORONHA else proj
    x, y = pf(m['lng'], m['lat']); m['x'] = round(x, 1); m['y'] = round(y, 1)

vp = os.path.join(D, 'votos_cand.json')
if os.path.exists(vp): d['votosCand'] = json.load(open(vp))
if os.environ.get('SNAPSHOT'): d['snapshot'] = json.load(open(os.environ['SNAPSHOT']))
ep = os.path.join(D, 'emendas.json')
if os.path.exists(ep): d['emendas'] = json.load(open(ep))
d['view'] = {'w': W + 2 * PAD, 'h': round(H + 2 * PAD, 1), 'inset': INS}
blob = json.dumps(d, ensure_ascii=False, separators=(',', ':')).replace('<', '\\u003c').replace('¿', '–')
html = open(TPL, encoding='utf-8').read().replace('/*__DATA__*/null', blob)
if os.environ.get('SNAPSHOT'):
    head = ('<!doctype html>\n<html lang="pt-BR">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">\n'
            '<meta name="description" content="Prefeitos, deputados federais 2026, votação por cidade, apoios e emendas parlamentares em Pernambuco.">\n'
            '<meta name="theme-color" content="#04100d">\n<link rel="manifest" href="manifest.webmanifest">\n<link rel="icon" href="icons/icon.svg" type="image/svg+xml">\n'
            '<link rel="apple-touch-icon" href="icons/icon-180.png">\n<meta name="apple-mobile-web-app-capable" content="yes">\n</head>\n<body>\n')
    sw = "\n<script>if ('serviceWorker' in navigator && location.protocol === 'https:') navigator.serviceWorker.register('sw.js').catch(() => {});</script>"
    html = head + html + sw + '\n</body>\n</html>\n'
open(OUT, 'w', encoding='utf-8').write(html)

def emcols(mid):
    E = d.get('emendas'); 
    if not E: return ['', '', '']
    by = {}
    for a, ano, t, vp, vo in E['mun'].get(mid, []):
        if 2023 <= ano <= 2026 and vp > 0: by[a] = by.get(a, 0) + vp
    if not by: return [0, '', '']
    top = max(by, key=by.get); au = E['autores'][top]
    nm = next((x['nome'] for x in d['deputados'] if x['id'] == au['sq']), None) or (d['candFed'].get(au['sq'] or '', {}).get('nome')) or au['nome']
    return [sum(by.values()), nm, by[top]]

with open(CSVOUT, 'w', newline='', encoding='utf-8-sig') as fh:
    w = csv.writer(fh, delimiter=';')
    w.writerow(['Código IBGE', 'Município', 'Região imediata', 'Mesorregião', 'Mais votado dep. federal 2026', 'Partido do mais votado', 'Votos do mais votado', '% na cidade', 'Mais votado se elegeu?', 'Oportunidade (mais votado não eleito)', 'Emendas pagas 2023-2026 à prefeitura (R$)', 'Maior autor de emendas 2023-2026', 'Valor do maior autor (R$)', '2º mais votado', 'Votos do 2º', 'Prefeito(a) (nome de urna)', 'Nome completo', 'Partido', 'Vice-prefeito(a)', 'Partido do vice', 'Coligação', 'Latitude da sede', 'Longitude da sede', 'Google Maps'])
    for m in sorted(d['municipios'], key=lambda m: m['nome']):
        V = d['votacao']; e = V['municipios'][m['id']]; C = V['candidatos']; t1 = e['top'][0]; t2 = e['top'][1]
        w.writerow([m['id'], m['nome'], m['regiao'], m['meso'], C[t1[0]]['nome'], C[t1[0]]['partido'], t1[1], str(round(t1[1] / e['total'] * 100, 1)).replace('.', ','), 'sim' if C[t1[0]]['eleito'] else 'não', '' if C[t1[0]]['eleito'] or not m.get('prefeito') else 'SIM', *emcols(m['id']), C[t2[0]]['nome'], t2[1], m.get('prefeito', 'Distrito estadual (sem prefeito)'), m.get('prefeitoNome', ''), m.get('partido', ''), m.get('vice', ''), m.get('vicePartido', ''), m.get('coligacao', ''), m['lat'], m['lng'], "https://www.google.com/maps/search/?api=1&query=" + quote(f"Prefeitura de {m['nome']} PE")])
print('ok', len(blob), d['view'])
