# Physical Item-play batches and ordered switch boundaries

## Question and card-text basis

Cross Switcher's included card snapshot (`swsh8-230`) says: **"You must play 2 Cross Switcher cards at once. (This effect works one time for 2 cards.)"** Its two physical Item cards contribute one card effect. The legal action may then execute one or two physical switches depending on Bench geometry.

Therefore the number of source card identities consumed, card-effect resolutions, and board-state boundaries are separate dimensions. A one-event-per-switch assumption would lose physical plays on the one-switch Cross case.

## Implementation

- `PlayKind.ITEM` extends the existing committed physical Trainer-play vocabulary.
- `JournalBoundary.play_batch` allows zero or more physical committed card identities at the same causal boundary. Existing `append_boundary(... committed_play=...)` remains supported for ordinary single-card sources.
- `tools/paired_switch_item_play_batch.py` projects actual source instance IDs from `execute_materialized_paired_switch`: each verified Item must move from **hand** to **discard**, with distinct IDs and the source-specific card name.
- `tools/paired_switch_event_bridge.py` attaches that entire batch to the **first** switch boundary, while each switch still advances Ability-lock causal state individually.

Two Cross Switcher card records are *simultaneous within the batch*. The implementation makes **no claim** that arbitrary "when you play an Item" triggers resolve twice; trigger multiplicity requires separate card-specific rules research. It does establish conservation and representation of both physical source cards.

## Exact regression matrix

| Source | Own Bench available | Physical Items played | Switch boundaries |
| --- | --- | ---: | ---: |
| Prime Catcher | No | 1 | 1 |
| Prime Catcher | Yes | 1 | 2 |
| Cross Switcher | No | 2 | 1 |
| Cross Switcher | Yes | 2 | 2 |

The test uses the identity ledger and the physical transaction kernel. It checks both source cards' hand-to-discard movement, output count, replay integrity, rejection of copied or non-hand source IDs, and the full batch being placed before the second physical switch.

Reproduce: `python results/paired_switch_item_play_batch/reproduce.py`.

## Scope

This is a physically grounded journal projection for the two audited paired-switch Items. General Item plays, trigger frequency, higher-level source permissions, and arbitrary effects remain outside this adapter. The card list is an English-language snapshot of the provided Expanded research resources.
