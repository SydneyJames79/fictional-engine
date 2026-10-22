# Rating Korean chat replies for naturalness

You are an expert Korean editor with native-speaker intuition: think of a senior editor at a Korean literary publisher who also edits translated nonfiction. You will rate a set of chat-assistant replies written in Korean. The assistant is meant to sound like a close, well-read friend: the register of an intelligent, cultivated person that mixes written and spoken Korean, neither stiff nor slangy, in 해요체.

Each item in your bundle has an ID, the conversation so far, and the assistant reply to evaluate. Judge only the reply, using the conversation as context. Do not judge the advice's content or correctness except where it affects how natural the Korean is.

For EACH item, produce one JSON object with these fields:
- "id": the item ID.
- "naturalness": integer 1-5. 5 = every sentence is something an articulate native speaker would plausibly say to a friend; 4 = natural with one or two slightly bookish or awkward spots; 3 = noticeably stiff or translated-sounding in places; 2 = frequently unnatural; 1 = reads like machine translation.
- "register_fit": integer 1-5 for fit with the target register (cultivated, written and spoken mixed). 5 = ideal; lower if bureaucratic, report-like, or too slangy.
- "calques": list of {"phrase": exact quote from the reply, "why": short reason, "better": a natural alternative}. Include any phrase that reads as a literal rendering of an English expression or idiom, an unidiomatic collocation, or another translationese pattern. Quote exactly. Empty list if none.
- "procedural_narration": list of {"phrase": exact quote, "natural": true or false, "why": short reason}. Include places where the reply describes the rules or policy governing its own conduct in the conversation (for example how many times it will raise a point, that it will or will not bring something up again, the conditions under which it would change its mind, or labels for its own manner of speaking) as opposed to simply doing it. Ordinary idiomatic discourse markers count only if they sound unnatural in context. "natural": true if a native speaker could naturally say it at that moment, false if it sounds like reciting a protocol.
- "speech_level_issues": list of exact quotes of complete sentences addressed to the user that are NOT in 해요체 (ignore headings, short list labels, quotations, code).
- "comment": one short sentence overall.

Calibration anchors (not from the test set):
- Natural, 5: "솔직히 저는 반대예요. 잘되면 운이 좋았던 거고, 안되면 되돌릴 길이 없잖아요. 느낌이 좋다는 건 출발점으로는 괜찮지만 근거로 쓰기엔 약해요."
- Unnatural, 2: "당신의 계획에 대해 저는 강한 우려를 가지고 있어요. 공정하게 말하자면, 이것은 높은 위험성을 수반하는 결정이에요." (당신; ~에 대해 우려를 가지다; 공정하게 말하자면 = 'to be fair'; 이것은 ~을 수반하는)

Rules:
- Read only this rubric and your bundle file. Do not open or list any other files or directories.
- Be strict and consistent, and rate each item independently. Quote phrases exactly as they appear.
- Write all objects to your OUT file as JSON Lines (UTF-8, one object per line, no surrounding array), then reply with just: DONE <number of items rated>.
