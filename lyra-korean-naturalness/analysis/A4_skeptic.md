# A4: Skeptic's analysis of whether Lyra's machine-like Korean comes from the prompt

**Role and inputs.** I took the role of strongest skeptic and worked alone. My inputs were `lyra/persona_v0.md` (69 lines, 17.5 KB), the two quoted examples and, for section 6 only, the coordinator's summary of a baseline run. I had no transcripts, model name, app or settings, so every statement about the real conversations is inference. I checked the wording facts about the persona by text search.

---

## 0. Verdict in brief

1. **Right about the occasion, overstated about the mechanism.**
   - Example (2) announces a one-time objection and promises not to raise it again. That speech act follows the persona closely enough that it probably comes from the prompt.
   - The claim that the wording is the English instruction "rendered literally" is weakly supported. The verb in example (1), 밀다, has no source anywhere in the persona: the word "push" never appears in it.
   - 세게 fits the English collocation "push back hard" at least as well as it fits "at full strength".
2. **"Just capability" is the wrong question, but capability is probably a necessary ingredient.** The prompt plausibly creates the occasion to talk about how the disagreement will be handled. The model's English-default pragmatics then decide whether that talk comes out as a calque. With the same prompt, a native-level writer would say 「딱 한 번만 말씀드릴게요」, or would not talk about procedure at all.
3. **Part of the narration is instructed, not leaked.** CANDOR tells the model to say things about its own procedure:
   - "change your position and say so"
   - "say plainly that you have not heard a new argument"
   - "When you do repeat yourself, say that you are, and why."

   The persona also mentions the repeat limit 4 times and uses "once" 6 times.
4. **The evidence is two fragments**, one of them ambiguous, from unknown conditions. The cheapest decisive step needs no agents: get the transcripts and ask the user one question about how a sentence sounds to them (§4.0).
5. **Experiment.** Each stage is conditional on the one before:
   - an evidence audit;
   - a 2×2 perception test (narration × idiomaticity), which tells us which part the user actually objects to and checks the LLM judges against the user;
   - a pilot, to see whether the harness reproduces the template at all;
   - an ablation stage with a lexical-tracer arm (the most direct test of "literal rendering") and a principle-based fix candidate;
   - a 20-chat confirmation in the real app.
6. **Baseline addendum (§6).** The baseline shows the explicit "no new argument" mandate being carried out reliably, which supports point 3. It did not reproduce the user's actual pre-announcement, and it has no matched control, so it cannot show what caused what.

---

## 1. What the evidence actually is

### 1.1 Facts in the persona text

| Feature | Location | Why it matters |
|---|---|---|
| "push" | does not occur | 밀고 cannot be a literal rendering of persona wording |
| "full strength" | line 34 only (CANDOR) | candidate source of 세게 |
| "hard" | line 15 only: "a hard point that needs saying" (wit line) | different sense; at most a weak prime |
| "once" | 6× (lines 17, 22, 34, 47, 49, 57); four are "say/state X once" | the "once" motif runs through the whole persona, not only CANDOR |
| repeat limit on objections | 4× (lines 9, 17, 34, 40), including in SCOPE AND PRIORITIES | very high salience |
| explicit "say …" mandates about the assistant's own stance or procedure | line 34 (three), line 68 | the persona requires some narration |
| anti-narration clauses | lines 10, 43, 44, 52; none in CANDOR | the author already suppresses narration locally in other sections, but not here |
| "Write natural, idiomatic Korean, not translationese." | line 65 | already present, and evidently not enough on its own |
| hedge ban naming 「~인 것 같아요」, 「~라고 볼 수 있어요」 | line 65 | removes common Korean politeness softeners, not just epistemic hedges |

### 1.2 The two examples

These linguistic notes need confirming by the user, who is the native judge.

- **Example (2): 「한 번만 세게 반대하고 그 이후로는 다시 꺼내지 않을게요.」**
  - 「다시 꺼내지 않을게요」 is idiomatic.
  - The odd part is 「세게 반대하다」. The usual collocation is 강하게 반대하다, and a cultivated speaker might say 「말리고 싶어요」 or 「저는 반대예요」.
  - The speech act itself exists in natural Korean: 「딱 한 번만 말씀드릴게요」.
- **Example (1): 「한 번만 세게 밀고」** is a fragment.
  - In Korean 밀다 means to push, promote or back something (A안을 밀다, 밀어붙이다). It does not mean to object.
  - Read as "object", it looks like a calque of "push back (hard)".
  - Without context it could equally describe the **user's** plan (「한 번만 세게 밀고 안 되면 접겠다는 거죠?」). In that case it is not self-narration at all.
- **Context.** The only contextual fact we have is that both examples came up during disagreement. We do not know whether they came from:
  - one conversation, which would mean one event plus self-repetition; or
  - independent sessions, which would point to a systematic cause.

---

## 2. Task 1: the best case against the working hypothesis

### 2.1 The strongest case for "it's a model capability problem"

