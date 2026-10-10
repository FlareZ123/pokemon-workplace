# Mixed Stadium entry channels shift the same-copy return frontier

## Question

How much does one unused ordinary Stadium play change the resources required
to leave and re-enter a previously used Grand Tree (`sv7-136`) within one
turn using Gothitelle (`xy3-41`) Teleport Room?

This is an **exact, conditional source-access** problem. The unsettled
tournament question is whether returning the **same physical copy** refreshes
the Stadium's once-per-turn voluntary effect. The experiment carries both
possibilities explicitly and does not purport to answer that ruling.

## Setup and rules

The initial board has one Grand Tree physical copy already in play, one
Brooklet Hill (`sm2-120`) in hand, optionally a second Grand Tree copy in
discard, 0 to 4 declared available Gothitelle Teleport Room source IDs, and
an unspent ordinary Stadium-play allowance. We assume eligible evolution
targets, so each accessible Grand Tree activation may succeed.

The ordinary Stadium action from hand and a Teleport Room discard-to-play
effect are different channels:

* Grand Tree G1 is used.
* The player **plays** Brooklet Hill B from hand. This uses their sole
  ordinary Stadium-play allowance, putting G1 in discard.
* One Gothitelle **puts** G1 from discard into play through Teleport Room.
  This does not spend another Stadium-play allowance.

The resulting G1 return has a fresh in-play entry epoch while retaining
the original physical card ID. Under a per-entry activation ledger, a second
Grand Tree effect use is available. Under a per-physical-card ledger, it is
spent. With a distinct copy G2 selected instead, the official different-copy
precedent permits the second activation under both models.

## Computation and exact results

`tools/stadium_reentry_usage_bounds.py` provides
`ordinary_play_successors`, which delegates entirely to the physical
`play_stadium_from_hand` kernel and increments the entry epoch on a valid
entry. The finite search can now include both Teleport Room and ordinary
Stadium play, while maintaining one authoritative physical card inventory,
one Stadium quota counter, and distinct source-specific Ability histories.

For each fixed number of Gothitelle source IDs, exhaustive search enumerates
every permitted ordering, physical target, and activation opportunity.

| Tree copies | Gothitelle sources | Per-entry max | Per-physical-copy max |
|---|---:|---:|---:|
| 1 | 0 | 1 | 1 |
| 1 | 1 | 2 | 1 |
| 1 | 2 | 2 | 1 |
| 1 | 3 | 3 | 1 |
| 1 | 4 | 3 | 1 |
| 2 | 0 | 1 | 1 |
| 2 | 1 | 2 | 2 |
| 2 | 2 | 2 | 2 |
| 2 | 3 | 3 | 2 |
| 2 | 4 | 3 | 2 |

The name-level interpretation, included only as a negative control, limits
all cases to one activation; it conflicts with the official second-copy
Brooklet Hill ruling.

Let n be the number of unused Gothitelle sources. The maximum under the
per-entry interpretation becomes
`1 + ceil(n/2)`, one activation higher than the two-source-only result
`1 + floor(n/2)` when n is odd. With a physical-copy once-per-turn
interpretation, the maximum is
`min(number_of_Grand_Tree_copies, 1 + ceil(n/2))`.

With only a single Gothitelle source, an ordinary Stadium play is sufficient
to produce the same-copy uncertainty witness. Without that ordinary play,
Brooklet Hill remains in hand. The existing physical kernel cannot use
Teleport Room to retrieve a different-named Stadium before a replacement
enters discard, and the benchmark gets only its initial Grand Tree use.

## Evidence and scope

The locally bundled card texts and Advanced Player's Rulebook I-B-04 anchor
the two distinct Stadium entry channels. The official Japanese Teleport Room
Q&A confirms discard-to-play works even when playing Stadiums from hand is
restricted: https://www.pokemon-card.com/rules/faq/details.php?id=9756

The official Brooklet Hill Q&A supports different-copy refresh:
https://www.pokemon-card.com/rules/faq/search.php?freeword=%E3%81%9B%E3%81%9B%E3%82%89%E3%81%8E%E3%81%AE%E4%B8%98&regulation_faq_main_item1=all

The exact same-copy return effect-use question remains explicitly unresolved
in this research. The calculation describes available **uses of a generic
Grand Tree effect** under stated identity semantics, excluding the need to
actually find evolution targets, perform a Stage 1/Stage 2 chain, preserve
board space, or survive Ability lock. Source IDs represent already-present,
currently usable Gothitelle and therefore do not estimate setup probability.

## Reproduction

`python results/stadium_mixed_entry_frontier/reproduce.py`

The reproducer checks the same-copy witness, the ruling-grounded different-
copy witness, conservation of each physical Stadium, the once-per-turn normal
Stadium play, a once-per-source Teleport Room restriction, and the complete
30-case census. It independently removes normal play as an ablation.
