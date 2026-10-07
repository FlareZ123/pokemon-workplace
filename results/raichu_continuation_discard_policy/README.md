# Harto Miki Raichu/Electrode: continuation-aware discard policy

## Question

Can the repository's continuation-aware discard framework distinguish between a card that is mechanically legal to discard now and a card whose discard destroys a later strategic endpoint, while executing the real Raichu Prize-rescue continuation?

Yes.

Regression: `results/raichu_continuation_discard_policy/reproduce.py`

It composes:

- `continuation_discard_policy.py`;
- the full physical Prized-target Raichu rescue chain;
- exact Quick Ball and Computer Search discard witnesses;
- literal Gladion Prize cycling;
- a final hand requirement representing another future resource that must survive.

## Witness

The seven-card hand contains:

- Quick Ball;
- three ordinary discard candidates: A, B, and C;
- one `future_piece`;
- two neutral cards.

All four candidate classes are mechanically legal choices for Quick Ball's one-card discard cost.

The modeled line then requires:

`Quick Ball -> Crobat V -> Dark Asset: Computer Search -> Computer Search: Gladion -> Gladion: Alolan Raichu`

Computer Search may spend two of A, B, and C.

The endpoint requires `future_piece` still to be in hand after the complete rescue line.

## Mechanical layer

Before considering continuation value, Quick Ball has four exact legal discard witnesses:

- discard A;
- discard B;
- discard C;
- discard `future_piece`.

This is the correct mechanical set.

A legality engine should not remove `future_piece` merely because a higher-level strategy currently values it.

## Continuation filter

Each exact Quick Ball discard witness is then executed through the entire physical rescue line.

Discarding A, B, or C leaves the other two ordinary candidates available for Computer Search and preserves `future_piece`.

Discarding `future_piece` still allows the Raichu rescue line itself to execute, but the final joint endpoint fails because the required future resource is gone.

The continuation-aware policy therefore retains exactly three Quick Ball witnesses and removes the `future_piece` witness.

This is a concrete deck-level example of the distinction:

`mechanically discardable != strategically continuation-safe`

## DCI ranking after feasibility

The regression then assigns illustrative discard desirability scores:

| Card | DCI-style discard desirability |
| --- | ---: |
| A | 0.6 |
| B | 0.9 |
| C | 0.7 |
| future_piece | 1.0 |

If the scalar score were used before continuation filtering, `future_piece` would appear to be the best discard.

The framework instead removes the endpoint-destroying witness first.

Among the three continuation-safe choices, B has the highest score and is selected as the top-ranked discard.

This gives the human-developed DCI idea a precise role inside the stronger representation:

`mechanical witnesses -> continuation feasibility -> DCI ranking -> exact execution`

## Why this matters for the Raichu line

The preceding probability models used a binary conservative disposable pool.

This result shows what a richer policy can do without changing the physical executor.

A card can be legal to pay Quick Ball, and even have a high local discard preference, while still being protected by a separate future requirement.

The future requirement does not need to be Raichu itself. It could represent another combo piece, Energy requirement, lock answer, or matchup-specific resource.

The same mechanism therefore generalizes beyond the particular witness.

## Relation to residual payment

The line also preserves the second-order payment structure.

If Quick Ball spends one ordinary candidate, two ordinary candidates remain for the later Computer Search cost.

The continuation filter therefore reasons over both:

- what the first payment destroys;
- whether later payment remains possible.

This is stronger than a scalar count of disposable cards because the identity of the first discarded class matters to the endpoint.

## Validation

CI executes every candidate Quick Ball witness through the same full physical rescue chain used by `raichu_full_prized_rescue_execution/`.

The regression asserts:

- four mechanical Quick Ball options exist in the constructed hand;
- exactly three are continuation-safe;
- `future_piece` is mechanically legal but absent from the safe set;
- the final safe ranking chooses B at score 0.9;
- every retained witness reaches the full Raichu rescue endpoint and preserves `future_piece`.

## Limits

The DCI scores are illustrative inputs rather than learned estimates.

The endpoint contains one extra retained hand card. Real games can have several interacting requirements, graded future values, recovery routes, matchup dependence, and uncertainty about which endpoint will matter.

The current generic continuation policy supports arbitrary validated continuations, so those richer questions can be added without changing its mechanical discard witness layer.

## Next useful work

The strongest deck-specific extension is belief-weighted continuation safety.

Before K1, the player may not know whether a singleton is Prized. A Quick Ball discard can therefore be safe in some Prize worlds and destructive in others.

Combining the current full rescue continuation with `belief_weighted_discard_policy.py` would assign each exact discard witness a probability of preserving the endpoint under K0 uncertainty, then allow DCI ranking to operate on that risk-aware feasible set.
