# Connector profile access: identical graph edges, different joint consistency

## Question

Can two connector packages expose the same simple reachability edges while producing very different probabilities of satisfying several required resource channels together?

Yes.

This result integrates the deterministic capacity profiles from `tools/connector_capacity.py` with exact valid-opening, Prize, and random-exposure states.

Implementation: `tools/connector_profile_access.py`

Independent validation: `results/connector_profile_access/reproduce.py`

## Exact state model

The deck is partitioned into:

- one category for each target channel;
- one category for each connector type;
- setup-eligible starters;
- filler.

Targets and connector types are non-starters in this baseline.

For each accepted opening, Prize state, and optional later random exposure:

1. a target already in hand satisfies its channel directly;
2. a target absent from hand must still exist in the searchable deck;
3. only connector copies exposed into hand are available;
4. the state-local connector capacity solver tests whether the remaining target-demand vector can be covered by the available connector profiles.

A naive comparison evaluates every target channel independently. If one exposed connector has a profile that can touch a target, the naive graph gives that target an access edge without accounting for the connector being consumed elsewhere.

## Baseline

Use:

- 60 cards;
- 6 Prize cards;
- a valid 7-card opening;
- 12 setup-eligible starters;
- three target channels;
- 2 copies of each target;
- no extra random draws.

Two connector shapes are compared.

**Capacity-one any-card connector**

One use can choose exactly one profile:

- `(1,0,0)`;
- `(0,1,0)`;
- `(0,0,1)`.

**True three-axis connector**

One use has profile:

- `(1,1,1)`.

A simple uncapacitated graph gives either connector edges to all three target channels.

## Main finding

| Connector package | True joint access | Naive joint access | Capacity overstatement |
| --- | ---: | ---: | ---: |
| one capacity-one any-card connector | 1.351569% | 11.227080% | 9.875511% |
| one true three-axis connector | 11.227080% | 11.227080% | 0.000000% |
| two capacity-one any-card connectors | 2.427705% | 20.881490% | 18.453785% |
| one any-card plus one three-axis connector | 11.954982% | 20.881490% | 8.926509% |

The first two rows have the same target copy counts, the same number of connector copies, and the same simple graph edge set.

Their exact joint access differs by a factor of about **8.31**.

The simple graph cannot distinguish them because it records reachability while discarding the number of channels one physical use can satisfy.

## Card interpretation

The bundled Expanded card pool provides concrete shapes that motivate the abstract profiles.

`Computer Search` `bw7-137` searches for one card after its discard cost is paid. For a state with several missing independent channels, one use has broad target choice and capacity one.

`Guzma & Hala` `sm12-193` and `sm12-229` can search a Stadium, and after its optional discard cost is paid it may also search a Pokémon Tool and a Special Energy. For those three categories, its full mode has a genuine three-axis capacity shape.

These cards have different timing and costs. Guzma & Hala is a Supporter and Computer Search is an ACE SPEC Item. The table is therefore a capacity experiment rather than a claim that the cards are interchangeable deck slots.

## Why the mixed package still has contention

One any-card connector plus one three-axis connector has the same naive joint access as two capacity-one connectors because both packages contain two cards whose simple edge sets reach all three channels.

The exact result is much higher for the mixed package because any state exposing the three-axis connector can cover several simultaneous needs.

Some contention remains when only the any-card connector is exposed or when the multi-axis card is inaccessible.

This illustrates why connector identity and exposure state both matter.

## Validation

The reproducer validates the integration in two independent ways.

First, when every connector uses capacity-one any-card profiles, the new engine reduces exactly to `tools/shared_connector_multichannel.py`.

Second, a small labeled deck containing both a capacity-one connector and a three-axis connector is exhaustively enumerated over:

- accepted opening hands;
- disjoint Prize cards;
- later draws;
- every physical connector profile choice.

Exact joint access, naive joint access, and contention probability match the integrated category model to floating-point precision.

## Implication for associativity models

An associativity representation needs more information than whether an edge exists.

At minimum, each search action should preserve:

- which channels it can reach;
- how many channels or units one physical use can satisfy;
- whether several outputs can be obtained simultaneously;
- the number of physical connector copies currently available.

Timing, discardability, locks, Bench space, and opportunity cost remain additional axes.

A capacity-aware hypergraph or state transition model can preserve these distinctions directly.

## Next useful work

The strongest continuation is to make connector profiles state-derived instead of supplied manually.

For each concrete card route, a state evaluator can expose profiles only when:

- its action timing permits use;
- costs are payable;
- required Bench space exists;
- relevant Abilities or Items are not locked;
- the target remains in the correct zone;
- the connector has not already been spent.

That would join the repository's existing timing, discard-gate, lock, and connector-domination work into one joint line-feasibility engine.
