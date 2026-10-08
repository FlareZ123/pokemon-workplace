# Recovering a forced starting-Active hand-to-Bench support

## Question

A singleton support Basic such as Tapu Lele-GX must sometimes be the starting
Active Pokémon because the opening hand contains no other Basic. Earlier
[setup-role contention](../setup_trigger_role_contention/) and
[Bench-trigger access](../bench_trigger_access/) models classified that
opening copy as unavailable for a *from-hand Bench entry* trigger.

That is a useful **no-recovery baseline**. In real Expanded play, however,
a pickup effect can return the original Active support to hand once another
Pokémon is ready to become Active. How much probability can this restore,
and can a direct-to-Bench search Item unexpectedly contribute to the line?

- Exact combinatorial model:
  [bench_active_trigger_rescue.py](../../tools/bench_active_trigger_rescue.py)
- Independent labeled-state oracle:
  [reproduce.py](reproduce.py)

## Card text and precise line

The bundled card pool verifies:

- Tapu Lele-GX `sm2-60`, Wonder Tag: an Ability triggered by playing this
  Basic **from hand onto Bench**.
- Nest Ball `sm1-123`: searches a Basic directly from deck to **Bench**.
- Super Scoop Up `bw1-103`: flip a coin; on heads, return one of your
  Pokémon and all attached cards to hand.
- Scoop Up Cyclone `bw10-95`: deterministic return to hand, subject to
  the ACE SPEC rule.

The line in the modeled state is:

`A forced starting Active -> Bench another Basic O -> Super Scoop Up A
(heads) -> promote O -> play A from hand onto Bench -> trigger A.`

The backup Pokémon is essential. Scooping the only Pokémon in play would
leave the player with no Pokémon and is not a viable continuation.
The hand-to-Bench entry is performed only after the pickup; the earlier
starting-Active role did not itself trigger the Ability.

**A direct-to-Bench Item contributes indirectly.** Nest Ball cannot
activate A's hand-entry trigger by putting A straight onto the Bench.
It can put the alternative Basic O onto the Bench, enabling the pickup of
the Active A. This is a role-dependent use of the very connector class
previously excluded from direct trigger access.

## Exact state assumptions

The 60-card toy contains one singleton support A, a specified number of
ordinary Basic backups O, idealized deck-to-hand Basic search Items, direct
deck-to-Bench Items, fair coin pickup Items or a guaranteed pickup, and
filler. Opening seven-card hands are conditioned on containing at least
one ordinary Basic, including A. Six hidden Prize cards are set and one
additional random card is drawn.

If A starts Active because there was no O in the opening, its recovery
requires:

1. A later drawn O, **or** a hand/direct-Bench connector in hand while
   an unprized O remains searchable in deck;
2. at least one available pickup Item;
3. at least one successful pickup outcome.

With `r` visible coin pickup Items and no deterministic pickup,
conditional recovery succeeds with probability `1 - 2^(-r)`. If a
guaranteed pickup is present, recovery succeeds deterministically
once a backup is available. The combinatorial evaluator integrates
over accepted opening categories, disjoint draws, Prize membership of
the singleton, and the count of other Basics among the Prizes.

All search effects are treated as usable without Quick Ball discard
payments. The model does not consider lock effects, opposing turns,
Active retreat, manual Bench occupancy beyond the one backup, setup
exceptions, exact hand effects of the support Ability, or future Prize
rescue. Direct-Bench Items are assumed able to establish an unprized
ordinary Basic. The recovery percentage is an **increment to a restricted
access model**, rather than a claim about all real-game rescue options.

## Illustrative results

Four ideal hand connectors, four fair coin pickups, one later random
draw, and six Prizes. All figures are conditional on an accepted
ordinary-Basic opening.

| Other Basic copies | Direct-Bench Items | Original no-recovery access | With Active recovery | Recovery gain |
| ---: | ---: | ---: | ---: | ---: |
| 1 | 0 | 23.129876% | **26.700680%** | +3.570804 pp |
| 1 | 4 | 23.129876% | **28.975421%** | +5.845545 pp |
| 3 | 0 | 35.038269% | **37.024241%** | +1.985971 pp |
| 3 | 4 | 35.038269% | **38.174803%** | +3.136534 pp |
| 5 | 0 | 39.287815% | **40.580717%** | +1.292902 pp |
| 5 | 4 | 39.287815% | **41.260673%** | +1.972858 pp |
| 8 | 0 | 42.419825% | **43.227555%** | +0.807730 pp |
| 8 | 4 | 42.419825% | **43.596557%** | +1.176731 pp |

For the original **one A, three O, four hand connectors, four direct-Bench
connectors** scenario, adding four Super Scoop Up-like pickup copies raises
exact trigger access from **35.038269% to 38.174803%**, a 3.136534-point
improvement. The no-recovery baseline exactly matches the earlier
`bench_trigger_access` implementation.

The recovery increment shrinks as more ordinary Basic starters are added:
it becomes less common for the singleton A to be forced Active in the
first place. But at fixed other-Basic count, additional direct-Bench
search Items can improve recovery by providing a backup even though they
do not satisfy A's own hand-entry condition.

## Independent validation

A **10-card labeled deck** contains A, two O, one hand connector H,
one direct-Bench connector D, two coin pickups R and three fillers.
The independent oracle enumerates **8,925 accepted labeled
opening/Prize/draw states**, choosing a physical starting Active and
remaining searchable deck explicitly.

Exact values match:

- No-recovery access: `46/119`.
- With Active rescue: `379/850`.
- Improvement: `353/5950`.

The reproducer also crosschecks the no-recovery baseline against the
previous independent `bench_trigger_access` kernel for eight 60-card
settings, asserts zero rescue without any pickup or any alternative
Basic, and tests the incremental contribution of direct-Bench Items.

## Strategic implications

An opening support card forced Active creates **temporary role debt**.
The debt can sometimes be repaid through an additional Bench occupant,
pickup resource, and successful timing sequence. An access model that
labels that support irretrievably consumed by setup can undercount
recovery opportunities.

The same Item can be irrelevant to the **direct** target trigger yet
valuable to the **rescue prerequisite**. This illustrates why access
edges should be evaluated against the full required transition sequence.

Next useful work should combine Active rescue with actual Quick Ball
payment and the previously developed two-support adaptive sequence
planner, including the Bench-resident backup and the physical
promotion requirement.
