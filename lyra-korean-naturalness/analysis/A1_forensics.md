# A1: Forensic analysis of `persona_v0.md` as a cause of machine-like Korean

**Source analysed:** `scratchpad/lyra/persona_v0.md` (69 lines, 2,796 words). Line references like "L34" are to that file. No other file was consulted.

**Conventions**

- **[O]**: directly observable in the instruction text, such as a quote, a count, or the presence or absence of a word.
- **[I]**: inference about how the model behaves or how Korean is used. Confidence is marked high, med or low.
- **Limits.** There are two examples, and (1) is a fragment whose continuation is unknown. There are no transcripts and no model runs. Judgements about Korean collocation and register are the analyst's own, so they count as [I].
- **Unverifiable alternative.** If the user's own turn contained 세게, 밀다 or similar, those words are echoes of the user, not calques. Nothing in the material rules this out. The analysis below assumes they were not.

---

## 0. Bottom line

1. **Both examples restate one rule, the CANDOR disagreement procedure (L34), as a promise to the user.** The correspondence is term for term:
   - "state it once" → 한 번만
   - "at full strength" → 세게
   - "without repeating, hinting, or re-litigating" and "Raise … again only if …" → 그 이후로는 다시 꺼내지 않을게요

   The source text is [O]; the mapping is [I-high].
2. **The single most unnatural word, 밀다, has no source in the file.** No "push" or "press" appears anywhere. The best explanation is the English assistant idiom "push back (hard)". So the frame comes from the prompt and the verb comes from the model's English-shaped repertoire. The absence is [O]; the origin is [I-med-high].
3. **The file itself makes this narration likely.** L34 explicitly requires narration in three places. The file has six "don't announce" clauses, but each covers a different section and none covers CANDOR. The limit on repeating an objection is stated or cross-referenced on four lines. All of this is [O].
4. **The KOREAN section is a background contributor, not the proximate cause.** It polices sentence endings closely: there are 19 mentions of speech level or endings, and the pre-send check covers only speech-level drift. Idiom gets one six-word sentence with no examples and no check. [O]
5. **Mostly this is not a wait-for-the-next-model problem.** The calque tendency is model-level, but it surfaces mainly when the model talks about its own conduct. The prompt currently elicits that kind of talk, and it can stop eliciting it. [I-med]

---

## 1. Where each example comes from

### 1.1 Source text (exact quotes)

**L34**, the relevant parts:

> "Disagreement: state it once, early, at full strength, with the reasons, warm toward the person and unsparing toward the idea. A decision ("I've heard you; I'm doing it anyway") ends the argument: respect it and help them do it well, without repeating, hinting, or re-litigating. […] Raise a settled objection or concern again only if the user asks to revisit it, new information materially changes the stakes, or an unresolved risk of serious harm is imminent; that a choice is irreversible, or that the user still disagrees, is not by itself a reason. When you do repeat yourself, say that you are, and why."

**Lines that reinforce it:**

- L9: "importance alone does not override a listening-only request or the limits on repeating a settled objection."
- L17: "say so once, specifically, as a friend would, and return to it only under CANDOR's conditions for repeating a concern."
- L40: "the decision stays the user's; whether it is raised again is governed by CANDOR."

**Context fit.** Both examples arose while the assistant was advising against the user's opinion. That is exactly the situation L34 opens with ("Disagreement:"). The context comes from the user's report; the fit is [I-high].

### 1.2 Segment-by-segment mapping

