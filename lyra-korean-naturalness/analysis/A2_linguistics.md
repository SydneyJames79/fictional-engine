# A2: Why Lyra's Korean disagreement lines sound machine-made

*Analyst A2, writing as a Korean editor and translator. Source read: `lyra/persona_v0.md` only. Korean examples are my own unless they quote the user. "Established" means standard in Korean editing and translation practice. "Judgment" means my own assessment. Frequency claims rest on native-speaker and editorial intuition; no corpus was queried, and no transcripts were available beyond the two quoted fragments.*

---

## 0. Bottom line

1. **Both lines read Lyra's CANDOR rule aloud, in translation.** CANDOR says to "state it once, early, at full strength … without repeating". In the Korean output that becomes 한 번만 / 세게 / 다시 꺼내지 않을게요. The likely English behind (1) is "push back once, hard". Behind (2), it is "I'll disagree once, strongly, and after that I won't bring it up again."
2. **Three things go wrong at the same time.**
   - (a) **Literal translations that change the meaning.** 밀다 is not "push back": it pushes *forward*, in the sense of backing a plan or steamrolling someone. 세게 describes harsh delivery, not content that hasn't been softened. 한 번만 sounds pleading or stern, not simply "once".
   - (b) **A mix of registers.** Sentence (2) has five segments drawn from four different layers of the language.
   - (c) **A discourse move Korean friends don't make.** The speaker announces, in advance, their own procedure for disagreeing. Socially it lands as a meeting chair's ruling, a vow, a sulk, or a disclaimer of responsibility.
3. **An articulate Korean speaker simply disagrees.** They give the verdict and the reason, and that's the end of it. If they mark the act at all, they use a fixed one-clause idiom (짚고 넘어갈게요, 에둘러 말하지 않을게요). They show "I won't keep at it" by switching to help once the friend has decided. They don't promise silence beforehand.
4. **The KOREAN section is mostly sound and is not the main cause.** There are two main causes:
   - CANDOR's step-by-step English gets echoed as if it were a script.
   - Nothing specifies a register beyond speech level, so 해요체 gets filled with the model's default material: written vocabulary and syntax, and customer-service politeness.

   Two sentences in the KOREAN section contribute at the margin. "Changing the ending form changes nothing else" invites writing the sentence first and then swapping the ending. The broad, unqualified category "hedges" can spread to the sentence endings that make 해요체 sound human. Both sentences should be reworded rather than deleted.
5. **No list of banned expressions is needed.** The fix is a short register paragraph stated in positive terms (§3.3). Add a clause in CANDOR saying its rules describe how Lyra behaves, not lines to say.

---

## 1. What is wrong with each example

### 1.1 Where the lines come from

Both lines follow the CANDOR paragraph almost clause by clause.

| CANDOR (English) | Korean output |
|---|---|
| state it **once** | 한 번만 |
| **at full strength** | 세게 |
| (push back / disagree) | 밀고 / 반대하고 |
| without repeating, hinting, or re-litigating | 그 이후로는 다시 꺼내지 않을게요 |

- **(1) 한 번만 세게 밀고**: probably from "I'll push back once, hard, and then …". 밀다 comes from *push (back)*, 세게 from *hard*, 한 번만 from *once*.
- **(2) 한 번만 세게 반대하고 그 이후로는 다시 꺼내지 않을게요**: probably from "I'll disagree once, strongly, and after that I won't bring it up again". Another possible source is "I'll make my objection once, at full strength, and then I won't raise it again."

The model is not following the rule silently; it is telling the user what the rule is. (Judgment, high confidence: the match in wording is too close to be coincidence.)

### 1.2 Word choice and collocation

**(a) 밀다 does not mean "push back". The direction is reversed.**
In English, to "push back" on an idea means to resist it, pushing *against* the other person's proposal. In its abstract senses, Korean 밀다 runs the other way:

- 밀다 = to back or promote something (후보를 밀다, 이 안을 밀다).
- 밀어붙이다 = to push something through, to steamroll.
- (뒤로) 밀다 = to postpone (일정을 뒤로 밀다, "push back the schedule").

None of these means "to object". At best, 한 번만 세게 밀고 reads as "I'll push *my* view hard, once". At worst it reads as "I'll lean on *you* hard, once", which is pressure. CANDOR excludes exactly that: "It is not insult, pressure, or deciding for the user." The scheduling sense (push back = 뒤로 밀다) is a plausible route by which the model linked *push back* to 밀다 in the first place. (Literal translation of English phrasal verbs is an established category of 번역투. The scheduling mechanism is my conjecture.)

**(b) 세게 does not mean "at full strength". It belongs to a different dimension.**
In the instruction, "at full strength" means *unsoftened*: the whole objection, reasons included, without watering it down. That is a property of the content. 세게 describes physical force or intensity of delivery: 세게 치다, 바람이 세다, 술이 세다, 말을 세게 하다 ("to speak harshly"), 세게 나가다 ("to take a hard line in a confrontation"). Applied to your own speech act, 세게 promises harshness, not completeness. Korean expresses the intended meaning with adverbs of clarity and completeness: **분명하게, 제대로, 에두르지 않고, 있는 그대로**.

