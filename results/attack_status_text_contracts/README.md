# Source contracts for exact attack-inflicted Special Conditions

## Scope

Attacks can inflict Poisoned, Burned, Asleep, Paralyzed or Confused as an
attack effect. The Advanced Player's Rulebook A-01 separates these effects
from damage calculation; Special Conditions are also checked in a separate
Pokémon Checkup phase.

`tools/attack_status_text_contracts.py` compiles an intentionally small
exact whole-text grammar into structured `AttackStatusSourceContract`
records. These record the real print-specific attack identity, the
condition, the opposing Active target, and whether the effect is
unconditional or happens after a heads/tails coin result.

Both old `The Defending Pokémon` and newer `Your opponent's Active Pokémon`
wording are accepted. Extra conditional effects, second instructions,
and other wordings remain outside this grammar.

## Representative real cards

- Alomomola `bw1-39` Water Pulse: Asleep, unconditional.
- Whirlipede `bw1-53` Poison Sting: Poisoned, unconditional.
- Darumaka `bw1-24` Singe: Burned, unconditional.
- Watchog `bw1-79` Confuse Ray: Confused, unconditional.
- Servine `bw1-3` Wrap: Paralyzed only on heads.

The nearby Servine Wring Out also discards an Energy on a heads result,
so a status-only compiler does not mark the whole text as supported.
The conditional damage-and-Paralysis Tandem Shock is excluded for the
same reason.

## Execution boundary

A compiled contract does not itself flip a coin or create a new physical
Special Condition. Executing it requires a live coin result when specified,
opponent Active identity at the correct attack step, attack-effect immunity,
and a downstream status transition. A Pokémon can have multiple compatible
conditions, and Special Conditions have different Checkup effects; this
source catalog does not reduce them to generic damage counters.

These contracts complement the separate agent48 work on *damage-triggered*
passive status reactions. They cover statuses directly inflicted by an attack.

## Reproduction

`results/attack_status_text_contracts/reproduce.py` verifies real
print-specific examples against the legality-filtered current card pool.
CI: `validate-attack-status-text-contracts.yml`.