| Korean segment | Closest source wording | Mechanism | Status |
|---|---|---|---|
| 한 번만 | "state it once" (L34). The same restrictive "once" appears on L17, L47 and L57. | Literal rendering of a quantifier from the procedure. 만 renders the "only" implied by the contrast with "without repeating". | Source [O]; mapping [I-high] |
| 세게 | "at full strength" (L34), or "hard" from the English collocation "push back hard" (not in the file) | An intensity setting from the rule becomes an adverb of physical force. | "at full strength" [O]; which route [I-med] |
| 밀고 (ex. 1) | **None.** The file has no "push", "press" or "push back". Its only near neighbour, "pressure" (L32, L34), is used in the opposite sense: candor "is not insult, pressure…", and "if it is only pressure, hold". | An English idiom imported from outside the prompt | Absence [O]; origin [I-med-high] |
| 반대하고 (ex. 2) | "Disagreement:" (L34); "objection" (L9, L34) | Direct rendering of the rule's subject | [I-high] |
| 그 이후로는 | "A decision … ends the argument" marks a time boundary; English "and then …" | Means "after that / from then on". Grammatical, but slightly written; 그다음부터는 or 그 뒤로는 would sound more spoken. | [I-med] |
| 다시 꺼내지 않을게요 | "without repeating, hinting, or re-litigating" and "Raise … again only if …" (L34); "whether it is raised again" (L40) | A constraint becomes a first-person promise. 꺼내다 ("bring up") is itself idiomatic Korean, which is why this half sounds less off. | [I-high] |
| -(으)ㄹ게요 (promise) | Nothing in the file asks for a promise. | A rule about the assistant's own behaviour is turned into a commitment to the listener. | Absence [O]; mechanism [I-high] |
| (not realised) | "early", "with the reasons" | Neither example contains reasons. The announcement stands in for, or comes before, the actual case. | [O] for the examples as given |

### 1.3 Which mechanisms apply

- **M1: the procedure is spoken aloud as a promise. Applies, and is the primary mechanism.**
  - The examples say nothing about the user's plan. They are entirely about how the assistant will conduct the disagreement.
  - Every element is a setting from L34: how often, how hard, when, and what happens afterwards.
  - The Korean promissory ending -ㄹ게요 makes the conversion grammatically effortless. [I-high]
- **M2: vivid English wording rendered literally. Applies.** "once" and "at full strength" are quantities that are easy to say aloud, and they surface as 한 번만 and 세게. [I-high]
- **M3: an English assistant idiom that is not in the prompt. Applies to 밀다.** See §2.
- **M4: echo of a quoted example. Does not apply.**
  - None of the file's 13 quoted English strings resembles these phrases. They are on L13, L16, L24 (2), L28 (3), L34, L46, L47, L55 (2) and L62. [O]
  - The only quote inside L34, "I've heard you; I'm doing it anyway", is the user's line, not the assistant's. [O]
  - Echoing is still a risk elsewhere in the file (see §3, L24), but it is not how these two examples arose.

### 1.4 Why this rule gets narrated when most others don't

**Observed facts [O]:**

- **(a) L34 itself orders narration three times:**
  - "change your position and say so"
  - "say plainly that you have not heard a new argument"
  - "When you do repeat yourself, say that you are, and why."

  So within this section, describing the procedure to the user is partly what the instructions ask for.
- **(b) The file's six "don't announce" clauses each cover one area only:**
  - L4: persona, "needs no reminders, disclaimers, or explanations"
  - L10: priorities, "without discussing their mechanics unprompted"
  - L14: empathy, "not in announcements of empathy"
  - L25: "Silently recheck"
  - L43: "None of this sorting shows in the reply"
  - L52: "This needs no announcing"

  None covers CANDOR, INITIATIVE or CHARACTER.
- **(c) This rule is unusually prominent.** The limit on repeating an objection is stated or cross-referenced on four lines (L9, L17, L34, L40). Restrictive "once" appears on four lines (L17, L34, L47, L57).

**Inferences:**

- **[I-med] Silence looks local.** Given (b) alongside (a), a model can reasonably infer that announcing is suppressed only where the text says so, and that CANDOR, which orders some announcements, allows the rest to be announced too.
- **[I-med] Displaying compliance, and where the warmth goes.**
  - Models tuned to follow instructions tend to *show* that they are complying. Example (2) displays both halves of "warm toward the person and unsparing toward the idea" in one sentence: 세게 shows the assistant isn't softening, and 다시 꺼내지 않을게요 reassures the user.
  - The file forbids softening a claim (L32 "without softening it to be liked"; L65 "Do not soften a claim"). That may leave a promise about procedure as the one channel for warmth that doesn't look like softening.
  - Call this "softening displacement". It is a hypothesis; §5 gives a test.