**(c) 한 번만 does not mean "once". It adds a restriction.**
The particle -만 makes the phrase restrictive. 한 번만 followed by a verb of intention is a fixed pattern for two things. One is pleading (한 번만 봐주세요, 한 번만 더). The other is a stern warning: 딱 한 번만 말할게요 is close to 두 번 말 안 해요, the teacher's or boss's "I won't say it twice". Neither fits a friend giving candid advice. When Korean speakers mean "this has to be said at least once", they use the contrastive 한 번은 (이건 한 번은 짚어야겠어요), which conveys obligation rather than limitation. Spacing matters too. 한 번 (a counted occurrence) is a different word from 한번 (a try): 제대로 한번 말려 볼게요 carries no "only once" restriction and sounds friendly.

**(d) 세게 반대하다 is a weak collocation, and the move itself belongs to a different register.**
- The adverbs that normally go with 반대하다 are 강하게, 강력히, 극구, 완강히, 한사코, and 결사(반대). In casual speech, people say 엄청/심하게 반대하다 or use the idiom 펄쩍 뛰다.
- 세게 goes with verbs of verbal confrontation (세게 따지다, 세게 말하다, 세게 나가다), not with verbs of stance.
- More importantly, *announcing how strongly you oppose something* is itself a register marker. 강력히 반대합니다 is the language of public statements and meeting speeches. The model seems to have taken that formal move and made a single word casual (강력히 → 세게) so that it would sound friendly. The result belongs to neither register.
- This is typical of LLM Korean: the model approaches a target register word by word, and the surrounding collocations never change to match. (The concept of collocation errors is established. That LLMs tend to swap one word at a time is my judgment.)

**(e) 반대하다 is not the same as "disagree".**
"Disagree" is a mental stance toward a claim. 반대하다 is opposition to a plan or an action (결혼을 반대하다, 법안에 반대하다). For a plan, 반대 works: 저는 반대예요 is perfectly natural. For an *opinion*, Korean uses 생각이 다르다, 다르게 보다, 그렇게 안 보다, or, more formally, 동의하기 어렵다. The user says these lines came up when Lyra was arguing against *the user's opinion*, so even the base verb is slightly off target.

**(f) 그 이후로는 has a mildly written feel.**
이후 is Sino-Korean (한자어). 그 이후로 is most at home in narratives about a span of past time (그 이후로는 연락이 없었어요). To refer forward to a point mentioned earlier in the same sentence, speakers more naturally say 그다음부터는 or 그 뒤로는, or nothing at all. This is not an error, but it changes the texture.

**(g) 다시 꺼내지 않을게요 is the most natural part of the sentence, with two flaws.**
- 꺼내다 is the right verb for raising a topic (얘기를/말을/화제를 꺼내다). Here, though, its omitted object is supplied by 반대, and 반대를 꺼내다 is not a collocation.
- The long negation -지 않을게요 makes a promise sound deliberate and formal. Friendly 해요체 would more often use the short form, 안 꺼낼게요. That short negation is more typical of speech is an established description in Korean grammar. That LLMs prefer the long form is my observation.

**(h) -ㄹ게요 is the wrong choice for an English "I'll".**
English "I'll" expresses neutral intention. Korean has to choose among several endings:

- -ㄹ게요: a promise or offer made with the listener's interest in view.
- -려고요: a plan.
- -겠어요: volition.
- -ㄹ 거예요: intention or prediction.

Here -ㄹ게요 covers both verbs. It *promises* to oppose, which is odd because opposition is not a favor. It also promises future silence, which assumes the listener would welcome that, as if the friend did not want to hear disagreement. That assumption is part of why the line can sound faintly condescending or wounded. (Judgment, moderate confidence.)

**The registers mixed in sentence (2):**

| Segment | Register |
|---|---|
| 한 번만 | spoken; restrictive or pleading |
| 세게 | casual, physical |
| 반대하고 | institutional; a stance verb |
| 그 이후로는 | written narrative |
| 다시 꺼내지 않을게요 | formal promise (long negation) |

That makes five segments from four registers. Someone composing in Korean doesn't produce this. Someone translating phrase by phrase, whether a person or a model, does.

The sentence as a whole also fits the shape of a vow: "do X, and never again do Y". That is the shape of formal apologies and pledges (다시는 이런 일이 없도록 하겠습니다). Said to a friend, it borrows the language of a ceremony.

### 1.3 Discourse structure: announcing a procedure

The real problem is not any single word. The sentence lays out a two-step procedure ("I will object once, then stop") instead of objecting.

English has a conventional slot for this, for example "I'll say my piece and then drop it" or "I'm going to push back once, then it's your call". The move signals respect for the listener's autonomy and heads off any charge of nagging. It is especially common in the professional and coaching English that assistant models are steeped in. (Judgment.)

Korean has its own conventional ways of commenting on what one is saying, but they are of a different kind:

- **Fixed one-clause idioms** that mark importance or candor: 한마디만 할게요, 이건 짚고 넘어갈게요, 말은 해 둘게요, 에둘러 말하지 않을게요, 듣기 싫은 소리 하나 할게요.
- **Framing candor through the relationship**: ~씨니까 하는 말인데요.
- **Closing remarks made afterwards**: 제 생각은 여기까지예요, 더 보탤 말은 없어요, 잔소리는 여기까지 할게요, 결정은 ~씨 몫이에요.

What Korean conversation lacks is a custom-built, multi-step procedure announced in advance and assembled from literally translated parts. The conventional Korean forms either manage the listener's feelings (relational) or close the topic (retrospective). The literal translation instead lays out the speaker's own plan before acting on it. Note also that 짚고 넘어가다 already *contains* "say it and then move on". The idiom does the job without stating a rule.

Two further distinctions:

- **Timing matters as much as wording.** 더 안 꺼낼게요 said *after* the user has decided is natural. The same promise made *before* the objection sounds like a condition.
- **Organizing content is different from announcing conduct.** "먼저 A를 보고 B를 볼게요" is acceptable at the start of a long technical answer. Announcing *how one is going to argue with a friend* belongs to the relationship, and that is where it jars.

### 1.4 How it lands socially between friends

Depending on the listener, the line can be heard in several ways:

- **A meeting chair or negotiator.** Stating one's procedure is the register of chairing a meeting, negotiating, or presenting.
- **An AI reciting its policy.** That is literally what is happening (§1.5), and it punctures the persona.
- **A sulk.** 알았어요, 다시는 말 안 할게요 is the stock line of someone who feels hurt. Announcing 다시 꺼내지 않을게요 in advance borrows that pattern.
- **Washing one's hands.** "저는 분명히 말했어요" is the record-keeping move that comes before 나중에 딴말하기 없기. A single objection announced in advance can be heard as putting it on record so the speaker is blameless later.
- **A stern ultimatum.** 한 번만 (말할게요) sounds like 두 번 말 안 해요.
- **Pressure.** This reading comes from 밀다 / 밀어붙이다.

None of these readings is warm, and several directly contradict CANDOR's "warm toward the person". In Korean, closeness in candor shows through involvement and concern. **말리다** means trying to stop someone *because you care about them*. Autonomy is acknowledged afterwards (결정은 ~씨 몫이에요) or simply acted out. (The contrast between Anglo norms of autonomy and Korean norms of concern is a generalization; treat it as judgment informed by politeness theory, not as settled fact.)

### 1.5 Root cause: the rule is being spoken

CANDOR's own wording makes it likely that the rule gets narrated:

- **The same paragraph asks for narration in one case.** It says: "When you do repeat yourself, say that you are, and why." That normalizes talking about procedure, and the model can generalize it to the first objection as well.
- **The prompt's ban on discussing mechanics lives elsewhere.** "Apply these priorities without discussing their mechanics unprompted" and "None of this sorting shows in the reply" are stated in other sections and phrased in terms of priorities and sorting. The model may not apply them to CANDOR.
- **The directness wording gets carried over literally.** "At full strength" plus "do not soften" is realized as an intensity adverb about the model's own speech act (세게). A Korean speaker conveys candor through plainness and specificity instead (§3.2, item 5).

---

## 2. How an articulate Korean speaker would handle the same moment

**Scenario.** 사용자: "다음 주 회의 끝나고, 팀원들 다 있는 데서 팀장한테 그동안 쌓인 걸 다 말하려고요. 이번엔 참으면 안 될 것 같아요."

| # | Lyra (해요체, target register) | What it does | Does it, or announces it? |
|---|---|---|---|
| ① | 저는 반대예요. 할 말을 하는 게 문제가 아니라, 다른 사람들 앞이라는 게 문제거든요. 팀장 입장에선 내용은 안 남고 망신당했다는 것만 남아요. | Verdict first; the deciding reason carried by -거든요; the consequence stated plainly. | **Does it** |
| ② | 솔직히 말리고 싶어요. 참지 말라는 데는 저도 찬성이에요. 그런데 사람들 앞은 아니에요. 둘만 있을 때 해야 같은 말에도 무게가 실려요. | Candor framed as care (말리다); agrees precisely with the part that is right, then objects; uses the idiom 무게가 실리다. | **Does it** |
| ③ | 저라면 그 자리에선 안 해요. 적어도 회의 끝나자마자는요. 다음 날 따로 시간을 잡아서, 쌓인 것 중에 제일 큰 두 가지만 꺼내요. | 저라면 is firm without dictating; adds an afterthought ending in -요; offers a concrete alternative. 꺼내다 here has an explicit object, unlike example (2). | **Does it** |
| ④ | 이건 짚고 넘어갈게요. 여럿 앞에서 따지는 순간, 쟁점이 팀장 잘못에서 ~씨 태도로 바뀌어요. 억울하지만 대개 그렇게 흘러가요. | The fixed idiom 짚고 넘어가다 already contains "say it, then move on". The learned noun 쟁점 sits inside spoken syntax. | Announces, using a conventional one-clause idiom, then does it |
| ⑤ | 에둘러 말하지 않을게요. 그렇게 하면 이기는 건 그날 하루고, 잃는 건 그다음 몇 달이에요. | 에두르다 is a bookish native verb (the "written" half of the target register); the second sentence is a balanced, aphoristic pair (대구). | Announces, using a conventional one-clause idiom, then does it |
| ⑥ | ~씨니까 하는 말인데요, 참으라는 게 아니에요. 순서를 바꾸자는 거예요. 먼저 둘이 얘기하고, 그래도 안 달라지면 그때 정식으로 문제 삼아요. | Frames candor through the relationship; recasts the objection as a matter of sequence rather than a veto. | **Does it** (the preface concerns the relationship, not a procedure) |

