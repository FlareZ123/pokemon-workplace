# Search acquisition and same-turn execution can reverse connector rankings

## Question

Can a connector be much better at putting a required Supporter into hand while being worse at completing a same-turn Supporter objective?

Yes.

This result adds an exact opening/Prize model for one singleton Trainer payload.

Implementation: `tools/singleton_payload_execution_probability.py`  
Regression: `results/search_payload_execution_probability/reproduce.py`

## Model

The 60-card baseline contains:

- 12 ordinary starter Pokémon;
- one required Supporter payload, represented by Boss's Orders;
- a connector package;
- a dedicated pool of cards considered acceptable discard payment;
- filler.

The opening hand has seven cards and is conditioned on containing at least one starter. Six Prize cards are then sampled from the remaining 53 cards.

A successful search route requires:

1. the payload is absent from the opening hand;
2. at least one connector copy is in hand;
3. the represented discard cost is payable from the dedicated fodder pool;
4. the singleton payload avoids the Prize cards and therefore remains in deck.

The model reports two endpoints:

- **acquisition**: the payload is in hand by the end of the connector line;
- **same-turn execution**: the payload is in hand and its required action window remains available.

The discard model is deliberately conservative. Only the dedicated fodder category is allowed to pay the connector cost.

## Concrete connector variants

Three separate deck variants are compared.

### Green's Exploration x4

Green's Exploration is a Supporter and, when its printed no-Ability play condition is met, searches for up to two Trainer cards.

For this narrow objective, four copies create strong access to Boss's Orders.

Under the ordinary one-Supporter turn, using Green consumes the same Supporter window required to play Boss's Orders afterward.

The connector therefore adds acquisition probability while adding zero same-turn execution probability.

### Computer Search x1

Computer Search is an ACE SPEC Item. It discards two cards and searches for any card.

When the dedicated two-card payment is available, it can retrieve Boss's Orders while preserving the Supporter window.

### Secret Box x1

Secret Box is an ACE SPEC Item. It discards three other cards and can retrieve a Supporter among its four typed outputs.

For this single-payload objective, its higher discard threshold makes it less available than Computer Search under the dedicated-fodder abstraction.

It still preserves the Supporter window after a successful search.

Computer Search and Secret Box are alternative ACE SPEC deck variants. The result does not put both in one legal deck.

## Exact baseline results

The probability that the singleton Boss's Orders is already in the valid opening hand is **10.979633%**.

Four Green's Exploration copies raise hand acquisition to **41.493111%** in every represented fodder regime. Under the ordinary one-Supporter limit, same-turn Boss's Orders execution remains **10.979633%**, exactly the direct-hand baseline.

The Item connectors behave differently:

| Dedicated fodder | Connector | Acquisition | Same-turn execution |
| ---: | --- | ---: | ---: |
| 10 | Computer Search x1 | 13.088028% | 13.088028% |
| 10 | Secret Box x1 | 11.355915% | 11.355915% |
| 20 | Computer Search x1 | 16.612511% | 16.612511% |
| 20 | Secret Box x1 | 13.439479% | 13.439479% |
| 35 | Computer Search x1 | 19.447175% | 19.447175% |
| 35 | Secret Box x1 | 18.008127% | 18.008127% |

This produces a ranking reversal.

For acquisition:

`Green x4 > Computer Search x1 > Secret Box x1`.

For the same-turn Supporter objective:

`Computer Search x1 > Secret Box x1 > Green x4`.

The reversal occurs even though Green has far more raw search access.

## Extra Supporter quota

A second Green projection treats the connector as preserving a payload Supporter window, corresponding to a state with another Supporter use available after Green.

In that state, Green's same-turn execution probability rises to its full **41.493111%** acquisition probability.

The card list and Prize distribution are unchanged. Action quota alone changes which access converts into executable success.

## Validation

The exact grouped calculation is independently checked against exhaustive labeled opening-hand and Prize enumeration in a small deck.

The regression also verifies bundled card text for:

- Green's Exploration `sm10-175`;
- Computer Search `bw7-137`;
- Secret Box `sv6-163`;
- Boss's Orders `swsh2-154`.

It verifies the bundled rulebook statements that Items can ordinarily be played any number of times during a turn and Supporters ordinarily only once.

## Interpretation

Connector ranking depends on the completion endpoint.

A search engine optimizing “required Supporter reaches hand” strongly favors Green in this example.

A planner optimizing “required Supporter effect executes this turn” favors the lower-access Item routes because their successful searches preserve the relevant action channel.

This is a probabilistic instance of connector domination after acquisition.

It also shows why deck optimization should avoid assigning one scalar value to search access without specifying the deadline and execution requirement of the payload.

## Limits

The Green result is conditional on its printed no-Ability play condition being satisfied.

The model only considers a singleton required Supporter, current opening-hand connector access, six random Prizes, and dedicated discard fodder. It omits later draws, secondary search for the connector itself, alternative discard candidates, side payload value, hand disruption, and competing actions.

Secret Box's Item, Tool, and Stadium side outputs are intentionally ignored because the experiment isolates one required Supporter endpoint.

## Next useful work

The natural next step is to let one deck state contain several connector types and several payload objectives, then optimize jointly over:

- which connector to spend;
- which payloads to acquire;
- which action windows to reserve;
- which objectives have current-turn or later deadlines.

That would unify pre-acquisition connector contention with post-acquisition execution contention in one policy problem.
