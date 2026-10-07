# Known negative reprint evidence

The reprint resolver preserves explicit negative evidence as well as positive candidates.

Thirty historical Darkness Energy prints and Metal Energy prints are Special Energy cards with additional effects, while every current legal Expanded card with those names is Basic Energy. They therefore fail the functional-identity requirement structurally.

The Tournament Handbook also gives Rainbow Energy from Team Rocket number 17 as an explicit non-equivalent example because doing 10 damage and placing 1 damage counter are different mechanics. The alternate Team Rocket Rainbow Energy number 80 has the same gameplay fingerprint as number 17, so the same negative evidence applies to both prints.

Two historical Life Herb printings now add a format-relative negative class. `ex5-90` and `ex6-93` explicitly exclude Pokémon-ex as targets, while current legal Life Herb does not. The current Expanded pool contains `me55c-108` Scizor ex, so that target-set difference is presently reachable. The structured derivation is preserved in [../reprint_divergence_predicates/](../reprint_divergence_predicates/).

The resulting known-negative set contains 34 prints:

- Darkness Energy: 15
- Life Herb: 2
- Metal Energy: 15
- Rainbow Energy: 2

This reduces the unresolved same-name semantic-review queue from 4,068 to 4,034 prints while leaving the 192 high-confidence positive candidates unchanged.

The evidence classes are intentionally narrow. Other Rainbow Energy, Warp Energy, Recycle Energy, Double Colorless Energy, and free-form Trainer wording variants stay unresolved unless separate evidence proves or disproves current functional identity.

Reproduce with:

`python results/reprint_negative_evidence/reproduce.py`

The Life Herb predicate derivation can be reproduced separately with:

`python results/reprint_divergence_predicates/reproduce.py`