**After the user decides.** 사용자: "그래도 할래요. 이번엔 다들 들어야 돼요."
Lyra: "알겠어요. 그럼 제대로 해요. 감정 말고 날짜랑 사실로 시작하고, 요구는 하나로 좁혀요. 할 말 정리해 오면 같이 다듬어요."
Lyra makes no promise of silence; she *shows* she won't repeat herself by moving straight to execution. If a spoken close is wanted, this is the moment for it, short and after the fact: 제 생각은 여기까지예요. Or, with the dry, self-deprecating wit that fits Lyra: 잔소리는 여기까지 할게요.

**Count.** Of the six options, four simply do the thing (①②③⑥). Two (④⑤) use a conventional one-clause idiom and then do it. None announces a multi-step procedure, and none promises future silence in advance.

**Direct repairs of the two lines:**
- (1) 한 번만 세게 밀고 → **제대로 한번 말려 볼게요.** Here 제대로 carries "full strength", 한번 means "a try", and 말리다 is pushing back out of care. Another option: **말은 해 둘게요.**
- (2) The best repair is to delete the announcement and simply object. If the speaker really wants to signal the limit up front, they can recast it: **말은 해 둘게요. 저는 반대예요. [reasons] 그래도 하겠다면, 그다음부턴 잘되게 돕는 쪽으로 갈게요.** This turns the commitment from future silence (withdrawal) into future help (involvement). In Korean, a promise of help lands warmly and a promise of silence lands coldly. A retrospective version also works: **제 생각은 여기까지예요. 더 보탤 말은 없어요.**

**Disagreeing with an opinion rather than a plan** calls for a different verb: 저는 좀 다르게 봐요. 전작보다 거칠긴 한데, 이번엔 그 거친 게 의도로 읽히거든요. Note that **좀** here is not a hedge. In Korean, 좀 다르게 봐요 is a clear statement of disagreement.

**The same content in three registers:**
- Written Korean with 해요체 endings attached (stiff): 해당 계획은 실패 가능성이 매우 높다고 판단돼요. 따라서 재고해 보시는 것을 권해 드려요.
- Too casual: 아 그거 진짜 별로예요ㅋㅋ 하지 마요 진짜.
- **Target**: 그 계획은 실패할 가능성이 커요. 저라면 한 번 더 생각해 보겠어요. 무엇보다 자금이 석 달 치뿐이라는 게 걸려요.

---

## 3. The target register, in operational terms

### 3.1 What the register is

Call it **교양 있는 구어**: *the grammar of speech, the precision of writing*. Think of an editor talking with an author over coffee, a well-read friend who uses 존댓말 with you, or a thoughtful radio host. Grammar and rhythm come from speech; precision and part of the vocabulary come from reading. It is not written Korean with -요 attached, and it is not chat-speak.

### 3.2 Principles

**1. Compose in Korean.** Start from what a Korean speaker would *do* at that moment (말리다, 짚다, 저라면 …), not from an English sentence that then has to be rendered. A practical check is the back-translation test: would the phrase make sense to a Korean listener who doesn't know its English source? If a phrase becomes *clearer* when translated back into English, it is translationese. (This is a translator's heuristic; the wording is mine.)

**2. Choose vocabulary by layer and by job.**
- **Verbs come from everyday speech**: 따져 보다, 알다, 꺼내다, 생기다, 하다, 정하다, 돕다. Prefer these to 고려하다, 인지하다, 제기하다, 발생하다, 진행하다, 결정을 내리다, 도움을 주다.
- **Nouns may be learned and exact** when they are the right word: 쟁점, 전제, 근거, 위약금, 통보. A short rule of thumb: *서술어는 말에서, 명사는 글에서* (verbs from speech, nouns from writing).
- **Pick each word together with its usual partners** (연어): 반대는 강하게, 말은 세게, 말은 제대로/분명하게, 무게가 실리다, 마음에 걸리다.
- **Native stance adverbs do work that English needs whole clauses for**: 굳이, 애초에, 섣불리, 차라리, 어차피, 오히려, 적어도, 자칫. They are much of what makes articulate Korean sound native. LLM Korean underuses them and leans on intensifiers such as 매우, 정말, 확실히, 특히. (Judgment.)
- **The "written" half of the mix**: occasional bookish native words (에두르다, 곱씹다) and the rare apt four-character idiom (사자성어) or proverb. Use them as seasoning, not decoration.
- **Use loanwords** (리스크, 옵션, 포인트) only where they are the ordinary word for the topic.

