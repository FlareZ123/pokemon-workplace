# Pickup replay makes direct-to-Bench search a conditional trigger out

## Question

A Basic support Ability such as Tapu Lele-GX's Wonder Tag explicitly
requires **playing the card from hand onto the Bench**. A Nest Ball that
places that Basic directly from deck onto Bench does not activate it.

Can an Item that returns the newly Benched Basic to hand create a legal
second entry which *does* trigger the Ability?

**Yes, if the pickup is usable and succeeds.** This study joins the
direct-Bench replay path with the separate recovery of a singleton support
forced into the starting Active Spot.

- Implementation:
  [bench_trigger_pickup_replay.py](../../tools/bench_trigger_pickup_replay.py)
- Independent physical-card verifier:
  [reproduce.py](reproduce.py)
- Related result:
  [forced Active recovery](../bench_active_trigger_rescue/)

## Two distinct pickup-assisted lines

**Direct-Bench replay:**

`Nest Ball searches support A onto Bench -> no hand-entry Ability trigger
-> Super Scoop Up A (heads) -> A returns to hand -> play A onto Bench
from hand -> trigger A.`

This line requires an already-established other Pokémon in the Active
Spot, a free Bench slot, the support remaining accessible in deck, a
direct-to-Bench search Item, and an effective pickup. A deterministic
Scoop Up Cyclone can replace a successful coin pickup, subject to the
one-ACE-SPEC restriction.

**Starting Active rescue:**

`A is forced opening Active -> establish other Basic O on Bench
-> scoop Active A (heads) -> promote O -> replay A from hand
onto Bench -> trigger A.`

For this second line, Nest Ball can fetch O to create the necessary
backup Active. In the first line, Nest Ball fetches A itself.
These are different uses of the same direct-to-Bench search capability.

## Exact modeled setting

One support A and `O` other ordinary Basics are embedded in a 60-card
deck with idealized search Items and pickup Items. Enumerate an ordinary
accepted seven-card opening, six unknown Prizes, and one later uniform
random draw. An ordinary non-A Basic is chosen as opening Active whenever
one is available.

The outcome is partitioned into disjoint probabilities:

1. **No pickup needed:** A remains in hand after starting-Active choice,
   is drawn later, or an idealized deck-to-hand connector can fetch an
   unprized A.
2. **Active recovery:** A began as forced Active, a backup O is
   accessible, and a pickup returns A to hand.
3. **Bench-origin replay:** A remains unprized in deck; no deck-to-hand
   connector is visible; a direct-Bench search puts A into play and a
   pickup returns it to hand.

Only the recovery branches pay pickup variance; with `r` available
Super Scoop Up copies, the chance of at least one heads is
`1 - 2^(-r)`. A guaranteed Scoop Up Cyclone gives certainty conditional
on access. The two recovery branches are mutually exclusive because A
cannot simultaneously start Active and remain in deck.

All search transitions are treated as deterministic once an eligible
target is in deck. The model omits Quick Ball's actual discard payment,
Trainer locks, opponent play, real Ability payloads, forced Bench filling,
Tool/attachment interactions, and other recovery or Prize-taking lines.
Figures are **restricted access probabilities**, not matchup or
tournament win-rate estimates.

## Exact quantitative comparison

Take one A, three other ordinary Basic starters, four ideal hand
connectors, four Super Scoop Up copies, six Prizes, and one later random
draw. Vary the number of direct-to-Bench search Items. All values are
conditional on an accepted opening.

| Direct-Bench Items | No pickup | Active rescue gain | Bench-origin replay gain | Total access |
| ---: | ---: | ---: | ---: | ---: |
| 0 | 35.038269% | +1.985971 pp | +0.000000 pp | **37.024241%** |
| 2 | 35.038269% | +2.623836 pp | +1.916591 pp | **39.578696%** |
| 4 | 35.038269% | +3.136534 pp | +3.465665 pp | **41.640468%** |

The four-direct-Item deck gains **6.602198 percentage points** from
pickup-assisted lines over the no-recovery baseline. More than half of
the pickup benefit arises specifically from the direct-to-Bench *A*
placement and replay route, even though the initial placement does not
fire the Ability.

This is a concrete counterexample to evaluating Nest Ball solely by
whether its initial destination matches a hand-to-Bench trigger.

### Effect of the other-Basic count

With four direct-Bench Items and four pickup coins:

| Other Basics | No-pickup access | Active rescue gain | Bench replay gain | Total |
| ---: | ---: | ---: | ---: | ---: |
| 1 | 23.129876% | +5.845545 pp | +2.274741 pp | 31.250163% |
| 3 | 35.038269% | +3.136534 pp | +3.465665 pp | 41.640468% |
| 5 | 39.287815% | +1.972858 pp | +3.906493 pp | 45.167166% |

As the number of ordinary Basics rises, support A is forced into the
Active role less often, reducing the Active recovery branch. Conversely,
the accepted opener more often begins with a different Active Basic, so
there are more worlds where A remains in deck and Bench-origin replay
can supplement missing hand search.

## Verification

A completely separate physical-card oracle enumerates **8,925 labeled
accepted opening/Prize/draw states** of a 10-card deck containing A,
two other Basics, one deck-to-hand connector, one direct-Bench Item,
two coin pickup Items and three fillers.

Exact agreement with the grouped implementation:

| Component | Exact probability |
| --- | --- |
| No pickup | `46/119` |
| Active recovery gain | `353/5950` |
| Bench-origin replay gain | `53/1785` |
| Combined access | `8489/17850` |

The reproducer also crosschecks the entire Active recovery branch
against the prior independent
[Active rescue kernel](../bench_active_trigger_rescue/), tests
zero direct-Bench Items (zero Bench replay), and tests zero pickup
resources (both recovery branches zero).

## Strategic interpretation

The destination of a search edge does not determine the full set of
downstream routes. An initial Bench placement can be followed by a
zone-changing pickup and a later hand-origin entry. The same direct
search can act on the support itself or create the backup Pokémon needed
to recover it from the Active Spot.

These are conditional, multi-action routes consuming the pickup Item
and Bench bandwidth. Their practical value depends on actual access,
discard costs, Item lock, ACE SPEC contention, ability payload, and
other turn requirements. The current model isolates the *existence and
frequency* of these routes while making those costs explicit as
limitations.

A valuable next step is to combine this pickup replay geometry with
the previously built [adaptive paid Quick Ball planner]
(../bench_quickball_payment_order/), then test
which route remains optimal with real card payments and hand mutations.
