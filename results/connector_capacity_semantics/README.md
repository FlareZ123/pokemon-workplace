# Connector capacity semantics: finite search resources across simultaneous needs

## Question

How should a search graph represent cards that can reach many resources when one physical use has limited capacity, while still giving proper credit to cards that genuinely satisfy several resource channels at once?

This result adds a deterministic state-local capacity layer for connector analysis.

Implementation: `tools/connector_capacity.py`

Independent validation: `results/connector_capacity_semantics/reproduce.py`

## Card-text motivation

The bundled Expanded card pool gives two useful contrasting examples.

`Computer Search` `bw7-137` is an Expanded-legal ACE SPEC Item. Its bundled text requires discarding two cards, then searches the deck for one card.

`Guzma & Hala` `sm12-193` and `sm12-229` are Expanded-legal TAG TEAM Supporters. Their bundled text searches for a Stadium. If the player discards two other cards, the effect may also search for a Pokémon Tool and a Special Energy.

These cards therefore have different resource-capacity geometry.

A single Computer Search use can choose among many target categories, while still providing one searched card.

A full-mode Guzma & Hala use can satisfy three distinct categories in the same Supporter action.

This comparison concerns search capacity only. Computer Search and Guzma & Hala have different action classes, costs, deck-building constraints, and timing. Those state predicates must be evaluated separately.

## Representation

Let the modeled resource demand be a vector:

`d = (d_1, d_2, ..., d_m)`

Each physical connector use chooses one valid outcome profile:

`p = (p_1, p_2, ..., p_m)`

The profile describes how many units of each resource channel that single use can satisfy.

Examples for three channels:

- one any-card search: possible profiles `(1,0,0)`, `(0,1,0)`, `(0,0,1)`;
- one true three-axis search: profile `(1,1,1)`.

Each connector copy can be unused or can realize one of its listed profiles.

The solver performs exact dynamic programming over remaining demand and reports:

- whether the complete requirement vector is feasible;
- whether a naive independent-edge graph calls every channel reachable;
- the minimum number of resource units still unmet;
- which individual channels appear reachable;
- one witness sequence of connector profiles when complete satisfaction is possible.

## Example 1: one broad one-shot connector

Demand:

`(1,1,1)`

Available connector:

- one any-card search with unit profiles for each channel.

A naive graph creates an edge from the connector to all three targets and marks every channel reachable.

Exact result:

- naive joint reachable: yes;
- exact joint feasible: no;
- minimum unmet units: 2.

The connector's breadth does not multiply its capacity.

For Computer Search specifically, the bundled ACE SPEC rule also limits the deck to one ACE SPEC card. This makes one physical copy a particularly clear illustration of the capacity-one case.

## Example 2: one true multi-axis connector

Demand:

`(1,1,1)`

Available connector:

- one connector with profile `(1,1,1)`.

Exact result:

- naive joint reachable: yes;
- exact joint feasible: yes;
- minimum unmet units: 0.

A payable full-mode Guzma & Hala has this capacity shape when the three modeled channels are Stadium, Pokémon Tool, and Special Energy.

The discard requirement must already be satisfiable before this full profile is admitted into the state. If the discard cost cannot be paid, the state-valid profile should expose only the Stadium channel.

## Example 3: combining broad and multi-axis capacity

Demand:

`(1,1,1,1)`

Available connectors:

- one three-axis connector with profile `(1,1,1,0)`;
- one any-card connector with unit profiles for all four channels.

The exact solver finds a complete plan. The three-axis connector satisfies the first three needs, while the any-card connector is spent on the fourth.

This is the kind of joint line that an optimizer should reward. It differs structurally from two broad capacity-one connectors, which can satisfy only two missing units.

## Relation to shared connector contention

`results/shared_connector_contention/` quantifies how often finite connector capacity changes joint-access probability in valid opening and Prize states.

The current result isolates the deterministic inner problem.

The probabilistic layer answers which cards are exposed and searchable.

The capacity layer answers whether the exposed connector resources can jointly satisfy the current requirement vector.

This separation provides a reusable route toward a more realistic associativity model.

## Relation to action timing and discard realism

Capacity is only one feasibility axis.

`results/supporter_outs_timing/` shows that a connector can reach a Supporter while consuming the action required to play it.

`results/discard_gated_supporter_access/` shows that a correctly timed connector can remain unusable because the discard requirement cannot be paid.

The connector-capacity solver expects those constraints to be resolved before constructing the available connector profiles.

For example:

- if Computer Search cannot pay two discards, it contributes no profile in that state;
- if Guzma & Hala cannot pay its optional two-card discard, its full Stadium plus Tool plus Special Energy profile is unavailable;
- if the current objective requires a later Supporter play in the same turn, Guzma & Hala's Supporter timing may make the otherwise valid capacity profile strategically unusable.

## Validation

The reproducer independently enumerates every unused/profile choice for each physical connector copy in several small states.

It compares the brute-force feasibility and minimum-unmet result with the dynamic program.

Regression cases include:

- one capacity-one any-card connector against three missing channels;
- three capacity-one any-card connectors;
- one three-axis connector;
- a mixed three-axis plus any-card package;
- repeated restricted profiles with multi-unit demand.

All cases are deterministic and require no Monte Carlo sampling.

## Strategic implication

Search breadth and search capacity are separate properties.

A graph can have excellent connectivity while lacking enough physical connector capacity to realize several edges in the same line.

The reverse also matters. A multi-axis card can have unusually high strategic value because one use produces several required channels together.

Future optimization should therefore represent a search card with state-valid outcome profiles rather than only a set of reachable nodes.

## Next useful work

The next integration is to place this capacity solver inside the probabilistic access model.

For each accepted opening, Prize state, and draw state, the model can construct the available connector profiles after applying:

- timing;
- discard gates;
- Bench constraints;
- locks;
- target availability.

The capacity solver can then decide whether the whole turn requirement vector is feasible.

A later layer can attach utility or win probability to alternative requirement vectors so a connector can be allocated to the strategically strongest line rather than simply checking one fixed goal.
