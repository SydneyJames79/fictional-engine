# A3: Translationese (번역투) in Claude's Korean under an English persona: what the evidence says

> Note: in this committed copy, names of individual Claude models are replaced with generic labels such as "[model]".


Prepared 2026-10-06. Unless stated otherwise, every "accessed" date is 2026-10-06.

## How to read the citations

- **[OPENED]**: I read the primary text myself. This covers Anthropic pages fetched in full (anthropic.com, platform.claude.com) and the authors' own GitHub READMEs.
- **[SEARCH]**: I found the source through web search but **did not open the full text**. This environment's network egress proxy blocked arxiv.org, aclanthology.org, openreview.net, transformer-circuits.pub, huggingface.co, semanticscholar.org and most secondary sites, for both WebFetch and curl. These findings are paraphrased from search-result abstracts and summaries. Numbers marked **(check)** come from a single search summary and should be checked against the paper before anyone repeats them.
- **[UNVERIFIED]**: reported somewhere, but I could not confirm the wording or details.

Evidence and inference are kept apart. Sections 1–5 report what sources say. Section 0 is a direct textual comparison. Section 6 is my assessment.

---

## 0. The case itself: persona text vs. the output

Persona (`lyra/persona_v0.md`), line 34, the CANDOR section:
> "Disagreement: state it once, early, at full strength, with the reasons … A decision ('I've heard you; I'm doing it anyway') ends the argument: respect it and help them do it well, without repeating, hinting, or re-litigating. … Raise a settled objection or concern again only if …"

Observed output: "한 번만 세게 밀고" / "한 번만 세게 반대하고 그 이후로는 다시 꺼내지 않을게요."

| Output fragment | Persona source | Comment (my reading) |
|---|---|---|
| 한 번만 | "state it **once**" | rule restated to the user |
| 세게 | "at **full strength**" | English intensity phrase rendered with a physical-force adverb; 강하게/분명하게 반대하다 is the usual collocation |
| 밀고 | (not in persona; grep finds no "push") | calque of the English idiom **"push back"** (= disagree). 밀다 doesn't carry that sense in Korean and reads as physical pushing or 밀어붙이다 |
| 그 이후로는 다시 꺼내지 않을게요 | "without repeating … re-litigating"; "raise … again only if" | rule restated to the user |

Where "push back" plausibly comes from. Anthropic's own English texts that shape Claude use the idiom. The constitution, which Anthropic says "plays a crucial role in our training process, and its content directly shapes Claude's behavior", says "we want Claude to push back and challenge us" and "push back when something seems off". The current claude.ai system prompts say "Claude is still willing to push back and be honest" ([OPENED], see §4 and §5). That this vocabulary carried over into the Korean is my inference.

The persona already has some anti-narration lines, but they are scoped elsewhere. Line 10 says "Apply these priorities without discussing their mechanics unprompted." Line 43 says "None of this sorting shows in the reply." Nothing tells the model not to recite the CANDOR protocol. Line 65 handles naturalness in a single sentence: "Write natural, idiomatic Korean, not translationese." It gives no reason and no examples. The persona is also heavily prohibitive: a rough grep finds about 93 tokens of not/never/no/don't/do not in about 2,800 words.

One nuance a native speaker should confirm: "이 얘기는 딱 한 번만 할게요" can be perfectly idiomatic on its own. What sounds machine-made is the calqued verbs plus the full recital of the rule's structure (once, hard, never again).

---

## 1. English-centric vs. language-agnostic internal representations

**What the studies show**

