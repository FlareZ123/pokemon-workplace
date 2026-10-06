# Connector abstraction gap: clean outs versus Quick Ball + Tapu Lele-GX

## Question

How accurately does an idealized count of four deterministic non-Supporter outs represent a concrete four-Quick-Ball plus one-Tapu-Lele-GX access package?

It can be badly wrong in either direction.

The comparison uses the same 60-card, 6-Prize, 12-starter, four-critical, two-Gladion baseline and conditions on a valid opening plus at least one critical being Prized.

Reproducer: results/connector_abstraction_gap/reproduce.py

## Models compared

### Idealized package

Four clean non-starter outs from tools/direct_rescue_outs.py.

Each out is assumed to be immediately playable, costless, and able to search one unprized Gladion from deck to hand.

With only the accepted opening seven exposed, this package gives:

**52.338794%** first-rescue access.

### Concrete compound package

Four Quick Ball plus one Tapu Lele-GX from tools/quick_ball_lele_access.py.

The package preserves:

- one Tapu Lele-GX as a setup-eligible starter;
- Wonder Tag's hand-to-Bench trigger;
- the forced-setup loss when Tapu Lele-GX is the only starter in the opening;
- Quick Ball's need for an acceptable discard card;
- Tapu Lele-GX and Gladion Prize risk.

The number of dedicated disposable non-starters is varied.

## Result

| Dedicated disposable cards | Quick Ball + Tapu Lele-GX access | Difference versus 4 clean outs |
| ---: | ---: | ---: |
| 0 | 29.898873% | -22.439921 pp |
| 2 | 34.655064% | -17.683731 pp |
| 4 | 38.626850% | -13.711945 pp |
| 8 | 44.615074% | -7.723720 pp |
| 12 | 48.569324% | -3.769470 pp |
| 16 | 51.061415% | -1.277379 pp |
| 20 | 52.543426% | +0.204632 pp |
| 24 | 53.361937% | +1.023143 pp |

The first integer disposable-pool size where the concrete package reaches the four-clean-out baseline is **20**.

## Interpretation

At low disposable density, treating Quick Ball as a clean out is strongly optimistic.

With only four dedicated disposable cards, the clean-out abstraction overstates first-rescue access by **13.71 percentage points**.

At 12 disposable cards, the overstatement is still **3.77 points**.

The direction eventually reverses. At 20 or more disposable cards in this exact composition, four Quick Ball plus Tapu Lele-GX slightly exceeds four idealized non-starter outs.

The reason is structural. Tapu Lele-GX is an additional access piece when preserved in the hand, and it is also a setup-eligible starter. The clean-out comparison gives the idealized package only four connector cards. The real package contains four Quick Ball plus a fifth card that sometimes directly supplies the Wonder Tag route.

This means there is no stable conversion such as:

4 Quick Ball + Tapu Lele-GX = 4 effective Gladion outs

The effective access contribution depends on discardability, setup composition, Prize topology, and the support Pokémon itself.

## Strategic consequence

An optimizer that compresses compound connector packages into an effective-out count can lose information in several ways.

The same Quick Ball count can have very different value as the deck's DCI composition changes.

The support Pokémon changes mulligan behavior because it is a Basic.

The support Pokémon can be forced into play during setup and lose its trigger.

The support Pokémon adds a Bench and Prize liability.

The connector can also have competing Pokémon targets.

A scalar "effective copies" approximation may still be useful as a local summary after these state variables are fixed. It should not be treated as an intrinsic property of the package.

## Relation to connector domination

The clean-out abstraction assumes the connector is dedicated to Gladion.

Quick Ball rarely is.

If the same Quick Ball is required to establish an attacker, a second support Pokémon, or an evolution line, the Gladion route competes with those uses. That contention can reduce practical access below every value in the concrete table.

The table therefore measures mechanical current-window access under a frozen discard policy and favorable Bench/Ability state. Strategic connector domination remains a later layer.

## Validation

The reproducer imports the two independently validated exact models rather than reimplementing their combinatorics.

It computes the clean four-out baseline, scans every integer disposable-pool size from 0 through 24, and asserts that the first crossing occurs at 20.

## Next useful work

A stronger package comparison should place a competing Basic-Pokémon target on Quick Ball.

That would let the model measure connector domination directly: how often using Quick Ball for Tapu Lele-GX blocks a required attacker/setup line, and how the optimal choice changes with Prize state and hand composition.