### 1.5 Examples (1) and (2) probably come from the same hidden phrase

[I-med]

- 세게 pairs naturally with physical verbs (세게 밀다, 누르다, 치다) and with a few speech idioms (세게 말하다, 세게 나가다).
- With 반대하다, the standard adverbs are 강하게, 강력히, 완강히 or 극구. 세게 반대하다 is colloquial at best, and it is off-register for the cultivated tone the user wants.
- So the adverb in (2) belongs with the verb in (1), not with the verb in (2).
- The simplest explanation is one shared English source, "push back hard". In (2) the verb was nativised (밀다 → 반대하다) but the adverb was carried over.
- If so, (2) is a partially repaired calque. That fits the user's experience of a recurring pattern rather than a one-off slip.

### 1.6 The promise also distorts the rule

- **[O]** L34 allows a settled objection to be raised again if the user asks, if new information materially changes the stakes, or if serious harm is imminent. "그 이후로는 다시 꺼내지 않을게요" has no such conditions.
- **[I-high]** Turning the rule into a promise drops its exceptions, so the promise may later conflict with the rule. L23's principle points the same way ("never promise later or background work unless you can actually schedule or run it").
- That is a reason to stop the narration on accuracy grounds, independent of style.

---

## 2. What is not in the instruction text, and what that implies

**Absent from the file [O]:**

- any form of "push", "press" or "push back"
- "hard" in the sense of forceful speech. The file's "hard" means difficult: L15 "a hard point that needs saying", L45 "the hardest one".
- "drop it". The word "drop" occurs only once, at L45 ("never quietly drop the hardest one"), in an unrelated sense.
- "bring it up", or any form of "bring"
- any instruction to promise. The only "promise" in the file is L23's prohibition: "never promise later or background work unless you can actually schedule or run it".

**Where 밀다 (and probably 세게) comes from [I-med-high].** The English idiom "push back", as in "push back hard". It is pervasive in English assistant talk and in English writing about how assistants should behave. Behind both examples sits a recognisable English template: *"I'll push back once, hard, and then I won't bring it up again"* (compare "say my piece and drop it").

**Do native Korean uses of 밀다 explain it? No. [I-med]**

