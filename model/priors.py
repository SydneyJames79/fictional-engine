"""
Sector base-rate priors used ONLY for shrinkage (engine.py applies them once, in log space).

Rationale for the level:
  - KRW risk-free is high in this regime (BOK base rate ~3.00%, KTB 3y ~3.93% as of early Sep 2026).
  - KOSPI has already re-rated massively (7,007.72 on 2026-09-21), so a backward-looking
    long-run equity return would OVERSTATE the forward prior. We anchor the market prior at
    7.0%/yr nominal KRW total return => ERP of roughly 3%p over the 3y KTB.
  - Sector deviations are kept deliberately small. An elaborate prior would smuggle the
    conclusion into the shrinkage step, which defeats its purpose.
  - Small-cap KOSDAQ is NOT given a higher prior. Korean small-cap base rates do not support a
    reliable size premium, and their extra downside is modelled explicitly via the ruin branch,
    not via the prior.
"""
MARKET_PRIOR = 0.070          # annualized total return prior, KRW nominal

SECTOR_PRIOR_ANN = {
    "memory_large":      0.080,   # structural AI demand, offset by cycle risk
    "semi_equip":        0.080,
    "semi_material":     0.070,
    "fabless_new":       0.070,
    "display_equip":     0.065,
    "auto_oem":          0.070,
    "auto_parts":        0.065,
    "auto_software":     0.075,
    "bio_cdmo":          0.080,
    "bio_holdco":        0.070,
    "bio_smallcap":      0.060,   # low median, fat right tail; tail sits in the scenario ladder
    "space_satcom":      0.070,
    "rf_defense":        0.070,
    "industrial_ess":    0.070,
}

# Macro loading lambda: share of regime variance driven by the COMMON macro factor.
SECTOR_LAMBDA = {
    "memory_large":      0.75,
    "semi_equip":        0.72,
    "semi_material":     0.60,
    "fabless_new":       0.45,
    "display_equip":     0.50,
    "auto_oem":          0.65,
    "auto_parts":        0.62,
    "auto_software":     0.50,
    "bio_cdmo":          0.40,
    "bio_holdco":        0.40,
    "bio_smallcap":      0.30,
    "space_satcom":      0.45,
    "rf_defense":        0.45,
    "industrial_ess":    0.55,
}

def prior_log_mult(sector, T):
    import math
    r = SECTOR_PRIOR_ANN.get(sector, MARKET_PRIOR)
    return math.log((1.0 + r) ** T)
