# Unknown Item-play provenance is distinct from a verified absence

## Problem

`record_paired_switch` can receive a successful physical switch transaction without an accompanying materialized Item source ledger. In this case the resolver knows the Trainer effect was successfully requested, yet it does not know which physical Item-card identities moved from hand. Previously the resulting journal had an empty `committed_plays` tuple, which could be misread as proving that no Item had been played.

## Verified model

`JournalBoundary.play_record_complete` states whether that boundary captured every played card identity. It is `False` for an Item paired-switch effect whose successful transaction did not supply `committed_items`, and `True` when a complete physical source batch is present. Any generic caller introducing an unobserved physical play must explicitly mark the boundary incomplete.

`CausalEventJournal.play_history_complete` requires complete coverage at every recorded boundary. `queried_play(player, kind, name_contains)` uses **three-valued evidence semantics**:

- `True`: a matching physical play has been witnessed, regardless of gaps elsewhere.
- `False`: no match and every recorded boundary is fully observed.
- `None`: no match and one or more boundaries have unobserved source identity.

An incomplete boundary may not simultaneously assert committed physical cards because that would hide which part of the play was observed. If partial capture of multi-card actions becomes a genuine producer scenario, extend the representation with an explicit expected/observed cardinality witness.

## Bounded witness

One Prime Catcher physical transaction is projected into two journals with identical resulting Pokémon boards, identical Ability-lock resolution and identical effects:

- Board-only adapter call omits Item source ID: an empty committed-play tuple and a tri-state Item query of `None`.
- Materialized adapter supplies its verified hand-to-discard source ID: one Item event and an Item query of `True`.

A later opaque action preserves a previously observed positive while making unwitnessed negatives indeterminate. Replay preserves the explicit coverage bit. Invalid combinations of incomplete coverage with asserted play records are rejected.

## Limits

Completeness covers submitted journal boundaries only. The journal cannot discover events that were skipped entirely by its producer. The true meaning of `False` is therefore conditional on the caller's promise to submit every relevant physical play event. In particular, an event-order capture failure can still corrupt Ability-lock precedence even if all submitted records are individually valid.

## Reproduce

`python results/partial_play_history/reproduce.py`.

Dependencies: [causal_event_journal](../causal_event_journal/), [paired_switch_item_play_batch](../paired_switch_item_play_batch/), [paired_switch_event_journal](../paired_switch_event_journal/).
