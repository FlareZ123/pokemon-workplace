# Harto Miki Raichu/Electrode: one-draw connector race for the backup Gladion

## Question

After Quick Ball reveals that Alolan Raichu is Prized and the visible Gladion has already been discarded, how much same-turn backup access comes from a one-card Dark Asset exposure when Computer Search and Forest Seal Stone are also still hidden?

The event union is small enough to compute exactly.

Implementation: `tools/raichu_backup_connector_race.py`  
Regression: `results/raichu_backup_connector_race/reproduce.py`

## Conditioning

The state continues the prior timing analysis:

- Quick Ball successfully searched Crobat V;
- the search established that Alolan Raichu is Prized;
- the visible Gladion was already discarded as the pre-inspection payment;
- 50 card identities remain unresolved;
- 5 unresolved positions are remaining Prizes;
- 45 unresolved positions are the shuffled post-search deck;
- backup Gladion, Computer Search, and Forest Seal Stone are three distinct unresolved singleton identities;
- none of those three is already exposed in the current hand.

Dark Asset draws exactly one card, the first of the 45 deck positions.

## Exact event decomposition

The direct event is simple:

`Dark Asset draws backup Gladion`

Its probability is **1/50 = 2.000000%**.

For a drawn Computer Search to rescue the backup:

1. Computer Search must occupy the exposed top-deck position;
2. the backup Gladion must occupy one of the other 44 deck positions;
3. Computer Search's residual two-card payment gate must be live.

With the gate live, that contribution is:

`(1/50) * (44/49) = 1.795918%`.

Forest Seal Stone has the same positional probability when its physical Tool/VSTAR/Ability gates are live:

**1.795918%**.

The three top-card identities are mutually exclusive, so these contributions form an exact disjoint union.

## Main result

| Live connector gates after the search | Same-turn backup access |
| --- | ---: |
| none | 2.000000% |
| Computer Search only | 3.795918% |
| Forest Seal Stone only | 3.795918% |
| both | **5.591837%** |

The post-search topology ceiling remains **90%**, because the backup Gladion is outside the five remaining Prize slots in 45 of the 50 unresolved locations.

Even with both connector gates live, **84.408163 percentage points** of that topology mass remains inaccessible through this one-card Dark Asset window.

## Why connector marginals are below 2%

A connector draw is only useful when the backup is also in deck.

Once Computer Search occupies the one exposed deck position, only 44 other deck positions remain among 49 possible locations for the backup.

The same applies to Forest Seal Stone.

This is a small correlation correction that an independent-out approximation would miss.

## Mechanical grounding

The connector gates are supplied from already validated physical work.

Computer Search's route has an exact two-card residual discard payment and preserves the Supporter window for Gladion.

Forest Seal Stone's physical route requires a legal Tool attachment to Crobat V, an effective Tool, enabled Abilities, an unused VSTAR Power, and the backup Gladion remaining in deck. It also preserves the Supporter window.

This result deliberately treats those gate states as exogenous booleans. It integrates hidden card placement exactly while leaving board/payment feasibility to the physical executors.

## Independent validation

The reproducer exhaustively assigns distinct positions to backup Gladion, Computer Search, and Forest Seal Stone across all 50 unresolved positions.

It then checks the top-deck exposure and deck-presence conditions directly for all four connector-gate combinations.

The enumerator matches the analytic probabilities to floating-point precision.

## Interpretation

The result exposes three separate reasons that apparent redundancy can fail:

- the backup copy can be Prized;
- the backup can be in deck but not exposed before the deadline;
- a drawn deterministic connector can still fail its own physical gate.

The exact connector union remains far below the 90% topology ceiling because this conditioned Dark Asset window exposes only one random card.

## Limits

This result does not include connectors that are already in hand before Dark Asset.

It also omits Ultra Ball, VS Seeker, Dedenne-GX, Squawkabilly ex, repeated draw effects, Forest Seal Stone already attached, ordinary Prize-taking, and any strategic reason to reserve Computer Search or the VSTAR Power.

The Computer Search and Forest Seal booleans represent mechanical readiness after their draw. Their real probabilities are state-dependent.

## Next useful work

The highest-value extension is to reconnect this conditioned race to the full Harto state distribution.

A state enumerator should carry the five-card post-Quick-Ball hand, exact residual discard identities, Forest Seal Stone exposure, Tool/VSTAR gates, and the shuffled post-search deck together. That would measure the actual conditional rescue probability rather than the current clean boundary cases.