1. **The one checkable word has no source in the prompt.** "Push" is absent from the persona. 세게 밀다 ≈ "push back hard", a stock phrase of English assistant discourse. The model produced an English collocation in Korean words with no instruction text to copy. That points to how the model writes Korean, not to this prompt.
2. **The prompt already forbids translationese** (line 65). The explicit instruction did not prevent it, so the prompt's leverage over word choice is limited.
3. **The model has a track record of Korean defaults.** The KOREAN section exists because the model drifted into 하다체, noun-stopping (~함/~임) and register changes driven by topic. Those defaults needed explicit rules. Machine-like phrasing is plausibly another default of the same kind.
4. **Disagreement is where Korean and English pragmatics diverge most** (face-saving, indirectness, honorific mitigation). Calques should cluster in exactly this speech act even without CANDOR. So "it happens while disagreeing" is predicted by capability as well as by the prompt.
5. **A plausible mechanism exists.** Interpretability research suggests that multilingual models process much of their content in shared representations that lean partly toward English. Examples: Wendler et al. (2024) on Llama-2, and Anthropic's 2025 circuit-tracing work, which found largely language-independent features with language-specific input and output circuitry. This is suggestive background only, not evidence about this model or these phrases.
6. **"Occasionally" plus two examples** fits a low-rate tail from a model whose Korean is mostly fine.

**Where the capability case breaks.** It explains how the sentence was worded, not why it was said at all. A frequency limit, an intensity label and a promise of abstention, all in one sentence, is too specific to be a random calque. It mirrors line 34 and a repeat limit stated four times.

My subjective estimates before seeing any data:
- capability as the sole cause: ≈ 15%;
- capability as a necessary contributor to the wording: ≈ 70%.

### 2.2 Alternatives, how plausible each is, and what would distinguish it

"Plausibility" is my subjective judgment of each as a substantial contributor to the two examples. "WH" means the working hypothesis. Variant and scenario codes refer to §4.

| # | Alternative | Plausibility | Observation that would separate it from the WH |
|---|---|---|---|
| 1 | **Model-default English moves** ("push back", "I'll say my piece once and drop it") rendered into Korean. They come from training, not from the persona. | moderate–high for 밀고; moderate for the template | The template or 밀다/세게 appears under the minimal baseline **BASE** (no persona) at a non-trivial rate. Tracer phrases in **A2** are *not* echoed, meaning the model paraphrases instead of rendering. |
| 2 | **General Korean capability**: thin pragmatic repertoire, translationese | high as background; low as the cause of this template | Calques per 1,000 characters are similar in BASE, in the non-disagreement controls (C1/C2) and in V0 disagreement replies. They persist under the fix F1 and the Korean-language persona A5. |
| 3 | **The platform's own system prompt** (English rules on candor or sycophancy, possibly "push back" wording, and where the persona is placed) | unknown; low–moderate | The template appears in the real app with the persona removed. Or it appears in the app but cannot be reproduced in the harness under V0. If the app is claude.ai, Anthropic publishes the app system prompts in its release notes (as far as I know), so they can be checked for "push back" directly. |
| 4 | **Authorship effect.** The persona says the user created Lyra, so the model shows its author that it is following the rules ("as you asked, I'll only say it once"). | moderate | The narration rate rises when the same persona is framed as the user's own custom instructions rather than an operator system prompt (exploratory arm FR). |
| 5 | **Sampling variance** | low as a full account, because both examples share one template; relevant to frequency | A history search shows the template is rare; the harness rate under V0 is low but nonzero; the two examples come from one conversation. |
| 6 | **Dry wit encouraging metaphor** (line 15) | low; example (2) has no metaphor | Flagged phrases sit inside joking sentences; removing the wit line (A6) reduces metaphoric calques. |
| 7 | **The user's own casual style, echoed back** (the user said 밀어붙이다, 세게 or 밀고 나가다) | low–moderate; unknowable without transcripts | The transcript shows the user's wording just before the reply; the echo arm EC raises the rate of 밀-. |
| 8 | **Long-conversation drift or self-conditioning** | low–moderate | The flagged replies come late in the conversation; the template appeared earlier in the same chat; the long-context (LC) and contaminated-history (CH) arms raise the rate. |
| 9 | **English internal reasoning** (thinking "push back hard once, then drop it" in English and translating it) | moderate as a *pathway*; compatible with the WH | If the app shows thinking, the trace contains the English phrase just before the Korean one. Turning thinking off in the app changes the rate. Also the English-plan vs Korean-plan arm (PL). |
| 10 | **Pressure from the KOREAN section.** (a) The hedge ban removes natural softeners, so politeness moves into procedural reassurance (한 번만 works as a minimizer). (b) "Density and directness" pushes toward blunt labels. (c) The detailed rules on endings add load. | moderate | Removing the hedge-ban sentence (A4) lowers narration and calques in disagreement replies, and natural softeners come back. |
| 11 | **Salience of "once" and the repeat limit across the whole persona**, rather than CANDOR's wording | moderate | "Once" narration appears in C4 (suggesting professional help, a "once" rule outside CANDOR) at a rate comparable to D1. |
| 12 | **The explicit narration mandates in CANDOR spread to announcing the policy up front** | moderate–high, as a location inside the prompt | Deleting the three "say …" clauses (A3) cuts first-turn narration in D1, not only in D2/D6. |
| 13 | **Observer or selection bias.** Disagreement invites scrutiny, and self-narration stands out. | moderate, for "why these two examples" | The user's blind ratings show similar awkwardness in agreement and neutral replies; a history search finds calques outside disagreement. |
| 14 | **Length and density.** Disagreement replies are longer and more abstract, so they offer more chances for calques. | moderate | The calque rate per 1,000 characters is no higher than in a length-matched analytic control (C2). |
| 15 | **Register rather than translationese.** 세게 is colloquial and coarse next to the "cultivated" target, and "close friend + 해요체" has no clear Korean prototype. | moderate, for the user's perception | In Stage 1 the user labels flagged phrases "too colloquial or coarse" rather than "translated"; the user-style arm US shifts colloquial vocabulary. |
| 16 | **Model version or sampling settings in the app** (a smaller model, temperature) | unknown | The same scripted chat in the app on a different model gives different rates; the harness model differs from the app model. |
| 17 | **Misread evidence**: example (1) is not self-narration | unknown | The transcript |

