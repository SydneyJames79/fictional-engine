"""Anonymize generated replies + controls into shuffled judge bundles.

usage: python3 -I blind.py <scratchpad> <tag> <n_judges> <seed> [glob ...]
Writes blind/<tag>/bundle_j<k>.md and key/<tag>_key.json
"""
import json, random, re, sys
from pathlib import Path

root = Path(sys.argv[1]); tag = sys.argv[2]
n_judges = int(sys.argv[3]); seed = int(sys.argv[4])
globs = sys.argv[5:] or ["gen/*.md", "controls/*.md"]
rng = random.Random(seed)
pat = re.compile(r"^([A-Za-z0-9]+)_([A-Z]\d+)_(\d+)(?:_([A-Za-z]+))?\.md$")

items = []
for g in globs:
    for f in sorted(root.glob(g)):
        m = pat.match(f.name)
        if not m:
            continue
        variant, scen, sample, model = m.group(1), m.group(2), m.group(3), m.group(4) or "A"
        conv = (root / "scenarios" / f"{scen}.md").read_text(encoding="utf-8").strip()
        reply = f.read_text(encoding="utf-8").strip()
        if not reply:
            continue
        items.append(dict(variant=variant, scenario=scen, sample=sample, model=model,
                          file=str(f.relative_to(root)), conv=conv, reply=reply))

ids = rng.sample(range(100, 1000), len(items))
for it, i in zip(items, ids):
    it["id"] = f"R{i}"

(root / "key").mkdir(exist_ok=True)
key = {it["id"]: {k: it[k] for k in ("variant", "scenario", "sample", "model", "file")} for it in items}
(root / "key" / f"{tag}_key.json").write_text(json.dumps(key, ensure_ascii=False, indent=1), encoding="utf-8")

out = root / "blind" / tag
out.mkdir(parents=True, exist_ok=True)
n_parts = int(__import__("os").environ.get("BLIND_PARTS", "1"))
for j in range(1, n_judges + 1):
    order = items[:]
    rng.shuffle(order)
    size = -(-len(order) // n_parts)
    for p_i in range(n_parts):
        chunk = order[p_i * size:(p_i + 1) * size]
        parts = []
        for it in chunk:
            parts.append(f"=== ITEM {it['id']} ===\n[Conversation so far]\n{it['conv']}\n\n"
                         f"[Assistant reply to evaluate]\n{it['reply']}\n=== END {it['id']} ===\n")
        suffix = f"_p{p_i + 1}" if n_parts > 1 else ""
        (out / f"bundle_j{j}{suffix}.md").write_text("\n".join(parts), encoding="utf-8")
print(f"{len(items)} items -> {out} ({n_judges} bundles); key -> key/{tag}_key.json")
