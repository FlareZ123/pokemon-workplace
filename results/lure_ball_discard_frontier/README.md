# Lure Ball: coin-conditioned public discard recovery

## Question

When Lure Ball is played with a known set of Stage 1/Stage 2 cards in
the discard pile, does the older Skyridge `ecard3-128` "choose and
show" effect have a different action frontier from the legal Expanded
Celestial Storm `sm7-138` "put an Evolution Pokémon" wording?

## Bounded result

For the modeled Stage 1/Stage 2 domain, the alternatives are the same.
Both cards flip three coins. Each heads allows an eligible discarded
Evolution card to move to hand. The choice of source card is implicit
under the numbered-choice rule. The older "show" clause reveals the
identity of a card that both players can already inspect in the face-up
discard pile.

The test explicitly models every ordered 3-coin outcome, every
possible ordered target-selection history, and shortage resolution
when the discard pile contains fewer Evolutions than heads. Coin
histories have rational probabilities of 1/8 each; target choices are
player actions and **are not assigned random probabilities**.

Results across 28 source configurations (0–6 eligible and 0–3
unrelated discarded cards) were identical for the two wordings,
covering **2,012** distinguishable conditional continuations.

| Eligible discarded Evolutions | Conditional coin/selection histories |
|---:|---:|
| 0 | 8 |
| 1 | 8 |
| 2 | 15 |
| 3 | 34 |
| 4 | 73 |
| 5 | 136 |
| 6 | 229 |

For n eligible cards and h heads, the number of ordered selection
histories is P(n,min(h,n)). Weighted by C(3,h) coin outcomes, the
sum across h=0..3 is the count shown above.

## Evidence

- Card text comes from `resources/cards/en/ecard3.json` and
  `resources/cards/en/sm7.json`.
- Rulebook I-B-01 and II-D-04 define Item use and mandatory choices.
- Rulebook II-A and II-D-04 require closest-possible counts when
  requested cards are unavailable.
- The Pokémon TCG glossary states discarded cards are face-up
  and available for inspection by either player:
  https://www.pokemon.com/us/play-pokemon/about/pokemon-tcg-glossary
- The modern card is in the paper Expanded set pool.

## Reproduce

`python -m results.lure_ball_discard_frontier.reproduce`

Code: `tools/lure_ball_discard_frontier.py`.

## Boundaries

The test assumes both historical "Evolution card" and modern
"Evolution Pokémon" refer to the same Stage 1 and Stage 2
target classes in its fixture. It does not establish equivalence
for special evolution classes (Pokémon BREAK, VMAX, VSTAR, LV.X,
or newer evolution mechanics) without independently checking
their category semantics under both wordings.

Coin-flip replacement effects, Item-lock constraints, and special
card-playability rulings are outside this isolated continuation.
The result is evidence of bounded operational equivalence; the
historical source deliberately remains `semantic_review`
in the central policy-aware reprint resolver.

Future work should explicitly check the broader target-domain
boundary before promoting the historical printing.
