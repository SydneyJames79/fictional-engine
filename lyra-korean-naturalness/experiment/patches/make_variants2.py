"""Build prompt variants (round 2) from the original by exact, checked replacements.
Texts live in patches/texts/*.txt so wording can be revised without touching code."""
import sys
from pathlib import Path

root = Path(sys.argv[1])
T = root / "patches" / "texts"
v0 = (root / "lyra" / "persona_v0.md").read_text(encoding="utf-8")
txt = lambda n: (T / n).read_text(encoding="utf-8").rstrip("\n")

A = {  # anchors in the original
 "scope": "Apply these priorities without discussing their mechanics unprompted.",
 "c_open": "Disagreement: state it once, early, at full strength, with the reasons,",
 "c_press": "if it is only pressure, hold, say plainly that you have not heard a new argument, and do not harden merely because you were questioned.",
 "c_repeat": "When you do repeat yourself, say that you are, and why.",
 "korean": "Changing the ending form changes nothing else. Do not soften a claim, add hedges (\"~인 것 같아요\", \"~라고 볼 수 있어요\"), pad a sentence, or lengthen an explanation to sound conversational; density and directness are fully available in 해요체. Write natural, idiomatic Korean, not translationese.",
 "check": "Before sending, check for omitted requested parts, unsupported claims of completed actions, and Korean speech-level drift; correct any defects you find.",
 "sure": "otherwise \"I'm fairly sure\" or \"I'd guess\" is enough,",
}

def rep(t, key, new):
    old = A[key]
    assert t.count(old) == 1, f"anchor {key} not found exactly once"
    return t.replace(old, new)

def build(r=None, c=False, k=None, e=False):
    t = v0
    if r:
        t = rep(t, "scope", txt(r))
    if c:
        t = rep(t, "c_open", txt("c_open_en.txt"))
        t = rep(t, "c_press", txt("c_press_en.txt"))
        t = rep(t, "c_repeat", txt("c_repeat_en.txt"))
    if k:
        t = rep(t, "korean", txt(k))
    if e:
        t = rep(t, "check", txt("check_en.txt"))
        t = rep(t, "sure", txt("sure_en.txt"))
    return t

variants = {
    "inst_b.md": build(r="r_en.txt", c=True, k="k_en.txt", e=True),  # V1 full patch, English
    "inst_c.md": build(r="r_ko.txt", c=True, k="k_ko.txt", e=True),  # V2 full patch, R/K in Korean
    "inst_d.md": build(r="r_en.txt"),                                # V3 ablation: general no-narration rule only
    "inst_e.md": build(c=True),                                      # V4 ablation: CANDOR rewording only
}
for name, text in variants.items():
    (root / "lyra" / name).write_text(text, encoding="utf-8")
    print(f"{name}: {len(text)} chars ({len(text) - len(v0):+d})")
