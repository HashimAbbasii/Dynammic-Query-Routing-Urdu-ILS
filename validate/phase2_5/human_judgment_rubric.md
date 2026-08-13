\# Phase 2.5 Human Judgment Rubric



\## Purpose



This rubric is used to determine whether a retrieved news article satisfies a user query from the available evidence.



The purpose is to empirically investigate the unresolved §4 bare-event labeling issue in Phase 2.5.



This rubric does NOT assume that 5–9 word bare-event queries are SHORT or LONG.



The judgment must be based only on the information need expressed by the query and the evidence contained in the retrieved article.



\---



\## Allowed Judgment Labels



Each retrieved article must receive exactly ONE of these labels:



\### HEADLINE-SUFFICIENT



Use this label when the article headline alone provides enough information to satisfy the query's information need.



The headline must clearly establish the event or fact requested by the query.



The article body may contain additional details, but those additional details are not necessary to establish that the query has been satisfied.



\### CONTENT-REQUIRED



Use this label when the article is relevant to the query, but the headline alone is insufficient.



The article body contains information that is necessary to establish or satisfy the query.



Examples of necessary body information may include:



\- who performed the action

\- what specifically happened

\- why something happened

\- when something happened

\- where something happened

\- the result or outcome

\- numerical details

\- an important qualification or condition



Do NOT use CONTENT-REQUIRED merely because the article contains more details than the headline.



The body must contain information that is actually necessary for satisfying the query.



\### AMBIGUOUS



Use this label when the available evidence does not allow a confident distinction between HEADLINE-SUFFICIENT and CONTENT-REQUIRED.



Do NOT force an ambiguous case into either category.



\---



\## Primary Decision Question



For every query/article pair, ask:



> "If I only had the article headline, would I have enough information to satisfy what the user is asking?"



If YES:



HEADLINE-SUFFICIENT



If NO, but the article body provides the required information:



CONTENT-REQUIRED



If the distinction cannot be made confidently:



AMBIGUOUS



\---



\## Important Rules



\### Rule 1 — Judge the information need



Judge what the user is asking for, not simply whether words overlap.



Shared words between the query and headline are not sufficient evidence.



\### Rule 2 — Do not use retrieval score



Do not consider:



\- retrieval\_score

\- ranking score

\- similarity score

\- retrieval mode



These are retrieval-system information, not relevance evidence.



\### Rule 3 — Do not use word count



Do not use the query's word count to determine the judgment.



A 5-word query and a 9-word query must be judged using exactly the same information-need principle.



\### Rule 4 — Do not use the pre-registered hypothesis



Do not use the LONG/SHORT hypothesis when judging an article.



The hypothesis is intentionally hidden from the judgment decision.



\### Rule 5 — Do not infer missing information



Do not assume information that is not explicitly supported by the headline or article.



\### Rule 6 — Bare-event queries



For a bare-event query, determine whether the headline itself establishes the requested event.



If the headline establishes the event but the article body only adds details:



HEADLINE-SUFFICIENT



If the headline only indicates a related topic and the body is required to establish the requested event:



CONTENT-REQUIRED



If the evidence is unclear:



AMBIGUOUS



\---



\## Examples



\### Example A — HEADLINE-SUFFICIENT



Query:



"اسٹاک مارکیٹ میں تیزی آئی"



Headline:



"اسٹاک مارکیٹ میں زبردست تیزی"



The headline directly establishes that the stock market experienced an increase.



Judgment:



HEADLINE-SUFFICIENT



\---



\### Example B — HEADLINE-SUFFICIENT



Query:



"اسٹاک مارکیٹ میں تیزی آئی"



Headline:



"اسٹاک مارکیٹ میں مسلسل دوسرے روز بھی تیزی کا رجحان"



The headline directly states that the stock market continued its positive trend.



Judgment:



HEADLINE-SUFFICIENT



\---



\### Example C — CONTENT-REQUIRED



Query:



"پاکستان کرکٹ ٹیم فائنل میں کیوں ہاری"



Headline:



"پاکستان کرکٹ ٹیم فائنل میں ہار گئی"



The headline establishes the event, but it does not explain WHY the team lost.



If the article body explains the reason, the body is necessary.



Judgment:



CONTENT-REQUIRED



\---



\### Example D — CONTENT-REQUIRED



Query:



"میچ کب شروع ہوگا"



Headline:



"پاکستان اور بھارت کے درمیان بڑا مقابلہ"



The headline identifies the match but does not provide the requested start time.



If the article body contains the start time, the body is required.



Judgment:



CONTENT-REQUIRED



\---



\### Example E — AMBIGUOUS



Query:



"اسٹاک مارکیٹ میں تیزی آئی"



Headline:



"مارکیٹ میں مثبت رجحان"



The headline suggests a positive market condition, but it may not clearly establish the exact event expressed by the query.



If the available evidence does not make the distinction clear:



AMBIGUOUS



\---



\## What the Human Judge Must NOT Do



The judge must NOT:



\- decide SHORT vs LONG directly

\- use the existing SVM prediction

\- use the baseline prediction

\- use retrieval score

\- use query word count

\- use the pre-registered LONG/SHORT hypothesis

\- use the LLM judgment as authority

\- change the query

\- rewrite the headline

\- assume information that is not present

\- force an ambiguous case into another label



\---



\## Judgment Procedure



For every selected row:



1\. Read the USER QUERY.

2\. Read the ARTICLE HEADLINE.

3\. Decide whether the headline alone satisfies the query.

4\. If yes, record HEADLINE-SUFFICIENT.

5\. If no, read the ARTICLE BODY.

6\. If the body supplies information necessary to satisfy the query, record CONTENT-REQUIRED.

7\. If the distinction remains unclear, record AMBIGUOUS.

8\. Record a short justification based on the evidence.



\---



\## Required Judgment Record



Each human judgment should contain:



\- query\_id

\- query

\- retrieval\_mode

\- rank

\- doc\_id

\- doc\_headline

\- human\_judgment

\- human\_confidence

\- human\_reason



Allowed human\_judgment values:



\- HEADLINE-SUFFICIENT

\- CONTENT-REQUIRED

\- AMBIGUOUS



Allowed human\_confidence values:



\- high

\- medium

\- low



The justification should be concise and evidence-based.



\---



\## Research Integrity



Human judgments are treated as the primary evidence for this phase.



LLM judgments are preliminary secondary evidence only.



No LLM output should be silently converted into a human judgment.



No ambiguous judgment should be silently converted into SHORT or LONG.



The Phase 2.5 evidence must remain traceable to the original retrieval output.



The original judgment\_template.csv must not be modified during human judging unless a separate, explicitly documented human-judgment copy is created.



\---



\## Relationship to §4



The purpose of this judgment process is NOT to prove the pre-registered LONG hypothesis.



The purpose is to determine empirically whether bare-event queries require article-body information or can be satisfied from headlines.



The eventual §4 policy must be derived from the observed evidence rather than imposed before judgment.



If the evidence does not support a single deterministic rule, the final thesis should report that limitation rather than forcing a rule.

