# Exact finite-draw access changes Serena versus Counter Catcher values

## Question

The [deterministic comparison](../gust_source_incomparability/) assumes
Boss's Orders and its alternative are already available. What changes when
both cards must be drawn from a finite shuffled deck?

## Conditional game

A player has six Prize cards remaining, with one Boss and one restricted
gust (Serena or Counter Catcher) hidden among `N-2` ordinary filler cards.
One normal card is drawn before each attacking turn. The player can preserve
drawn cards, and chooses whether to gust after seeing that turn's draw.
After every KO, the opponent adversarially selects the next Active Pokemon
*before* the next card is drawn.

As in `tools/stochastic_gust_draw.py`, the defender's maximization has
privileged symbolic hand knowledge, so this is a conservative conditional
game-tree benchmark. The opponent Prize count is fixed at four. Opposing
Pokemon are one-hit KOs in the N1/N2/N3/V2/V3 categories of the prior typed
minimax. No additional Pokemon, setup, draw engine, opponent attacks,
Supporter collision, Prize cards or Item lock are represented. The draw pile
is always long enough to avoid a deck-out turn.

The implementation uses exact rational arithmetic and interleaves draws,
attacker decisions, and worst-case defender promotions.

## Witness A: Counter's one usable draw order

Opposing Active N1, Bench N3/N3, opponent four remaining Prizes.

Serena cannot gust either three-Prize non-V target, so Boss + Serena takes
three attacks. Boss + Counter wins in two only if **Counter is drawn first
and Boss second**. Counter gusts the first N3 while legal, then the opponent's
next Active is replaced by Boss gusting the second N3. Boss first then
Counter is insufficient: after the three-Prize KO, Counter's Prize threshold
has expired.

There is one favorable ordered pair among `N(N-1)` possibilities:

\[
E_A(\mathrm{Boss+Counter})=3-\frac{1}{N(N-1)},\qquad
E_A(\mathrm{Boss+Serena})=3.
\]

Two unrestricted Boss gusts permit both special-card draw orders, giving
`3 - 2/[N(N-1)]`.

## Witness B: Serena's two cards in the first three draws

Opposing Active N2, Bench N1/N2/V2, opponent four remaining Prizes.

Taking the natural N2 KO first ties the Prize counts and closes Counter's
window. Boss + Counter requires four attacks.

Boss + Serena wins in three attacks if both gust cards are drawn within
the first three normal draws. The attacker can then naturally KO the
starting N2 and gust the two remaining two-Prize targets on later attacks.
Six ordered pairs of draw positions qualify, giving:

\[
E_B(\mathrm{Boss+Serena})=4-\frac{6}{N(N-1)},\qquad
E_B(\mathrm{Boss+Counter})=4.
\]

These probabilities follow from exact without-replacement drawing. The
chance game verifies that optimal action timing realizes both formulas.

## Exact expected attacker turns

| Deck size N | A: Boss + Counter | A: Boss + Serena | B: Boss + Counter | B: Boss + Serena |
| ---: | ---: | ---: | ---: | ---: |
| 6 | 2.966667 | 3.000000 | 4.000000 | 3.800000 |
| 8 | 2.982143 | 3.000000 | 4.000000 | 3.892857 |
| 10 | 2.988889 | 3.000000 | 4.000000 | 3.933333 |
| 12 | 2.992424 | 3.000000 | 4.000000 | 3.954545 |
| 20 | 2.997368 | 3.000000 | 4.000000 | 3.984211 |

The one-attack difference in the all-in-hand deterministic model becomes
a small expected attack-turn difference when both cards begin hidden.
The structural winner of each witness stays the same.

## Reproduction

- `tools/stochastic_typed_gust_draw.py`: exact Fraction-valued game tree
  with drawing, hand preservation, typed/gated targeted gust, and defender
  promotion after KO.
- `results/stochastic_typed_gust_draw/reproduce.py`: verifies both closed
  forms for five deck sizes, matching all-in-hand deterministic endpoints,
  and agreement with `tools/stochastic_gust_draw.py` when both sources
  are unrestricted Boss-type gusts.

All tested formulas are exact rational equalities, not simulations.

## Limits and further work

The size `N` is the current conditional remaining deck size; it is not a
complete 60-card starting-state model. Real Prize cards, opening hands,
search connectors, draws from abilities, Supporter competition, opponent
Prize progress, and lock interactions can change the access probability.
Full realistic valuation will need a belief-aware, physical hand/deck state
and card-level resource payments before applying this terminal utility.