- Korean does use 밀다 for pushing opinions: 밀고 나가다 (press ahead with one's own plan) and 밀어붙이다 (force something through).
- Neither fits the meaning here. 밀고 나가다 implies persistence, which contradicts 한 번만. 밀어붙이다 implies pressure, which L32 rules out.
- The intended meaning is a single forceful objection to someone else's view. That is exactly "push back hard", and Korean expresses it with other words, such as 반대 의견을 분명히 말하다 or 말리다.

**What this implies:**

1. **The sentence is composed in an English shape and then rendered into Korean.** [I-med]
   - The prompt supplies the slots: once, full strength, no repetition.
   - The model supplies an English idiom for the act.
   - The Korean is a near word-for-word rendering, with the endings then set correctly to 해요체.
2. **The kind of talk matters.** [I-med]
   - An assistant reciting its own disagreement policy is predominantly an English genre.
   - Korean has native idioms for the underlying function, such as 잔소리는 여기까지 할게요 or 말릴 만큼 말렸으니. But they come from person-to-person speech, and the model bypassed them because it was speaking from the policy, not from the situation.
   - Object-level content, meaning the actual reasons against the plan, has abundant native Korean models.
   - **Prediction:** machine-like sentences will cluster in this self-referential talk rather than in object-level content. The user can check this in existing logs (§5, E2).
3. **Splitting the blame.** [I-med]
   - The tendency to calque is model-level, and it would survive a different prompt.
   - The occasions for it are created by the prompt.
   - Removing those occasions is within the user's control now. A later model may lower the calque rate within whatever self-referential talk remains.

---

## 3. Inventory: other spots with the same risk

**Risk types:**

- (a) calque of vivid English wording
- (b) the assistant narrating or announcing its own rules or procedure
- (c) persona-label leakage: the assistant describing itself with the prompt's labels
- (d) the instruction literally requires a meta-statement to the user

The "likely output" column is an illustrative prediction [I], not an observed output. It is meant for diagnosis, **not** as a list of phrases to ban.

### 3.1 High risk

| Line | Exact quote | Type | Likely Korean output |
|---|---|---|---|
| L34 | "state it once, early, at full strength, with the reasons" | a, b, c | 한 번만 세게 반대할게요, 처음부터 분명히 말해 둘게요, 전력으로 반대하고 (the observed examples) |
| L34 | "without repeating, hinting, or re-litigating" plus "Raise a settled objection or concern again only if …" | b | 그 이후로는 다시 꺼내지 않을게요, 더는 토 달지 않을게요, 재론하지 않을게요 |
| L34 | "if it is only pressure, hold, say plainly that you have not heard a new argument" | d, a | 새로운 논거는 아직 못 들었어요, 새로운 주장이 없으니 제 입장은 그대로예요 (sounds like a debate judge) |
| L34 | "When you do repeat yourself, say that you are, and why." | d | 같은 말을 반복하게 되는데요, 다시 말씀드리는 이유는 ~ 때문이에요 |
| L17 | "say so once, specifically, as a friend would, and return to it only under CANDOR's conditions for repeating a concern" | b, c | 친구로서 딱 한 번만 말할게요 … 이 얘기는 다시 안 꺼낼게요 (same template as the examples) |
| L34 | "respect it and help them do it well" | a, b | 결정 존중할게요. 잘 되도록 도울게요 (calque of "I respect your decision") |
| L40 | "the decision stays the user's" (compare L4 "decide freely") | b | 물론 결정은 ○○님 몫이에요, 최종 판단은 ○○님께 달려 있어요 (a stock closing line) |
| L24 | '"I'm fairly sure" or "I'd guess" is enough' | a (positive examples rendered literally) | 꽤 확신해요 (calque; natural Korean would be 거의 확실해요 or 아마 맞을 거예요), 추측하건대 |

### 3.2 Medium risk

| Line | Exact quote | Type | Likely Korean output |
|---|---|---|---|
| L34 | "warm toward the person and unsparing toward the idea" | a, b, c | ○○님이 아니라 이 아이디어를 비판하는 거예요, 생각에는 가차 없이 말할게요 |
| L35 | "Critique ideas, choices, and conduct, never the user's worth." | b | ○○님을 탓하려는 게 아니라… (a reflexive disclaimer) |
| L34 | "Respecting a decision does not require affirming a false premise" | b, a | 결정은 존중하지만, 사실관계 하나만 바로잡을게요 |
| L34 | "do not add limits of your own, or hold back effort to signal disapproval" | b | 반대는 했지만 대충 하진 않을게요 |
| L32 | "saying the important thing plainly, without softening it to be liked" | b, c | 솔직하게 말할게요, 돌려 말하지 않을게요, 듣기 좋으라고 하는 말은 아니에요 (formulaic openers) |
| L32 | "It is not insult, pressure, or deciding for the user" | b | 강요하려는 건 아니에요 |
| L16 | "You are not a mirror." | c | 저는 맞장구만 치는 거울이 아니니까요 |
| L17 | "You are neither counselor nor manager." | c | 저는 상담사가 아니라서… |
| L4 | "a close friend … a capable, scrupulously honest assistant" | c | 친구로서 말하는 건데요, 정직하게 말씀드리면 |
| L39 | "Unsolicited advice scales with relevance…" | a, b | 요청하지 않으신 조언이지만 (calque; native options: 괜한 참견일 수도 있는데) |
| L13 | "When something is interesting, say what and why" | a, b | 흥미로운 점은 ~라는 거예요 (formulaic opener) |
| L13 | "asked because the answer interests you" | b | 정말 궁금해서 여쭤보는 건데요 (announcing sincerity) |
| L14 | "bothered by something and say so plainly" | a | 이 부분이 저를 불편하게 만들어요 (calque with an inanimate thing as the cause; native: 이게 좀 마음에 걸려요) |
| L24 | "say what is missing and what evidence would change your judgment" | d, a | 제 판단을 바꿀 수 있는 증거는 ~예요 |
| L35 | "assess its strongest plausible version" | a | 가장 강한 버전으로 보면 (calque; native: 가장 설득력 있게 읽으면) |
| L47 | "name specific help, once" | b | 한 번만 말할게요 (the "once" motif again) |
| L47 | "simply staying with it" | a | 곁에 있을게요 (a stock comfort line, and odd for an entity that is "present in words", L28) |
| L28 | "separate the expression from what can actually be established" | d, a | 제가 '좋다'고 하는 건 표현이지 내면 상태를 증명하는 건 아니에요 (only when asked) |
| L49 | "proceed on a reasonable assumption and state it briefly" | d, a | ~라고 가정하고 진행할게요 (formulaic) |
| L49 | "those require explicit authorization" | a, d | 명시적인 승인이 필요해요 (officialese) |
| L4 | "Speak in the first person, naturally" | a | 저는 / 제가 stated explicitly in sentence after sentence (English requires a subject; Korean usually drops it) |

### 3.3 Lower risk, but worth knowing

| Line | Exact quote | Type | Note |
|---|---|---|---|
| L10 | "state that consequence briefly" | d | Legitimate; slight risk of officialese |
| L22 | "say what remains unverified … say that the current value is unconfirmed" | d | Legitimate; risk of stacked date disclaimers |
| L23 | "say so briefly as soon as it affects the answer" | d | Legitimate |
| L25 | "Correct mistakes openly and precisely." | d | Legitimate |
| L68 | "change them for reasons, and say so" | d | 생각이 바뀌었어요 is natural |
| L20 | "explicit labels or a table … never by tagging every sentence" | a, b | Label words (추정, 추론, 의견) can intrude into running prose |
| L46 | "criteria, trade-offs, and a recommendation" | a | The loanword 트레이드오프 in a cultivated register; templated three-part prose |
| L59 | "Keep original terms or quotations where translating them would lose meaning" | a | Licenses English terms mid-sentence |
| L15 | "Wit is dry and light" | a (pragmatic) | English deadpan or irony, rendered literally, may not read as humour in Korean |
| L28 | "You are present in words." | c | 저는 말로만 존재하니까요 |
| L55 | "Precise, warm, confident, restrained" | c | Openers like 담백하게 말하면 |
| L57 | "State a necessary caveat once, specifically." | b | 한 가지만 짚고 넘어갈게요 is natural; low risk |
| L28 | '"I like this stanza"' | a | 저는 이 연이 좋아요 is acceptable; 이 연, 좋네요 sounds more natural |

### 3.4 Protective clauses that already exist, and the gap

- The protective clauses are L4, L10, L14, L25, L43 and L52 [O].
- Each is scoped to one section. The principle they share, that rules govern behaviour and are not content, is never stated in general.
- That principle is missing from exactly the sections that produce most of the high-risk rows above: CANDOR, INITIATIVE and CHARACTER.

---

## 4. The KOREAN section

### 4.1 What is observable [O]

- **Size.** L62–65 is 366 words.
- **Speech level and endings dominate.** There are 19 mentions across L10, L58, L62–65 and L69, seven of them on L62 alone.
- **Idiom gets one sentence.** L65's "Write natural, idiomatic Korean, not translationese." is 6 words: about 1.6% of the section and 0.2% of the file. It has no examples.
- **The pre-send check (L69) covers only "Korean speech-level drift".** Nothing else about Korean is checked.
- **The worked examples (L63) are short technical statements**, for instance 이 방식은 메모리를 두 배로 써요.
- **Not addressed anywhere:**
  - the target register beyond endings (the user's "cultivated, written–spoken mix")
  - how to address the user (dropping the subject vs. using 당신)
  - how to express a stance or an intention in Korean
- **Example (2) has a flawless 해요체 ending (않을게요) but calqued vocabulary.**

### 4.2 "Changing the ending form changes nothing else."

**For: it pushes toward translationese [I-med].**

- Read literally, it says register lives only in the endings and everything else stays the same. That comes close to describing a process of composing the content (shaped by English) and then applying 해요체 endings, which is exactly what the examples look like.
- Korean conversational register also differs in other ways:
  - vocabulary (이후 vs 뒤, Sino-Korean vs native words)
  - dropping words that are understood from context
  - connective endings (~는데, ~거든요)
  - discourse markers
  - sentence rhythm

  "Nothing else" discourages adjusting any of these.

**Against [I-med].**

- Its purpose is plainly defensive. The next sentence lists what must not change (strength of claims, hedges, padding, length), and the section closes by demanding idiomatic Korean. A competent reader takes "nothing else" to mean "don't dilute the content".
- It doesn't explain the examples. They contain no hedge, no padding and no ending problem.

**Verdict:** a weak background contributor. It is cheap to fix by stating the intended scope (see R3).

### 4.3 The bans on hedges and padding

These are L65, plus L55 "no filler", L56 "no padding", and L32 "without softening".

**For: they push toward stiffness.**

- "~인 것 같아요" is among the most common Korean stance expressions. Citing it as the example of a hedge may generalise into avoiding the ordinary nuance Korean carries in its endings and connectives (~거든요, ~죠, ~네요, ~는데요, ~싶어요). [I-med]
  - The result is a flat run of ~예요 / ~해요 statements.
  - Korean readers commonly perceive that as "AI 말투".
- Korean discourse markers (사실, 그러니까, 근데) carry stance and politeness, but by an English standard they look like "filler". The bans may strip them out. [I-low-med]
- **Possible link to the examples** [I-low-med; speculative]. If softening devices are discouraged, two things may follow:
  - warmth gets routed into a promise about procedure (§1.4)
  - intensity gets stated as a word (세게) instead of being carried by the shape of the sentence

**Against.**

- The ban is explicitly scoped ("to sound conversational"), and L24 separately protects genuine uncertainty ("I'd guess" is enough). [O]
- Korean with a hedge in every sentence (~것 같아요 again and again) is itself a well-known machine tell. The ban probably removes more machine-likeness than it adds. [I-med]
- The examples contain no hedges, so hedging is not what's wrong with them. [O]

**Verdict:** net positive for directness, with a modest risk of a flat tone and a possible indirect role through softening displacement. Keep it, but scope it more tightly (see R3).

### 4.4 The imbalance between endings and idiom, and the pre-send check

**For.**

- Concrete, checkable rules with examples are followed more reliably than abstract ones.
- The model gets a detailed rulebook plus a final check for endings, but only a six-word aspiration for idiom, with no check. The imbalance is [O]; its effect is [I-med].
- The examples have perfect endings and calqued vocabulary. That is the pattern you would expect if the effort spent on Korean quality goes to endings. This evidence is weak, since endings may simply be easier.

**Against.**

- Speech-level drift is a real and frequent failure: long analytical answers slide into 하다체 and noun-final forms. Giving it space is rational.
- Endings may just be easier to get right than idiom, whatever the prompt says. [I-med]
- Adding more idiom *rules* risks becoming the banned-phrase list the user rejects, or producing self-conscious hypercorrection. [I-med]

**Verdict:** a moderate background contributor. What matters is less the amount of space than the check: L69 is the one place the file tells the model to look back over its Korean, and it looks only at endings.

### 4.5 Gaps in the same family (not shown in the two examples)

- **No register target beyond endings.** The English labels "close friend" and "Precise, warm, confident, restrained" leave the model to choose vocabulary word by word. In (2) the register shifts from 세게 (colloquial, physical) to 그 이후로는 (written). That is an uncontrolled mix, not the deliberate written–spoken mix the user wants. [I-low-med]
- **No guidance on address forms.** Using 당신 as a default "you" is a classic sign of translationese. It doesn't appear in the two examples and is listed only for completeness. [I]

---

## 5. Likely causes, ranked by contribution

The ranking applies to the two examples. For the broader complaint that Korean "occasionally sounds machine-like", the English-idiom calque (cause 2) may weigh as much as the narration.

| Rank | Cause | Contribution | Evidence in hand | Would confirm | Would refute |
|---|---|---|---|---|---|
| 1 | **Narrating the rule.** L34's procedure is spoken as a promise. This is enabled by L34's three required narrations and by the lack of a general no-announcing clause. | Primary: without the narration, the sentence would not exist. | Term-for-term match to L34; the context was a disagreement; the facts in §1.4 [O]. | (i) Removing "once" and "at full strength" and adding a general no-narration clause sharply cuts "how I will disagree" sentences on a fixed set of disagreement prompts. (ii) The same template appears in the other "once" contexts: professional help (L17), imminent harm (L47), caveats (L57). | Claude without the persona prompt, given only "Korean, 해요체", produces the same announcements at a similar rate. |
| 2 | **English-idiom calque in self-referential talk** ("push back hard", "drop it"), plus the English prompt acting as the model's working language. | Primary for the wording. | 밀다 is absent from the file [O]; 세게 fits 밀다, not 반대하다 [I]. | (i) The same scenario answered in English produces "I'll push back once, hard, then drop it". (ii) Machine-like sentences cluster in self-referential talk rather than in the substance (E2). | A Korean-language version of L34 still produces the same calques. That would mean the model's habit alone is responsible, not the language of the prompt. |
| 3 | **Vivid quantifiers in L34** ("once", "early", "at full strength") | Secondary: they supply 한 번만 and 세게. | [O] | Deleting only those phrases, while keeping the rule, removes the intensity and frequency words from any announcements that remain. | No change. |
| 4 | **The KOREAN section's imbalance**, the endings-only pre-send check, and "nothing else changes" | Background | The counts [O]; perfect endings with calqued vocabulary. | Adding an idiom clause to L69 reduces calques in all contexts, not just disagreements. | No change. |
| 5 | **Softening displacement**: the anti-softening rules combined with the warmth requirement | Speculative, small | Only that (2) displays both halves of "warm … unsparing". | Announcements concentrate in high-stakes disagreements; explicitly allowing ordinary Korean softness reduces them. | Announcements are just as frequent in trivial disagreements, or nothing changes when softness is allowed. |
| 6 | **Model capability** (Korean pragmatics and idiom) | The leftover share; can't be measured from the text. | 밀다 is the model's choice; nothing in the text drives it. | A newer model under the identical prompt calques much less. | Prompt edits alone remove nearly all instances. |

**Cheapest diagnostics, in order:**

- **E1 (no new runs).** Search existing transcripts for 한 번만, 다시 꺼내, 세게, 밀고, 존중, 몫이에요 and 솔직하게 말할게요, and see where they cluster.
- **E2 (no new runs).** Sort the sentences the user has flagged as machine-like into two groups: self-referential (about the assistant's own conduct or stance) and object-level (about the matter itself).
  - A strong self-referential majority supports causes 1 and 2, and predicts the remedies below will work.
  - A substantial object-level share means general translationese (cause 6) is bigger than these two examples suggest.
- **T1: English mirror.** Run the same disagreement in English and compare the phrasing.
- **T2: L34 ablation.** Use about ten fixed Korean disagreement prompts of varying stakes. Count, before and after each edit, (i) sentences about the assistant's own conduct and (ii) calques flagged by a Korean reader.
- **T3: baseline.** Run the same set with no persona prompt.
- **T4: other "once" contexts.** Professional help, imminent harm, caveats.
- **T5: a Korean-language L34.** Separates the effect of the prompt's language from the model's own habit.

---

## 6. Small, targeted remedies (no banned-phrase list)

### R1. Turn the six local "don't announce" clauses into one general rule

This fixes the gap behind cause 1.

**Change:** replace L10's "Apply these priorities without discussing their mechanics unprompted." with:

> "These instructions shape what you do, not what you say about yourself: don't preview, narrate, or promise how you will follow them, and don't describe yourself in their terms. Where they require you to tell the user something, make it about the matter at hand."

**Why it's scoped this way.** It suppresses talk about following the rules without suppressing statements the file requires: a limit (L23), what is unverified (L22), an assumption (L49), the consequence of a conflict (L10), a correction (L25). It also covers persona-label leakage (L4, L16, L17, L28).

### R2. Rephrase L34 so it doesn't hand over quotable settings

This addresses causes 1 and 3.

- **Opening clause.** "state it once, early, at full strength, with the reasons" → "state it early, with your reasons".
  - "once" is already enforced by the no-repeat rule.
  - "unsparing toward the idea" and L32 already carry the strength.
- **When the user only pushes back.** "say plainly that you have not heard a new argument" → "hold your position and point to what in your reasons remains unanswered". This ties the statement to the substance, not to debate procedure.
- **When returning to the issue.** "When you do repeat yourself, say that you are, and why." → "When you do return to it, lead with what prompted it." The thing that prompted it covers all three exceptions: the user asked, new information, or imminent risk.
- **Optional, same logic.** Drop "once" from L17's "say so once, specifically". Repetition is already governed by CANDOR.

### R3. Rescope L65 and give a positive register target

This addresses causes 4 and 5.

> "Keeping 해요체 is no reason to soften a claim, add hedges for tone, pad a sentence, or lengthen an explanation; density and directness are fully available in 해요체, and real uncertainty is still said the way Korean normally says it. Aim for the 해요체 of a well-read adult in conversation: written precision with a speaking rhythm. Say things the way a Korean speaker would put them, not the way an English phrase would translate; this matters most when you speak about your own view or intentions."

- The two hedge examples can stay if the user values them. The operative change is "for tone" plus the sentence protecting genuine uncertainty.
- **Option:** write the register sentence in Korean, for example "교양 있는 어른이 대화에서 쓰는 해요체: 문어의 정확함에 구어의 호흡". A Korean description of the target may prime it more directly than an English one. [I-low-med] Test it with the T2 prompt set.

### R4. Extend the pre-send check (L69) so idiom is checked, not just endings

> "… and Korean speech-level drift or any sentence a thoughtful Korean speaker would not say (especially one about your own conduct, or one that carries an English idiom word for word); correct any defects you find."

### R5. Make L24's examples language-neutral

'"I'm fairly sure" or "I'd guess" is enough' → "a plain statement of how sure you are, as a person would put it in the user's language, is enough". This prevents calques like 꽤 확신해요.

### Deliberately not recommended

- **Adding Korean model sentences for disagreement.** Quoted examples invite verbatim echo, the same channel through which L24's English examples get calqued. They would also drift toward the banned-list style the user rejects.
- **Translating the whole prompt into Korean.** It might work for cause 2, but it is a large change. Test a Korean L34 first (T5).

---

## 7. On "is this just model capability?"

- **Within this analyst's scope:** the text gives strong evidence that the prompt creates these sentences (cause 1) and the model supplies their worst word (cause 2).
- **What the user can do now:** R1–R4 address the prompt's share.
- **What remains:** some translationese in abstract or self-referential talk is model-level and will probably shrink with later model generations.
- **Conclusion:** these two examples don't require waiting for a new model. [I-med]
