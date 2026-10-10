# Energy Recycle System: public-discard action-frontier equivalence

## Question

Do historical EX-era `Energy Recycle System` Item printings
(`ex3-84`, `ex10-81`, `ex16-73`) provide the same reachable
card-material actions as the Expanded-legal `sm7-128` printing?

## Result (bounded, rules-grounded)

**Yes, for the modeled material and information transition.** Each card
offers two alternatives: move one basic Energy from the discard pile
to hand, or shuffle three basic Energy from the discard pile into the
deck. The original prints preface these with "Search your discard
pile" and explicitly "show" the cards. The current print frames them
as "Choose 1."

Under the Advanced Player's Rulebook, numbered choices use the
available count when fewer cards exist, and an Item cannot be played
with no state change. Therefore the 3-Energy branch can shuffle all
one or two available basic Energy, while an empty eligible discard pile
offers no effective action. In both wordings, the selected Energy
identities are public: Pokémon's official glossary says all discard
cards remain face up and visible to either player.

The stored exhaustive harness compares both textual implementations
across **108 distinct-card source states** covering 0–5 discarded
basic Energy, 0–2 unrelated discarded cards, 0–2 initially ordered
deck cards, and 0–1 hand cards. It enumerates every legal eligible
subset, every possible post-shuffle deck order, and the conditional
uniform permutation probability. The two modeled action-frontier sets
are identical in every case.

## Evidence

The dataset records all four printed card texts and their Item
subtype. The official glossary establishes that cards in the
discard pile are already public information:

https://www.pokemon.com/us/play-pokemon/about/pokemon-tcg-glossary

The bundled Advanced Player's Rulebook provides the Item and
numbered-effect interpretation: I-B-01, II-A, II-D-04, and II-D-05.

The historical printed card also appears in the official database:

https://www.pokemon.com/us/pokemon-tcg/pokemon-cards/ex-series/ex3/84/

## Reproduction

`python -m results.energy_recycle_equivalence.reproduce`

The model is in `tools/energy_recycle_equivalence.py`. Its output
records a deterministic count of independently distinguishable
conditional continuations, rather than an estimated gameplay rate.

## Limits and integration status

These three historical cards **remain `semantic_review`** in the
current central reprint resolver. This experiment is positive
state-model evidence, pending a separate policy-aware integration
decision. It does not assert that a present-day tournament handbook
explicitly certifies this reprint family.

The proof assumes normal shuffle randomization and the card-identity
model embodied by the bundled rules. It does not infer strategic
deckbuilding value or usage frequency. Trigger effects associated
solely with the act of revealing already-public discard-pile cards
would require an explicit rules counterexample before a stronger
universality claim.
