# Melt Away reverses attachment-count dominance after Retreat overpayment

## Result

The restricted typed gust minimax can prune nonminimal Retreat Energy
payments because, within its rules, keeping additional attached Energy
only increases the defender's future Retreat options.

An exact, printed-card counterexample shows why that monotonicity
does not extend even to all Retreat-only continuations:

**Ethan's Magcargo**, ability **Melt Away**, has no Retreat Cost whenever
it has no attached Energy. Paying *more* Energy now can leave it with
zero Energy and enable a subsequent zero-cost Retreat that a smaller
payment cannot achieve.

This counterexample needs no Dashing Pouch and no card returned to hand.

## Physical two-turn witness

Use the English Ethan's Magcargo print `sv10-36`, a Stage 1 with
printed Retreat Cost three and the Melt Away Ability. Initially it is
Active with one Double Colorless Energy and two Basic Psychic Energy
cards attached. A Pivot and Backup are on the Bench.

Its ordinary Retreat Cost is three because it still has Energy
attached, so Melt Away is inactive.

| First Retreat payment to Pivot | Energy remaining on Magcargo | Melt Away afterward |
| --- | --- | --- |
| Double Colorless plus one Basic Energy | One Basic Energy | Inactive |
| Double Colorless plus both Basic Energy | None | **Active** |

Both choices are legally executable physical payments under the
canonical board kernel's conservative selected-card-count rule.
One paid Energy card supplies two units, and the discarded set
contains two or three physical Energy cards respectively.

Then the opponent Knocks Out Pivot and promotes Magcargo; a new turn
begins and Galar Mine is in play, ordinarily increasing Retreat
Cost by two.

- The first-payment survivor retains one Basic Energy, disabling
  Melt Away. Effective Retreat Cost is five, so it cannot Retreat
  with the one attached Energy.
- The larger-payment survivor has zero Energy, so Melt Away gives it
  **no Retreat Cost**. The D-13 no-cost effect takes priority over
  Galar Mine's increase. The player can Retreat to Backup with an
  empty Energy payment.

When Melt Away is suppressed, the Energy-free survivor also has
effective Retreat Cost five and cannot Retreat.

The canonical physical-action enumerator and action budget verify
the first Retreat, the Knock Out and promotion topology, start-of-turn
Retreat reset, resolved future cost, and empty-payment second Retreat.
Knock Out damage and opponent Stadium placement are represented as
scenario transitions rather than full opponent-turn move simulation.

## Source-backed integration

The added exact-print effect in
`tools/retreat_environment_modifiers.py` recognizes the following
bundled English print IDs:

- `sv10-36`
- `me2pt5-24`
- `me2pt5-222`

All have the same Melt Away Ability text in the supplied card pool.
The effect is applied only when the source's Ability is enabled and
the holder has no attached Energy. Unknown print IDs are excluded.

The supplied Advanced Player's Rulebook section D-13 explicitly
uses Ethan's Magcargo's Melt Away to show that an unconditional
no-Retreat-Cost state takes priority over cost-increase effects.

## Implication

This is a decisive failure of a tempting generic dominance claim:
more Energy remaining attached need not imply at least as many
future Retreat options. The condition creating the exception is a
state-dependent **zero-attached-Energy** Ability.

Safe pruning must check whether future rules depend on an empty
Energy set, even when no hand-return or other destination
replacement effect exists.

The witness establishes game-state reachability, not a tournament
deck-construction recommendation, prevalence estimate or win-rate
improvement.

## Reproduce

Run `python results/retreat_melt_away_overpayment/reproduce.py`.

The dedicated CI also validates the existing board environment
modifier and exhaustive physical Retreat action regressions.