- **Wendler, Veselovsky, Monea, West (2024). "Do Llamas Work in English? On the Latent Language of Multilingual Transformers." ACL 2024.** https://aclanthology.org/2024.acl-long.820/ (arXiv 2402.10588). [SEARCH; the citation also appears in the authors' repo https://github.com/epfl-dlab/llm-latent-language, OPENED]
  - Logit-lens analysis of Llama-2 on non-English prompts with single-token answers.
  - They report three phases. In the middle layers the model can already decode the semantically correct next token, but it gives the **English version higher probability** than the input-language version. Only in the final layers does the representation move to the input-language-specific region.
  - The authors frame this as an abstract "concept space" that lies closer to English, not as literal English text.
  - Context: Llama-2's pretraining data is reported as 89.70% English (Touvron et al. 2023, Table 10), as cited by secondary sources found in search, e.g. https://datawrapper.dwcdn.net/QUPvo/2/. [SEARCH; primary not opened]
- **Schut, Gal, Farquhar (2025). "Do Multilingual LLMs Think In English?"** arXiv 2502.15603, https://arxiv.org/abs/2502.15603. Search results list an ICLR 2025 page, but I did not confirm the venue. [SEARCH]
  - LLMs make key decisions in a representation space closest to English, whatever the input and output language.
  - Semantically loaded words appear first as English-like representations, then get "translated" into the target language.
  - Steering vectors work better when computed in English.
- **Dumas, Wendler, Veselovsky, Monea, West (2025). "Separating Tongue from Thought: Activation Patching Reveals Language-Agnostic Concept Representations in Transformers." ACL 2025.** arXiv 2411.08745. [SEARCH]
  - The output language is encoded at an earlier layer than the concept.
  - Concept and language can be patched independently.
  - Patching in the mean of a concept's representation across languages improves translation, which points to **language-agnostic** concept representations.
- **Wu, Yu, Yogatama, Lu, Kim (2025). "The Semantic Hub Hypothesis: Language Models Share Semantic Representations Across Languages and Modalities." ICLR 2025.** https://proceedings.iclr.cc/paper_files/paper/2025/hash/84fb08ae30ab266953d1ff72eb0611b1-Abstract-Conference.html [SEARCH]
  - Semantically equivalent inputs in different languages have similar intermediate representations.
  - That shared space is interpretable through the model's **dominant pretraining language**.
- **Zhong et al. (2024). "Beyond English-Centric LLMs: What Language Do Multilingual Language Models Think in?"** arXiv 2408.10811 (listed as Findings ACL 2025; venue not confirmed). [SEARCH]
  - Japanese-specialized models (Swallow, LLM-jp) use Japanese and English as latent languages, whereas Llama-2 uses only English.
  - The latent language is "majorly determined by the language of its training corpora."
- **Harrasse, Draye, Pandey, Jin, Schölkopf (2025). "Tracing Multilingual Representations in LLMs with Cross-Layer Transcoders."** arXiv 2511.10840. [SEARCH]
  - Models trained **without English** develop the same shared multilingual structure.
  - Weaker non-English performance traces to dim late-layer features, weak middle-layer clusters and tokenizer bias, and fine-tuning strengthens these. The shared space is not inherently English, and the decoding stage can be trained.
- **Bafna, Li, Murray, Mortensen, Yarowsky, Sirin, Khashabi (2025). "The Translation Barrier Hypothesis: Multilingual Generation with Large Language Models Suffers from Implicit Translation Failure." IJCNLP-AACL 2025.** https://aclanthology.org/2025.ijcnlp-long.83 [SEARCH]
  - Generation works like an implicit pipeline: solve the task in a largely language-agnostic way, then translate the answer concepts into the target language.
  - Failure at the translation stage explains a dominant share of errors, worst for low-resource languages.
- **Sonkin, Baeumel, Gurgurov, van Genabith, Ostermann (2026). "Separating Syntax from Language: A Mechanistic Account of Translation in Multilingual LLMs."** arXiv 2609.01356 (Sept 2026). [SEARCH]
  - Models build target-side word order before they produce the target-language surface form.
  - Content passes through a language-agnostic bottleneck.
