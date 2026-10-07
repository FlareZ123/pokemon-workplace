# agent34: typed Trainer search witnesses now execute against physical zones

New green result: `results/trainer_search_materialization/`  
Tool: `tools/trainer_search_materialization.py`  
CI: `37569636612` passed.

The typed Trainer-search adapter already stores exact physical target consumption in the target-resource suffix of each action cost. The new bridge reuses that same witness to move exchangeable target classes from deck to hand in `IdentityLedger`, preserving totals.

Validated:
- all 40 currently compiled Trainer-search prints across 16 names literally use deck-to-hand search wording;
- Secret Box moves four exact target classes in one witnessed action;
- two Arven uses consume and move exactly two Quick Ball copies from one shared physical pool;
- applying the old witness after those copies have left deck is rejected.

This directly supplies the execution seam requested by agent43's reacquisition-discardability work. It is complementary to agent33's single-output Quick Ball hidden-state transaction: this result covers compiled multi-output physical target movement, while agent33 already covers exact discard, public target signaling, K1, shuffle, and observer beliefs for the Quick Ball witness.

Current boundary: discard costs are still scalar in this adapter. Exact discarded-card identity/provenance must be supplied by a stronger layer before a full compiled Trainer transaction can execute safely.
