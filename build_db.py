"""Génère projectors.json (format compact lu par l'app) à partir de projecteurs-app.json (base de recherche,
avec sources et notes). La base de recherche reste la référence ; ce fichier-ci n'est qu'une projection
allégée : clés courtes, pas de sources, ~75 ko au lieu de ~430 ko.

Format : {"v": version, "date": "AAAA-MM-JJ", "models": [{"b": marque, "m": modèle, "a": [alias], "r": résolution,
"asp": rapport largeur/hauteur (nombre), "lm": lumens, "L": [[nom, throw_min, throw_max, shift_v_min, shift_v_max,
offset_v|null, fiabilité v|d|p, standard 0|1], ...]}]}  — shift et offset en fraction de hauteur d'image,
centre de l'image par rapport à l'axe objectif, + = haut (projecteur à l'endroit)."""
import json, re, sys, datetime, os
D = os.path.dirname(os.path.abspath(__file__))
src = json.load(open(os.path.join(D, 'projecteurs-app.json'), encoding='utf-8'))
FB = {'vérifié': 'v', 'déduit': 'd', 'plage du projecteur': 'p'}

def ratio(m):
    a = m.get('aspect')
    if a and re.fullmatch(r'\d+:\d+', a):
        w, h = map(int, a.split(':')); return round(w / h, 4)
    r = re.search(r'(\d{3,5})\s*[x×]\s*(\d{3,5})', m.get('resolution') or '')
    return round(int(r.group(1)) / int(r.group(2)), 4) if r else 1.6

out = {'v': src.get('version', 1), 'date': datetime.date.today().isoformat(), 'models': []}
for m in src['models']:
    L = [[l['name'], l['throw'][0], l['throw'][1], l['shift_v'][0], l['shift_v'][1], l.get('offset_v'),
          FB[l['fiabilite']], 1 if l.get('standard') else 0] for l in m['lenses']]
    out['models'].append({'b': m['brand'], 'm': m['model'], 'a': m.get('aliases') or [], 'r': m.get('resolution') or '',
                          'asp': ratio(m), 'lm': m.get('lumens'), 'L': L})
s = json.dumps(out, ensure_ascii=False, separators=(',', ':'))
open(os.path.join(D, 'pwa', 'projectors.json'), 'w', encoding='utf-8').write(s)
print('projectors.json :', len(out['models']), 'modèles,', sum(len(m['L']) for m in out['models']), 'objectifs,', len(s), 'octets')