- **Nie, Schmid, Schütze (2025). "Mechanistic Understanding and Mitigation of Language Confusion in English-Centric Large Language Models." Findings EMNLP 2025.** Repo: https://github.com/ercong21/lang_confusion [README OPENED; findings via SEARCH]
  - Language switching is driven by transition failures in the final layers.
  - Editing a small set of neurons reduces it without hurting fluency.
- **Anthropic (Mar 27, 2025). "Tracing the thoughts of a large language model."** https://www.anthropic.com/research/tracing-thoughts-language-model [OPENED; exact quotes checked against the page text]
  - "Claude sometimes thinks in a conceptual space that is shared between languages, suggesting it has a kind of universal 'language of thought.'"
  - "the same core features for the concepts of smallness and oppositeness activate, and trigger a concept of largeness, which gets translated out into the language of the question."
  - "We find that the shared circuitry increases with model scale, with an earlier Claude model sharing more than twice the proportion of its features between languages as compared to a smaller model."
  - Caveat in the same post: "Even on short, simple prompts, our method only captures a fraction of the total computation performed by Claude, and the mechanisms we do see may have some artifacts based on our tools which don't reflect what is going on in the underlying model."
- **Anthropic (2025). "On the Biology of a Large Language Model."** https://transformer-circuits.pub/2025/attribution-graphs/biology.html [UNVERIFIED in detail]
  - Search summaries say the paper finds a mix of language-specific and language-independent circuits in an earlier Claude model. They also say English acts as a mechanistic "default" in some pathways, with abstract features connecting more directly to English outputs.
  - **I could not open the paper**, and an exact-phrase search for "English is mechanistically privileged" returned nothing. Treat that wording as unconfirmed.

**What these studies do not show**

- **No causal link to surface translationese.** None of them shows that an English-leaning concept space *causes* calques in fluent long-form output. That link is plausible, but it is still a hypothesis.
- **Narrow settings.** Most results come from open models of 70B parameters or fewer, single-token or short tasks, and coarse probes like the logit lens. The Claude-specific work is on an earlier Claude model with short prompts, and Anthropic says the method captures only a fraction of the computation.
- **"Thinks in English" is the wrong takeaway.** The better-supported picture is a shared, mostly language-agnostic middle stage that sits closer to the dominant training language, with the output language realized late. How English-leaning that stage is depends on training data (Zhong; Harrasse).
- **Nothing on pragmatics.** None of this research addresses choices like announcing one's own rules.

---

## 2. Translationese and reduced naturalness in LLM output

**General**

- **Guo et al. (2025). "Do Large Language Models Have an English Accent? Evaluating and Improving the Naturalness of Multilingual LLMs." ACL 2025.** Apple, Inria Paris, École Polytechnique, Sapienza; full author list not confirmed. https://aclanthology.org/2025.acl-long.193/ (arXiv 2410.15956). [SEARCH]
  - The paper adds corpus-level **lexical** and **syntactic** naturalness metrics.
  - On French and Chinese benchmarks, LLM output shows English-influenced patterns.
  - A search summary says the models were 7–12B open models (Qwen1.5/2-7B, Mistral-7B, Mistral-Nemo-12B, Llama-3/3.1-8B). All showed higher divergence in non-English languages. **(check)**
  - Their fix is DPO with human-written responses as "chosen" and responses back-translated through English as "rejected". It improved naturalness without hurting general benchmarks, so the problem can be addressed in training.
- **Valentini, Wright, Granados, Colunga, von der Wense (2026). "An Investigation of Translationese in the Generations of Multilingual Large Language Models."** arXiv 2608.17399, accepted to COLM 2026. [SEARCH]
  - Using established translationese indicators across five languages, LLM-generated text shows some translationese in every language, even English, and **more in non-English**.
  - One summary gives German outputs classified as translated at 60.2% (Gemini) and 37.6% (Llama), 18–26 points above English. **(check)**
  - The authors discuss the "thinking in English, then translating" hypothesis.
