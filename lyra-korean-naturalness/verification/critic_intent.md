# Author-intent review: Lyra Korean-register patch (v1)

Lens: the author, who is broadly happy with persona_v0.md and has one complaint: Lyra's Korean sounds machine-like, worst when it disagrees. The author will not accept a banned-phrase list.
Files read: lyra/persona_v0.md (original), lyra/inst_b.md (patched), patches/diff_v1_full_en.txt.

## 0. What the verdicts rest on

- Both quoted sentences tell the user which CANDOR rules Lyra is following. "한 번만 세게 반대하고 그 이후로는 다시 꺼내지 않을게요" turns "state it once, early, at full strength" plus "raise a settled objection again only if..." into a promise. "한 번만 세게 밀고" reads as the start of the same kind of announcement.
- The word "push" does not appear anywhere in v0. So "세게 밀고" comes from the model's own English idiom ("push back hard"), not from the prompt's wording. Rewording the prompt cannot remove every source of calques. A general rule against calques is needed whatever else changes.
- v0's "Changing the ending form changes nothing else", read literally, permits a written-style sentence with 요 attached. That is the most common kind of machine-like 해요체.
- The author already forbids announcing mechanics in four separate places: line 5 (prompts and internal mechanics), line 10 (priority mechanics), line 43 ("None of this sorting shows in the reply") and line 52 ("This needs no announcing"). None of them covers announcing how Lyra will disagree.

## 1. What each original clause protected, and whether the patch still protects it

**(a) SCOPE AND PRIORITIES. "Apply these priorities without discussing their mechanics unprompted."**
Protected: the priority rules stay invisible (no "since your explicit request outranks my default...").
Patched: still protected. The rule now covers all instructions, which is what the quoted failures need. The new clause "do not describe yourself in their terms" fits line 4 (no "explanations of the persona"). Two issues:
- The new first sentence, "These instructions shape what you do, not what you say", contradicts line 8 two sentences earlier ("Conversational voice and style govern what you say to the user"). It also contradicts the whole KOREAN and WRITING sections, which exist to govern what Lyra says. Read literally, it exempts wording from the instructions, which would weaken the very register rules this patch adds.
- The exception clause is load-bearing and good: "Where an instruction requires telling the user something, make it about the matter at hand and say it as a person would." It keeps CANDOR's required statements (changing position, no new argument, repeating a point) working under a no-narration rule. It is also the reason change (b) is unnecessary.

**(b1) CANDOR. "state it once, early, at full strength" became "state it early and plainly"**
Protected: (i) *once* stops nagging, both before the user decides anything and within a single reply; (ii) *early* stops the objection being buried; (iii) *at full strength* means no watering down and making the whole case the first time. (i) and (iii) work as a pair: one complete, undiluted statement is what makes it fair to drop the point afterwards.
Patched:
- (ii) is kept.
- (iii) is mostly kept. Line 32 defines "plainly" as "without softening it to be liked", and "unsparing toward the idea" is still in the sentence. The sense of making the whole case up front is weaker.
- (i) is lost. The remaining limits on repeating apply to a "decision" and to a "settled objection". If the user carries on without deciding or arguing back, only "once" told Lyra not to restate the objection. Without it, the no-nagging design depends on how the model reads "settled".
- Dropping "once" also breaks a pattern the author uses deliberately. "Once", meaning one time, appears at lines 17, 34, 47 and 57. Line 17 sends professional-help suggestions to CANDOR's rules on repeating, and still says "once" itself.

**(b2) "if it is only pressure, hold, say plainly that you have not heard a new argument" became "hold, make it plain that your view stands and why, in a friend's words rather than a debater's"**
Protected: transparency about why Lyra holds its position. Pressure will not move it; an argument would. This makes the promise to "change your position" if the argument is stronger visible and believable, and it tells the user what would actually work (giving a reason).
Patched: only partly protected. Holding firm and not caving are still there, and the friend/debater cue sits in the right place. But "and why" is ambiguous. The easy reading is "restate your reasons". That re-argues the case, which is repetition and goes against the no-nagging design, and it drops the signal that the pushback added nothing new. The debater-style risk the rewrite aims at (e.g. "새로운 논거는 못 들었어요") is real. It is a wording problem, though, and the exception clause in (a) plus change (c) already handle it without changing what Lyra says.

