# Execute paired gust effects on conserved physical board state

## Goal and dependency

The [paired switch program catalog](../paired_switch_order_catalog/)
distinguishes opponent-first gusts from Team Rocket's Giovanni's
own-first switch. The prior [Prime Catcher geometry study](../prime_catcher_order_geometry/)
models attack-readiness constraints. This bridge executes those source
programs on actual Pokemon object identities using the already-validated
`tools/board_object_kernel.py` and `tools/turn_action_budget.py`.

## Source program semantics

| Card | First switch | Dependent second switch | Source requirement |
| --- | --- | --- | --- |
| Prime Catcher | Opponent | Own | Item allowed, ACE SPEC source provided |
| Cross Switcher | Opponent | Own | Item allowed, two copies in hand |
| Guzma | Opponent | Own | Supporter quota |
| Team Rocket's Giovanni | Own eligible Team Rocket pair | Opponent | Supporter quota |

In the first three, a successful opponent gust survives when the player's
Bench is empty. With an own Bench, the caller must choose a legal Pokemon
for the mandatory second switch.

Giovanni requires an own Active and Bench pair with Team Rocket tags.
When this first switch succeeds, the opponent switch follows if it has
an eligible opposing Benched target. With no opponent Bench, Giovanni
can still accomplish the own-side switch.

The transaction rejects an invalid source or mandatory target choice
atomically. It returns both updated boards, action quota, source copies
consumed and the actual ordered switch steps.

## Physical mechanics reused

The source-specific program calls
`board_object_kernel.switch_active()` rather than duplicating card
movement logic. In the resulting board, the moved Pokemon retains its
damage, physical Energy cards, Tools, printed identity and other
persistent metadata. The outgoing Active loses Special Conditions and
temporary attack and retreat effects. Switching does not consume
normal retreat quota or discard Energy.

Guzma and Team Rocket's Giovanni consume one Supporter play through
`TurnActionBudget`. Prime and Cross use a separate Item-play permission
predicate. Cross needs two simultaneous source cards. The result
reports card-copy spending for a higher-level hand/discard ledger, which
this adapter does not own.

## Reproducibility

`tools/paired_switch_physical_transaction.py` is the adapter.

`results/paired_switch_physical_transaction/reproduce.py` independently
uses the audited abstract switch-effect catalog to check the expected
effect order in **384** combinations of card name, own/opponent Bench
presence, Team Rocket classification, Supporter quota, Item permission
and available source copies. Accepted transitions assert identity
and attachment conservation, damage persistence, condition removal on
the outgoing Active, quota consumption and invalid-choice rejection.

Physical examples include Prime with empty own Bench, Guzma moving a
Poisoned attacker to its Bench with its Double Colorless Energy and Tool
intact, and Giovanni resolving its own switch when the opponent has no
Bench.

## Limitations

Card availability in hand, source card identities and their subsequent
discard placement remain upstream. The caller provides whether Item
play is legal and which targets are effect-eligible. Source-dependent
Ability triggers, immunity, Tool locks, attack readiness, temporary
opponent effects and opponent hidden information require additional
integration.

This is a correctness and state-conservation bridge, not a complete
Trainer or combat simulator.
