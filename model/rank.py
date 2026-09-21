"""Cross-sectional scoring and ranking across horizons and risk preferences."""
import numpy as np
from engine import pct_rank, WEIGHTS


def build_table(results, horizon):
    """results: list of dicts with keys name, code, metrics per horizon."""
    rows = [r for r in results if horizon in r["m"]]
    e_ann  = np.array([r["m"][horizon]["e_ann"]   for r in rows])
    e_cum  = np.array([r["m"][horizon]["e_cum"]   for r in rows])
    sort   = np.array([r["m"][horizon]["sortino"] for r in rows])
    cvar   = np.array([r["m"][horizon]["cvar10"]  for r in rows])

    # Expected-return ranking metric: 1y uses cumulative TSR, 3y/5y use annualized
    ret_metric = e_cum if horizon == 1 else e_ann

    p_ret  = pct_rank(ret_metric, True)
    p_sort = pct_rank(sort, True)
    p_cvar = pct_rank(cvar, True)          # less negative CVaR -> higher score

    out = {}
    for tag, w in WEIGHTS.items():
        out[tag] = w["ret"] * p_ret + w["sortino"] * p_sort + w["cvar"] * p_cvar

    for i, r in enumerate(rows):
        r.setdefault("score", {})[horizon] = {
            "p_ret": p_ret[i], "p_sort": p_sort[i], "p_cvar": p_cvar[i],
            **{k: v[i] for k, v in out.items()},
        }
    # ordinal ranks
    def ordinal(vals, hib=True):
        v = np.asarray(vals, float)
        order = np.argsort(-v if hib else v)
        rk = np.empty(len(v), int)
        rk[order] = np.arange(1, len(v) + 1)
        return rk

    rk_ret  = ordinal(ret_metric)
    rk_risk = ordinal(sort)
    rk_bal  = ordinal(out["balanced"])
    rk_agg  = ordinal(out["aggressive"])
    rk_def  = ordinal(out["defensive"])
    for i, r in enumerate(rows):
        r["score"][horizon].update(rank_ret=int(rk_ret[i]), rank_risk=int(rk_risk[i]),
                                   rank_bal=int(rk_bal[i]), rank_agg=int(rk_agg[i]),
                                   rank_def=int(rk_def[i]))
    return rows


def instability_flag(row):
    """Rank swing across risk preferences within the same horizon -> 'rank unstable'."""
    sw = []
    for h in (1, 3, 5):
        if h in row.get("score", {}):
            s = row["score"][h]
            sw.append(abs(s["rank_agg"] - s["rank_def"]))
    return (max(sw) if sw else 0)
