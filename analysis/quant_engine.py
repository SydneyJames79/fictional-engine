"""시나리오 혼합분포 몬테카를로, 위험지표, 순위 산정 엔진.

입력(JSON): 종목별·기간별 시나리오 목록(확률, 기간 말 주당가치, 누적 주당배당), 기준가,
            목표 총변동성, 무위험수익률, 지수 기대수익률.
원칙
- 각 시나리오 i의 누적 총수익 배수 G_i = (V_i + D_i) / P0.
- 시나리오 내부 잡음은 평균 1의 로그정규 배수: ln(eps) ~ N(-s^2/2, s^2). 따라서 확률가중 기대 TSR은
  분석가 시나리오의 확률가중 평균과 정확히 같다(잡음이 기대값을 부풀리지 않음).
- s(T)는 혼합분포 전체의 로그수익률 표준편차가 목표치 sigma_f * sqrt(T) * m(T)에 맞도록 보정하되,
  시나리오 간 분산이 이미 목표를 넘으면 하한 s_floor * sqrt(T)만 둔다.
"""
import json
import math
import numpy as np

HORIZONS = {'h1': 1.0, 'h3': 3.0, 'h5': 5.0}
MEANREV = {'h1': 1.0, 'h3': 0.92, 'h5': 0.85}   # 장기 로그분산의 약한 평균회귀 보정
S_FLOOR = 0.10                                   # 시나리오 내부 잡음의 연환산 하한
N_SIM = 400_000


def mixture_stats(probs, gross):
    lg = np.log(np.maximum(gross, 1e-6))
    m = np.sum(probs * lg)
    v = np.sum(probs * (lg - m) ** 2)
    return m, v


def calibrate_within_sigma(probs, gross, sigma_f, T, key):
    """시나리오 내부 잡음 s(T)를 정한다(연환산이 아닌 기간 전체 기준)."""
    target = sigma_f * math.sqrt(T) * MEANREV[key]
    _, between_var = mixture_stats(probs, gross)
    floor = S_FLOOR * math.sqrt(T)
    s2 = target ** 2 - between_var
    return max(math.sqrt(s2) if s2 > 0 else 0.0, floor), target, math.sqrt(between_var)


def simulate(probs, gross, s, rng, n=N_SIM):
    probs = np.asarray(probs, float)
    gross = np.asarray(gross, float)
    idx = rng.choice(len(probs), size=n, p=probs / probs.sum())
    z = rng.standard_normal(n)
    eps = np.exp(-0.5 * s * s + s * z)
    return gross[idx] * eps - 1.0          # 누적 TSR 표본


def metrics(tsr, T, rf_ann):
    """누적 TSR 표본에서 지표를 계산한다. rf_ann은 소수(예: 0.028)."""
    tsr = np.asarray(tsr)
    exp_cum = tsr.mean()
    exp_ann = (1 + exp_cum) ** (1 / T) - 1 if exp_cum > -1 else -1.0
    q = np.percentile(tsr, [10, 50, 90])
    p_loss = (tsr < 0).mean()
    p_loss30 = (tsr < -0.30).mean()
    k = max(1, int(len(tsr) * 0.10))
    cvar10 = np.sort(tsr)[:k].mean()
    # 하방편차: 로그 누적수익률이 기간 무위험 누적수익률에 못 미치는 부분의 제곱평균, sqrt(T)로 연환산
    lr = np.log1p(np.maximum(tsr, -0.999999))
    hurdle = T * math.log1p(rf_ann)
    dd_T = math.sqrt(np.mean(np.minimum(lr - hurdle, 0.0) ** 2))
    dd_ann = dd_T / math.sqrt(T)
    sortino = (exp_ann - rf_ann) / dd_ann if dd_ann > 0 else float('nan')
    med_ann = (1 + q[1]) ** (1 / T) - 1
    return {
        'exp_cum': exp_cum, 'exp_ann': exp_ann, 'median_cum': q[1], 'median_ann': med_ann,
        'p10': q[0], 'p50': q[1], 'p90': q[2], 'p_loss': p_loss, 'p_loss30': p_loss30,
        'cvar10': cvar10, 'downdev_ann': dd_ann, 'sortino': sortino,
    }


def pct_rank(values, higher_better=True):
    """0~100 백분위(동점은 평균순위). N=1이면 100."""
    v = np.asarray(values, float)
    n = len(v)
    if n == 1:
        return np.array([100.0])
    order = v if higher_better else -v
    ranks = np.empty(n)
    sorted_idx = np.argsort(order, kind='mergesort')
    i = 0
    while i < n:
        j = i
        while j + 1 < n and order[sorted_idx[j + 1]] == order[sorted_idx[i]]:
            j += 1
        avg = (i + j) / 2.0
        for t in range(i, j + 1):
            ranks[sorted_idx[t]] = avg
        i = j + 1
    return ranks / (n - 1) * 100.0


def rank_desc(values):
    """1이 가장 좋은 순위(큰 값 우선). 동점은 같은 순위."""
    v = np.asarray(values, float)
    order = np.argsort(-v, kind='mergesort')
    r = np.empty(len(v), int)
    prev, cur = None, 0
    for pos, i in enumerate(order):
        if prev is None or v[i] != prev:
            cur = pos + 1
            prev = v[i]
        r[i] = cur
    return r


if __name__ == '__main__':
    # 자체 점검: 2-시나리오 예제에서 기대값 보존과 지표 계산 확인
    rng = np.random.default_rng(7)
    probs = np.array([0.3, 0.5, 0.2])
    gross = np.array([0.6, 1.1, 1.8])
    s, target, between = calibrate_within_sigma(probs, gross, 0.45, 1.0, 'h1')
    t = simulate(probs, gross, s, rng)
    m = metrics(t, 1.0, 0.028)
    print('within s=%.3f target=%.3f between=%.3f' % (s, target, between))
    print('analyst E[TSR]=%.4f  simulated=%.4f' % ((probs * gross).sum() - 1, m['exp_cum']))
    print({k: round(float(v), 4) for k, v in m.items()})
    print(pct_rank([3, 1, 2, 2]), rank_desc([3, 1, 2, 2]))
