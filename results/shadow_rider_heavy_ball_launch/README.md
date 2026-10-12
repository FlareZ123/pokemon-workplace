# Aichi champion Shadow Rider: Hisuian Heavy Ball Prize rescue adds dual-VMAX access

## Question

The [2026 Aichi champion Shadow Rider Calyrex reference list](../competitive_deck_baselines/)
contains one **Hisuian Heavy Ball** and one **Radiant Eternatus**. Existing
[Radiant two-VMAX launch work](../shadow_rider_radiant_launch/) measured
first-turn Climactic Gate through Radiant in hand or four Mysterious Treasure
copies. What additional access does the actual list gain when Radiant is
Prized and the player has Hisuian Heavy Ball?

**Answer in the defined first-turn action model:** +**1.2387815822 percentage
points** of Basic-valid starts going second, increasing two-VMAX launch access
from **43.6991624304% to 44.9379440125%**. The source list is unchanged.

Implementation: `tools/shadow_rider_heavy_ball_launch.py`  
Reproducer: `results/shadow_rider_heavy_ball_launch/reproduce.py`  
[Passing Windows CI 38241869121](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38241869121)

## Card-text grounding

The bundled effectively legal English source prints provide the three
enabling actions:

- `swsh12pt5-105` Radiant Eternatus: when played **from hand onto the Bench**,
  Climactic Gate can put up to two Pokémon VMAX from the deck directly onto
  the Bench, and using it ends the turn.
- `sm6-113` Mysterious Treasure: discard a card from hand, then fetch one
  Psychic or Dragon Pokémon from deck to hand.
- `swsh10-146` Hisuian Heavy Ball: look at the face-down Prize cards,
  reveal one Basic Pokémon found there, move it to hand, and put Heavy Ball
  face down in its former Prize slot, then shuffle the remaining face-down
  Prizes.

The exact champion baseline contains **one** Radiant, **four** Shadow Rider
VMAX, **four** Treasure, **one** Heavy Ball, **13** other starting-eligible Basic
Pokémon, and **37** remaining cards. All six categories are derived and
checked against the actual 60-card list.

## Exact model

We condition on a seven-card accepted opening containing a Basic, choose a
non-Radiant starting Active from that *opening*, set six face-down Prize
cards from the remaining cards and optionally take one first-turn natural
draw. An eligible other Basic in the original opening is needed because
Radiant must subsequently enter the Bench from hand for Climactic Gate.

A dual-VMAX success requires all these conditions:

1. At least one non-Radiant Basic appeared in the initial seven.
2. Radiant can reach hand from: initially/drawn in hand; or via held Heavy
   Ball if it is Prized; or via held Mysterious Treasure if it remains in deck.
3. At least two Shadow Rider VMAX remain in the deck when Climactic Gate
   searches. Prized VMAX or VMAX already in hand cannot be fetched by it.

For this first-turn source-isolated comparison we give direct, Heavy Ball,
and Treasure routes mutually exclusive classifications. Treasure's
one-card discard is assumed mechanically payable without pricing its
strategic cost. No other search/draw effects, opponent interactions,
Ability or Item lock, Bench traffic, Hisuian Heavy Ball alternative target,
or later-turn attack value are included.

## Exact result

| Modeled route | Going first, no draw | Going second, one draw |
| --- | ---: | ---: |
| Radiant already in hand | 10.500089331% | 12.017840120% |
| Mysterious Treasure to Radiant in deck | 29.078698828% | 31.681322310% |
| **Hisuian Heavy Ball retrieves Prized Radiant** | **1.081695521%** | **1.238781582%** |
| **Total dual-VMAX access** | **40.660483680%** | **44.937944013%** |

The first two routes reproduce the existing model's prior exact values
with the Heavy Ball print retained in the actual 60-card inventory. The
new Heavy Ball rescue is an **absolute 1.238781582 percentage point**
improvement on the after-one-draw event, a **2.834795% relative uplift**
over the 43.699162430% old two-route rate.

The net difference between going-second and going-first modeled launch
access becomes **+4.277460333 percentage points**. This is an access
comparison only. The choice of play order changes many other decisions
and opponent opportunities.

## Independent validation

The primary enumerator sums exact multivariate hypergeometric weights
over every category-vector opening, six-card Prize composition, and legal
first draw. All calculations use rational fractions and assert total
probability mass equals one.

An independent labeled-physical-card oracle enumerates **8,925** exact
toy-game combinations with a ten-card pool, three-card opening, two Prize
cards, and a first draw. It also tests the no-draw physical worlds. Every
route/outcome frequency matches the grouped model.

The reproducer verifies the literal card effects from the bundled card
files, the actual champion list counts, the previous Radiant two-route
numbers, and the new Heavy Ball probabilities with exact fractions:

- Before draw: `132395819839/12239656844800`.
- After draw: `121298091771/9791725475840`.

## Strategic interpretation

Hisuian Heavy Ball has a distinctive recovery role: a copy in hand can
turn a normally inaccessible Prized Radiant into a first-turn board
accelerator. The exact single-slot effect is relevant even though its
average uplift is modest. It also changes the Prize contents by putting
the spent Heavy Ball where Radiant was, which matters later but is beyond
this launch-only model.

The measured percentage belongs to the **existing champion deck** and
the tightly defined two-VMAX opening event. It does not justify adding
another Heavy Ball, swapping cards, or claiming an equivalent win-rate
increase. Those decisions would need matched deck changes, opportunity
costs, and later-turn matchup outcomes.

## Next experiments

A high-value extension is to quantify competing searches with the
single Heavy Ball: rescue another Prized Basic, leave it unused for later,
or fetch Radiant immediately. Other extensions can model specific deck
discard payment policies for Mysterious Treasure and first-turn
Bench availability, and distinguish opening information before and after
the first deck search.
