# Shadow Rider champion Heavy Ball vs Psychic Energy: an early-setup objective inversion

## Question

The verified 2026 Aichi Open League champion Shadow Rider Calyrex list has
**one Hisuian Heavy Ball and eleven Psychic Energy**. An exact first-turn
study found that the singleton Heavy Ball adds a small but real Prized
Radiant Eternatus retrieval route, increasing early two-VMAX access.

If additional Heavy Ball copies occupy slots originally held by Basic
Psychic Energy, does that improve the overall first-turn resource situation?

**Within two explicitly defined first-turn metrics, no single swap dominates.**
More Heavy Ball raises the probability of the dual-VMAX search, while
lowering the probability of combining that launch with at least one
Psychic Energy already in the first-eight hand.

Implementation: `tools/shadow_rider_ball_energy_frontier.py`  
Reproducer: `results/shadow_rider_heavy_ball_energy_frontier/reproduce.py`  
[Passing Windows CI 38243375953](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38243375953)

## Five exact-print, conservatively legal 60-card variants

The variants keep **all other 58 unique card-name quantities unchanged**
except the two displayed names (baseline has H=1/E=11). If H=0,
the replaced Ball slot becomes a twelfth Psychic Energy; if H=2/3/4,
one/two/three Energy slots respectively become additional Heavy Ball
copies. The precise actual baseline source is
[competitive_deck_baselines](../competitive_deck_baselines/).

| Hisuian Heavy Ball H | Psychic Energy E | Dual VMAX launch only | Dual VMAX launch AND at least one early Psychic Energy in hand |
| ---: | ---: | ---: | ---: |
| 0 | 12 | 43.699162% | **35.462812%** |
| **1 (published)** | **11** | **44.937944%** | **35.014627%** |
| 2 | 10 | 46.035451% | 34.183380% |
| 3 | 9 | 47.005411% | 32.955289% |
| 4 | 8 | **47.860458%** | 31.313127% |

The published deck's one-Ball access and exact direct/Treasure/Hisuian
Heavy Ball routes agree with the independent earlier
[Heavy Ball launch](../shadow_rider_heavy_ball_launch/) result.

In particular, the **H=1 to H=2** swap raises the two-VMAX launch
event by **1.097506964 percentage points**, while the joint
launch-and-hand-Energy event falls by **0.831247246 percentage points**.
Evaluating only the first column would miss this resource tradeoff.

## Model contract

Every variant has 60 cards, one Radiant Eternatus, four Shadow Rider VMAX,
four Mysterious Treasure, 13 other starting-eligible Basic Pokémon and
the displayed H and E counts. The remaining generic non-Energy category
contains 26 fixed cards.

The same conditional Basic-valid seven-card opener, physical six-Prize
setup, first natural draw going second, non-Radiant initial Active, and
named direct/Treasure/Heavy Ball routes are used for each row. The first
metric counts **two VMAX remaining in deck** when Radiant's Climactic
Gate becomes available.

The second metric additionally requires at least one Psychic Energy
among the first eight cards observed naturally (opening seven plus first
turn's draw). It is an *early hand-energy reserve* condition. The
hypothetical policy preserves that Energy for the upcoming Underworld
Door turn by paying any Mysterious Treasure discard with another card.
This may carry a strategic discard cost.

This joint condition does not require a successful next-turn attack,
and an Energy card absent from the initial hand may still be drawn from
Underworld Door or another effect later. Accordingly, the joint metric is
one **diagnostic** measure of future resource readiness, not a complete
energy-acceleration or match-winning criterion.

## Exact probability mechanism

The source engine enumerates the grouped opening, six-Prize composition,
and first draw without replacement. It aggregates each successful
two-VMAX world by the number `f` of generic filler cards in the
first-eight hand.

If E of F generic fillers are Psychic Energy in a given variant,
conditional on `f`, the chance of at least one Energy among those
cards is

`1 - C(F-E,f)/C(F,f)`.

For every displayed candidate, `F = 38-H` and `E = 12-H`; therefore
`F-E = 26` remains fixed. The exact rational formula is applied to
the combinatorially weighted successful worlds. There are no random
sampling errors.

An independent physical toy oracle labels every card instance, every
Energy subclass and every opening/Prize/draw choice for H=0,1,2 in
10-card decks. It checks **8,925 accepted first-draw worlds per
variant**. Both launch and joint Energy-reserve probabilities agree
exactly with the grouped calculation. The regression also locks the
five actual-list variant probabilities to exact rational fractions.

All five complete 60-card variants are passed through the repository's
conservative deck-construction and Expanded snapshot legality proof at
2026-10-12, preserving one Radiant, one ACE SPEC and the
four-of card-name cap.

## Practical interpretation

Additional Hisuian Heavy Ball copies increase the chance of rescuing a
Prized Radiant early but consume slots that the published champion uses
for Psychic Energy. Underworld Door is a repeating source of Energy
acceleration and draw, so early Energy availability can be a critical
component of actual setup strength. These effects compete even before
considering future attachments or opponent disruption.

**No swap is recommended on these two metrics alone.** A serious
deck-building choice needs to integrate later turns, hand disruption,
the value of drawing a spare Ball when Radiant is accessible, Treasure
discard opportunity costs, opposing Item/Ability locks, the exact
matchup field, and a gameplay policy. The tournament winning baseline
is evidence for its original configuration; the counterfactuals are
mechanically legal hypothetical decks with no measured match win rates.
