# Defense demo script (5-7 minutes)

Run this live (does not retrain):

```
python validate/dual_index_routing/demo_confidence_tiers.py
```

Do not open old notebooks that still search one combined Chroma index.

---

## Slide 0 - one sentence (10 seconds)

ULTRA flips rooms with 150 letters. That tape almost never fires. This system replaces the decision and the search: SHORT means a headline is enough; LONG means need the article. The SVM opens one of two rooms. Lights mix them when the model is unsure.

Point at `validate/dual_index_routing/figures/fig_two_rooms_lights.png`.

---

## Slide 1 - three tables, not one (45 seconds)

Show `validate/dual_index_routing/figures/fig_three_evaluation_layers.png`.

1. Development 100% vs theta=150 50% only proves the task is learnable. Do not claim 100%.
2. Frozen Phase 3B, V2 eight features, 50 primary queries: 86% vs 84% word count. McNemar p = 1. Almost a tie.
3. Frozen 40 traps, never trained: 60% vs 20% vs 50%. Classification win on need labels.

If interrupted on 100%: that split is in-distribution. Headline generalization is 86/84, then 60/20.

---

## Slide 2 - the honest limit (45 seconds)

Show `validate/dual_index_routing/figures/fig_cue_split.png`.

- 18 queries with why/how/fact words: SVM 18/18, word count 2/18.
- 22 queries without those words: both 27.27%.
- Beats length when the query wears cue words. Otherwise it still behaves like the six-word tape.

Do not say the model understands information need.

---

## Slide 3 - retrieval did not follow (45 seconds)

Show `validate/dual_index_routing/figures/fig_heldout_p5.png`.

- Same 40 queries, 400 graded headline judgments.
- Graded P@5: word count 36.50%, always headline 35.00%, always full 34.25%, SVM 33.00%.
- nDCG@5 is best for always headline (0.6868).
- Typical miss: a LONG why-query still retrieves "petrol became expensive," not causes.

This is the remaining ULTRA problem (corpus/answers), not a fake P@5 win.

---

## Live demo (2-3 minutes)

For each query, point at the light, then the room, then one headline.

### Demo A - GREEN (one room)

Query: cricket match in Urdu (کرکٹ میچ)

- Label SHORT, about 100% -> headline is enough.
- Action HEADLINE -> only the headline room.
- Top-1 is a cricket headline. theta=150 would also call this short. The difference is you search headlines, not mixed body text.

### Demo B - YELLOW (mix both rooms)

Query: how much did the dollar rise (ڈالر کی قیمت کتنی بڑھی)

- Confidence about 82% -> not sure enough for one room.
- Action HYBRID -> mix headline room and full-article room.
- This is the light ULTRA does not have.

### Demo C - near the RED band (honest live pickle)

Query: `آج سٹاک ایکسچینج کتنے پوائنٹ پر`

- Live 12-feature pickle: LONG, YELLOW, about 66% (probed 23 Aug 2026).
- Action: mix both rooms.
- Do **not** claim RED on `آج پاکستان کا اسکور کیا ہے`. That query is GREEN ~97% on this pickle (old JSON was stale).
- RED (<60% → expand, then mix) is implemented in `retrieve.py`. A probe of defense + trap queries found **no LOW**. Say that if asked.

Optional fourth: `cricket match ka nateeja` to show Roman Urdu dictionary to Urdu headlines.

---

## If they ask

| Question | Answer |
| --- | --- |
| Did you replace ULTRA? | The switch and the indexes. Not a new encoder. |
| Why not 96%? | Leaks traps into Phase 3B. Refused. |
| Two human annotators? | No. Written protocol, first pass assisted, sheet saved. 40/40 with the rule. |
| Why still lose P@5? | Right room, weak articles. Archive answers price-rose, not why. |
| Word count almost as good? | On Phase 3B, yes. On traps, only when there are no cue words. |

---

## What not to click

- Old retrieve functions that always query combined_text.
- Any slide that puts 100%, 86%, and 60% in one unlabeled bar chart.
- LLM 100% routing as the main result (development only; 0.45 ms vs 600-900 ms is supporting).

---

## Timing

| Block | Time |
| --- | --- |
| One sentence + architecture figure | 0:30 |
| Three tables | 0:45 |
| Cue split | 0:45 |
| P@5 honesty | 0:45 |
| Three live queries | 2:30 |
| Buffer | 1:00 |