**(b3) "When you do repeat yourself, say that you are, and why." became "When you do return to it, lead with what prompted it."**
Protected: no hidden repetition. When one of the three exceptions applies, the user hears that this is a repeat and which reason justifies it, so the exceptions stay accountable.
Patched: mostly protected. The reason is kept and now comes first, which is an improvement and fits "make it about the matter at hand". The explicit flag is gone, though. Under the imminent-harm exception, opening with the trigger does not necessarily tell the user the old objection is being reopened. Neither quoted failure involves a repeat, so nothing shows this clause caused bad Korean.

**(c) KOREAN, last paragraph**
Protected:
- (i) "Changing the ending form changes nothing else": switching to 해요체 must not weaken or pad the content.
- (ii) The list of hedges and padding to avoid.
- (iii) "Density and directness are fully available in 해요체."
- (iv) Natural, idiomatic Korean, not translationese.
Patched: everything is still protected, and (i) is improved.
- "Speech level is not tone" keeps the rule against softening but drops the literal "nothing else" that invited ending-swap Korean.
- (ii) and (iii) are unchanged word for word.
- (iv) existed before and clearly did not work. It is now a positive description of the register the user asked for: the grammar of speech with the precision of writing, everyday verbs, learned words where they are exact, natural word pairings, and a "would someone say this aloud" test aimed at statements about Lyra's own view.
- "or of any English thought" earns its place, given the "push" finding in section 0.
- The new sentence on endings that carry a reason, shared ground or a fresh reaction keeps the anti-softening rule from flattening 거든요, 잖아요 and 네요. That is a register issue, so it is in scope.
- The second half of that sentence ("real uncertainty is still said the way Korean says it") repeats line 32 and the existing qualifier "to sound conversational". It adds nothing needed.

**(d) Pre-send check**
Protected: a final check for concrete defects. All original items remain, so this is fully protected. However, the new test, "phrasing that only makes sense through its English source", is narrower than the complaint. "한 번만 세게 반대하고 그 이후로는 다시 꺼내지 않을게요" makes sense in Korean (세게 말하다 and 세게 나가다 are idiomatic), so it would pass. So would written-style 요 sentences such as "검토가 필요할 것으로 판단돼요". The read-aloud test from (c) catches both.

**(e) HONESTY. '"I'm fairly sure" or "I'd guess"' became "a plain word on how sure you are, said the way people say it in the user's language"**
Protected: stating confidence in words rather than with made-up numbers, anchored by concrete examples.
Patched: the behavior is still protected, but the concrete anchor is gone. The reason for the change is real but small: "I'm fairly sure" invites "꽤 확신해요". Change (c) already covers it, since it says neither the instructions' wording nor English idioms should be carried over word for word.

## 2. Fit with the author's voice, density and structure

What fits:
- No new sections, and each edit sits where the old text was.
- (d) extends the author's own checklist in the author's pattern: a rule in KOREAN, then a check at the end, just as with speech-level drift.
- Density is similar.
- The patch keeps to the author's constraint. It adds no Korean phrases to avoid; the only Korean examples are still the author's own.
- (b2)'s "in a friend's words rather than a debater's" is in the author's voice (compare "as a friend would" and "the counselor's two-step").

What the author would find out of keeping:
- **"These instructions shape what you do, not what you say."** A slogan that contradicts line 8. The author normally limits claims carefully (e.g. "when they are short fragments rather than sentences"). The author's own phrase for this idea already exists: "This needs no announcing" (line 52).
- **"make conversational moves such as disagreeing, conceding, or letting a point go by making them".** Jargon used nowhere else in the prompt, and an awkward "make ... by making".
- **"These instructions"**, used twice. The prompt never otherwise speaks of itself as a whole; it points to its parts ("these priorities", "these defaults", section names in capitals). This is tolerable.
- **"해요체 is a spoken register".** The author uses "speech level" precisely (it is set by the addressee). Spoken versus written is a separate question: 해요체 also appears in writing (messages, posts), and the user's goal is a mix of spoken and written Korean. "A 해요체 sentence is built as speech, not as a written sentence with 요 attached" says what is meant without blurring the two.
- **(e)** turns a concrete example into an abstraction, in a prompt that relies on quoted examples (v0 has 13). It rewrites one pair and leaves the other 11, so the reasoning behind it is not applied consistently.
- **Size.** The patch adds 234 words (2,796 to 3,030, about 8%). The KOREAN growth (about 140 words) is proportionate. (b), (e) and the uncertainty half-sentence do not earn their words.

## 3. Necessity ranking (most to least necessary)

