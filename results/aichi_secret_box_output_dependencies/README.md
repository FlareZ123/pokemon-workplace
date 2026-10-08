# Aichi Secret Box output-category dependency

## Question

Secret Box can search one Item, one Pokémon Tool, one Supporter, and one
Stadium.

How many of those four output categories are actually required to create the
first-turn core gains measured by the Aichi Vileplume Secret Box experiment?

This audit replays the same paired states and selectively enables every one of
the 16 possible Secret Box output-category subsets.

Implementation:

- `tools/aichi_secret_box_output_dependencies.py`
- `results/aichi_secret_box_output_dependencies/reproduce.py`
- `results/aichi_secret_box_output_dependencies/reproduce_full.py`

The original planner was parameterized with an output mask. Its default remains
all four outputs, and the established 500,000-state Secret Box regression still
passes unchanged.

## Full paired result

Seed: `20261007`.

The full 500,000 accepted-opening sample reproduces:

- Grand Tree baseline successes: 353,262;
- full Secret Box successes: 374,047;
- Secret-Box-only incremental successes: 20,785.

For every incremental state, the audit asks which restricted Secret Box output
sets can still reach:

`Bunnelby in play + TM: Evolution + Jet Energy in hand`

before the first-turn attack sequence.

## Finding 1: every incremental win has a one-category witness

The minimum number of enabled Secret Box output categories needed per
incremental state is:

| Minimum categories | States | Share |
| ---: | ---: | ---: |
| 1 | 20,785 | 100.000000% |
| 2 | 0 | 0% |
| 3 | 0 | 0% |
| 4 | 0 | 0% |

The four printed Secret Box categories are never jointly required for this
endpoint in the sampled incremental states.

This does not mean the other outputs have no value. It means that at least one
single category can start a downstream route that completes the core.

## Finding 2: the Item output is almost universal because it finds Tag Call

Singleton-category success among the 20,785 incremental states is:

| Enabled Secret Box category only | States retained | Share |
| --- | ---: | ---: |
| Item | 20,783 | 99.990378% |
| Supporter | 20,703 | 99.605485% |
| Tool | 2,313 | 11.128217% |
| Stadium | 623 | 2.997354% |

The Item output obtains Tag Call.

Tag Call can then obtain Guzma & Hala.

Guzma & Hala supplies the Tool and Special Energy axes and can also obtain
Artazon for Basic access.

So one immediate Secret Box output can fan out through downstream connectors.

## Finding 3: the two Item-only failures are four-Tag-Call Prize collapse

There are exactly two incremental states where Item output alone fails.

In both states, the raw remaining deck contains zero Tag Call.

The established paired experiment also shows that no incremental state starts
with Guzma & Hala or Tag Call in hand.

Because the list has four Tag Call copies, those two states have all four Tag
Call copies in the Prize cards.

Direct Supporter output remains available there and provides the one-category
rescue.

This is also why Supporter is the only category that is indispensable under a
full-output ablation in any state:

| Category removed from full Secret Box | States that fail |
| --- | ---: |
| Item | 0 |
| Tool | 0 |
| Supporter | 2 |
| Stadium | 0 |

The two failures are the same all-Tag-Call-Prized states.

## Finding 4: direct Supporter search has a different failure mode

Supporter-only Secret Box fails in 82 of the 20,785 incremental states.

The number of Guzma & Hala copies remaining in the raw deck for those failures
is:

| Searchable Guzma & Hala copies | Failure states |
| ---: | ---: |
| 0 | 0 |
| 1 | 0 |
| 2 | 5 |
| 3 | 24 |
| 4 | 53 |

So these are not Guzma & Hala Prize-depletion failures.

The direct Supporter route can acquire Guzma & Hala, while still failing the
later line because it does not receive the same intermediate hand material and
routing options as the Item -> Tag Call route.

This matches the temporal resource result in
`results/composed_connector_fanout/`: Tag Call can contribute a second TAG
TEAM card that becomes later payment material before Guzma & Hala's optional
two-card discard.

## Finding 5: most states have two independent one-category routes

Count the number of singleton categories that individually preserve each
incremental success:

| Working singleton categories | States | Share |
| ---: | ---: | ---: |
| 1 | 44 | 0.211691% |
| 2 | 17,849 | 85.874429% |
| 3 | 2,888 | 13.894636% |
| 4 | 4 | 0.019245% |

The exact singleton signatures are:

| Working one-category routes | States | Share |
| --- | ---: | ---: |
| Item only | 42 | 0.202069% |
| Supporter only | 2 | 0.009622% |
| Item + Tool | 40 | 0.192446% |
| Item + Supporter | 17,809 | 85.681982% |
| Item + Tool + Supporter | 2,269 | 10.916526% |
| Item + Supporter + Stadium | 619 | 2.978109% |
| Item + Tool + Supporter + Stadium | 4 | 0.019245% |

The dominant geometry is redundancy between:

`Secret Box -> Item -> Tag Call -> Guzma & Hala`

and:

`Secret Box -> Supporter -> Guzma & Hala`

The Item route is slightly more robust because Tag Call can add another TAG
TEAM card to the hand before the later discard payment.

## Relation to abstract connector capacity

`connector_capacity_marginal_phase/` shows that abstract slot marginals can
reverse when a connector has enough direct independent output capacity.

This concrete Aichi endpoint has different structure.

Secret Box physically offers four categories, while its sampled incremental
successes all have minimum immediate category use one.

The chosen output can itself be a connector.

Printed breadth, immediate category use, and downstream terminal fan-out are
therefore separate properties.

A deck optimizer should compile downstream executable paths before assigning a
connector to an abstract capacity regime.

## Validation

The fast seeded 100,000-state regression pins:

- 4,175 incremental successes;
- every 16-mask success count;
- every singleton-route signature;
- singleton failure diagnostics;
- zero monotonicity violations.

The full 500,000-state audit reproduces the established paired totals and the
full dependency geometry above.

The original all-output Aichi Secret Box regression also remains green after
the output-mask parameterization.

No result here changes the original card-text semantics or the default
all-output planner.

## Limits

The endpoint remains the narrow first-turn Bunnelby + TM: Evolution + Jet
Energy core.

The audit does not value:

- later Grand Tree evolution utility;
- which Stage 2 lock pieces are established;
- future value of discarded cards;
- matchup-dependent DCI;
- opponent interaction;
- later turns.

The category mask also preserves the current compressed search policy within
each enabled category.

## Modeling implication

A search card's effective capacity should be defined relative to a terminal
objective and an executable connector chain.

For this Aichi core, treating Secret Box as a four-independent-output action
would substantially misdescribe the mechanism of its measured gain.