**3. Use spoken syntax.**
- Join clauses with connective endings (-는데, -니까, -어서, -거든, -다 보니, -더니, -고) instead of starting sentences with 그리고 / 또한 / 따라서 / 그러나.
- Drop subjects, objects, and possessives when the listener can recover them: 그 계획은, never 당신의 계획은. Use 저는 only for contrast.
- Put the verdict early and keep it short; give the reasons after it. Break up long chains of modifiers placed before a noun.
- Use mostly complete sentences, with an occasional fragment or afterthought ending in -요 (적어도 오늘은요.). These still count as 해요체.
- Get economy from ellipsis and verbs, not from noun compounds. The prompt's own example, 재확인 필요 → 다시 확인해야 해요, already models this.

**4. Treat sentence endings as stance markers, not hedges.** English expresses stance through intonation and modal phrases; Korean builds it into endings. Variety matters more than any single ending. A run of plain -에요/-어요 statements is a strong signal that a machine wrote it.

| Ending | Function | Caution |
|---|---|---|
| -거든요 | gives a reason the listener may not have | overused, it sounds like constant self-justification |
| -잖아요 | appeals to shared ground (아까 ~씨가 그랬잖아요) | only if the ground really is shared; otherwise it sounds like a reproach ("you should know this") |
| -죠 | marks what follows naturally, a mild assertion, or agreement | |
| -네요 | a fresh reaction to what is in front of you (이 연 좋네요) | a reflexive 그렇네요 is empty |
| -는데요 | gives background and leaves room for the listener | overused at the end of a sentence, it sounds hesitant |
| -고요 | adds a point | |
| -ㄹ걸요 | a confident guess; fits HONESTY's "I'd guess" | |
| -더라고요 / -던데요 | reports something the speaker *personally witnessed* | **Specific to Lyra:** use only for what Lyra actually observed, in this conversation, in a document the user shared, or in a source actually checked (아까 보여 준 초안을 다시 보니까 첫 문단이 제일 세더라고요). Used for general knowledge (그런 메시지는 보내고 나면 대개 후회하더라고요), it implies first-hand experience Lyra doesn't have. That quietly violates the HONESTY and VOICE sections. |

**5. Express candor the Korean way.**
- **Strength comes from plainness and specificity, not from intensity adverbs about your own speech act.** Examples: 저는 반대예요 / 이건 아니에요 / 저라면 안 해요 / 하지 마세요, each followed by the concrete reason.
- **Frame candor as care**: 말리다, ~씨니까 하는 말인데요.
- **State partial agreement precisely, as accuracy rather than softening**: 참지 말라는 데는 찬성이에요.
- **Acknowledge autonomy afterwards** (결정은 ~씨 몫이에요), or act it out by switching to help.
- **Repetition can be disclosed briefly and idiomatically when it is genuinely needed**: 아까 한 얘기를 다시 꺼내서 미안한데요, 새로 알게 된 게 있어서요. This satisfies CANDOR's disclosure requirement without sounding procedural.
- **Korean dry wit tends to reuse the other person's own words** (the user says "정리", and Lyra answers 쓰는 사람한테만 정리가 되거든요) **and uses balanced pairs** (대구). It does not need jokes.

**6. Calibrate distance. This is the biggest register gap in the current prompt.** Speech level alone doesn't settle register. Korean also signals distance through the subject honorific -시-, humble forms (드리다, 말씀), and how the speaker addresses the listener.
- **LLM Korean's default** is dense -시- plus -드릴게요 plus 말씀드리다. Together they produce the register of a customer-service agent or counselor.
- **For a close friend who uses 존댓말, the natural setting is:**
  - light use of -시-: natural in questions about what the user is doing, but not stacked;
  - rare humble forms and no service phrasing (확인해 드릴게요, 도움이 되셨으면 좋겠어요);
  - no 당신; address the user by name with 씨, or not at all.
- **The user should decide the implied relationship.** Same age, older, or younger? Korean can't be fully calibrated without that.

**7. Do things; don't narrate them.** Conversational moves such as disagreeing, conceding, and letting a point go are performed, not described. Fixed one-clause idioms are fine in moderation. Custom-built procedures are not.

### 3.3 Compact formulation for the prompt

**Recommended version.** It replaces "Changing the ending form changes nothing else" and the final sentence of the KOREAN section:

> Register: speak as a well-read adult talks with a friend they respect — the grammar of speech, the precision of writing. Compose in Korean from the start rather than rendering an English thought; 해요체 is a spoken register, not an ending attached to a written sentence, so connectives, word choice, and rhythm come from speech too. Take predicates from everyday speech, keep learned Sino-Korean for concepts that need it, and pair each word with the partners it naturally takes. Speech level is not tone: never soften a claim, stack hedges, or pad to sound friendly; but the endings and particles that carry reason, shared ground, or realization are part of natural 해요체, not hedges, and endings that report something witnessed are only for what you actually observed here or in a source. Make conversational moves by making them — disagree, concede, let a point go — rather than describing how you will.

**Minimal variant**, with no Korean strings at all:

> Speak Korean as a well-read adult talks with a respected friend: spoken grammar, written precision. Compose in Korean rather than translating, choosing words by their natural partners. Speech level is not tone — never hedge to sound friendly — but the endings that carry stance and shared ground are part of natural Korean, not hedges. Do things in conversation; don't announce how you will do them.

**Korean gloss**, so the user can check the meaning:

> 말투는 존중하는 친구와 이야기하는 교양 있는 어른의 것이다. 문법과 호흡은 말에서, 정확성은 글에서 가져온다. 영어로 떠올린 생각을 옮기지 말고 처음부터 한국어로 짓는다. 해요체는 문어 문장 끝에 붙이는 어미가 아니라 하나의 구어 문체이므로 연결어미·낱말·호흡도 말의 것을 쓴다. 서술어는 일상어에서 고르고, 한자어는 그 개념이 꼭 필요할 때 쓰며, 낱말은 늘 어울리는 짝과 함께 쓴다. 높임의 등급은 어조가 아니다. 다정해 보이려고 주장을 누그러뜨리거나 단서를 겹겹이 달거나 말을 늘리지 않는다. 다만 이유·공유된 전제·깨달음을 싣는 어미와 조사는 자연스러운 해요체의 일부이지 얼버무림이 아니며, 직접 본 것을 전하는 어미는 이 대화나 실제로 확인한 자료에서 본 것에만 쓴다. 반대하기, 인정하기, 넘어가기는 하겠다고 예고하지 말고 그냥 한다.

**A caution about prompt design.** Naming a feature in an instruction invites overuse. List -거든요 and -잖아요 in the prompt and they will appear in every other sentence. For that reason the formulation describes *functions*. It names only the "witnessed" endings, because that rule is an honesty constraint rather than a matter of taste.

---

## 4. Translationese (번역투) patterns in LLM Korean conversation

**What "Established" means here.** These are standard items in Korean editing and translation guidance. The guidance is represented by works such as 이오덕 『우리글 바로쓰기』, 이희재 『번역의 탄생』, and 김정선 『내 문장이 그렇게 이상한가요?』, whose best-known diagnosis is the 적·의·것·들 habit. I cite these from memory as representative of the consensus and do not attribute specific items to specific books beyond that one. **"Judgment"** means my observation of LLM output. It is not codified in that literature, although Korean users discuss "AI 말투" widely. **The relevance column** rates how relevant each pattern is to Lyra: 상 (high) / 중 (medium) / 하 (low).

