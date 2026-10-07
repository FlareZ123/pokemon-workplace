# Endpoint-sensitive connector policy: acquisition ties can hide execution losses

## Question

If two connectors can both acquire the same required Supporter, can an acquisition-only policy choose the wrong connector for a same-turn objective?

Yes.

This result puts Green's Exploration x4 and Computer Search x1 in the same legal deck model and measures states where either connector can retrieve a singleton Boss's Orders.

Implementation: `tools/mixed_payload_connector_policy.py`  
Regression: `results/mixed_payload_connector_policy/reproduce.py`

## Why the connector choice matters

Green's Exploration is itself a Supporter. When its no-Ability play condition is satisfied, it can search the required Boss's Orders, but the ordinary Supporter window is then spent.

Computer Search is an Item. When its two-card discard gate is payable, it can search the same Boss's Orders and leave the Supporter window available.

An acquisition-only objective treats both successful routes as equivalent because both end with Boss's Orders in hand.

A same-turn execution objective distinguishes them.

## Exact model

The baseline contains:

- 12 ordinary starters;
- one Boss's Orders;
- four Green's Exploration;
- one Computer Search;
- a dedicated discard-fodder pool;
- filler.

The seven-card opening hand is conditioned on containing at least one starter. Six Prize cards are sampled from the remaining deck.

The model compares:

- any-route acquisition;
- execution-aware policy, which uses Computer Search whenever its route can complete the same-turn Supporter objective;
- Green-priority acquisition policy, which chooses Green whenever Green is available;
- the probability mass where both connector routes are available and the choice changes same-turn execution.

The next-turn endpoint assumes the acquired Supporter is retained and receives a fresh ordinary Supporter window.

## Results

| Dedicated fodder | Any acquisition | Optimal same-turn execution | Green-priority same-turn execution | Decision-sensitive overlap |
| ---: | ---: | ---: | ---: | ---: |
| 10 | 43.076797% | 13.088028% | 12.563319% | 0.524709% |
| 20 | 45.542303% | 16.612511% | 15.028825% | 1.583686% |
| 35 | 47.209160% | 19.447175% | 16.695682% | 2.751493% |

For each row:

`optimal same-turn execution - Green-priority same-turn execution = decision-sensitive overlap`

exactly.

The overlap grows as the discard gate becomes easier to pay because more hands simultaneously support both routes.

## Deadline reversal

For a next-turn execution objective, either connector can acquire Boss's Orders now and the ordinary Supporter quota refreshes before use.

Under the stated retention assumption, next-turn execution probability therefore equals any-route acquisition:

- 43.076797% with 10 dedicated fodder;
- 45.542303% with 20;
- 47.209160% with 35.

The same overlap states that require Computer Search for current-turn execution become acquisition-equivalent for the later deadline.

## Interpretation

Connector domination depends on the completion endpoint and deadline.

In overlap states:

- Green is sufficient for acquisition;
- Computer Search is required for same-turn execution under the ordinary Supporter quota;
- either route is sufficient for next-turn execution if the payload survives in hand.

A planner that stops evaluating a line when the target enters hand can therefore choose a route that destroys the tactical action window the target was meant to use.

This is a policy-level version of the staged endpoint:

`searchable -> acquired -> schedulable -> executed`.

## Validation

The grouped hypergeometric calculation is independently reproduced by exhaustive labeled opening-hand and Prize enumeration in a small deck.

The regression verifies bundled text for Green's Exploration `sm10-175`, Computer Search `bw7-137`, and Boss's Orders `swsh2-154`.

## Limits

Green's Exploration is conditioned on its printed no-Ability play condition being satisfied.

Only dedicated fodder can pay Computer Search in the model. Other potentially disposable cards are protected.

The current-turn policy isolates one required Supporter payload. It does not value Green's second Trainer output, Computer Search's unrestricted target flexibility, alternative actions, later random draws, hand disruption, or the strategic value of cards discarded as payment.

## Next useful work

The next step is a multi-objective policy where connector actions can acquire several payloads and each payload has its own completion stage and deadline.

That layer should preserve the decision-sensitive overlap mass as option value rather than treating all acquisition-success states as interchangeable.
