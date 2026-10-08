# Exact joint access to two Bench-entry support triggers with pickup variance

## Research question

A line may appear to have both support Pokémon accessible and a way to clear
Bench space, but how often are **both** singleton hand-to-Bench triggers
actually executable before the chosen deadline?

This result combines four effects previously modeled separately:
(1) mandatory starting-Active role, (2) Prize placement,
(3) zone-correct, single-use Pokémon searches, and (4) the coin-flip cost
of recycling one transactional Bench slot.

- Core implementation: [bench_double_trigger_access.py](../../tools/bench_double_trigger_access.py)
- Independent labeled-deck oracle: [reproduce.py](reproduce.py)

## Scope and assumptions

The deck has two different, singleton Basic support Pokémon A and B whose
desired activations require *playing that physical card from hand onto the
Bench*. The opening hand must contain at least one ordinary Basic. When an
ordinary non-target Basic exists in the opener, it is chosen as Active;
otherwise one of the support Basics must be the starting Active and can no
longer trigger through a hand-to-Bench play.

The idealized **hand connector** searches exactly one remaining Basic from the
deck to hand. Each copy is usable once without an additional card-payment or
action cost. A **direct-Bench connector** is counted by a deliberately naive
baseline, but it cannot produce the required hand-origin trigger.

The player has a specified number of transactional Bench slots after other
core occupancy. With exactly one slot, a pickup Item must remove the first
support before the second support can enter. The model permits multiple
coin-flip pickup attempts in sequence. Each flips a fair independent coin,
and one success is enough. A certain pickup is deterministic. Both types are
assumed usable, properly timed, and in the visible hand by the deadline.

The model does **not** execute the support Abilities or imply that their
payloads are useful. A Dedenne-GX discard-and-draw can consume needed cards;
Crobat V's draw volume depends on hand size; Tapu Lele-GX's Supporter output
can be redundant or contested. The estimates are *mechanical upper bounds*
for such concrete lines, before those card-specific behaviors, costs, locks,
target eligibility, and opponent actions.

## Card and rule anchors

The local card pool supplies the relevant mechanical examples:

- Tapu Lele-GX `sm2-60` (Wonder Tag), Crobat V `swsh3-104` (Dark Asset),
  and Dedenne-GX `sm10-57` (Dedechange) require a **from-hand Bench play**.
- Quick Ball `swsh1-179` searches one Basic into hand and requires a
  discard; its cost is intentionally idealized away in the modeled connector.
- Super Scoop Up `bw1-103` flips a coin and, on heads, returns one of
  your Pokémon and attached cards to hand.
- Scoop Up Cyclone `bw10-95` returns one of your Pokémon and attached
  cards to hand deterministically, but consumes the ACE SPEC allowance.

The Advanced Player's Rulebook sections G, H, B-01, A-04, and E-06 ground
accepted opening, six Prize placement, Item timing, Bench capacity, and
the distinction between a played-from-hand trigger and direct placement.
The model assumes ordinary legal actions under no applicable lock.

## Exact method

Let the seven modeled categories be A, B, other ordinary Basics, hand
connectors, direct-Bench connectors, guaranteed pickups, and coin pickups;
all remaining cards are filler. The two support categories have one copy
each. Enumerate every grouped accepted opening and every grouped subsequent
uniform random draw.

Prize cards are placed **between** opening and later draws. Since the Prize
set and later draw are disjoint uniform samples, conditional on the observed
opening and later draw, the Prize set is uniform among the still-unseen
cards. Thus only zero, one, or two unseen target singletons need explicit
Prize indicators. If `m` required targets remain unseen among `U`
cards and `p` of those targets are Prized, the number of compatible
Prize sets is `C(U-m, P-p)`, where `P` is the Prize count.

This marginalization is exact and is only a computation shortcut. It does
not give the modeled player foreknowledge of Prize identities.

The structural tests are nested:

1. **Nominal:** either connector type counts as a reusable independent
   out for both supports; an available pickup is treated as guaranteed.
2. **Role-aware:** a support copy forced to be the starting Active stops
   counting as an available hand-origin trigger.
3. **Typed one-use:** direct-Bench search is disallowed for the trigger,
   and `k` missing targets require `k` distinct hand-connector uses.
4. **Stochastic exact:** with `r` visible Super Scoop Up copies and
   no deterministic pickup, release succeeds with probability
   `1 - 2^(-r)`. With two free slots, pickup is unnecessary.

Each probability is conditional on a valid ordinary-Basic opening. The
denominator accounts for the complete grouped opening, future draw, and
hidden Prize topology; integer weighting yields exact `Fraction` values.

## Exact illustrative 60-card result

Use one copy each of A/B, four other ordinary Basics, four hand
connectors, four direct-Bench connectors, **two coin pickups**, six Prizes,
and four idealized later uniform draws. The remaining 44 cards are filler.
The Bench contains four protected core occupants, leaving one transactional
slot. Conditional accepted-opening probability is 54.143608% before
conditioning; all figures below are conditional on its acceptance.

| Access model | Joint double-trigger probability |
| --- | ---: |
| Nominal independent access | **20.867773%** |
| Correct starting-Active role | **14.632453%** |
| Correct search zone and one-use capacity | **4.739994%** |
| Realized pickup coin outcomes | **2.454142%** |

The cumulative nominal-to-realized discrepancy is **18.413631 percentage
points**. Its sequential components are 6.235320 points of starting-Active
role error, 9.892460 points of connector/zone error, and 2.285852 points of
pickup-coin error. The result illustrates why separate marginal support-out
counts cannot be multiplied into a realistic double-activation estimate.

### Pickup-package sensitivity

Keep the same deck classes except swap the pickup package, replacing it with
filler as necessary:

| Pickup package, one free slot | Nominal | Typed one-use | Realized |
| --- | ---: | ---: | ---: |
| Two Super Scoop Up copies | 20.867773% | 4.739994% | **2.454142%** |
| Four Super Scoop Up copies | 35.815631% | 8.285937% | **4.590978%** |
| One Scoop Up Cyclone | 11.285335% | 2.538287% | **2.538287%** |
| No pickup, two free slots | 67.882806% | 17.081520% | **17.081520%** |

Four coin pickups outperform a single deterministic pickup *within this
access-only benchmark* because four copies are likelier to be observed.
That says nothing about the opportunity cost of slots, ACE SPEC competition,
or actual deck strength. The free-second-slot sensitivity shows that
capacity itself can dominate the value of additional cleanup outs.

## Verification

The independently written labeled oracle enumerates opening subsets, disjoint
Prize subsets, later single draws, physical starting-Active selection, and
both coin outcomes for a nine-card deck. It checks **8,880 weighted labeled
sequences** and agrees *exactly* with the grouped implementation:

- nominal: `121/740`;
- role-aware: `53/740`;
- typed one-use: `11/370`;
- realized: `11/740`.

Regression tests additionally check zero pickups, zero slack, deterministic
pickup, two free slots, and monotone nesting of the four measures. The
reproducer prints all benchmark percentages.

## Strategic interpretation and next step

The relevant resource is an **executable two-trigger schedule**. It needs
two physical support identities, hand-origin access for each, sufficient
independent connectors, a Bench slot for the first support, and a timely
successful release before the second.

For real decks, the next priority is to replace abstract connector access
with Quick Ball or Ultra Ball's discard cost and enforce ability-specific
hand mutations and once-per-turn restrictions. A stateful policy could then
choose trigger order and discard payments jointly with pickup sequencing.
