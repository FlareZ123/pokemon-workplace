# Reserving even one extra Basic can change Item discard payability

## Question and setup

The [general first-turn discard-quota model](../basic_valid_discard_quota/) explores whether extra Basic Pokémon can serve as disposable cards for Quick Ball, Ultra Ball and Secret Box after selecting the mandatory Active Basic. A player's actual game plan may require establishing a Bench or retaining a Basic for later evolution. How much does reserving one or more additional Basics reduce the apparent ability to pay an Item discard requirement?

The constructed 60-card decks retain 12 opening Basics, 8 designated disposable filler, a printed Item source (4 Quick Ball, 4 Ultra Ball or 1 Secret Box), and protected remainder. Going second: condition seven opening cards on containing at least one Basic, put one Active, set six random Prizes, and draw one normal card. Card search outputs, Bench plays, future turns, and opponent interference are excluded.

The player may discard all held F filler and any **spare copies of the same Item beyond the one played**. If b additional Basics remain in the hand after setting the Active, and the player reserves r of them for possible later Bench or evolution use, at most max(0,b-r) Basics may be discarded. For an Item that needs m *other* cards, a payment is accepted only when

F_held + (Q_held − 1) + max(0, B_held − r) is at least m.

This is a model of strategic resource protection, not a claim that Basic cards cannot legally be discarded in Pokémon TCG. The exact actual rules permit discarding them; the deck-line constraint is hypothetical.

## Exact 60-card results

| Basic cards protected after Active | Quick Ball (1 discard) | Ultra Ball (2 discards) | Secret Box (3 discards) |
| ---: | ---: | ---: | ---: |
| 0 | **38.788363%** | **26.718521%** | **2.695779%** |
| 1 | **33.982272%** | **17.081308%** | **0.885039%** |
| 2 | **31.479100%** | **13.516184%** | **0.494577%** |
| 7 (all held Basics protected) | **30.693460%** | **12.786962%** | **0.453336%** |

All percentages condition on a Basic-valid opening followed by a normal turn draw. They are exact rational computations displayed to six decimals.

For the singleton Secret Box, preserving just **one** extra Basic reduces the relaxed payment gate from 2.695779% to 0.885039%. Requiring two saved Basics reduces it further to 0.494577%, very close to the no-Basic-payment fallback of 0.453336%.

For four-copy Ultra Ball, protecting one Basic reduces the relaxed payability from 26.718521% to 17.081308%. The physical Item-presence probability remains 42.738824%, because reserving a Basic changes acceptable payment, not whether the Item was drawn.

The general reserve monotonicity is immediate: increasing r can only reduce the term max(0,b-r) in each physical hand, so payability can only decrease. The exact enumerator validates this across all reserve levels and models.

## Validation and methodology

- [Bench-reserve source gate](../../tools/bench_reserve_discard_gate.py) computes an exact valid-Basic opening distribution, excludes one Active Basic, integrates random Prize placement and the natural turn draw, then prices every hand's payment count with its reservation budget.
- [Independent physical reproducer](reproduce.py) explicitly enumerates **1,404** combinations of small labeled physical decks, valid initial hands, disjoint Prize selections and natural draws. It checks exact paid-source frequencies under several protected-Basic quotas and reproduces each 60-card witness.
- [Windows regression](../../.github/workflows/validate-agent2-bench-reserve-discard.yml) runs Python 3.13.

Actual Bench requirements are state- and archetype-dependent; a deck may want zero, one or several Basics, and could often search replacements. Nothing here asserts that a particular Basic should always be protected. The result measures how much a theoretical Item access estimate shifts when a realistic board-development constraint is imposed, and is not a competitive match-win estimate.