- **Li, Zhang, Wang, Zhang, Cui, Yin, Xiao, Zhang (2025). "Lost in Literalism: How Supervised Training Shapes Translationese in LLMs." ACL 2025.** https://aclanthology.org/2025.acl-long.630 (arXiv 2503.04369). Data repo: https://github.com/yafuly/LLM_Translationese [SEARCH; repo opened, but it holds only data notes]
  - More than 40% of GPT-4's En→Zh translations contain translationese.
  - **Prompts asking for naturalness did not consistently reduce it.** One summary says GPT-4 rose from 0.50 to 0.53 **(check)**.
  - **Self-polishing** cut it from about 43% to about 25% **(check)**.
  - They trace the cause to translationese in supervised fine-tuning data.
- **Chen, Yu, Guo, Haddow (2024). "Is It Good Data for Multilingual Instruction Tuning or Just Bad Multilingual Evaluation for Large Language Models?" EMNLP 2024.** arXiv 2406.12822. [SEARCH]
  - Native and translated instruction data produce noticeably different models, but only native or generation benchmarks reveal the difference.
  - Translated data cannot carry language-specific knowledge and adds translation defects.
- **Chen, Guo, Haddow, Heafield (2024). "Iterative Translation Refinement with Large Language Models." EAMT 2024.** https://aclanthology.org/2024.eamt-1.17/ [SEARCH]
  - Repeatedly prompting the model to refine its output improved human-judged fluency and naturalness and reduced translationese.
- **Mora, Aryabumi, Ko, Hooker, Kreutzer, Fadaee (2025). "The Art of Asking: Multilingual Prompt Optimization for Synthetic Data."** Cohere, arXiv 2510.19806. [SEARCH]
  - Multilingual synthetic data is bottlenecked by prompts translated from English.
  - Optimizing prompts in the target language for naturalness and cultural grounding helps.

**Factors behind it**

- **English-dominant pretraining**: Llama-2 at about 90% English, above.
- **English-dominant preference and reward modeling:**
  - **Dang, Ahmadian, Marchisio, Kreutzer, Üstün, Hooker (2024). "RLHF Can Speak Many Languages." EMNLP 2024.** https://aclanthology.org/2024.emnlp-main.729 [SEARCH]. Preference-optimization work has concentrated on a few high-resource languages. Directly generated multilingual data worked better than translated data.
  - **Gureja et al. (2025). "M-RewardBench: Evaluating Reward Models in Multilingual Settings." ACL 2025.** arXiv 2410.15522 [SEARCH]. Reward models perform significantly worse outside English, and their preferences shift across languages. So in non-English text, a reward model's signal about naturalness is plausibly weaker (my inference).
- **Takase & Honda (2026). "Toward LLMs Beyond English-Centric Development."** CyberAgent, arXiv 2605.15613. [SEARCH] Open-weight LLMs' generations are heavily biased toward English.

