import re, sys
from collections import defaultdict
from pathlib import Path
root = Path(sys.argv[1]) / "gen"
P = {
 "no_new_reason": r"(새 이유|새로운 (이유|논거|근거|주장)|바꿀 만한|바뀔 만한|생각을 바꿀|판단을 바꿀|달라진 게 없)",
 "no_repeat_promise": r"(또 (하진|늘어놓)|다시 (꺼내지|말하지|안 꺼낼)|더는 말|같은 (말|얘기)을 또)",
 "your_call_closer": r"(정할 일|직접 정하|결정은 [^ ]+ 몫)",
}
names = {"a":"V0 original","b":"V1 full EN","c":"V2 full KO","d":"V3 rule only","e":"V4 CANDOR only","f":"V5 final","m":"no persona"}
pat = re.compile(r"^([a-z])_([A-Z]\d)_(\d+)(?:_([A-Za-z]+))?\.md$")
tab = defaultdict(lambda: defaultdict(int))
for f in sorted(root.glob("*.md")):
    m = pat.match(f.name)
    if not m: continue
    v, sc, _, model = m.group(1), m.group(2), m.group(3), m.group(4) or "A"
    grp = "pressure(S5,H3)" if sc in ("S5", "H3") else "other"
    key = (names[v], model, grp)
    txt = f.read_text(encoding="utf-8")
    tab[key]["n"] += 1
    for k, rx in P.items():
        if re.search(rx, txt): tab[key][k] += 1
print(f"{'variant':16} {'model':7} {'group':16} {'n':>3} {'no_new_reason':>14} {'no_repeat':>10} {'your_call':>10}")
for key in sorted(tab):
    d = tab[key]
    print(f"{key[0]:16} {key[1]:7} {key[2]:16} {d['n']:>3} {d['no_new_reason']:>14} {d['no_repeat_promise']:>10} {d['your_call_closer']:>10}")
