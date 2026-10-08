# Trainer-effect immunity changes conditional paired-switch execution

## Verified source interaction

Prime Catcher, Cross Switcher and Guzma first select an opposing Benched Pokémon to move Active. Their text permits a later own Active switch only if the first opposing switch succeeds. Team Rocket's Giovanni instead first switches two own Team Rocket's Pokémon, then conditionally switches an opposing Benched Pokémon.

The rulebook sections C-05 and E-20 make target immunity and the effect ordering consequential. With a protected Benched Axew (Unnerve, sm11-154), the first three Trainer effects fail their initial switch and cannot proceed to their own switch. With Giovanni, the own Team Rocket switch succeeds, and the protected opponent's Bench target prevents only the second opposing switch. That successful first step consumes the Supporter card and ordinary quota.

| Source | Protected step | Effects that succeed | Successful source play |
| --- | --- | --- | --- |
| Prime Catcher | First opposing switch | None | No |
| Cross Switcher | First opposing switch | None | No |
| Guzma | First opposing switch | None | No |
| Team Rocket's Giovanni | Second opposing switch | Own Team Rocket's switch | Yes |

A physically successful Giovanni partial effect gives a SwitchTransaction with effect_sequence=("own",) and a matching CausalEventJournal with **one committed Supporter and one board-movement boundary**.

## Source-class reversals

When Active Togekiss's Bright Veil protects ordinary Bench targets from Item effects, Prime Catcher cannot perform the opponent's switch while Guzma can. Active Diancie's Princess's Curtain protects Benched Basic targets from Supporters, reversing that eligibility.

## Implementation

[Source-aware protected transaction](../../tools/protected_paired_switch_execution.py) composes the audited Trainer effect-immunity predicate with the physical paired-switch kernel. Ordinary permitted moves delegate to the physical kernel. A denied first effect yields no transaction. When Giovanni's *second* effect is denied, its eligible first switch and spent quota persist.

This is a bounded static-effect model. If Giovanni's first own move changes a live Ability-lock source, the opposing Pokémon's immunity must be recomputed before resolving the second effect; this wrapper expects no such change. Trainer source availability, precise hand-to-discard card IDs, and coin-gated Trainer attempts are verified in separate models.

## Reproduce

[Regression](reproduce.py) verifies exact positions, protected and unprotected counterfactuals, Supporter quota consumption, and journal compatibility. GitHub Actions run 37818250185 passed on October 8, 2026.
