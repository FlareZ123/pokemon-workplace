# Payment-substitution slack: when a connector should become discard fodder

## Question

How does discard pressure change when a stronger connector can use a weaker connector as payment?

This result generalizes the Harto Raichu connector-order finding and links it to `discard_information_slack/`.

Implementation: `tools/payment_substitution_slack.py`  
Regression: `results/payment_substitution_slack/reproduce.py`

## Model

Let:

- `A` be a weaker connector with discard cost `a`;
- `B` be a stronger connector with discard cost `b > 0`;
- `B` directly satisfy the local endpoint;
- `A` be a legal payment card for `B`;
- `s` be the number of external cards that are always safe to discard for this local endpoint.

Ignore new card inflow between actions for the moment.

If the line plays `A` and later needs `B`, the two payments require `a + b` cards from the external payment pool.

The minimum number of strategically critical cards forced into those payments is therefore:

`q(A -> B) = max(0, a + b - s)`

If `B` moves first and discards `A` as one of its own payments, then `A` itself contributes one safe payment card:

`q(B first) = max(0, b - s - 1)`

The number of external safe cards required to preserve every critical card shifts from:

- `a + b` for `A -> B`;
- `b - 1` for `B first`.

So the preservation threshold falls by exactly:

`a + 1`

cards.

## Harto Quick Ball -> Ultra Ball / Computer Search

For the Harto branch:

- Quick Ball has one-card discard cost: `a = 1`;
- Ultra Ball / Computer Search has two-card discard cost: `b = 2`.

The deterministic pre-draw payment pressure is:

| External safe disposables `s` | Quick Ball first: forced critical cards | Stronger connector first: forced critical cards |
| ---: | ---: | ---: |
| 0 | 3 | 1 |
| 1 | 2 | **0** |
| 2 | 1 | **0** |
| 3 | 0 | 0 |
| 4 | 0 | 0 |

The branch definition already guarantees at least one conservative disposable.

That means the stronger-first line has zero critical-payment pressure throughout the branch: discard Quick Ball plus one disposable.

Quick-Ball-first only reaches zero pre-draw critical pressure at three external disposables.

This exactly explains the visible thresholds in the validated K0 rule:

- at three or more disposables, Quick Ball can spend one disposable and still leave two for the later connector;
- at two disposables, spending Gladion on Quick Ball preserves both disposables for the later two-card cost;
- at one disposable, the deterministic two-connector payment chain is short of material and must rely on another route or later card inflow.

## Relationship to the exact Harto decomposition

The closed-form slack model predicts where ordering should matter.

The exact hidden-world result in `raichu_connector_order_decomposition/` confirms the prediction:

- when Quick-Ball-first chooses a disposable and Crobat V is available, the direct-first ordering gain is exactly zero;
- **91.857172%** of the full ordering gain appears in worlds where the Quick Ball policy chose Gladion instead;
- the remaining gain comes from bypassing Crobat-search failure.

The formula is therefore a structural explanation for the exact simulation result rather than a replacement for it.

## General interpretation

Discardability is endogenous to the selected action sequence.

A search card can have high strategic value as the current connector and high discardability as soon as another visible connector subsumes its local job.

This suggests a refinement to DCI-like models:

`discard value = f(state, endpoint, chosen action order)`

rather than only `f(card, state)`.

It also sharpens connector domination. The opportunity cost of choosing a connector includes the fact that playing it removes a potentially valuable payment card from the hand.

## Connection to discard-information slack

The earlier `discard_information_slack/` result uses:

`q = max(0, d - s)`

for one discard-before-search payment.

Payment substitution changes the effective safe-card count before that formula is applied.

When `B` can consume `A`, the weaker connector contributes one unit of safe payment capacity. When `A` is played first, that unit disappears and `A` may also consume additional safe cards through its own cost.

So information value, DCI, and connector order are coupled through the same slack variable.

## Limits

The theorem is a deterministic payment-skeleton result.

It assumes:

- `B` directly satisfies the local endpoint;
- `A` is expendable once `B` is selected;
- `A` is legally discardable to `B`;
- no new cards arrive between the two modeled payments;
- every external safe card is interchangeable for payment;
- future utility of discarded cards is outside the local endpoint.

Real sequences may add draw, search outputs, discard-pile utility, lock interactions, or future option value. Those effects require the fuller state model.

## Next useful work

A reusable planner should enumerate payment substitutions explicitly.

For each candidate action, it should ask whether another visible connector becomes dominated for the current endpoint and can therefore enter the payment pool. This can lower the action's effective DCI cost before any hidden-state search is performed.
