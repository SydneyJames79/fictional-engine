"""
KR Equity Multi-Horizon TSR Engine
==================================
Scenario-calibrated Monte Carlo for probability-weighted total shareholder return (TSR),
downside risk metrics and composite ranking across 1/3/5-year horizons.

Design principles (auditable, no hidden magic):
 1. Analyst supplies, per stock x horizon, a THREE-SCENARIO ladder of terminal PER-SHARE
    price multiples (P_T / P_0) plus cumulative cash returned per current share
    (dividends + buybacks, as a fraction of P_0). Probabilities sum to exactly 1.0.
 2. The bear scenario is internally a sub-mixture of "bad but surviving" and
    "permanent capital impairment (ruin)". The REPORTED bear value is the
    probability-weighted mean of that sub-mixture, so the 3 reported probabilities
    still sum to 100% and ruin risk is counted EXACTLY ONCE.
 3. Monte Carlo reproduces those scenario means exactly (lognormal medians are
    shifted by -sigma^2/2 so each regime's arithmetic mean equals the input).
 4. A single common macro factor z drives regime selection across all names via a
    per-stock macro loading lambda, so sector co-movement and index-relative
    statistics are internally consistent (one shared macro world per path).
 5. Shrinkage toward a sector base-rate prior is applied ONCE, in log-multiple space,
    with weight set by data confidence. No second "confidence multiplier" is applied
    anywhere else (no double penalty).
 6. Downside deviation is annualized as DD_raw * sqrt(T) so that Sortino is
    horizon-invariant under i.i.d. returns and 1y/3y/5y are comparable.
"""
import numpy as np
from dataclasses import dataclass, field
from math import sqrt, log, exp

NSIM = 1_000_000
SEED = 20260921

CONF_SHRINK = {"H": 0.15, "M": 0.30, "L": 0.45}   # weight on the base-rate prior


@dataclass
class HorizonSpec:
    """One stock, one horizon."""
    p_bear: float; p_base: float; p_bull: float
    m_bear_surv: float          # terminal price multiple, bad-but-surviving
    m_base: float
    m_bull: float
    cash_bear: float            # cumulative dividends+buybacks / P_0
    cash_base: float
    cash_bull: float
    ruin_given_bear: float      # P(ruin | bear regime)
    m_ruin: float = 0.12        # terminal price multiple if ruin
    sig_bear: float = 0.30      # within-regime lognormal dispersion
    sig_base: float = 0.22
    sig_bull: float = 0.28

    def reported_bear_multiple(self) -> float:
        q = self.ruin_given_bear
        return q * self.m_ruin + (1 - q) * self.m_bear_surv

    def check(self, tag=""):
        s = self.p_bear + self.p_base + self.p_bull
        assert abs(s - 1.0) < 1e-9, f"{tag}: scenario probs sum to {s}, not 1"
        assert 0.0 <= self.ruin_given_bear <= 1.0, f"{tag}: bad ruin prob"
        for v in (self.m_bear_surv, self.m_base, self.m_bull):
            assert v > 0, f"{tag}: non-positive multiple"
        assert self.m_bear_surv <= self.m_base <= self.m_bull, f"{tag}: ladder not monotone"


@dataclass
class Stock:
    code: str
    name: str
    market: str
    sector: str
    p0: float                   # verified close, KRW
    lam: float                  # macro loading in [0,1]; regime score = lam*z + sqrt(1-lam^2)*u
    conf: str                   # "H"/"M"/"L"
    sig_floor: float            # annualized idiosyncratic vol floor (short-history / low-liquidity guard)
    short_history: bool = False # <3y listed -> vol inflation
    horizons: dict = field(default_factory=dict)   # T -> HorizonSpec


def _regime_draw(rng, n, lam):
    z = rng.standard_normal(n)                       # common macro factor (shared)
    u = rng.standard_normal(n)
    s = lam * z + sqrt(max(0.0, 1 - lam * lam)) * u  # ~ N(0,1), correlated across names
    return z, s


