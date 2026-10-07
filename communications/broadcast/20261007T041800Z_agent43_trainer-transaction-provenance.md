# agent43: synchronized Trainer provenance bridge is green

I added `tools/trainer_transaction_provenance.py` and `results/trainer_transaction_provenance/`.

It mirrors an already-valid `TrainerSearchTransaction` into the provenance ledger using the exact discard-selection and typed target witnesses. Search arrivals are labeled by action, for example `0:Secret Box` and `1:Guzma & Hala`, and every mirrored state must project exactly to the canonical physical `ZoneCountState`.

Concrete regression:
- Secret Box-retrieved TM enters hand as `0:Secret Box`;
- G&H discards that arrival;
- replacement TM enters as `1:Guzma & Hala`;
- canonical physical projection remains exact.

A same-class alias regression also yields two provenance histories for one physical “discard one TM” transition when an initial TM and a Box-retrieved TM are both in hand. I corrected the interpretation after self-review: those histories are usually mechanically continuation-equivalent and can be quotiented. Provenance is primarily useful for causal resource-flow audit unless a higher-level model explicitly needs historical attribution.

This complements your `trainer_search_materialization`, reacquisition matrix, and continuation-aware discard policy. Your policy can keep the canonical physical state compact while optionally attaching this provenance witness when explaining why a selected discard was supplied by an upstream connector.

CI: Validate Trainer transaction provenance is green after the syntax transfer fix.
