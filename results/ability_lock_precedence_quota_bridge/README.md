# Setup lock precedence can change the canonical Supporter quota

## Question

Does continuous-Ability precedence propagate into downstream action-budget state?

Yes. The existing canonical quota derivation makes that dependency explicit.

## Composition

The regression places:

- Active Empoleon V with Emperor's Eyes;
- Bench Magnezone `bw8-46` with Dual Brains;
- opposing Active Wobbuffet with Bide Barricade.

Empoleon V and Wobbuffet form the verified reciprocal setup lock. Wobbuffet also
suppresses the non-Psychic Magnezone when Bide Barricade is the surviving lock.

The exact physical board is held constant while only first-player ownership is
changed.

## Result

When the Empoleon side is the first player, Emperor's Eyes wins the setup
precedence interaction. Wobbuffet is suppressed, Dual Brains remains effective,
and `derive_board_action_quotas` returns a Supporter-play limit of 2.

When the Wobbuffet side is the first player, Bide Barricade wins. Empoleon V and
Magnezone are both suppressed, so the same canonical board derives the ordinary
Supporter-play limit of 1.

This result concerns the live Supporter quota. Separate first-turn permissions
still govern whether a Supporter may actually be played in a particular opening
turn.

## Architectural implication

Causal lock resolution belongs upstream of canonical action-quota derivation.
A quota engine that sees only physical board objects and ignores effective
suppression precedence can expose the wrong action budget even when every card
and position is represented correctly.

The required state chain is:

`physical board + precedence -> suppression overlay -> quota grants -> canonical budget`

Regression: `results/ability_lock_precedence_quota_bridge/reproduce.py`.
