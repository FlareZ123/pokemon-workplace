# Shadow Rider champion: Forest Seal Stone complements the Quick Ball launch frontier

## Result

The [2026 Aichi winning 60-card Shadow Rider baseline](../competitive_deck_baselines/)
contains **one Forest Seal Stone** and **three Shadow Rider Calyrex V**.
The Pokémon Tool grants a once-per-game Star Alchemy Ability to a Pokémon
V, which can search the deck for any card. Its direct access to a missing
Radiant Eternatus, and its potential to fetch Hisuian Heavy Ball when
Radiant is Prized, add two real setup routes omitted from the earlier
restricted [Quick Ball access frontier](../shadow_rider_quick_ball_frontier/).

| Restricted first-turn source set | Unrestricted one-card discard | Psychic Energy as only discard | Energy or extra held search Item |
| --- | ---: | ---: | ---: |
| Direct + Treasure + Heavy Ball + Quick Ball | 50.659437625% | 42.703458196% | 45.066291589% |
| **Plus naturally available V + held Forest Seal Stone** | **53.106724029%** | **45.643268336%** | **47.890192495%** |
| **Increment** | **+2.447286405 pp** | **+2.939810139 pp** | **+2.823900905 pp** |

For the unrestricted-payments case, the new **Stone directly finds Radiant**
branch contributes **2.056169263 pp**; the **Stone finds Heavy Ball for a
Prized Radiant** branch contributes **0.391117141 pp**. The latter is
unchanged across payment policies because it requires no discard.

These percentages are conditioned on an accepted Basic-containing opening
of seven cards, six face-down Prizes and one first-turn natural draw going
second. They measure only the specified dual-VMAX access endpoint.

## Source and action fidelity

- Original list and print IDs are unchanged. Its V is swsh6-74, Tool is
  swsh12-156, Radiant is swsh12pt5-105, and Heavy Ball is swsh10-146.
- A different Basic must be in the original opening to be Active.
  A Shadow Rider Calyrex V may be held initially or drawn at the beginning
  of the turn and then put into play, providing a legal Tool host.
- Forest Seal Stone must be physically held in the first eight cards;
  its Tool slot must be empty and the VSTAR Power unused. The Tool may
  attach to the Active or a Benched V.
- When Radiant is in deck, Star Alchemy retrieves Radiant directly.
  When Radiant is Prized and the Heavy Ball is in deck, Stone can obtain
  Heavy Ball, which trades for Prized Radiant. If Heavy Ball was already
  held, that route belongs to the earlier direct Heavy Ball branch.
- Radiant's Climactic Gate subsequently requires two Shadow Rider VMAX
  still in the deck. It ends the turn when used.
- Priorities allow directly held Radiant and paid direct Item searches
  first, using Stone only as the fallback. The discard policies are
  hypothetical opportunity-cost constraints; they do not change the
  mechanical legality of the Item cards.

## Exact solver and independent physical validation

The [implementation](../../tools/shadow_rider_forest_stone_frontier.py)
uses the existing eight-category source counts
(1 Radiant, 4 VMAX, 4 Treasure, 1 Heavy Ball, 1 Quick Ball,
13 other Basics, 11 Psychic Energy, 25 remaining). Of the 13 other
Basics, 3 are the Shadow Rider V; of the 25 generic remaining cards, one
is the Forest Seal Stone. Conditional on a grouped opening/draw state
holding b other Basics and f generic remaining cards, the exact chance
of holding Stone and an eligible V is:

P(Stone and V) = (f / 25) × [1 - C(10, b) / C(13, b)].

The expression follows physical exchangeability and remains valid after
the six-Prize allocation is integrated, because the exact sampled
opening/draw identities are exchangeable within their category.
Every route mass uses exact rational numbers; each of the three
payment-policy route partitions sums to one.

The [reproducer](reproduce.py) independently enumerates fully labeled
physical cards in two smaller toy decks, explicitly marking which Basic
is a Pokémon V and which generic filler is the Stone. It matches
**every route** for each payment policy in both toy cases, and pins
the actual-list exact rational results.

## Boundaries

This is an analytical setup-access result, **not a game or match win rate**.
An available V and Stone are assumed able to resolve normally. We omit
opponent Tool/Ability/Item restrictions, alternative V search, the
Quick Ball -> Shadow Rider V -> Stone -> Radiant two-action chain,
competing uses of Star Alchemy, other draw/search effects, Bench pressure,
opponent interaction and later turns. The extra Stone use can have a
substantial future opportunity cost. No deck modification is recommended
on this access objective alone.
