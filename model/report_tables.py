"""Markdown table generation for the final report (Parts 3 and 4)."""

def pct(x, d=1):
    return "N/A" if x is None else f"{x*100:.{d}f}%"

def num(x, d=2):
    return "N/A" if x is None else f"{x:.{d}f}"

def won(x):
    return "N/A" if x is None else f"{int(round(x)):,}"

CONF_KR = {"H": "높음", "M": "보통", "L": "낮음"}


def horizon_table(rows, horizon):
    """Part 3: full ranking table for one horizon, sorted by balanced composite rank."""
    rows = sorted(rows, key=lambda r: r["score"][horizon]["rank_bal"])
    head = ("| 균형 | 기대 | 위험 | 종목(코드) | 현재가 | 기대누적TSR | 기대연환산 | 중앙값누적 | "
            "P10 | P50 | P90 | 손실확률 | -30%확률 | Sortino | CVaR10 | 신뢰도 | 핵심 근거 |")
    sep  = "|---:|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|:---:|---|"
    out = [head, sep]
    for r in rows:
        s, m = r["score"][horizon], r["m"][horizon]
        out.append("| {bal} | {ret} | {rsk} | {nm}({cd}) | {p0} | {ec} | {ea} | {mc} | "
                   "{p10} | {p50} | {p90} | {pl} | {pl30} | {so} | {cv} | {cf} | {why} |".format(
            bal=s["rank_bal"], ret=s["rank_ret"], rsk=s["rank_risk"],
            nm=r["name"], cd=r["code"], p0=won(r["p0"]),
            ec=pct(m["e_cum"]), ea=pct(m["e_ann"]), mc=pct(m["med_cum"]),
            p10=pct(m["p10"]), p50=pct(m["p50"]), p90=pct(m["p90"]),
            pl=pct(m["p_loss"]), pl30=pct(m["p_loss30"]),
            so=num(m["sortino"]), cv=pct(m["cvar10"]),
            cf=CONF_KR[r["conf"]], why=r["why"].get(horizon, "")))
    return "\n".join(out)


def shift_table(rows):
    """Part 4: composite rank migration across horizons and risk preferences."""
    rows = sorted(rows, key=lambda r: r["score"][5]["rank_bal"] if 5 in r.get("score", {}) else 99)
    head = "| 종목(코드) | 1년 종합 | 3년 종합 | 5년 종합 | 공격형(5y) | 방어형(5y) | 순위 변화 방향과 이유 |"
    sep  = "|---|---:|---:|---:|---:|---:|---|"
    out = [head, sep]
    for r in rows:
        g = lambda h, k: (r["score"][h][k] if h in r.get("score", {}) else "–")
        out.append(f"| {r['name']}({r['code']}) | {g(1,'rank_bal')} | {g(3,'rank_bal')} | "
                   f"{g(5,'rank_bal')} | {g(5,'rank_agg')} | {g(5,'rank_def')} | {r.get('drift','')} |")
    return "\n".join(out)


def top_list(rows, horizon, key, n=5, label=""):
    order = sorted(rows, key=lambda r: r["score"][horizon][key])[:n]
    return "\n".join(
        f"{i+1}. **{r['name']}**({r['code']}) — "
        + (f"기대누적 {pct(r['m'][horizon]['e_cum'])}" if horizon == 1
           else f"기대연환산 {pct(r['m'][horizon]['e_ann'])}")
        + f", Sortino {num(r['m'][horizon]['sortino'])}, 손실확률 {pct(r['m'][horizon]['p_loss'])}"
        for i, r in enumerate(order))
