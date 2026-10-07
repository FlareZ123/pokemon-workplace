# Pokédex: physical equivalence with epistemic refinement

## Question

The official historical reprint benchmark has two remaining `semantic_review` rows: Base Set Pokédex `base1-87` and Base Set 2 Pokédex `base4-115`.

The old text says:

`Look at up to 5 cards from the top of your deck and rearrange them as you like.`

The later Expanded print `bw1-98` says:

`Look at the top 5 cards of your deck and put them back on top of your deck in any order.`

Are these mechanically and strategically the same operation under current rules?

## Result

They have the **same reachable physical deck-order outcomes**, but they do not induce the same private-information observation in every action witness.

This is a useful reason to keep the two old prints in `semantic_review` instead of forcing them into either exact equivalence or known non-equivalence.

## Physical outcome proof

Let `m = min(5, cards remaining in deck)`, with `m >= 1`.

Current Pokédex observes all `m` available cards and may put those `m` cards back in any order. Its physical outcome set is therefore every permutation of the top `m` cards.

Old Pokédex uses "up to 5". Under current D-05 semantics for a Trainer, the player chooses a positive number up to the available bound. Choosing `m` is always among the old card's legal witnesses. With that choice, old Pokédex can produce every permutation current Pokédex can produce.

Every old witness that chooses fewer than `m` only permutes a shorter prefix and leaves the rest of the top `m` cards in place. That resulting order is also one of the full-`m` permutations available to current Pokédex.

Therefore the physical outcome sets are equal.

For five distinct top cards:

- current Pokédex has 120 ordering witnesses and 120 physical outcomes;
- old Pokédex has 153 action witnesses across choices 1 through 5;
- those 153 witnesses collapse to the same 120 physical outcomes;
- 24 of those physical outcomes have at least one old witness that observes fewer than all five cards.

The same set equality holds for 1 through 5 available cards.

## Epistemic difference

The old card can intentionally choose a smaller inspected prefix.

For an exact top sequence `A, B, C, D, E`, old Pokédex can choose one card, leave the deck physically unchanged, and learn only `A`. Current Pokédex can also leave the deck physically unchanged, but it necessarily observes `A, B, C, D, E`.

The final material deck can therefore be identical while the acting player's information state differs.

This repository already treats observer-relative knowledge as part of strategic state for Prize cards, shuffled tops, and private search. Collapsing these Pokédex texts solely because their material transitions coincide would erase an epistemic distinction that the simulator is otherwise designed to preserve.

## Interpretation for reprint resolution

This result does **not** conclude that the old Pokédex is currently tournament-illegal as a functional reprint.

The official 2012 Modified-Legal Reprint List marked both historical Pokédex printings as usable without a reference card under that historical policy. That is real positive evidence.

The current card texts still differ under present "up to" semantics, and the difference changes private observation. No current official source located in this investigation explicitly certifies the old and new Pokédex wording as functionally identical.

The strongest current repository state is therefore:

- physical-transition equivalence: **proven**;
- observation equivalence: **false** as a literal state transition;
- present-day tournament functional equivalence: **unresolved**.

That three-way distinction is stronger than forcing one boolean equivalence label.

## Tooling

`tools/pokedex_information_semantics.py` enumerates action witnesses separately from unique physical outcomes.

For each available-prefix size from 1 to 5, the regression checks:

1. old and current physical outcome sets are identical;
2. both produce `m!` unique physical orders;
3. old Pokédex has lower-information witnesses when `m > 1`;
4. current Pokédex always records observation of the full available prefix.

The model uses distinct labels to make witness multiplicity visible. Equality of physical outcome sets does not depend on labels being distinct because the old action includes the full-prefix choice.

## Evidence classes

**Current rule fact.** D-05 defines "up to" as a player choice among positive counts for Trainers when the effect can change state.

**Card-text fact.** The bundled database preserves the old "up to 5" wording and the later fixed-five wording.

**Historical official evidence.** The 2012 Modified-Legal Reprint List marks Base Set and Base Set 2 Pokédex as "Reference Required: No".

**Mathematical result.** The two wordings induce identical physical ordering outcome sets.

**State-model result.** They differ in the actor's possible observation counts.

**Methodological judgment.** A semantic resolver used by an information-aware simulator should keep material-effect equivalence and epistemic-effect equivalence as separate axes.

## Sources

- Repository Advanced Player's Rulebook, D-05: `resources/advanced-players-rulebook.md`
- 2012 Modified-Legal Reprint List: https://assets.pokemon.com/assets/cms/pdf/op/tournaments/2012/2012_modified_legal_reprints.pdf

## Next work

A broader reprint representation should carry an effect-equivalence vector rather than only one fingerprint: material transitions, public observations, private observations, timing, target domain, and rule-category semantics can each agree or diverge independently.