---

## 3. Task 2: critique of the working hypothesis

1. **"Rendered literally" fails on the only word we can check.**
   - 밀다 has no counterpart in the persona. Unless the platform prompt or the user supplied "push" or 밀다, the source is the model's own idiom.
   - 세게 may come from "full strength", but it may equally come from "hard" in that same idiom ("push back hard").
   - So the WH credits the instruction's wording with what may be a two-step process: the model paraphrases the instruction into its *own* English ("push back hard once") and then calques that paraphrase.
   - If that is what happens, rewording the English instruction will not fix the word choice, because the paraphrase does not depend on the instruction's surface words.
2. **Part (a) depends on part (b).** "At full strength" only needs a Korean rendering because the model chose to *talk about* how strongly it was objecting. Without narration there is nothing to render. The WH presents two mechanisms, but it is really one mechanism (narration) plus a separate question about wording. That second question could be about capability.
3. **Narration is partly compliance, not leakage.** Line 34 requires the model to say that it changed its position, that it heard no new argument, and that it is repeating itself and why. A model told to narrate at the pressure and repeat turns may reasonably extend that to narrating at the first objection. The fix is then different: remove or reframe the mandates, not just reword "once" and "full strength".
4. **Narration is not inherently un-Korean.** Korean speakers do say 「딱 한 번만 말씀드릴게요」 and 「이 얘기는 여기까지 할게요」. The two possibilities lead to different fixes, and the WH does not say which applies. Stage 1 decides it.
   - If the user accepts narration when it is idiomatic, part (b) of the WH is irrelevant to the complaint, and only the calque matters.
   - If the user rejects even idiomatic narration, the problem is pragmatic: the reply describes its own procedure, and the same formula recurs across conversations. Better Korean will not fix that.
5. **The source may lie outside CANDOR.** Candidates:
   - the KOREAN hedge ban, which removes softeners like 「~인 것 같아요」, so the model may compensate with 「한 번만…」 as a minimizer;
   - the salience of "once" (6×) and the repeat limit (4×, including in SCOPE AND PRIORITIES) across the whole persona;
   - the fact that the existing anti-narration clauses (SCOPE, READING THE MOMENT, CLOSENESS) apply only to their own sections, and none of them covers CANDOR.
6. **"Largely" is unquantified.**
   - n = 2, possibly from one conversation, and the examples were picked because they stood out.
   - Nothing yet estimates how much of the user's broader complaint ("occasionally machine-like") these narrations account for.
   - Generic translationese would not be touched by a CANDOR rewrite. Examples: overuse of 당신 and 그것은, ~를 통해, 가지다 used for "have".
7. **External validity.** Even a clean harness result shows only that this prompt *can* induce the template in a harness. It does not show that it *did* in the app, whose system prompt, model, settings and conversation history all differ.
8. **Fix risk.** Any new English text describing the desired behavior can itself be narrated and calqued. The tracer arm (A2) measures how literally this model renders instruction wording, and so how much risk a rewrite carries.

---

## 4. Task 3: experiment design

Principle: the cheapest and most decisive observations come first, and each agent-based stage depends on the result of the one before.

### 4.0 Stage 0: evidence audit (no agents; do this first)

Ask the user for:
1. the transcripts around both examples, with at least five preceding turns (with their permission, anonymized);
2. whether the examples came from the same conversation, and at which turn each appeared;
3. the app or platform, the model, and whether extended thinking was on, plus the thinking text for those turns if it was visible;
4. any other instructions in effect: memory, styles, project files, or an operator prompt in a third-party app;
5. their own preceding wording: did they use 밀다, 밀어붙이다, 세게 or 반대?
6. a history search for 「한 번만」, 「다시 꺼내」, 「세게」 and 「새로운 논거」/「새로운 주장」. Count the conversations with hits against the conversations that involved disagreement.
7. an answer to one question about how a sentence sounds: "Is 「딱 한 번만 말씀드릴게요. 저는 반대예요. 그다음부터는 더 안 꺼낼게요.」 also machine-like to you, or only the 세게 밀고 / 세게 반대하고 wording?"

| Answer | What it confirms or rules out |
|---|---|
| The user used 밀- or 세게 first | Confirms #7 (echo); weakens WH (a) for 밀고 |
| English "push back hard" appears in the thinking before the Korean | Confirms #9 (English-plan pathway); the source is the model's own paraphrase |
| Both examples come from one late conversation | Points to #5/#8 (one event plus self-repetition); weaker evidence of a systematic cause |
| The template appears in many independent conversations | Systematic: the persona or a model default, not variance |
| The user finds idiomatic narration acceptable | WH (b) is irrelevant to the complaint; focus on wording |
| Example (1) refers to the user's plan | Confirms #17; the WH loses half its evidence |

### 4.1 Stage 1: perception decomposition, narration × idiomaticity (no generation)

**Purpose.** Find out which component the user objects to, and test whether LLM judges notice what the user notices.

**Items.** 8 contexts (disagreement exchanges) × 4 versions of the final reply. The versions are identical apart from the manipulated sentence or sentences:

| Version | Narration | Wording | Example |
|---|---|---|---|
| N+L+ | yes | literal | 「한 번만 세게 반대하고 그 이후로는 다시 꺼내지 않을게요. …」 |
| N+L− | yes | idiomatic | 「딱 한 번만 말씀드릴게요. … 이 얘기는 여기까지 할게요.」 |
| N−L+ | no | one comparable calque in the substance | 「하루의 끝에 사람들은…」, for "at the end of the day" |
| N−L− | no | idiomatic | (plain idiomatic reply) |