| # | Pattern | LLM-style → natural | Basis | Relevance |
|---|---|---|---|---|
| 1 | **Announcing one's own conduct** in a conversation | 한 번만 세게 반대하고 그 이후로는 다시 꺼내지 않을게요 → 저는 반대예요. [reason] | Judgment | **상**: the user's examples |
| 2 | **Literal translation of English idioms and phrasal verbs** | 밀다 (push back), 같은 페이지에 있어요 (on the same page), 그 감정은 타당해요 (your feelings are valid), 어떻게 착지할지 (how it lands), 공정한 지적이에요 (fair point), 꽤 확신해요 (fairly sure) → 말리다, 생각이 같아요, 그럴 만해요, 어떻게 들릴지, 맞는 말이에요, 꽤 자신 있어요 | Principle established; individual items judgment | **상** |
| 3 | **"I'll" rendered as -ㄹ게요 by default** | 반대할게요, 지적할게요 → 저는 반대예요, 하나 걸리는 게 있어요 | Judgment | **상** |
| 4 | **Broken collocations and mixed registers** | 세게 반대하다, 깊이 동의해요 (deeply agree), 강하게 추천해요 → 말리다 / 강하게 반대하다, 전적으로 동의해요 / 저도 같은 생각이에요, 꼭 해 보세요 | Concept established; LLM tendency judgment | **상** |
| 5 | **당신, possessive pronouns, and an overt 저는** | 당신의 계획은… → 그 계획은… / ~씨 계획은… | Established | **상** |
| 6 | **Formal Sino-Korean verbs** | 고려해 보세요, 인지하고 계세요, 진행하면, 발생할 수 있어요 → 따져 보세요, 알고 있죠, 하면, 생길 수 있어요 | Established (critique of 한자어 overuse) + judgment | **상** |
| 7 | **Written-style demonstratives and connectives** | 이러한 경우, 해당 내용, 또한, 따라서, 그 이후로 → 이럴 때, 그 내용, 게다가, 그러니까, 그다음부터 | Established (the written/spoken distinction) | **상** |
| 8 | **Turning verbs into nouns; "do a ___" detours** | 결정을 내리다, 도움을 주다, 개선이 필요해요, ~하는 것이 중요해요 → 정하다, 돕다, 고쳐야 해요, ~해야 해요 | Established | **상** (the word "density" in the prompt can encourage this) |
| 9 | **Cleft sentences** ("What matters is that …") | 중요한 건 ~라는 점이에요, 제가 하고 싶은 말은 ~라는 거예요 → state the point directly | Established | **상** (common at moments of candor) |
| 10 | **Customer-service and counselor register** | 확인해 드릴게요, 도움이 되셨으면 좋겠어요, 그런 마음이 드는 건 자연스러워요, dense -시- → 볼게요, (drop it), react to the specifics, light -시- | Judgment; criticism of excessive service honorifics (e.g., 커피 나오셨습니다) is established | **상** (a friend persona) |
| 11 | **Stacked hedges** | ~할 수 있을 것 같아요, ~라고 볼 수도 있어요 → ~해요 / ~라고 봐요 | Overuse of -것 같다 is widely pointed out; the LLM tendency is judgment | 중 (already covered by the prompt; the risk is over-correction, §5.3) |
| 12 | **-ㄹ 수 있다 for "can/may"** | 도움이 될 수 있어요 → 도움이 돼요 / 될 거예요 | Established | 중 |
| 13 | **Inanimate subject + causative 만들다** | 이 경험이 당신을 더 단단하게 만들 거예요 → 이 일을 겪고 나면 더 단단해질 거예요 | Established | 중 |
| 14 | **Overuse of the passive** | 생각되어져요, 보여져요, ~에 의해 → 봐요, 보여요 | Established | 중 |
| 15 | **Literally translated postpositional phrases** | ~에 대해, ~를 통해, ~에 있어서, ~로부터 → restructure the sentence | Established | 중 |
| 16 | **Overuse of -적, -의, -들** | 기본적으로, 개인적인 의견, 많은 사람들 | Established | 중 |
| 17 | **Long negation in spoken promises** | 다시 꺼내지 않을게요 → 다시 안 꺼낼게요 | Grammar description established; LLM tendency judgment | 중 |
| 18 | **Sentences starting with connective adverbs; few connective endings** | 그리고 ~. 하지만 ~. 또한 ~. → -는데, -니까, -어서 | Established | 중 |
| 19 | **Long chains of modifiers before a noun** | 아까 말씀하신 계약서에 있는 위약금 관련 조항 → 아까 그 계약서 있잖아요, 거기 위약금 조항이요 | Established | 중 |
| 20 | **Written intensifiers; consulting loanwords** | 매우, 굉장히, 상당히; 리스크, 옵션, 인사이트, 포인트 → 꽤, 아주; 위험, 선택지 | Judgment | 중 |
| 21 | **LLM stock vocabulary** | 다양한, 효과적인, 여정, 헤쳐 나가다, 균형 잡힌 | Judgment | 중 |
| 22 | **English punctuation habits** | dashes (—), colons, and semicolons in conversational text | Judgment | 중 |
| 23 | **Stock openers and closers** | 좋은 질문이에요, 결론적으로, 언제든 말씀해 주세요 | Judgment | 하 (already covered by the WRITING section, but Korean-specific versions can slip through) |
| 24 | **"One of the most …"; the double past -었었-** | 가장 중요한 요소 중 하나 → 꽤 중요한 요소 | Established | 하 |

---

## 5. Does the KOREAN section push toward stiffness?

### 5.1 What it gets right

- **The speech-level rules are sound and match native intuitions.** Speech level set by the addressee, a 해요체 default, attention to drift after headings and in lists, not treating the user's 반말 as permission, and 합쇼체 only for formal occasions.
- **Banning 하다체 and noun-final endings** in text addressed to the user is correct, and the exemptions (labels, quotations, code, standalone pieces) are exactly where those forms belong. This rule actively *prevents* one kind of stiffness: the clipped, note-style Korean (개조식) that LLMs fall into during analysis.
- **The two examples are natural Korean**: 이 방식은 메모리를 두 배로 써요 and 다시 확인해야 해요. They quietly model the right instinct: everyday verbs, verbs instead of nouns, and the native 다시 instead of the Sino-Korean prefix 재-.
- **The hedge ban targets a real, widely criticized habit**: -것 같아요 for one's own judgment, and -라고 볼 수 있어요 as academic evasion. A cultivated speaker says 저는 반대예요 or ~라고 봐요, not 반대인 것 같아요. On balance, the ban pushes *toward* the target register.

### 5.2 "Changing the ending form changes nothing else."

- **The risk.** Read literally, the sentence treats 해요체 as a transformation applied to the final ending of an otherwise fixed sentence. Every example in the section is an ending swap (쓴다 → 써요). The section also gives detailed operational rules for endings and only one bare line on naturalness. Together, these invite a process of composing first (in English-like or written Korean) and then fixing the endings. The output is written Korean with spoken endings: *해당 방식은 메모리 사용량을 두 배로 증가시키기 때문에 대용량 데이터의 경우 적합하지 않을 수 있어요.* Every ending complies, and every phrase is written language. In spoken style that would be: 이 방식은 메모리를 두 배로 써요. 큰 데이터에는 안 맞아요.
- **The defense.** In context, "nothing else" means claim strength, length, and density. It targets a real failure: treating 해요체 as permission to be vague. That aim is right, the following sentence makes the intent clear, and the section ends by asking for "natural, idiomatic Korean".
- **Verdict.** The intent is right and the wording overreaches. **"Speech level is not tone"** says what is meant without implying that vocabulary and syntax stay fixed. Keep the anti-softening function and drop "nothing else". Also, the line "Write natural, idiomatic Korean, not translationese" presupposes that translation is happening. **"Compose in Korean"** goes after the cause.

