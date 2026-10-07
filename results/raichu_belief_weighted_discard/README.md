# Harto Miki Raichu/Electrode: belief-weighted discard safety before K1

## Question

Can the same mechanically legal Quick Ball discard have different continuation value solely because Alolan Raichu's Prize status is still unknown?

Yes.

This result composes the repository's belief-weighted discard framework with the physical Harto Raichu execution layers.

Regression: `results/raichu_belief_weighted_discard/reproduce.py`

## Representative K0 state

The current seven-card hand contains:

- Quick Ball;
- three ordinary discard candidates A, B, and C;
- Gladion;
- two neutral cards.

Crobat V is in deck. Alolan Raichu has not appeared among the eight cards already observed across the opening hand and one later ordinary draw.

The exact binary target-zone posterior for this representative snapshot is therefore:

- Alolan Raichu in deck: **46/52 = 88.461538%**;
- Alolan Raichu Prized: **6/52 = 11.538462%**.

The physical executor uses one canonical Prize slot to represent each binary world. The 46/52 and 6/52 masses are the full six-Prize posterior weights; the one-slot physical topology is only a compact execution representative.

## Two zone-dependent continuations

Every candidate is mechanically legal to discard for Quick Ball.

After Quick Ball searches Crobat V and Crobat enters the Bench:

1. **Target in deck:** Dark Asset's exact one-card witness draws Alolan Raichu directly. Gladion is unnecessary for this narrow endpoint.
2. **Target Prized:** the line preserves Gladion and resolves its literal Prize exchange to move Alolan Raichu into hand. If Quick Ball discarded Gladion, this continuation is gone.

Both branches use the repository's conserved physical state transitions. The Prized branch additionally consumes the ordinary Supporter window and performs Gladion's literal Prize-to-hand / Gladion-to-Prize movement.

## Exact belief-weighted safety

| Quick Ball discard | Probability the Alolan Raichu endpoint remains reachable |
| --- | ---: |
| A | 100.000000% |
| B | 100.000000% |
| C | 100.000000% |
| Gladion | **88.461538%** |

The 11.538462-point safety deficit for discarding Gladion is exactly the posterior mass where Alolan Raichu is Prized.

This is a concrete K0 form of state-dependent DCI:

`mechanically discardable != safe in every hidden Prize world`

## K0 versus K1 discard ranking

To make the policy consequence explicit, the regression assigns illustrative local discard-desirability scores:

| Card | Illustrative DCI |
| --- | ---: |
| A | 0.6 |
| B | 0.9 |
| C | 0.7 |
| Gladion | 1.0 |

Under K0, if preserving the Alolan Raichu endpoint is treated as a hard constraint, Gladion is excluded because its safety is below 1. The highest-DCI robust choice is **B at 0.9**.

Under exact K1:

- if Raichu is in deck, all four discards are safe and Gladion becomes the highest-DCI choice;
- if Raichu is Prized, Gladion is protected and B remains the highest-DCI safe choice.

The expected DCI of the K1-safe choice is **0.988462**, an **+0.088462** gain over the K0 robust choice while preserving endpoint success in every world.

The number is illustrative because the DCI inputs are illustrative. The structural result is not: information changes the feasible discard set before it changes the ranking inside that set.

## Why this matters

A scalar DCI attached to Gladion before deck inspection cannot represent this decision correctly.

The relevant object is closer to:

`discard witness -> hidden Prize world -> executable continuation -> endpoint -> ranking`

Before K1, the player must account for both worlds. After exact deck/Prize information arrives, the target-in-deck world releases Gladion for other uses while the target-Prized world continues to protect it.

This connects three repository themes in one deck-level witness:

- DCI is state-dependent;
- K0/K1 information changes action value;
- access claims should be evaluated through executable continuations.

## Validation

The regression checks every exact one-card Quick Ball discard in both physical worlds.

For the target-in-deck world it executes:

`Quick Ball -> Crobat V -> Dark Asset exact hit: Alolan Raichu`

For the target-Prized world it executes:

`Quick Ball -> Crobat V -> Gladion -> Alolan Raichu`

It then feeds those world-specific outcomes through `belief_weighted_discard_policy.py` and confirms the exact posterior-weighted safety values above.

## Limits

This is a binary target-zone decision model, not a full-turn optimizer.

It intentionally does not model:

- all six physical Prize identities simultaneously;
- the second Gladion copy in Harto's full list;
- alternative Computer Search, Forest Seal Stone, Ultra Ball, or ordinary Prize-taking lines;
- the option value of using Computer Search before Quick Ball;
- matchup-specific future value of Gladion;
- competing Bench, Supporter, or VSTAR objectives.

Those omissions make the 11.538462% figure a property of this representative decision snapshot, not a deck-wide failure rate.

## Next useful work

The next extension should replace the binary endpoint with multiple simultaneous objectives and the actual two-Gladion package.

A useful exact model would let the second Gladion be in deck, hand, or Prizes, then ask when discarding the visible Gladion remains safe because another rescue path survives. That would connect belief-weighted discardability to multi-Prize collapse and redundant rescue topology.