**Korean-specific** (sparse; I found **no study measuring translationese in Claude's Korean**)

- **Park, Kim, Kim, Han (2025). "KatFishNet: Detecting LLM-Generated Korean Text through Linguistic Feature Analysis." ACL 2025.** https://aclanthology.org/2025.acl-long.1030/ ; README https://github.com/Shinwoo-Park/katfishnet [OPENED README; the abstract is quoted there in full]
  - Human and LLM-generated Korean (GPT-4o, Solar, Qwen2, Llama3.1) differ in spacing, part-of-speech n-gram diversity and comma usage. Korean has "less frequent comma usage compared to English."
  - README: "Human text typically exhibits a richer variety of syntactic patterns compared to LLM-generated text, which tends to repeat common structures."
  - The README does not say whether LLM comma use leans English, so the paper does not establish English as the cause.
- **"Cross-lingual Collapse: How Language-Centric Foundation Models Shape Reasoning in Large Language Models"** (2025). arXiv 2506.05850; authors not confirmed. [SEARCH]
  - Under GRPO, chain-of-thought drifts toward the dominant pretraining language.
  - The drift is moderate for **Korean** (mid-resource) and largely irreversible.
- **Son et al. (2024). "KMMLU: Measuring Massive Multitask Language Understanding in Korean."** arXiv 2402.11548. [SEARCH] Machine-translated benchmarks contain unnatural language, so KMMLU uses native Korean exam questions.
- **Yu, Kim, Yun, Kim (2025). "Making Sense of Korean Sentences: A Comprehensive Evaluation of LLMs through KoSEnd Dataset." ACL SRW 2025.** https://aclanthology.org/2025.acl-srw.29 [SEARCH]
  - 11 LLMs were tested on how natural 15 Korean sentence-ending forms are.
  - Telling models explicitly about the relevant linguistic feature improved performance.
- **Lee (2026). "An LLM-Associated Register Shift in Korean Journal Abstracts …"** arXiv 2609.07447. Single-author, non-peer-reviewed preprint. [SEARCH] LLM-associated style verbs rose in Korean abstracts, e.g. 시사하다 in 21.4% of 2026 abstracts vs 5.3% expected **(check)**. This is evidence of LLM lexical fingerprints in Korean, not specifically of translationese.

---

## 3. Effect of instruction or system-prompt language

- **Marchisio, Ko, Bérard, Dehaze, Ruder (2024). "Understanding and Mitigating Language Confusion in LLMs." EMNLP 2024.** arXiv 2406.20052; benchmark README https://github.com/for-ai/language-confusion [README OPENED for setup; findings via SEARCH]
  - The README confirms the cross-lingual setting: "the model is instructed in English to generate in the target language", and Korean is included. It also has native Korean prompts.
  - Findings: English-centric instruct models are more prone to confusion, and complex prompts and high temperature make it worse. Few-shot prompting, multilingual SFT and preference tuning **partially** mitigate it.
  - Language confusion is a coarser failure than translationese.
- **Enomoto, Kim, Chen, Komachi (2025). "A Fair Comparison without Translationese: English vs. Target-language Instructions for Multilingual LLMs." NAACL 2025 (short).** https://aclanthology.org/2025.naacl-short.55/ [SEARCH]
  - Once translated instructions and data are removed, English instructions' advantage is "not overwhelming."
  - Models **follow English instructions more closely**, but effects depend on the task: target-language instructions did better on lexical simplification.
- **Etxaniz, Azkune, Soroa, Lopez de Lacalle, Artetxe (2024). "Do Multilingual Language Models Think Better in English?" NAACL 2024 (short).** README https://github.com/juletx/self-translate [OPENED README; the abstract is reproduced there]
  - Having the model translate its input into English first "consistently improves performance, and … the gap is bigger for models with higher capabilities."
  - "language processing and task solving are coupled to some extent."
  - This is about reasoning accuracy, not naturalness.
- **Zhang, Zhou, Ergen, Logeswaran, Lee, Jurgens (2025). "Cross-Lingual Prompt Steerability: Towards Accurate and Robust LLM Behavior across Languages."** arXiv 2512.02841. [SEARCH]
  - English system prompts did slightly worse than same-language prompts on accuracy and consistency, but only marginally.
  - Better system prompts reduced unnecessary language switching.
- **AlKhamissi, ElNokrashy, AlKhamissi, Diab (2024). "Investigating Cultural Alignment of Large Language Models." ACL 2024.** https://aclanthology.org/2024.acl-long.671 [SEARCH] Prompting in a culture's dominant language gives greater cultural alignment.
- **Mondshine, Paz-Argaman, Tsarfaty (2025). "Beyond English: The Impact of Prompt Translation Strategies across Languages and Tasks in Multilingual LLMs." LoResMT 2025.** https://aclanthology.org/2025.loresmt-1.9 [SEARCH] Which prompt components to pre-translate into English depends on similarity to English, translation quality and pretraining data size.
- **Qi, Chen, Xiong, Fernández, Bitterman, Bisazza (2025). "When Models Reason in Your Language: Controlling Thinking Language Comes at the Cost of Accuracy." Findings EMNLP 2025.** README https://github.com/Betswish/mCoT-XReasoning [OPENED README for citation; findings via SEARCH]
  - Reasoning models often fall back to English in their thinking.
  - Forcing user-language thinking makes the reasoning more readable but less accurate.

**Gap:** I found no study that directly measures the *naturalness* of non-English chat output as a function of system-prompt language. Existing work measures accuracy, instruction adherence or language confusion.

---

## 4. Anthropic's official prompting guidance (all [OPENED], accessed 2026-10-06)

**Prompting best practices**: https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices. The old URLs for be-clear-and-direct, multishot-prompting, system-prompts and extended-thinking-tips now redirect here.

- **Positive instructions:** "**Tell Claude what to do instead of what not to do** — Instead of: 'Do not use markdown in your response' Try: 'Your response should be composed of smoothly flowing prose paragraphs.'"
- **Reasons:** "Providing context or motivation behind your instructions, such as explaining to Claude why such behavior is important, can help Claude better understand your goals and deliver more targeted responses."
  - The page's example sets "NEVER use ellipses" (less effective) against "Your response will be read aloud by a text-to-speech engine, so never use ellipses since the text-to-speech engine will not know how to pronounce them" (more effective).
  - "Claude is smart enough to generalize from the explanation."
- **Prompt style:** "**Match your prompt style to the desired output** … The formatting style used in your prompt may influence Claude's response style." The page discusses formatting (markdown). Extending this to the *language* of the prompt is my inference, not Anthropic's claim.
- **Examples:** "Examples are one of the most reliable ways to steer Claude's output format, tone, and structure." Make them "**Diverse:** Cover edge cases and vary enough that Claude doesn't pick up unintended patterns." "Include 3–5 examples for best results."
- **Role:** "Setting a role in the system prompt focuses Claude's behavior and tone for your use case."
- **Strong wording:** "two recent Claude models are also more responsive to the system prompt than previous models … The fix is to dial back any aggressive language."
- **Context:** "Think of Claude as a brilliant but new employee who lacks context on your norms and workflows."

**Multilingual support**: https://platform.claude.com/docs/en/build-with-claude/multilingual-support

- "For enhanced fluency, you can prompt Claude to use 'idiomatic speech as if it were a native speaker.'"
- "Consider cultural context: Effective communication often requires cultural and regional awareness beyond pure translation."
- The language table gives Korean at 96.7% of English ([model]) and 93.3% ([model]), both with extended thinking. These figures are on MMLU "translated into 14 additional languages by professional human translators." They measure knowledge and reasoning, **not naturalness**.

**Increase output consistency**: https://platform.claude.com/docs/en/test-and-evaluate/strengthen-guardrails/increase-consistency (the old keep-claude-in-character URL redirects here)

- "Provide examples of your desired output. This is more effective than abstract instructions."
- "Prepare Claude for possible scenarios: Provide a list of common scenarios and expected responses in your prompts."

**Model-specific pages** (check the page for whichever model is deployed; the user's model is unknown)

- [model] (…/prompting-claude-[model]):
  - "Positive examples of the communication style you want tend to be more effective than instructions about what not to do."
  - "a Claude model narrates readily … it tends to announce what it is about to do."
  - "The model also narrates corrections to its earlier statements more than prior models do, which can be undesirable in user-facing products."
- [model] and [model] (…/prompting-claude-[model], …/prompting-claude-[model]): "interprets prompts literally and explicitly … it does not infer requests you didn't make."
- [model] (…/prompting-claude-[model]):
  - "Give the reason, not only the request … context lets it connect the task to relevant information rather than inferring intent on its own."
  - Its sample instruction reads: "Do not re-derive facts …, re-litigate a decision the user has already made, or narrate options you will not pursue in user-facing messages."
- [model] (…/prompting-claude-[model]), writing density: "Mannered prose substitutes metaphor and flourish for direct statement … Metaphors drag in connotations the writer did not choose and cannot control. The fix is to say what you mean. When a literal phrase is available, use it."

**Claude's constitution**: https://www.anthropic.com/constitution. Published Jan 21, 2026 per news coverage found in search.

- "relying on a mix of good judgment and a minimal set of well-understood rules tends to generalize better than rules or decision procedures imposed as unexplained constraints."

Note: I recalled an older Anthropic line saying extended thinking "performs best in English". It is **not on the current consolidated page**, so I do not cite it.

---

## 5. Models echoing or verbalizing system-prompt rules

**Documented by Anthropic** [OPENED]

- **claude.ai system prompts** (https://platform.claude.com/docs/en/release-notes/system-prompts/overview) repeatedly tell Claude not to surface prompt content unless it is relevant. Opening the per-model pages:
  - a Claude model, 2024-07-12: "It does not mention this information about itself unless the information is directly pertinent to the human's query."
  - [model], 2024-11-22: "Claude never mentions the information above unless it is pertinent to the human's query."
  - [model], 2025-02-24: "Claude never mentions this information unless it is pertinent to the person's query."
  - [model], 2026-01-18: "Claude does not mention this information unless it is relevant to the user's query."
  - [model], 2026-09-22, and [model] (child-safety context): Claude "states the principle rather than the detection mechanics … since narrating the boundary teaches how to reframe around it."
  - These lines show that Anthropic writes explicit no-narration instructions. They do not show how often Claude narrates without them.
- **Constitution:** "Claude can reveal the contents of its context window if relevant or asked to." Claude has no default of treating its instructions as secret, so stating a rule when it seems relevant is consistent with its defaults (my inference).
- **Model narration and literalism** (§4): [model] narrates readily; [model] and [model] follow instructions literally; [model]'s sample instruction suppresses re-litigating and narrating.
- **Reduce prompt leak** (https://platform.claude.com/docs/en/test-and-evaluate/strengthen-guardrails/reduce-prompt-leak):
  - "Attempts to leak-proof your prompt can add complexity that may degrade performance."
  - "Extra content distracts Claude from focusing on 'no leak' instructions."

**Research on prohibitions** (relevant to a banned-phrase list)

- **Castricato, Lile, Anand, Schoelkopf, Verma, Biderman (2024). "Suppressing Pink Elephants with Direct Principle Feedback."** arXiv 2402.07896. [SEARCH] Telling a model to avoid a named topic (the "Pink Elephant") is hard for prompted baselines. Their fix required fine-tuning.
- **Jang, Ye, Seo (2022/23). "Can Large Language Models Truly Understand Prompts? A Case Study with Negated Prompts." PMLR v203.** https://proceedings.mlr.press/v203/jang23a.html [SEARCH] 2022-era models performed worse on negated prompts as they scaled (inverse scaling). This is dated and not evidence about current frontier models.
- **Zheng, Pei, Logeswaran, Lee, Jurgens (2024). "When 'A Helpful Assistant' Is Not Really Helpful: Personas in System Prompts Do Not Improve Performances of Large Language Models." Findings EMNLP 2024.** arXiv 2311.10054. [SEARCH] Personas did not improve factual accuracy. That supports persona prompting for tone, as Anthropic frames it, rather than for capability.

**Gap:** I found no peer-reviewed study that measures spontaneous verbalization of system-prompt rules in persona chat. The evidence here is vendor documentation plus inference.

---

## 6. Assessment (inference; based on the evidence above)

### 6.1 Two different problems in the quoted sentences

1. **Pragmatic: reciting the rule.** The sentence restates the persona's CANDOR procedure (once, at full strength, then drop it) almost clause by clause.
   - This is **prompt-induced**, with high confidence:
     - the textual match is near-verbatim;
     - newer Claude models follow instructions literally and readily announce what they are about to do;
     - Anthropic itself has to write "never mentions this information" lines;
     - the persona's anti-mechanics lines don't cover CANDOR.
   - Perfect Korean wording would still sound like a policy being read out.
2. **Lexical: calques.** 세게 밀다 for "push back", and 세게 for "at full strength".
   - **Mixed cause.** "Push back" is not in the persona, so it plausibly comes from the model's English-lexicalized concept. Anthropic's training texts use the idiom, and research finds an English-leaning concept space rendered late (Wendler; Schut; Bafna) and measurable English-influenced lexical choices (Guo; Valentini).
   - The prompt amplifies it in two ways. First, its English intensity phrasing invites a literal rendering. Second, it gives one generic line ("Write natural, idiomatic Korean, not translationese") with no reason and no examples.

### 6.2 How much is prompt-induced vs. capability-limited

This is my judgment, not a measurement. **Most of what makes these two sentences machine-like is fixable by prompting:**
- the rule recital entirely, or nearly;
- the calques partly, via examples, literal rather than metaphorical persona wording, and the native-speaker instruction with a reason.

**A residual rate of English-shaped word choice is a training property of current models.** Two findings support this:
- Simple "be natural" instructions did not reliably reduce translationese, while revision passes did (Li et al. 2025, [SEARCH]).
- Naturalness improved through training interventions: DPO on naturalness, polished SFT data, native preference data (Guo et al.; Li et al.; Dang et al.).

### 6.3 Would waiting for a newer model fix it?

- **Rule recital: probably not.** Newer Claude models are documented as more literal and more responsive to the system prompt. A protocol written as a procedure may be recited *more*, not less, until the prompt changes.
- **Calques: maybe somewhat.** Research shows naturalness can be trained, and Anthropic notes newer models are "less machine-like" in English communication style. But Anthropic publishes **no Korean naturalness trend data**: its multilingual table measures MMLU accuracy only. So a future reduction is plausible but unverified, and it won't help with the prompt-induced part.

### 6.4 What a fix looks like, derived from the guidance (a list of things to test, not proven results)

1. **Rewrite CANDOR as intent plus reason** instead of a procedure. For example:
   > "When you disagree, say so plainly with your reasons, as a candid friend would, and once the user decides, let it go. The user should experience this simply as you disagreeing, so speak the disagreement itself rather than describing how often or how strongly you will raise it."
2. **Add 3–5 varied Korean examples** of natural 해요체 disagreement and of accepting a decision. Wrap them in `<example>` tags and label them as tone illustrations, not wording to copy.
3. **Replace English idioms and metaphors in the persona** ("at full strength", "re-litigate") with literal descriptions, following the [model] guidance to use a literal phrase when one exists.
4. **Use the multilingual doc's wording with a reason.** For example: "the user is a native Korean speaker who notices English-shaped phrasing; use idiomatic speech as if you were a native speaker."
5. **A/B-test a Korean-language KOREAN section and Korean examples** against the English versions. Target-language instructions help some tasks, while English instructions are followed more closely (Enomoto et al.), so test rather than assume.
6. **Avoid a banned-phrase list.** Anthropic's guidance favors positive instructions, and prohibitions are weak levers.
7. **For important long-form Korean, add a second "native editor" pass** (Li et al.; Chen et al. 2024). This is practical through the API, less so inside chat.

---

## 7. What would change this conclusion

Run a small controlled test: about 20 Korean disagreement scenarios under three conditions:
- (a) the current persona;
- (b) CANDOR rewritten, plus Korean examples;
- (c) (b) plus Korean-language persona sections.

Score each with blind native-speaker naturalness ratings, a count of rule recitals and a count of calques.

- If (b) or (c) removes the rule recitals but calques remain at a similar rate, the remainder is the model's capability.
- If calques also drop sharply, the problem was mostly prompt-driven.

Also worth checking: whether the chat product's own (English) system prompt adds to the effect, and which Claude model is deployed, since narration and literalism differ by model.
