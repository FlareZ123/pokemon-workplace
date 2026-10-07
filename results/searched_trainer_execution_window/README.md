# Searched Trainer acquisition can consume its own execution window

## Question

When a deck-search connector successfully puts a Trainer card into hand, does that mean the searched Trainer can still be used in the required turn window?

No.

This result composes the repository's typed search allocator, exact Trainer transaction, turn-action budget, and play-lock channels. It adds a small reusable bridge, `tools/acquired_trainer_action_window.py`, that checks whether an already acquired Trainer still has the generic hand/action window required by its subtype.

Regression: `results/searched_trainer_execution_window/reproduce.py`

## Representation

The search stack already distinguishes:

- a physical target being searchable;
- the target moving from deck to hand;
- the search connector's own discard and action costs.

The new bridge adds the next state boundary.

For an acquired Trainer it records:

- copies in hand;
- whether its Item, Tool, Supporter, or Stadium play channel is open;
- remaining turn quota where the subtype has one;
- whether the generic action window is currently available.

`window_available` is only a necessary execution prerequisite. Card-specific conditions remain downstream. For example, a Stadium can still fail a same-name restriction and a Pokémon Tool can still lack a legal attachment target.

## Rosa searching Boss's Orders

Rosa is a Supporter whose compiled broad Trainer output can retrieve a Supporter target.

The existing static typed connector layer correctly reports the Supporter acquisition demand as feasible when one Supporter play remains.

Executing Rosa changes the state:

1. Rosa leaves hand for the resolving zone.
2. The searched Supporter moves from deck to hand.
3. Rosa goes to the discard pile.
4. The ordinary one-Supporter quota is consumed.

The searched Supporter is physically in hand, but its remaining same-turn Supporter quota is zero.

Validated state:

| Quantity | Result |
| --- | ---: |
| Static typed acquisition feasible | yes |
| Boss's Orders reaches hand | yes |
| Same-turn Supporter window after Rosa | no |
| Next-turn Supporter window if the card is retained | yes |

This is a concrete false positive if an acquisition output vector is interpreted as an executed-effect vector.

## Extra Supporter quota restores execution

The same Rosa transaction is rerun with a Supporter limit of two.

After Rosa resolves:

- one Supporter use has been consumed;
- one remains;
- Boss's Orders is in hand;
- the generic Supporter action window is available.

The physical search route did not change. Only the action-budget state changed.

This matches the broader Expanded requirement to represent quota-modifying effects separately from search access.

## Cross-class payloads behave differently

Rosa can also use its broad Trainer output to retrieve an Item target.

Rosa still consumes the Supporter quota, but it does not consume the Item play channel.

The regression therefore finds:

- searched Item reaches hand;
- same-turn Item action window remains available.

The execution penalty is typed. A search connector consuming one action class does not automatically delay every payload it can retrieve.

## Secret Box searching the same Supporter

Secret Box is an Item.

In the regression it pays its exact three-card discard cost and retrieves the same Supporter target.

After Secret Box resolves:

- the searched Supporter is in hand;
- the ordinary Supporter quota remains at one;
- the generic same-turn Supporter window is available.

So two connectors with access to the same target class have different executable value:

| Connector | Payload acquired | Same-turn Supporter window |
| --- | ---: | ---: |
| Rosa | yes | no |
| Secret Box | yes | yes |

This is connector domination induced by the downstream execution channel.

## Lock state separates acquisition from execution again

A final regression applies Supporter lock while leaving Item play open.

Secret Box still resolves and moves the Supporter target into hand because the search action itself is an Item.

The searched Supporter's action window is closed by the Supporter lock.

This gives another state where acquisition succeeds and execution fails, for a different reason than quota contention.

## Methodological implication

A connector output needs a declared semantic endpoint.

At minimum, planners should distinguish:

`searchable -> acquired -> window-feasible -> executed`

The typed connector allocator is correct when its demand means acquisition. It becomes overly optimistic only if a downstream model silently treats that acquisition as completed execution.

For ALS and same-turn optimization, the state therefore needs both:

- the acquired card and its zone;
- the remaining action window required to use that card.

This is especially important for broad Trainer search, Prize recovery, and chained connector lines where the access action and payload can compete for the same Supporter or Stadium quota.

## Evidence type and limits

The result is a deterministic transition-model finding grounded in the bundled card compiler and rules-backed action-budget implementation.

It does not execute Boss's Orders' gust effect, validate a legal gust target, attach Pokémon Tools, or resolve Stadium same-name restrictions. The new bridge intentionally stops at generic action-window availability.

The regression also assumes the searched payload remains in hand across the modeled next-turn projection.

## Next useful work

A stronger planner should attach an execution requirement to each strategic demand and carry it through target acquisition.

That would let one objective mean "Boss's Orders is in hand" while another means "a gust Supporter effect has been executed by this deadline," preventing the two from sharing the same completion predicate.