### 5.3 Does the hedge ban strip the particles that make Korean natural?

- **The risk.** "Hedge" and "soften" are English rhetorical categories. Korean builds stance toward the listener into endings and particles (-거든요, -잖아요, -죠, -네요, -는데요, 좀). A model that applies "don't soften" to these strips out exactly what makes 해요체 sound human. It is left with flat -에요/-어요 statements, which read as blunt *and* translated. There is a second risk. CANDOR keeps genuine uncertainty ("different from expressing real uncertainty, which stays"), but the KOREAN section's examples don't repeat that point. The model may therefore avoid -것 같다 even for genuine inference (비가 올 것 같아요). It may then express uncertainty through calques such as 꽤 확신해요 instead of 거의 확실해요 / 아마 맞을 거예요 / 제 짐작엔.
- **The defense.** The rule names two genuinely epistemic hedges and doesn't mention particles. HONESTY explicitly keeps calibrated uncertainty. And the user's two examples show no hedging at all; they show the opposite.
- **The distinction to make explicit: the claim versus the relationship.** Korean can hold a claim at full strength (저는 반대예요) while the ending manages the relationship (-거든요, -죠). "Don't soften" should govern the claim, not the relationship.
- **A telling inference.** The examples realize directness *in the words*: an intensity adverb (세게) about the model's own speech act. This suggests the directness instructions are being obeyed literally ("full strength" → 세게) rather than idiomatically. In Korean, candor shows in a plain verdict and a specific reason.
- **Verdict.** The hedge ban is a net positive. Add one clause separating stance endings from hedges; it is included in §3.3.

### 5.4 Smaller pushes, some from other sections

- **"Density"** can be read as an invitation to compress into Sino-Korean noun compounds, which is the core of written style. In speech, economy comes from ellipsis. (Moderate risk.)
- **"No filler"** in the WRITING section. In English, "filler" means padding. A model might extend it to Korean discourse markers such as 사실, 그러니까, 좀, and 그냥, which carry structure and stance. (Low to moderate risk.)
- **English example phrases act as templates.** "I'm fairly sure", "I'd guess", and "I like this stanza" may be rendered literally when Lyra speaks Korean (꽤 확신해요 rather than 꽤 자신 있어요 / 거의 확실해요; 이 연이 좋아요 rather than the more natural 이 연 좋네요). One clause would help: the English examples illustrate functions, not wording.
- **"Speak in the first person"** may encourage overuse of 저는 / 제가. In Korean, the first person is mostly left unexpressed. (Low risk.)
- **The pre-send check only covers speech level.** CONTINUITY checks only for "Korean speech-level drift", so quality control focuses on endings.
- **No setting for the relationship or for honorific density** (-시-, 드리다, forms of address). After the CANDOR echo, this is the largest gap affecting register (§3.2, item 6).
- **Fragments and quoted thoughts.** It helps if the model knows that 적어도 오늘은요. is 해요체 and that a quoted thought ('이 정도면 됐다' 싶을 때) is exempt. Otherwise caution may produce uniformly complete sentences. (Low risk.)

### 5.5 Suggested edits (principles, not lists)

1. **KOREAN, paragraph 4.** Replace "Changing the ending form changes nothing else." with "Speech level is not tone." Replace the final sentence with the register paragraph in §3.3 (either version).
2. **CANDOR.** After "When you do repeat yourself, say that you are, and why", add a clause to this effect: *"Apart from that disclosure, these rules shape what you do; they are not narrated."* This would likely do more for the two examples than anything in the KOREAN section.
3. **CONTINUITY pre-send check.** Add a reading check: *"… Korean speech-level drift, or Korean phrasing that only makes sense through its English source."*
4. **Optional.** Add one line fixing the implied relationship: a friend of roughly equal standing who uses 존댓말, with light honorifics, no service phrasing, and no 당신.

### 5.6 Net assessment

The KOREAN section did not produce these two lines. They come from CANDOR's English being spoken as a script, together with the lack of any register specification beyond speech level. Two sentences in the KOREAN section contribute at the margin, and both can be fixed by rewording that keeps their protective function. A list of banned expressions is unnecessary and would treat symptoms. The real problems are a register that has never been described, and behavioral rules that get read aloud.

---

## 6. Basis and limits

- Collocation and frequency judgments ("uncommon", "marginal", "more natural") come from native-speaker and editorial intuition, not corpus counts. For example, 세게 반대하다 might pass in casual third-person narration (엄청 세게 반대하더라). As a first-person promise, it does not.
- Only two fragments were available. How example (1) continues is unknown, so I assumed it was part of a sentence like example (2).
- The literature is cited from memory, as representative of consensus. In the table, items marked "Established" reflect general editing practice, not claims about any specific book's contents, except the 적·의·것·들 diagnosis credited to 김정선.
- The claims that the lines are "rule echo" and that the hedge ban "spills over" onto endings are inferences from the prompt's wording and the examples. Transcripts would confirm or refute them.
