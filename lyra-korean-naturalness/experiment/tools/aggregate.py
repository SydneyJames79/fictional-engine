"""Join blind judge ratings with the key and summarize.

usage: python3 -I aggregate.py <scratchpad> <tag> <judge_jsonl> [<judge_jsonl> ...]
"""
import json, sys, itertools, statistics as st
from collections import defaultdict
from pathlib import Path

root = Path(sys.argv[1]); tag = sys.argv[2]; jfiles = sys.argv[3:]
key = json.loads((root / "key" / f"{tag}_key.json").read_text(encoding="utf-8"))

def load(fp):
    out = {}
    for line in Path(fp).read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            o = json.loads(line)
        except json.JSONDecodeError:
            continue
        out[o.get("id")] = o
    return out

judges = {Path(f).stem: load(f) for f in jfiles}
for j, d in judges.items():
    missing = [i for i in key if i not in d]
    if missing:
        print(f"[warn] judge {j} missing {len(missing)} items: {missing[:8]}")

def feats(o):
    narr = o.get("procedural_narration") or []
    return dict(nat=o.get("naturalness"), reg=o.get("register_fit"),
                calq=len(o.get("calques") or []),
                narr_bad=sum(1 for n in narr if n.get("natural") is False),
                narr_all=len(narr),
                speech=len(o.get("speech_level_issues") or []))

rows = []
for iid, meta in key.items():
    per = [feats(d[iid]) for d in judges.values() if iid in d]
    if not per:
        continue
    nj = len(per)
    rows.append(dict(id=iid, **meta, nj=nj,
        nat=st.mean(p["nat"] for p in per if p["nat"] is not None),
        reg=st.mean(p["reg"] for p in per if p["reg"] is not None),
        calq_mean=st.mean(p["calq"] for p in per),
        calq_major=sum(p["calq"] > 0 for p in per) * 2 > nj,
        narr_bad_any=any(p["narr_bad"] > 0 for p in per),
        narr_bad_major=sum(p["narr_bad"] > 0 for p in per) * 2 > nj,
        speech_any=any(p["speech"] > 0 for p in per)))

def group(r):
    s = r["scenario"]
    g = "candor" if s.startswith("S") else ("control" if s.startswith("C") else "heldout")
    return g

def summarize(sel, label):
    if not sel:
        return
    n = len(sel)
    print(f"| {label} | {n} | {st.mean(r['nat'] for r in sel):.2f} | {st.mean(r['reg'] for r in sel):.2f} | "
          f"{st.mean(r['calq_mean'] for r in sel):.2f} | {sum(r['calq_major'] for r in sel)}/{n} | "
          f"{sum(r['narr_bad_major'] for r in sel)}/{n} | {sum(r['narr_bad_any'] for r in sel)}/{n} | "
          f"{sum(r['speech_any'] for r in sel)}/{n} |")

print("\n| group | n | naturalness | register | calques/item | calque(majority) | bad-narration(majority) | bad-narration(any judge) | speech-level(any) |")
print("|---|---|---|---|---|---|---|---|---|")
by = defaultdict(list)
for r in rows:
    by[(r["variant"], r["model"], group(r))].append(r)
for k in sorted(by):
    summarize(by[k], f"{k[0]}/{k[1]}/{k[2]}")

print("\nPer scenario (variant/model/scenario):")
bys = defaultdict(list)
for r in rows:
    bys[(r["variant"], r["model"], r["scenario"])].append(r)
for k in sorted(bys):
    sel = bys[k]
    print(f"  {k}: n={len(sel)} nat={st.mean(r['nat'] for r in sel):.2f} calq={st.mean(r['calq_mean'] for r in sel):.2f} badnarr_major={sum(r['narr_bad_major'] for r in sel)}")

def ranks(xs):
    order = sorted(range(len(xs)), key=lambda i: xs[i])
    rk = [0.0] * len(xs); i = 0
    while i < len(xs):
        j = i
        while j + 1 < len(xs) and xs[order[j + 1]] == xs[order[i]]:
            j += 1
        for t in range(i, j + 1):
            rk[order[t]] = (i + j) / 2 + 1
        i = j + 1
    return rk

def spearman(a, b):
    ra, rb = ranks(a), ranks(b)
    ma, mb = st.mean(ra), st.mean(rb)
    num = sum((x - ma) * (y - mb) for x, y in zip(ra, rb))
    den = (sum((x - ma) ** 2 for x in ra) * sum((y - mb) ** 2 for y in rb)) ** 0.5
    return num / den if den else float("nan")

print("\nInter-judge agreement (naturalness Spearman; bad-narration flag agreement):")
names = list(judges)
for a, b in itertools.combinations(names, 2):
    common = [i for i in key if i in judges[a] and i in judges[b]]
    xa = [judges[a][i].get("naturalness") for i in common]
    xb = [judges[b][i].get("naturalness") for i in common]
    fa = [feats(judges[a][i])["narr_bad"] > 0 for i in common]
    fb = [feats(judges[b][i])["narr_bad"] > 0 for i in common]
    agree = sum(x == y for x, y in zip(fa, fb)) / len(common)
    print(f"  {a} vs {b}: rho={spearman(xa, xb):.2f}, narration-flag agreement={agree:.2f} (n={len(common)})")

# phrase dump for auditing
dump = root / "judge" / f"{tag}_flags.md"
lines = []
for r in sorted(rows, key=lambda r: (r["variant"], r["model"], r["scenario"], r["sample"])):
    lines.append(f"\n## {r['id']} {r['variant']}/{r['model']}/{r['scenario']}#{r['sample']}  nat={r['nat']:.2f}")
    for jn, d in judges.items():
        o = d.get(r["id"])
        if not o:
            continue
        for c in o.get("calques") or []:
            lines.append(f"- [{jn}] CALQUE: {c.get('phrase')}  -> {c.get('better')}  ({c.get('why')})")
        for n in o.get("procedural_narration") or []:
            lines.append(f"- [{jn}] NARR natural={n.get('natural')}: {n.get('phrase')}  ({n.get('why')})")
dump.write_text("\n".join(lines), encoding="utf-8")
print(f"\nflag dump -> {dump}")