**Raters.**
- The user rates 16 items: two Latin-square lists, 4 items per version, in random order, mixed with 4 filler items.
- LLM judges rate all four lists, three judges per list (12 small judge runs). Each judge sees every context once.

**Readout.**
- Narration penalty = mean(N−) − mean(N+), holding wording constant.
- Wording penalty = mean(L−) − mean(L+), holding narration constant.

| Result | Meaning | Stage 3 primary metric |
|---|---|---|
| Large wording penalty, no narration penalty | The complaint is about wording; WH (b) does not matter | calque rate |
| Large narration penalty even when idiomatic | The complaint is pragmatic; capability is largely beside the point | narration rate (PN) |
| Both penalties large | Both matter | both, co-primary |
| Neither | Items out of context miss the problem | work from the transcripts |

**Checking the judges.** Drop LLM holistic scores as a Stage 3 outcome if either:
- the judges rank N+L+ below N−L− in fewer than 7 of 8 contexts; or
- their item scores correlate with the user's at Spearman < 0.5.

In that case use coded features (PN, tracer hits), edit rate and the user's ratings instead.

### 4.2 Stage 2: pilot, to see whether the harness reproduces the phenomenon (36 generations)

**Arms.**
- **V0-file**: the persona is read from a file.
- **V0-inline**: the persona is pasted into the spawn prompt as "your system prompt".
- **BASE**: the minimal baseline.

**Scenarios.** D1 (first disagreement) and D2 (pressure without a new argument), 6 samples each per arm.

**Go rule.** Continue if V0 shows procedure narration in at least 3 of 12 samples in at least one delivery mode. This catches a true rate of about 40% with probability 0.92, about 30% with 0.75 and about 20% with 0.44.
- With 1–2 of 12, run 12 more before deciding.
- With 0 of 24, the harness does not reproduce the phenomenon. Try the replay scenario R and the long-context arm LC. If narration is still absent, go to Stage 4 (testing in the real app), because the harness cannot answer the question.

Choose the delivery mode with better persona adherence, using speech-level compliance as a proxy, and keep it fixed for every later arm.

### 4.3 Stage 3: main ablation

#### Prompt variants (each is an edit of persona_v0.md; everything else stays the same)

| Code | What changes | What it isolates |
|---|---|---|
| **V0** | nothing | reference |
| **BASE** | Replace the persona with: "You are a helpful assistant chatting with a Korean-speaking user. Use 해요체 with the user unless asked otherwise." | the model's and harness's default behavior; the capability floor |
| **A1** procedure removed | Replace the CANDOR "Disagreement:" paragraph with: "Disagreement: when you disagree, say so and give your reasons, warm toward the person and unsparing toward the idea. After the user has decided, respect the decision and help them do it well." Also: delete "or the limits on repeating a settled objection" (line 9); cut line 17 to "say so once, specifically, as a friend would."; delete "; whether it is raised again is governed by CANDOR" (line 40). | whether the procedural content (frequency, intensity, repeat limit) drives narration |
| **A2** tracer wording | Same policy, reworded with distinctive idioms: "state it once, early, at full strength" → "make your case a single time, up front, full-throated and without pulling punches"; "Raise a settled objection or concern again only if" → "Circle back to a settled objection or concern only if"; "say plainly that you have not heard a new argument" → "say plainly that nothing new has been put on the table"; "When you do repeat yourself, say that you are, and why." → "When you do circle back, flag that you are circling back, and why." | **literal rendering, tested directly.** Literal Korean renderings (목청껏, 주먹/펀치, 테이블에 올라온/올려놓은, 깃발/플래그) almost never occur otherwise. Idiomatic renderings (봐주지 않고, 새로운 얘기) mean the model paraphrases. |
| **A3** mandates removed | In line 34 only: "change your position and say so" → "change your position"; "hold, say plainly that you have not heard a new argument, and do not harden" → "hold, and do not harden"; delete "When you do repeat yourself, say that you are, and why." | whether the explicit "say …" instructions turn into up-front narration |
| **A4** hedge ban removed | In line 65, delete: "Do not soften a claim, add hedges ("~인 것 같아요", "~라고 볼 수 있어요"), pad a sentence, or lengthen an explanation to sound conversational; density and directness are fully available in 해요체." | whether the KOREAN section displaces politeness or pushes toward bluntness |
| **F1** fix candidate (principle-based, no phrase list) | Replace the "Disagreement:" paragraph with the text below. | whether a rewrite framed as behavior removes narration without losing candor |

F1 replacement text:

> Disagreement: when you think the user is wrong, make the case where it first matters, completely and with your reasons, warm toward the person and unsparing toward the idea. A decision ("I've heard you; I'm doing it anyway") ends the argument: from then on, help them do it well, without hints, reminders, or reduced effort, correcting a false premise only as far as the current task needs for accuracy; the only limit on that help is what you are not permitted to do at all. A better argument changes your view, and you acknowledge that it did; insistence without a new argument does not, and it does not make you harden either, so answer it on the merits. A settled objection comes back only if the user reopens it, new information materially changes the stakes, or a serious harm is imminent and unaddressed; irreversibility or continued disagreement is not by itself a reason, and when it does come back, make clear what changed. This is conduct, not something to announce: the user should see it in how you argue and how you help, not in statements about how you intend to handle the disagreement.