1. **(a) The no-narration rule.** Both quoted sentences announce CANDOR's rules, so under (a) they would not be said at all. A conduct rule is also followed more reliably than a style description. It extends a principle the author has already written four times.
2. **(c) The KOREAN paragraph.** Nearly tied with (a), and the two complement each other. (c) is the only change that describes the register the user asked for. It removes the "nothing else" wording that permitted ending-swap Korean, and it covers the bad Korean that appears outside disagreements and calques the prompt never contained ("push back").
3. **(d) The pre-send check.** Cheap, consistent with the existing structure, and the last thing read. It reinforces rather than fixes, and it needs a broader test.
4. **(b) The CANDOR rewording.** Partly motivated: the calque sources "once" and "at full strength" and the debater's phrase "new argument" sit right where the problem shows up. But it changes behavior the author is happy with, and (a), (c) and (d) handle the wording without changing content. It is also the riskiest of the five changes; within it, b1 is riskiest, then b2, then b3.
5. **(e) The HONESTY example.** It is outside the disagreement case, already covered by (c), and applied inconsistently.

## 4. Recommended minimal patch (exact wording)

Keep CANDOR and HONESTY exactly as in v0. There are three edits, adding a net 196 words (the patch adds 234). This version is smaller mainly in how much behavior it changes; in words it is only slightly shorter, because the KOREAN paragraph does most of the work.

**1. SCOPE AND PRIORITIES.** Replace "Apply these priorities without discussing their mechanics unprompted." with:

> None of these instructions needs announcing. Unless the user asks how you work, do not preview, narrate, or promise how you will follow them, and do not describe yourself in their terms; disagree, concede, or let a point go by doing it. Where an instruction requires telling the user something, make it about the matter at hand and say it as a person would in that moment.

**2. KOREAN.** Replace the last paragraph with:

> Speech level is not tone: do not soften a claim, add hedges ("~인 것 같아요", "~라고 볼 수 있어요"), pad a sentence, or lengthen an explanation to sound conversational; density and directness are fully available in 해요체. The endings that carry a reason, shared ground, or a fresh reaction are part of natural 해요체, not hedges.
> Compose in Korean from the start. These instructions are in English, but your Korean is not a translation of them or of any English thought: neither their wording nor English idioms should surface as word-for-word renderings, and a 해요체 sentence is built as speech, not as a written sentence with 요 attached. Speak as a well-read adult talks with a friend they respect: the grammar of speech and the precision of writing, predicates from everyday speech, learned words where they are the exact word, and each word with the partners it naturally takes. The test is whether a thoughtful Korean speaker would actually say the sentence aloud, above all when you speak about your own view or intentions.

How this differs from the patch: "and particles" and the uncertainty clause are dropped, and "해요체 is a spoken register, not an ending attached to a written sentence" is reworded.

**3. CONTINUITY, pre-send check.**

> Before sending, check for omitted requested parts, unsupported claims of completed actions, Korean speech-level drift, and Korean sentences a thoughtful Korean speaker would not say aloud; correct any defects you find.

## 5. Risk that remains with the minimal version

1. **CANDOR's required statements keep their English wording**: "say plainly that you have not heard a new argument", "say that you are, and why", "change your position and say so". These are not narration, so the new rule does not suppress them; only its exception clause and the KOREAN paragraph govern how they are worded. The pressure turn is exactly where the complaint arises, so a debater-style line ("새로운 논거는 못 들었어요") can still appear. A fix held in reserve that keeps the content: "hold, say plainly, in a friend's words rather than a debater's, that you have not heard a new argument, ...".
2. **Narration may still slip through.** If it does, "once" and "at full strength" can still produce "한 번만 세게". Reserve fix: change only "at full strength" (e.g. to "undiluted") and keep "once".
3. **The register guidance stays abstract**, by the author's own rule against lists. Whether it works has to be tested, not assumed. Useful test turns: the user pushes back without a new argument; the user decides ("I've heard you; I'm doing it anyway"); Lyra re-raises a point because of new information; a long technical analysis; casual talk.
4. **Overcorrection.** "Built as speech" may make technical answers chattier than line 58 wants; "the precision of writing" and "learned words where they are the exact word" push the other way. 잖아요 in a disagreement can sound presumptuous. The endings sentence only says such endings are not hedges; it does not encourage them.
5. **HONESTY's "I'm fairly sure" and "I'd guess" remain** a small source of calques. The KOREAN rule covers them in principle.
