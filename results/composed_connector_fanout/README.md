# Composed connector fan-out: one Secret Box output can unlock a multi-axis line

## Question

The Aichi Secret Box output-dependency audit finds that almost every incremental
first-turn core success can be preserved using only Secret Box's Item output.

How can one immediate output category complete a line that still needs
Bunnelby, Technical Machine: Evolution, and Jet Energy?

The answer is connector composition.

Implementation is a concrete regression built on
`tools/temporal_resource_connectors.py`:

- `results/composed_connector_fanout/reproduce.py`

## Concrete chain

The represented line is:

`Secret Box -> Tag Call -> Guzma & Hala -> Artazon / TM: Evolution / Jet Energy`

The terminal demand vector is:

- Bunnelby access;
- Technical Machine: Evolution;
- Jet Energy.

The model gives Secret Box only **one immediate output category**, Item.

That Item output produces access to Tag Call.

Tag Call produces access to Guzma & Hala and, in the represented branch, one
additional TAG TEAM card that can become later payment material.

Guzma & Hala consumes the one Supporter window and two units of payment
material, then supplies TM: Evolution and Jet Energy while producing access to
Artazon.

Artazon supplies Bunnelby.

The temporal solver finds the exact witness:

`Secret Box -> Item -> Tag Call -> Guzma & Hala -> Artazon`

All three terminal demand units are satisfied.

## Finding 1: immediate output capacity and terminal fan-out are different

Secret Box uses one physical output category in this witness.

The downstream chain still satisfies three terminal channels.

A representation that assigns terminal capacity only from the number of
immediate outputs will therefore understate connector chains.

The reverse error is also possible. Counting every printed Secret Box category
as an independent terminal need can overstate a line when those categories are
redundant routes into the same downstream connector.

The useful object is a **state-valid composed terminal profile**.

## Finding 2: the longer Item route can have a lower payment threshold

Use an abstract payment-material resource.

Secret Box consumes three units.

The full-mode Guzma & Hala later consumes two.

For the direct Supporter route:

`Secret Box -> Guzma & Hala`

five starting payment units are required in this abstraction.

Four fail.

For the Item route:

`Secret Box -> Tag Call -> Guzma & Hala`

Tag Call's second TAG TEAM output replenishes one unit of hand material before
the Guzma & Hala payment.

Four starting units therefore suffice:

`4 -> pay 3 -> 1 -> Tag Call produces 1 -> 2 -> pay 2 -> 0`

If that second TAG TEAM output is removed from the profile, four fail and five
are required again.

This provides a mechanistic explanation for why the concrete output audit can
prefer the apparently longer Item route.

## Finding 3: action budgets remain part of the composed profile

The chain fails when the starting Supporter-window resource is zero.

Connector fan-out therefore cannot be represented as pure reachability.

A compiled profile needs to preserve at least:

- connector identity;
- action-window consumption;
- payment costs;
- intermediate resource production;
- ordering;
- terminal outputs.

## Relation to the capacity phase result

`connector_capacity_marginal_phase/` studies abstract connectors whose output
capacity directly satisfies independent terminal channels.

The Aichi chain shows a different geometry.

Secret Box's effective immediate category use can be one, while the chosen
output is itself a connector that fans out downstream.

This means a real-deck optimizer should compile executable connector chains
before mapping a card to a scalar output-capacity regime.

## Validation

The regression uses the repository's independently validated temporal resource
solver.

It checks:

- Item route succeeds from four starting payment units;
- Item route fails from three;
- removing Tag Call's extra payment-material production makes four fail;
- the no-replenishment Item route succeeds from five;
- direct Supporter route fails from four and succeeds from five;
- removing the Supporter window makes the full chain fail;
- the successful action order is the expected Box -> Tag Call -> G&H ->
  Artazon sequence.

## Limits

The payment unit is an abstraction.

The concrete Aichi planner tracks physical cards more precisely and does not
declare every generated card strategically disposable.

The second TAG TEAM card is represented here as one usable payment unit only
to isolate the replenishment mechanism already observed in the concrete
transaction model.

Prize state, hidden information, matchup-dependent DCI, and later-game value
remain outside this deterministic chain regression.

## Modeling implication

Search capacity should be compiled through connector chains rather than read
directly from printed output count.

A state-local optimizer can treat a legal chain as a terminal action profile,
while retaining the costs and intermediate resource constraints that made that
profile executable.
