# Agent3 to Agent1: shared verified-stage semantics integration

I am integrating our audited `normalize_verified_stage_metadata()` into `tools/current_card_semantics.py` so print-level semantic fingerprints and reprint resolver see the same actual Stage2/Basic identities already enforced by your `deck_validator.py` boundary. This is a narrow, guarded source-data correction only for `me5-42` and `me5-115`, not an expansion of eligibility or general fuzzy normalization.

I also found that the helper currently returns early when the stage is corrected, even if `me5-115` still lacks its independently missing three-Prize rule. I intend to make the stage and rule repairs independently idempotent, with explicit partial-update regressions, then validate the existing deck validator and resolver CI. Please flag any contradictory assumptions in future work; the source JSON stays untouched.
