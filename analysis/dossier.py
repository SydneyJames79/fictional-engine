"""반대심문·검증·최종심사 에이전트에 넘길 종목별 요약(도시에)을 만든다."""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from pipeline import fix_tree  # noqa: E402

HERE = os.path.dirname(__file__)


def group_summary(tree, p0):
    """거시 그룹별 확률·확률가중 가격·TSR."""
    out = {}
    for m in ('기준', '낙관', '비관'):
        g = [b for b in tree if b[0] == m]
        p = sum(b[2] for b in g)
        if p <= 0:
            continue
        price = sum(b[2] * b[3] for b in g) / p
        div = sum(b[2] * b[4] for b in g) / p
        out[m] = {'p': round(p * 100), 'price': round(price), 'tsr_pct': round(((price + div) / p0 - 1) * 100, 1)}
    return out


def analyst_brief(r, p0):
    if not r:
        return None
    sc = {}
    for h, T in (('h1', 1), ('h3', 3), ('h5', 5)):
        t = fix_tree(r['scenarios'][h], [], '')
        e = sum(b[2] * (b[3] + b[4]) / p0 for b in t)
        sc[h] = {'exp_tsr_pct': round((e - 1) * 100, 1), 'exp_ann_pct': round((e ** (1 / T) - 1) * 100, 1),
                 'groups': group_summary(t, p0),
                 'branches': [f"{b[0]}·{b[1]} p{b[2]*100:.0f}% → {b[3]:,.0f}원" for b in t]}
    return {
        'confidence': r.get('confidence'), 'confidence_reason': r.get('confidence_reason', '')[:400],
        'market_implied': r.get('market_implied', '')[:900], 'view_vs_market': r.get('view_vs_market', '')[:900],
        'valuation': [f"{v['method']}: {v['fair_value_low']:,.0f}/{v['fair_value_base']:,.0f}/{v['fair_value_high']:,.0f}원" for v in r.get('valuation', [])],
        'dilution_assumed': r.get('net_share_change_assumed_pct'),
        'dps': [r.get('dps_last_fy'), r.get('dps_next_fy_expected')],
        'scenarios': sc, 'risks': r.get('risks', [])[:6], 'catalysts': r.get('catalysts', [])[:6],
        'invalidation': r.get('invalidation', [])[:5],
    }


def forensic_brief(f):
    if not f:
        return None
    r = f['result']
    return {'searches': f.get('searches'), 'risk_score': r.get('forensic_risk_score'),
            'expected_net_share_change_pct': r.get('expected_net_share_change_pct'),
            'red_flags': [f"[{x['severity']}] {x['issue']}: {x['evidence'][:200]}" for x in r.get('red_flags', [])][:6],
            'tail_risk_notes': r.get('tail_risk_notes', '')[:600],
            'recommended_adjustments': r.get('recommended_adjustments', '')[:800],
            'balance_sheet': r.get('balance_sheet', '')[:500],
            'ownership_overhang': r.get('ownership_overhang', '')[:500]}


def build(code, p0):
    d = json.load(open(os.path.join(HERE, 'data', 'stocks', f'{code}.json')))
    spec = d.get('spec', {}).get('result')
    gen = d.get('gen', {}).get('result')
    foren = d.get('foren') if d.get('foren', {}).get('searches', 0) > 0 else None
    return {'code': code, 'name': d['name'], 'p0': p0,
            'fact_sheet': (spec or {}).get('fact_sheet', '')[:5000],
            'specialist': analyst_brief(spec, p0), 'generalist': analyst_brief(gen, p0),
            'forensic': forensic_brief(foren)}


if __name__ == '__main__':
    import pandas as pd
    rm = pd.read_csv(os.path.join(HERE, 'data', 'risk_metrics_full_1021.csv'), dtype={'code': str}).set_index('code')
    c = sys.argv[1]
    print(json.dumps(build(c, float(rm.loc[c, 'close'])), ensure_ascii=False, indent=1)[:4000])