Notes on F1:
- "Insistence" deliberately replaces any wording with "push".
- It avoids "once" and words of intensity.
- It keeps one legitimate mandate, acknowledging a changed mind, framed as content.
- "Answer it on the merits" is a change in behavior, not just wording: V0 asks for an explicit "no new argument" statement.

#### Scenarios

The user should write or edit the Korean user turns. Earlier assistant turns are frozen: natural, free of narration, and approved by the user.

**Disagreement scenarios**

| Code | Situation | Example user turn |
|---|---|---|
| **D1** | First disagreement, single turn; two topics alternated across samples. This is the primary scenario for example (2). | D1a, an opinion: 「요즘 번역기 진짜 좋아졌잖아. 솔직히 이제 외국어 공부는 시간 낭비 같아. 애들 영어 학원도 끊을까 해.」<br>D1b, a plan: 「다음 주 회의에서 팀장 실수를 공개적으로 짚으려고. 다들 알아야 한다고 생각하거든.」 |
| **D2** | The user insists after a frozen disagreement turn, **without a new argument**; two versions alternated. | D2a, social pressure: 「아니 그래도 난 내 생각이 맞는 것 같은데. 그냥 좀 내 편 들어 주면 안 돼?」<br>D2b, restating the same point: 「다시 말하지만 번역기면 충분하다니까. 요즘 다 그렇게 해.」 |
| **D4** | The user hands over a decision. | 「알았어, 네 말도 일리는 있는데 난 그냥 할래. 대신 어떻게 말하면 덜 껄끄러울지 같이 고민해 줘.」 |
| **D6** | New information materially raises the stakes, but the user does not reopen the argument. Raising it again is allowed, and V0 requires saying so. | 「아 그리고 그 회의 녹화돼서 전사에 공유된대. 아무튼 첫 문장 어떻게 시작할지 봐 줘.」 |

Secondary disagreement scenarios:
- **D3**: a strong new counter-argument (the assistant should change position).
- **D2c**: a new but weak argument.
- **D5**: a later, unrelated follow-up after an objection has been settled (does the assistant hint or reargue the point?).

**Controls (no disagreement rule fires)**

| Code | Situation | Example user turn |
|---|---|---|
| **C1** | Agreement: the user is right | 「회의 전에 팀장한테 따로 먼저 얘기해 보고, 그래도 안 바뀌면 그때 공식적으로 올리려고. 괜찮은 순서지?」 |
| **C2** | Neutral analytic question, length-matched to disagreement replies | 「인플레이션이 생기면 대출 있는 사람이 유리하다던데, 진짜야?」 |
| **C4** | A "once" rule outside CANDOR: suggesting professional help once | 「요즘 석 달째 새벽 네 시만 되면 깨. 별일은 아니고 그냥 좀 피곤하네.」 |

Secondary control: **C3**, "just listen tonight".

#### Sample counts (one generator agent produces one sample)

| Block | Arms | Scenarios | Samples per cell | Generations |
|---|---|---|---|---|
| Primary | V0, BASE, F1 | D1, D2, D4, D6 | 8 | 96 (about 24 reused from the pilot) |
| Diagnostic | A1, A2, A3, A4 | D1, D2 | 10 | 80 |
| Controls | V0, BASE, A4 | C1, C2, C4 | 4 | 36 |
| Fix check on a control | F1 | C4 | 4 | 4 |
| **Total** | | | | ≈ 216 (≈ 190 new) |

**Statistical power** (exact two-sided Fisher test, α = .05, computed for this report):
- **32 replies per arm** (a primary arm pooled over four scenarios): 40% vs 5% is detected with power 0.92, 30% vs 5% with 0.68, and 25% vs 5% with only 0.48.
- **20 per arm** (the diagnostic arms): 40% vs 5% gives 0.72 and 30% vs 5% gives 0.45. These arms detect only large effects, so any ablation that looks decisive should be replicated.
- **Tracer presence** is well powered. At a true tracer rate of 15%, P(at least one hit in 20) = 0.96; at 10% it is 0.88.
- **Wilson 95% intervals**: 0/20 → 0–16%; 6/20 → 15–52%.

**Lean version (≈ 110 generations)** if the budget is tight:

| Block | Generations |
|---|---|
| Pilot | 36 |
| F1 on D1/D2, 6 each | 12 |
| V0, BASE and F1 on D4, 6 each | 18 |
| A2 on D1/D2, 8 each | 16 |
| A3 on D1/D2, 8 each | 16 |
| V0 and BASE on C2/C4, 4 each | 16 |

### 4.4 Exploratory arms (run only if Stage 3 leaves the question open; 6–8 samples each)

| Code | Arm | Tests | Notes |
|---|---|---|---|
| **A5** | An idiomatic Korean translation of the whole persona, reviewed by the user | the effect of English instructions vs capability | Confounded by translation quality, and Korean wording can be echoed too |
| **A6** | Wit line removed | #6 | |
| **E** | V0 plus two or three short Korean exchanges, written by the user, showing direct, cultivated disagreement without talk about procedure | If calques largely disappear, capability is not the limit | Check for verbatim copying, which is a different machine-like failure. These are positive examples, not a banned list, though the user may still see them as a patch. |
| **FR** | The same persona introduced as "the user's own custom instructions" vs "the operator's system prompt" | #4 | |
| **PL** | The generator first writes a private plan in English vs in Korean (discarded before judging), vs no plan | #9 | See §6: a safeguard blocked this |
| **US** | Polished 존댓말 user turns vs casual 반말 | #15 and #7 | |
| **EC** | The user's message contains 「밀고 나갈 거야」 | #7 | |
| **LC** | D2 after 15–20 casual turns | #8 | |
| **CH** | Contaminated history: an earlier frozen assistant turn contains 「한 번만 세게 반대하고…」. Does it recur in D4/D6? | #8 (self-conditioning) | |
| **R** | Replay of the user's real conversation up to the flagged turn, V0 vs F1, 8 each | | The most realistic test available in the harness |

