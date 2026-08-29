# Future work (not implemented)

Recorded during Phase 8. **None of this was built.** The frozen system stays as specified.

These are hypotheses, not commitments, and **not** authorization to use H001–H040 for design.

1. **Graded qrels** for a sample of queries (not the sealed test) if a later study needs topical usefulness separately from known-item identity.
2. **Date-aware news retrieval** if a future corpus and queries include timestamps; current QTRN wires often omit the date.
3. **Naturalistic Roman Urdu** (chat-style `kya`/`kia`) is a different distribution from Phase 2 `title_roman`. Method D is frozen for the `title_roman` romanizer, not proven for user Roman.
4. **Headline as a second room** recovered 3/78 known-items in an oracle. Phase 7 forbade fusion for that small set. Revisit only with a pre-registered protocol that does not peek at H001–H040.
5. **GPU long-context dense indexing** (e5-small, 512 tokens) failed the Phase 4B CPU 4-hour gate. A GPU run would still be a new experiment, not a patch to this freeze.
6. **Reranking among topical neighbours** (e.g. snooker final vs semi-final) remains untested; Phase 7 said it is not justified as the next step.

Do not implement these in order to chase 90% ExactSource Hit@5 on n=78.