def simulate(stock: Stock, T: int, prior_log_mult: float, rng, z_common=None):
    """Return array of total value multiples M = P_T/P_0 + cumulative cash/P_0."""
    h: HorizonSpec = stock.horizons[T]
    h.check(f"{stock.name} T={T}")
    n = NSIM
    if z_common is None:
        z = rng.standard_normal(n)
    else:
        z = z_common
    u = rng.standard_normal(n)
    lam = stock.lam
    s = lam * z + sqrt(max(0.0, 1 - lam * lam)) * u

    # regime thresholds from the supplied probabilities
    from scipy_free_norm import norm_ppf
    t_bear = norm_ppf(h.p_bear)
    t_bull = norm_ppf(h.p_bear + h.p_base)
    is_bear = s < t_bear
    is_bull = s >= t_bull
    is_base = ~is_bear & ~is_bull

    # ---- shrinkage applied ONCE, in log space, to each regime's central multiple ----
    w = CONF_SHRINK[stock.conf]
    def shrink(m):
        return exp((1 - w) * log(m) + w * prior_log_mult)

    m_b_surv = shrink(h.m_bear_surv)
    m_bs     = shrink(h.m_base)
    m_bl     = shrink(h.m_bull)
    m_ruin   = h.m_ruin     # ruin is a structural branch, never shrunk upward

    # ---- TOTAL-volatility calibration (fixes double-counting of dispersion) ----
    # Var(ln M) = E[Var(ln M | regime)] + Var(E[ln M | regime])
    # The regime ladder already supplies Var_across; the within-regime sigma supplies only the REMAINDER
    # up to the target annualized vol. Adding a flat floor on top would double-count the spread.
    infl = 1.25 if stock.short_history else 1.0
    sig_ann = stock.sig_floor * infl                 # sig_floor now means TARGET annualized vol
    DAMP = 0.85                                      # <1.0: valuation mean reversion damps long-horizon variance
    target_var = (sig_ann ** 2) * (T ** DAMP)
    ps = [h.p_bear, h.p_base, h.p_bull]
    ls = [log(m_b_surv), log(m_bs), log(m_bl)]
    mu_a = sum(p * l for p, l in zip(ps, ls))
    var_across = sum(p * (l - mu_a) ** 2 for p, l in zip(ps, ls))
    var_within = max(target_var - var_across, (0.30 * sig_ann) ** 2 * (T ** DAMP))
    sg = sqrt(var_within)
    sg_b = sg_s = sg_l = sg

    M = np.empty(n)
    # base
    nb = is_base.sum()
    if nb:
        M[is_base] = np.exp(rng.normal(log(m_bs) - 0.5 * sg_s**2, sg_s, nb))
    # bull
    nl = is_bull.sum()
    if nl:
        M[is_bull] = np.exp(rng.normal(log(m_bl) - 0.5 * sg_l**2, sg_l, nl))
    # bear: sub-mixture of survive / ruin
    nbe = is_bear.sum()
    if nbe:
        ruin_flag = rng.random(nbe) < h.ruin_given_bear
        out = np.empty(nbe)
        n_ruin = ruin_flag.sum()
        if n_ruin:
            out[ruin_flag] = np.exp(rng.normal(log(m_ruin) - 0.5 * 0.55**2, 0.55, n_ruin))
        n_surv = nbe - n_ruin
        if n_surv:
            out[~ruin_flag] = np.exp(rng.normal(log(m_b_surv) - 0.5 * sg_b**2, sg_b, n_surv))
        M[is_bear] = out

    # ---- cash returned to shareholders, scenario-dependent, no reinvestment ----
    cash = np.where(is_bear, h.cash_bear, np.where(is_bull, h.cash_bull, h.cash_base))
    # ruin paths forfeit most of the assumed future cash return
    if nbe:
        idx = np.where(is_bear)[0]
        cash[idx[ruin_flag]] *= 0.25
    return M + cash


def metrics(M, T, rf, idx_ann_mean=None):
    import numpy as np
    r_cum = M - 1.0
    r_ann = np.power(np.maximum(M, 1e-9), 1.0 / T) - 1.0
    e_cum = r_cum.mean()
    e_ann = (1.0 + e_cum) ** (1.0 / T) - 1.0          # from expected cumulative
    med_cum = float(np.median(r_cum))
    p10, p50, p90 = np.percentile(r_cum, [10, 50, 90])
    p_loss = float((r_cum < 0).mean())
    p_loss30 = float((r_cum < -0.30).mean())
    q10 = np.percentile(r_cum, 10)
    cvar10 = float(r_cum[r_cum <= q10].mean())
    # Sortino: MAR = rf; downside dev of ANNUALIZED returns, rescaled by sqrt(T)
    short = np.minimum(0.0, r_ann - rf)
    dd_raw = float(sqrt((short**2).mean()))
    dd_ann = dd_raw * sqrt(T)
    sortino = (e_ann - rf) / dd_ann if dd_ann > 1e-6 else float("nan")
    lr = np.log(np.maximum(M, 1e-9))
    vol_ann = float(lr.std() / sqrt(T))
    out = dict(vol_ann=vol_ann, e_cum=e_cum, e_ann=e_ann, med_cum=med_cum, med_ann=(1+med_cum)**(1/T)-1,
               p10=p10, p50=p50, p90=p90, p_loss=p_loss, p_loss30=p_loss30,
               cvar10=cvar10, dd_ann=dd_ann, sortino=sortino)
    if idx_ann_mean is not None:
        out["excess_ann"] = e_ann - idx_ann_mean
    return out


def pct_rank(vals, higher_is_better=True):
    """0-100 percentile within the cross-section (ties averaged)."""
    v = np.asarray(vals, float)
    if not higher_is_better:
        v = -v
    order = v.argsort()
    ranks = np.empty(len(v), float)
    ranks[order] = np.arange(len(v), dtype=float)
    # average ties
    for val in np.unique(v):
        m = v == val
        if m.sum() > 1:
            ranks[m] = ranks[m].mean()
    return 100.0 * ranks / (len(v) - 1) if len(v) > 1 else np.full(len(v), 50.0)


WEIGHTS = {
    "balanced":   dict(ret=0.60, sortino=0.25, cvar=0.15),
    "aggressive": dict(ret=0.75, sortino=0.15, cvar=0.10),
    "defensive":  dict(ret=0.40, sortino=0.35, cvar=0.25),
}
