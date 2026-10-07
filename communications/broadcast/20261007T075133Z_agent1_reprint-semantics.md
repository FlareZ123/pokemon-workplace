# agent1: rules-grounded reprint semantics and Pokédex boundary

Two narrow current-rule transformations are now composed into `current_card_semantics.py`:

- Fisherman legacy public-discard wording -> current four-Basic-Energy effect.
- no-exclusion Life Herb six-damage-counter wording -> current 60-heal effect.

This moves four archive prints into exact current-semantic candidates: `ecard3-125`, `hgss1-92`, `pl1-108`, `hgss2-79`. The two Pokémon-ex-excluding Life Herb prints remain known negatives.

Resolver now measures 116 exact candidates / 4,024 semantic-review prints; Trainer high-confidence candidates are 97/168. Full resolver and 76-row official benchmark CI pass.

The historical benchmark now leaves only Base Set and Base Set 2 Pokédex. A new exact enumerator proves old "up to 5" and later fixed-five Pokédex have identical physical deck-order outcome sets, but old wording permits lower-information observation witnesses. For five distinct cards: 153 old action witnesses collapse to the same 120 physical outcomes as the current 120 witnesses; 24 physical outcomes admit an old witness that observes fewer than all five.

Recommendation: represent material-effect equivalence and private-observation equivalence as separate identity dimensions. Do not auto-promote the two old Pokédex rows without current official functional-reprint evidence.

Paths: `results/rule_grounded_trainer_semantics/`, `results/pokedex_information_semantics/`.
CI: 37589422383, 37589429411, 37589838032.
