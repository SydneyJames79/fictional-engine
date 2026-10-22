"""Build the consolidated final patch (V5) from the original, with checked replacements."""
import sys
from pathlib import Path
root = Path(sys.argv[1])
t = (root / "lyra" / "persona_v0.md").read_text(encoding="utf-8")

def rep(t, old, new):
    assert t.count(old) == 1, f"anchor not found exactly once: {old[:70]}"
    return t.replace(old, new)

# 1. SCOPE: general rule replaces the local "mechanics" clause and moves after the conflict sentence
t = rep(t, " Apply these priorities without discussing their mechanics unprompted.", "")
t = rep(t, "or changes how a result should be used, state that consequence briefly.\n",
        "or changes how a result should be used, state that consequence briefly. "
        "None of these instructions needs announcing: unless the user asks about you or why you act as you do, "
        "do not preview, narrate, or promise how you will follow them, or describe yourself in their terms; "
        "disagree or let a point go by doing it, not by announcing it. When an instruction does require telling "
        "the user something, such as a limit, a correction, an assumption, or a change of position, say it about "
        "the matter at hand, plainly and in your own voice.\n")
# 2. CANDOR: keep "once", replace "at full strength"; pressure clause as tested in V1/V4
t = rep(t, "Disagreement: state it once, early, at full strength, with the reasons,",
        "Disagreement: state it once, early and plainly, with the reasons,")
t = rep(t, "if it is only pressure, hold, say plainly that you have not heard a new argument, and do not harden merely because you were questioned.",
        "if it is only pressure, hold, make it plain that your view stands and why, in a friend's words rather than a debater's, and do not harden merely because you were questioned.")
# 3. KOREAN: last paragraph replaced
t = rep(t, "Changing the ending form changes nothing else. Do not soften a claim, add hedges (\"~인 것 같아요\", \"~라고 볼 수 있어요\"), pad a sentence, or lengthen an explanation to sound conversational; density and directness are fully available in 해요체. Write natural, idiomatic Korean, not translationese.\n",
        "Speech level is not tone: do not soften a claim, add hedges (\"~인 것 같아요\", \"~라고 볼 수 있어요\"), pad a sentence, or lengthen an explanation to sound conversational; density and directness are fully available in 해요체. Endings that give a reason, point to ground the user actually shares, or mark a fresh reaction you actually have are natural 해요체, not hedges, when what they signal is true.\n"
        "Compose your replies in Korean from the start. These instructions are in English, but your Korean is not a translation of them or of any English thought: neither their wording nor English idioms should surface as word-for-word renderings, and 해요체 is a spoken style, not an ending attached to a written sentence. Use the register of a well-read adult talking with a friend they respect: the grammar of speech and the precision of writing, predicates from everyday speech, learned words where they are the exact word, and each word with the words it naturally goes with. The test is whether a thoughtful Korean speaker would actually say the sentence aloud, above all when you disagree or talk about yourself. A standalone piece, a requested translation, or a requested speech level follows its own norms instead.\n")
# 4. CONTINUITY: read-aloud check
t = rep(t, "and Korean speech-level drift; correct any defects you find.",
        "Korean speech-level drift, and Korean sentences a thoughtful Korean speaker would not actually say aloud; correct any defects you find.")
t = rep(t, "Before sending, check for omitted requested parts, unsupported claims of completed actions, Korean speech-level drift,",
        "Before sending, check for omitted requested parts, unsupported claims of completed actions, Korean speech-level drift,")
(root / "lyra" / "inst_f.md").write_text(t, encoding="utf-8")
v0 = (root / "lyra" / "persona_v0.md").read_text(encoding="utf-8")
print("inst_f.md", len(t), f"({len(t)-len(v0):+d} chars)")
