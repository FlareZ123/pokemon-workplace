# Paired-switch microsteps as Ability-lock event boundaries

## Question

A single Trainer can switch the opposing Active Pokémon and then the user's Active Pokémon in a specified order. How should a causal Ability-lock model record a card play that produces more than one mechanically meaningful board transition?

## Mechanism

`tools/paired_switch_event_bridge.py` consumes a **successful** `SwitchTransaction` from `execute_paired_switch` and the audited `PairedSwitchProgram`. It replays each switch using the existing physical board kernel, checking that the microstep sequence reproduces the source transaction's final physical boards.

The immutable `CausalEventJournal` gets one boundary per switch. An ordinary Supporter `CommittedPlayEvent` is attached only to the first boundary. Thus a two-sided Guzma play produces two lock recomputations but one physical Supporter play. A copied Supporter effect is outside this physical-card-play adapter.

Prime Catcher with an empty own Bench gives one legal opponent switch, so the journal has one boundary. Team Rocket's Giovanni resolves own eligible Team Rocket switch first, then opposing switch. The bridge preserves this reverse order.

The current committed-play schema has only Supporter and Stadium events. Item records for Prime/Cross are **not** silently fabricated or mislabeled as Supporters; the physical Item hand-to-discard event remains with the upstream transaction/ledger until the event schema is generalized.

## Tested cases

- Guzma against setup Empoleon V / Wobbuffet creates two ordered physical switch boundaries, both with recomputed lock state, plus exactly one Supporter event.
- Prime Catcher with no own Bench creates one executed opponent switch and leaves the current attacker Active.
- Team Rocket's Giovanni creates two boundaries in the reverse order.
- A missing Supporter commit and a forged transaction post-state are rejected.
- Each journal replays identically.

Regression: `python results/paired_switch_event_journal/reproduce.py`.

## Limitations

The caller still supplies source availability, target choice, source permissions, copy identities, and a physically valid transaction. The bridge verifies consistency with that validated transaction. It does not infer source legality or prove that all effects within arbitrary card text were recorded. This is a mechanical boundary adapter for the four already-audited paired-switch programs.

References: [paired_switch_physical_transaction](../paired_switch_physical_transaction/), [paired_switch_order_catalog](../paired_switch_order_catalog/), [causal_event_journal](../causal_event_journal/).