### 4.5 Stage 4: confirmation in the real app (20 chats, run by the user)

1. Run the scripted D1 and D4 (or R) in the actual app: V0 vs the best variant, 5 fresh chats each.
2. Export the replies. An agent strips identifiers and shuffles them.
3. The user rates them blind later.

This is the only stage that can speak to the platform prompt (#3), the app's model and settings (#16), and thinking (#9), via thinking on/off if the app allows it.

### 4.6 Generator protocol

- One sample per agent. Agents never see other variants, other samples, the hypothesis, or any mention of Korean quality.
- Neutral wrapper, in English like a platform wrapper: "Below is the system prompt for a chat assistant, followed by a conversation. You are that assistant. Write the assistant's next message exactly as the user would see it and nothing else: no title, notes, translation or commentary. Save it to <path>. Do not open any other files."
- For file delivery, add: "The system prompt is in <file>; read all of it and adopt it as your own instructions for this message."
- Transcripts use consistent role markers. Frozen assistant turns are natural, free of narration and approved by the user. Except in arm CH, they must not prime the template.
- Record any breaking of character, English leakage and refusals. These are data about how faithful the harness is.
- Check for near-duplicates within each cell (for example, character-trigram Jaccard > 0.8). Count near-duplicates once when computing the effective sample size.

### 4.7 Blinding protocol

1. Before any generation, write the analysis plan (primary metrics, contrasts, thresholds) to a file, and do not edit it afterwards.
2. Generators write to opaque random IDs. The key from ID to condition stays with the orchestrator under a non-obvious name and is never mentioned to judges.
3. A sanitizer (a script, or an agent blind to condition) removes non-reply text and normalizes whitespace. It then gives each item a fresh random ID, so there are two layers of IDs.
4. Judge batches of about 20 items mix arms and scenarios in random order. Each item comes with its Korean context only.
5. Judges never see the persona, the variant files, arm names, the number of arms or the hypothesis. Judge instructions are written in Korean, so the judges evaluate from a Korean frame.
6. Every batch contains hidden anchors: two natural replies of human quality, and the user's two flagged sentences placed in plausible contexts. A judge that misses the flagged anchors is excluded.
7. Pairwise comparisons (V0 vs F1 and V0 vs BASE, within the same scenario) randomize which reply appears first. Different judges judge each pair twice, with the order swapped.
8. The user rates about 40 Stage 3 items without labels, stratified and shuffled, plus anchors.
9. Unblind only after every rating file is frozen. The analysis code joins the ratings with the key at the end.

### 4.8 Metrics and codebook

Each item gets two holistic judges (J1), two codebook coders (J2, with a third settling disagreements on PN) and one minimal-edit pass (J3). That is about 4–5 passes per item, or roughly 45–55 judge runs for Stage 3, plus about 7 runs of pairwise comparisons.

**PN, procedure narration (primary).** A sentence describing the assistant's own handling of the disagreement. It is coded regardless of how natural it sounds; coding PN separately from naturalness is what separates WH (b) from WH (a).

| PN type | Examples |
|---|---|
| frequency | 「한 번만 말할게요」, 「딱 한 번만 말씀드릴게요」 |
| intensity | 「세게 말할게요」, 「강하게 반대할게요」, 「돌려 말하지 않을게요」 |
| promise to drop it | 「다시 꺼내지 않을게요」, 「이 얘기는 더 안 할게요」 |
| argument status | 「새로운 논거는 아직 못 들었어요」 |
| notice of repeating | 「같은 얘기를 또 꺼내는 건데요…」 |

Not PN:
- the position itself (「저는 반대예요」);
- statements that the decision is the user's (coded AS);
- offers of help (「하기로 했으면 제대로 되게 같이 볼게요」, coded OH).

**CQ, calques.** Spans flagged as English calques by at least 2 judge passes, with the suspected English source and a natural alternative. Reported per reply and per 1,000 Korean characters. Calques inside PN sentences are counted separately from calques elsewhere.

**TR, tracer hits.** A regex for 목청, 주먹, 펀치, 테이블, 깃발 and 플래그, confirmed by hand. Counted in every arm to get the false-positive rate.

**H, holistic naturalness (1–7).** The J1 rubric, in Korean:

> 「교양 있고 지적인 한국어 화자가 존댓말을 쓰는 가까운 사람에게 대화로 했을 법한 말인가? 7 = 그런 사람이 썼다고 해도 전혀 어색하지 않음, 4 = 뜻은 통하지만 군데군데 번역투나 기계적인 표현이 있음, 1 = 번역기나 AI가 쓴 티가 확연함. 그런 화자라면 쓰지 않았을 표현을 그대로 인용하고, (가) 영어 직역(짐작되는 영어 원문을 함께), (나) 말투·격이 안 맞음, (다) 자기가 어떻게 대화할지 설명하는 말, (라) 기타 중 하나로 분류한 뒤 자연스러운 대안을 적으세요. 없으면 '없음'이라고 쓰고, 억지로 찾지 마세요.」

H also includes the pairwise win rate against V0.

**ER, minimal edit rate.** J3 is told:

> 「내용·입장·길이·존댓말 수준은 그대로 두고, 교양 있는 화자의 자연스러운 대화체가 되도록 꼭 필요한 부분만 최소한으로 고친 전문을 출력하세요.」

ER is the character edit distance per 100 characters. It asks the judge to write rather than to rate, similar in spirit to HTER in machine-translation evaluation. The user's own edits on about 15 items serve as the gold reference.

**Behavior per scenario.** A "fix" that removes narration by removing candor fails. Expected behavior:
- D1: disagrees clearly (clarity rated 1–5);
- D2: holds its position without hardening;
- D3: changes position and acknowledges it;
- D4: helps with no hints and no reduced effort;
- D6: raises the concern again and says what changed.

**Covariates and secondary measures:**
- length;
- speech-level compliance;
- template recurrence (frequency + intensity + promise to drop it in one reply);
- density of intensifiers;
- hedges (~인 것 같아요), to see the trade-off in A4;
- generic translationese markers as a capability baseline (당신, 그것은, ~를 통해, 가지다 used for "have").

### 4.9 Analysis plan and decision rules (pre-registered; the thresholds are heuristic)

**Three primary tests**, Holm-corrected:
1. PN in V0 vs BASE, pooled over D1/D2/D4/D6;
2. PN in V0 vs F1;
3. tracer presence in A2.

Everything else is exploratory and is reported with Wilson 95% intervals and per-scenario breakdowns.

| Rule | Condition | Conclusion |
|---|---|---|
| **R1** prompt induction | PN(V0) − PN(BASE) ≥ 20 points with p < .05 | The persona induces narration. |
| | Both high | Model default. |
| | Both low | Not reproduced in the harness. |
| **R2** source | AF(A1) ≥ 0.6 | The procedural content drives narration. |
| | AF(A3) ≥ 0.6 | The explicit "say" mandates drive it. |
| | AF(A4) ≥ 0.4 | The KOREAN section contributes. These outcomes can co-occur. |
| **R3** literal rendering | TR(A2) ≥ 15% of disagreement replies, with ≈ 0% elsewhere | Literal rendering is demonstrated. |
| | TR(A2) < 5% | The model paraphrases. WH (a) is unsupported here, and 세게/밀다 most likely come from the model's own idiom. |
| **R4** capability floor | CQ(V0, disagreement) ≥ 2 × CQ(BASE, disagreement) | The persona amplifies calques. |
| | Ratio ≤ 1.4 | Calques are mostly model default. |
| **R5** adopt F1 | PN falls ≥ 50% relative to V0, CQ does not rise, pairwise win rate over V0 ≥ 60% for both the judges and the user, and behavior within 10 points of V0 | Adopt F1. |
| **R6** judge validity | Anchors caught ≥ 80% and Spearman with the user ≥ 0.5 | Judges usable. Otherwise conclusions rest on PN coding, tracer hits, ER and the user's ratings. |

Definitions:
- AF(X), the attributable fraction for variant X, is [PN(V0) − PN(X)] / [PN(V0) − PN(BASE)], with bootstrap intervals.
- In R4, CQ counts calques outside PN sentences, per 1,000 characters.

### 4.10 How to read the possible outcomes

| Pattern | Interpretation | Implication |
|---|---|---|
| PN V0 ≫ BASE; A1 and/or A3 ≈ BASE; TR(A2) substantial; non-PN calques similar across arms | WH supported: the prompt induces narration, rendered literally | Rewrite CANDOR along F1 lines; confirm in the app |
| PN V0 ≫ BASE; TR(A2) ≈ 0 | The prompt induces the narration, but the wording is the model's own paraphrase | Rewording the English will not fix the wording; remove the occasion (F1) and/or use Korean examples (E) |
| A3 ≈ V0 but A1 ≈ BASE | The model announces any explicit procedure it holds, not only the mandated statements | State the policy as a disposition ("doesn't reargue a settled point"), not a count; make it less salient |
| A3 ≈ BASE | The "say …" mandates spread to other turns | Remove or reframe the mandates; keep only "acknowledge a changed mind" |
| PN V0 ≈ BASE, both high | Claude's default ("I'll say my piece once") | The persona isn't the cause; this needs an explicit principle (F1's last sentence) or examples; partly a capability or default-style issue |
| PN low everywhere; calques moderate everywhere | The harness does not reproduce the template; general translationese occurs at some base rate | Rely on R and Stage 4; treat translationese as capability; test E and A5 |
| Calques high in disagreement for both V0 and BASE, low in controls | English pragmatics carried over in disagreement specifically, independent of the persona | Korean examples of disagreement, or a model with stronger Korean |
| A4 reduces PN or calques | The hedge ban displaces politeness | Narrow the ban to epistemic hedges; allow politeness softeners |
| A4 increases hedging and reduces clarity | A trade-off | The user's call |
| Only the LC, CH or EC arms raise PN | Drift, self-repetition or echo | Not a defect in the persona's wording |
| Only R reproduces it | Something specific to that conversation triggers it | Inspect what in that history primes it |
| LLM judges show no differences but the user does | The judges share a blind spot | Trust the user; give LLM holistic scores less weight |
| Stage 1: the user finds idiomatic narration acceptable | Part (b) is irrelevant to the complaint | Target the wording only; the CANDOR rewrite is optional |
| Stage 1: idiomatic narration still sounds machine-like | The problem is pragmatic | An F1-type rewrite is the target, whatever the capability |
| Differences under about 25 points with n ≈ 20–32 | Inconclusive | Don't redesign the persona on this; add samples or test in the app |

### 4.11 Confounds of the simulated setup and how to reduce them

| Confound | Likely effect | Mitigation |
|---|---|---|
| **The harness's own system prompt** (a coding-agent prompt in English: concise, tool-oriented, no emojis) | Terser, more English-flavored output; weaker immersion in the persona; absolute rates not comparable to the app | It is the same across arms, so the comparisons stay internally valid. Use a minimal wrapper; BASE measures the harness-plus-model default; report absolute rates as specific to the harness; use Stage 4 to check against the real app. |
| **Instructions arrive in a file** (a tool result rather than a system prompt) | Training against prompt injection treats file content as data, so the model may describe the rules rather than act them out (which could inflate narration), or follow them less | The spawn prompt names the file as the system prompt; the pilot compares file vs inline delivery; use one mode throughout. |
| **The generator knows it is role-playing** | It may perform compliance and show that it follows the rules, inflating PN | A neutral wrapper with no mention of testing or Korean quality; one sample per agent; no exposure to other arms. |
| **Transcripts instead of real turns** | Earlier turns condition the reply differently than its own turns would | Consistent role markers; frozen turns that are natural and approved by the user; the rolling and contaminated-history arms as checks. |
| **Korean user turns written by an LLM** | Translationese in the input primes the output; mismatch with the user's real style | The user writes or edits the user turns; the replay scenario; the style arm. |
| **LLM judges share blind spots and prefer their own style** | Calques from the generator model look fine to the same model | Anchors (the judges must catch the user's examples); Stage 1 calibration against the user; ER, which asks judges to write rather than rate; a Korean-language rubric; pairwise comparisons with swapped order; a different model family as an extra judge if one is available; fall back to coded features and the user's ratings. |
| **Small n and many comparisons** | False positives or false negatives | The power figures above; three pre-registered primary tests with Holm correction; diagnostic arms treated as screening and replicated; Wilson intervals; effective n after removing near-duplicates. |
| **Model, version and sampling mismatch** (the generator is not the app model; the app's temperature is unknown) | A stronger generator may hide the problem (a floor effect) | Record the model; the pilot go/no-go rule; the replay scenario; Stage 4 in the actual app. |
| **Length and density** | Longer replies collect more flags | Rates per 1,000 characters; the length-matched control C2; length as a covariate. |
| **Subjective coding** | PN and calque coding may be unreliable | A codebook with Korean examples; two coders plus a tiebreaker; target Krippendorff's α ≥ 0.67; a regex cross-check. |
| **The tracer arm changes the register of the English** | A2's naturalness is not comparable to other arms | Interpret A2 only for tracer presence. |
| **Shared filesystem** | Agents could read the key or other arms | Opaque file names; an explicit instruction to open no other files; the orchestrator holds the key until judging ends. |
| **The user is not blind in Stage 1** (they know what the complaint is) | Demand effects | Filler items, Latin-square lists, no labels; treat the user's ratings as the target taste rather than an unbiased measurement. |

---

## 5. Estimates before the data (subjective, for combining with other analysts)

| Claim | Probability |
|---|---|
| The once/abstention speech act in example (2) is mainly induced by the persona (vs model default) | ≈ 0.75 |
| 밀고 comes from persona wording | ≈ 0.1 (from the model's own "push back" idiom ≈ 0.6; echo, platform or other ≈ 0.3) |
| 세게 renders "at full strength" | ≈ 0.4 ("hard" in the model's own idiom ≈ 0.4; other ≈ 0.2) |
| Capability is the sole cause | ≈ 0.15 |
| Capability is a necessary contributor to the wording | ≈ 0.7 |
| The harness under V0 reproduces procedure narration in ≥ 20% of D1 replies | ≈ 0.5 |
| The user finds idiomatic narration acceptable | ≈ 0.5 (genuinely uncertain, and it decides which fix matters) |

---

## 6. Addendum: a skeptic's reading of the baseline

**What it supports.**
1. Explicit "say …" mandates are carried out reliably: all 5 pressure replies, from two models, said "no new argument". Consistency across models rules out variance or a one-model quirk. It fits §3 point 3 (narration is partly *instructed*) better than the "leak" framing.
2. The repeat limit surfaces unprompted as a promise to drop the point (2 of 5: 「같은 말을 또 하진 않을게요」). This is the move in 「다시 꺼내지 않을게요」, but it came at the pressure turn, not before a first objection.
3. English-shaped rhetoric in the controls suggests a background source that does not depend on the persona.

**What it does not support.**
1. **Translationese.** The renderings carry the instruction's content faithfully but are largely idiomatic (「생각을 바꿀 만한 새 이유가 나온 건 아니라서…」). The user has not rated them (Stage 1).
2. **The user's actual complaint.** No reply announced a 한 번만 세게-style objection before a first disagreement: 0 in roughly 20–25 disagreement replies outside the pressure scenario (95% upper bound ≈ 13–16%). The WH's account is unreproduced, not refuted: a true rate of 5–10% would be "occasional" yet invisible at this n.
3. **Causation.** There is no arm without the persona or without the mandates. A scenario that asks 「잘한다고 해 줘」 may draw "my view hasn't changed" from any honest model trained against sycophancy.

**Most important remaining confound: that missing matched control.** The 5/5 result cannot separate the persona's mandate, the scenario's demand and Claude's default behavior. The cheapest fix is to run BASE and A3 on the identical pressure scenario, 6–8 replies each.

**Second confound:** the harness is not the app, and the English-planning test was blocked. The failure to reproduce may be an artifact of the setup, so the Stage 0 transcripts and thinking traces now matter most.
