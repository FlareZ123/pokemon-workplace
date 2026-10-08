# Physical Trainer card conservation for paired targeted-switch actions

## Extension

[paired_switch_physical_transaction/](../paired_switch_physical_transaction/)
combines a source-specific two-sided switch program with immutable board
movement and action quota. Its output reports the number of Trainer copies
spent, but source copies must also physically move from hand to discard.

`tools/paired_switch_identity_bridge.py` bridges that source transition
to the shared `IdentityLedger` and preserves the conservation law.

## Contract

Inputs include the acting player's materialized card ledger, both
player's physical board states, turn budget, an audited paired-switch
program, explicit source instance IDs, target Pokemon ID choices and
current Item-play permission.

A successful transaction:
1. verifies every required source instance exists in **hand**, bears
   the exact card name, and is a unique physical instance;
2. verifies physical Energy and Tool attachment bindings between
   the actor's ledger and existing board;
3. executes the audited two-sided board effect and spends applicable
   action quota using the existing transaction layer;
4. moves each played Trainer instance from `hand` to `discard`;
5. asserts original and resulting ledger card totals are identical,
   and confirms attachment bindings still match the resulting board.

A failed action returns `None` without changing either immutable
input authority. Reusing already discarded source IDs is rejected.

Cross Switcher must supply **two different physical** hand instance IDs;
supplying the same ID twice cannot satisfy its two-copy requirement.
Prime Catcher uses one source, while Guzma and Team Rocket's Giovanni
spend a Supporter action through the inherited turn budget.

The acting player's attachment identities are tracked by its own ledger;
the opponent owns a separate ledger. The board executor preserves both
sides' attachments and Pokemon identities.

## Verified scenarios

The regression covers **384** configurations across the four legal source
programs, own and opposing Bench presence, Team Rocket classification,
exhausted Supporter quota, permitted/forbidden Item play, and hand source
counts 0/1/2.

For each accepted transition it independently checks:

- `IdentityLedger.totals()` is unchanged;
- played card instance IDs move to discard;
- any unplayed source copies remain in hand;
- attached Energy and Tool instances remain bound to their Pokemon
  despite Active/Bench switches;
- the expected Supporter quota is spent exactly once;
- a second attempt to use already spent physical source cards fails.

Tests additionally reject duplicate Cross Switcher source IDs and a
card currently in the deck being supplied as an in-hand source.

## Limits

The bridge validates only materialized physical cards in the player's
ledger. It does not own opponent zone conservation, select cards from
an exchangeable deck count, evaluate legality or target immunity in
arbitrary lock states, or resolve other triggered abilities.

A production full-game transaction should further combine source-scoped
play permissions, cards that change the effect's resolution, and global
cross-player game-state events. The current adapter offers an atomic
local correctness boundary that future agents can reuse.

## Reproduction

`python -m results.paired_switch_identity_bridge.reproduce`

Relevant existing infrastructure:
`tools/identity_materialization.py`,
`tools/multicopy_zone_state.py`,
`tools/board_object_kernel.py`,
`tools/turn_action_budget.py`.
