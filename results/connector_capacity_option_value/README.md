# Connector capacity slack and the option value of waiting

## Question

The earlier `connector_option_value` result showed that a capacity-one universal search can be worth preserving when two different target channels are missing: a later natural draw reveals which channel the connector should repair.

How does that effect change when one connector can satisfy several distinct target channels at once?

This result isolates **capacity slack**: the gap between the number of currently missing target channels and the number of distinct channels one connector use can satisfy.

Implementation: `tools/connector_capacity_option_value.py`  
Independent regression: `results/connector_capacity_option_value/reproduce.py`

## Model

The model begins at an action point with one connector already in hand.

State contains:

- one or more missing target channels, each with an exact number of copies still in deck;
- one connector with output capacity `k`, meaning one use can search one copy from each of up to `k` distinct missing channels;
- optional currently acceptable discard cards in hand and deck;
- filler cards;
- a finite number of future natural draws.

The objective is narrow: secure every target channel by the deadline.

At each action point the policy may:

1. spend the connector now, choosing the target subset after observing the current state; or
2. preserve it, take the next natural draw, and choose again afterward.

The `optimal` policy may wait. The `eager` policy spends the connector as soon as its discard gate is payable, while still choosing the best output subset.

Search physically removes one target copy from the deck for every channel it secures. Natural draws are without replacement. This means early search changes later draw probabilities rather than being represented as a free graph edge.

## Structural bound

If `m` target channels are still missing, the connector has capacity `k`, and only `T` natural draws remain, then success is impossible when:

`m > k + T`

Each natural draw can secure at most one previously missing channel, and the one connector use can secure at most `k` others.

At the opposite extreme, when `k >= m`, the connector can immediately satisfy every missing channel. Under this narrow access objective, with no competing use and a payable cost, waiting has zero value because immediate connector use already yields success probability 1.

The interesting regime is therefore **positive capacity slack that is still recoverable before the deadline**:

`0 < m - k <= T`

## Exact one-draw family

A particularly clean case has:

- `m = k + 1` missing channels;
- `r` copies of every channel in a deck of size `N`;
- no discard gate;
- exactly one future natural draw.

If the player waits, drawing *any* target channel reveals which `k` other channels the connector should fetch. Therefore:

`P(optimal wait success) = m r / N`

If the connector is spent eagerly, it removes one copy from each of `k` channels and leaves one channel unresolved. The remaining natural draw must hit that channel:

`P(eager success) = r / (N - k)`

For ordinary decks where `N > m`, the waiting value is strictly larger.

### 40-card canonical comparison

Using two copies per target channel and a 40-card remaining deck:

| Missing channels `m` | Connector capacity `k` | Optimal | Eager | Waiting gain |
| ---: | ---: | ---: | ---: | ---: |
| 2 | 1 | 10.000000% | 5.128205% | **+4.871795 pp** |
| 3 | 2 | 15.000000% | 5.263158% | **+9.736842 pp** |
| 4 | 3 | 20.000000% | 5.405405% | **+14.594595 pp** |
| 5 | 4 | 25.000000% | 5.555556% | **+19.444444 pp** |

The connector becomes more powerful as capacity rises, yet its *adaptive* value can also increase when demand rises with it and remains exactly one channel beyond capacity. The key variable is capacity relative to unresolved demand.

## More future draws amplify the adaptive gap

The dynamic program can wait more than once. Keeping the same symmetric 40-card states and `m = k + 1`:

| `m / k` | 1 draw: optimal / eager | 2 draws | 3 draws | 4 draws |
| --- | ---: | ---: | ---: | ---: |
| 2 / 1 | 10.0000% / 5.1282% | 19.2308% / 10.1215% | 27.7328% / 14.9798% | 35.5455% / 19.7031% |
| 3 / 2 | 15.0000% / 5.2632% | 28.0769% / 10.3841% | 39.4332% / 15.3627% | 49.2548% / 20.1991% |
| 4 / 3 | 20.0000% / 5.4054% | 36.4103% / 10.6607% | 49.7976% / 15.7658% | 60.6522% / 20.7207% |
| 5 / 4 | 25.0000% / 5.5556% | 44.2308% / 10.9524% | 58.9069% / 16.1905% | 70.0131% / 21.2698% |

For the 5-channel, capacity-4 state with four future draws, adaptive preservation reaches **70.0131%** while eager use reaches **21.2698%**, a **48.7433-point** difference.

The mechanism is target-choice information. Waiting lets natural draws decide which channels no longer need connector capacity. Eager play commits outputs before that information arrives.

## Discard scarcity creates a different kind of waiting

Capacity slack is not the only reason an action may be delayed.

Consider four missing channels, capacity four, a cost-three connector, two acceptable discard cards already in hand, ten more acceptable discard cards in a 40-card deck, and two copies per target channel.

The connector has enough output capacity to solve all four channels immediately, but it is not yet payable.

Exact success after future draws is:

| Future draws | Success |
| ---: | ---: |
| 1 | 25.000000% |
| 2 | 44.230769% |
| 3 | 58.906883% |
| 4 | 70.030638% |

With three acceptable discard cards already in hand, success is 100% immediately for every horizon.

This separates two phenomena:

- **informational waiting**: the connector is playable, but preserving it lets later draws determine the best target allocation;
- **forced waiting**: the connector has enough output capacity but cannot yet pay its resource gate.

Both can make a search line temporally unavailable, but they should not be represented by the same state variable.

## Relation to prior connector work

This result extends several existing findings:

- `connector_option_value/` established the two-channel, capacity-one case;
- `connector_capacity_semantics/` separated search breadth from finite output capacity;
- `connector_output_capacity/` showed that higher capacity can overcome a worse discard gate;
- `multi_output_slot_marginals/` showed that discardability can become more valuable when one paid action activates several outputs;
- `competing_connector_deadlines/` showed that expiring windows reduce allocation flexibility.

The new contribution is a finite-horizon link between **output capacity and target-choice information**.

A connector should not receive a permanent scalar "capacity bonus." Its value depends on the current unresolved demand vector and how much information can arrive before the action deadline.

## Validation

The implementation is an exact memoized dynamic program over target-copy counts, secured channels, discard stock, connector availability, and remaining draws.

The reproducer validates it three ways:

1. the `m = k + 1`, one-draw rows match the closed forms above exactly;
2. a separate labeled-card game-tree enumerator reproduces every one-draw row;
3. the labeled enumerator also matches a multi-draw three-channel regression and a discard-gated full-capacity regression.

No Monte Carlo sampling is used.

## Limitations

The connector is already in hand and has no competing strategic use beyond the modeled target channels.

Target channels are abstract and unrestricted. A concrete Secret Box interpretation would require distinct eligible Item, Tool, Supporter, and Stadium outputs, plus exact timing and payment legality. The model also omits Supporter contention, Bench constraints, locks, Prize zones, draw-engine effects, and state-dependent strategic value after target access.

The scalar discard pool represents mechanically and strategically acceptable payments under the modeled policy. It does not derive DCI from exact card identities.

## Next useful work

The strongest extension is **deadline-sensitive capacity slack**. Give different target channels different expiry turns and measure when an early deadline forces the connector to commit before later information arrives. That would unify this capacity result with `competing_connector_deadlines/` and provide a reusable model for multi-axis cards whose outputs have unequal timing requirements.
