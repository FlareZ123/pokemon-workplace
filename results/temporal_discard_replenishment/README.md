# Temporal discard replenishment: throughput is not initial discard stock

## Question

When a line pays several discard costs in sequence, can a static resource model add those costs and require the full sum to be disposable before the first action?

No.

The concrete counterexample is the Aichi Vileplume Secret Box line already modeled in `aichi_vileplume_secret_box/`.

A common incremental structure is:

`Secret Box -> Guzma & Hala -> Jet Energy`

Secret Box discards 3 cards. The paid Guzma & Hala branch later discards 2 more cards. Total discard **throughput** can therefore be 5 cards.

Secret Box also puts several new Trainer cards into the hand before Guzma & Hala resolves. Those generated cards can pay Guzma & Hala's later two-card cost. The number of cards that must already be disposable when Secret Box starts can therefore be only 3.

Implementation and reproducer: `reproduce.py`.

## Two different resources

This result separates:

- **discard throughput**: total number of cards discarded across all effects in the line;
- **initial discard stock**: the minimum number of cards that must already be available to sacrifice before the first discard-cost action begins.

For two staged costs, let:

- first cost = `c1`;
- second cost = `c2`;
- `g` = cards generated after the first cost that remain acceptable fodder for the second cost.

A simple lower bound on initial discard stock is:

`c1 + max(0, c2 - g)`

For Secret Box into paid Guzma & Hala:

- `c1 = 3`;
- `c2 = 2`;
- if at least 2 generated outputs can be sacrificed, initial stock is `3`, even though throughput is `5`.

The formula is only a lower bound. Retention requirements, target availability, Supporter timing, and other state constraints can make a specific line require more.

## Provenance-aware model

The reproducer reuses the published paired Aichi state generator and core planner.

At the moment Secret Box is played, every surviving card already in hand is tagged as **pre-Box**.

Cards retrieved by Secret Box and later searches are tagged as **generated**.

The continuation search then imposes one additional constraint:

> any later Guzma & Hala two-card discard must be paid entirely with generated cards.

Playing a pre-Box card normally is allowed. Keeping a pre-Box payload such as Jet Energy or TM: Evolution is allowed. The restriction applies only to later discard payment.

This asks an existence question:

**Does the successful Secret Box line have a continuation where Secret Box's own three-card payment is the only discard drawn from the hand stock that existed when Box started?**

## 100,000-state seeded regression

Seed: `20261007`.

The paired opening, Prize, first-draw, and Stellar Wish model is the same as the existing Secret Box result.

| Quantity | Count | Rate / share |
| --- | ---: | ---: |
| Grand Tree core successes | 70,709 | 70.7090% |
| Secret Box core successes | 74,884 | 74.8840% |
| Secret-Box-only successes | 4,175 | 4.1750% of trials |
| Incremental successes with a self-funded continuation | **4,175** | **100% of incremental successes** |
| Incremental successes with Jet Energy absent from the raw hand | 3,197 | 76.5749% of incremental successes |
| Missing-Jet incremental successes with a self-funded continuation | **3,197** | **100% of missing-Jet incremental successes** |

The 100,000-state baseline and Secret Box counts match the existing planner exactly for this seed prefix.

For this sample, every incremental Secret Box success has at least one successful continuation where no later discard cost consumes another pre-Box hand card.

## Relation to the existing 4.5334-card result

The existing 500,000-state Secret Box result reports a mean minimum discard burden of 4.5334 cards across incremental successes.

That statement counts cards actually discarded by the effects:

- 3 when Jet Energy is already present;
- 5 when paid Guzma & Hala is needed.

This result measures a different quantity.

In the 100,000-state prefix, mean discard throughput is 4.531497 cards, yet the successful self-funded continuation needs only 3 cards from the hand stock present when Secret Box starts.

Both facts can be true because cards searched by Secret Box are created between the two discard payments.

## Why static connector-cost addition fails

A static allocator might represent the line as:

- Secret Box: discard cost 3;
- Guzma & Hala: discard cost 2;
- shared disposable-card capacity required: 5.

That representation rejects states with only 3 initially disposable cards.

A sequential state transition can instead do:

1. pay Secret Box's 3-card cost;
2. resolve Secret Box and add multiple Trainer outputs to hand;
3. play Guzma & Hala;
4. use two generated cards as Guzma & Hala's optional discard;
5. obtain the missing Tool / Special Energy outputs.

The second cost sees a different hand from the first cost.

The resource is replenishable inside the line.

## Modeling consequence

Discard capacity should be modeled as a state variable that can decrease **and increase** between actions.

For a sequence planner, an action should expose at least:

- exact cards consumed;
- exact cards produced;
- timing of those transitions;
- which produced cards remain eligible as future discard fodder;
- retention constraints from the intended continuation.

A scalar `discardable_cards` budget is still useful inside a single frozen action. Summing several action costs against the original scalar state can create false negatives when earlier actions generate later fodder.

This complements `resource_constrained_connectors/`:

- shared resources cannot be double-spent;
- replenishable resources also cannot be treated as if they only decrease.

The same issue can apply beyond discard costs whenever an action creates a resource consumed by a later action.

## DCI / AMR interpretation

This result adds a temporal qualification to DCI-style reasoning.

A card retrieved by Secret Box may have low strategic continuation value and therefore become high-DCI immediately, even though it did not exist in hand when Box's first cost was evaluated.

Discardability is therefore state-dependent in two ways:

1. the value of existing cards changes with the line;
2. the set of candidate cards itself changes between costs.

A future DCI policy should evaluate discard witnesses against the hand at each payment point rather than assign one fixed opening-hand discard pool to the entire turn.

## Limits

The model inherits the scope of the Aichi first-turn core planner.

It does not assign future continuation value to the cards sacrificed, evaluate the full Grand Tree versus Secret Box deck-level tradeoff, or prove that every possible 500,000-state incremental success has the same provenance property.

The reported provenance result is a deterministic check over the seeded 100,000-state regression.

It establishes existence of a self-funded continuation, not uniqueness. Other successful lines from the same state may discard additional pre-Box cards.

## Next useful work

The natural infrastructure extension is a temporal resource ledger.

Instead of attaching one static discard-capacity vector to an entire route, each action would mutate:

- hand card classes;
- discardable witness sets;
- generated-card provenance;
- action quotas;
- downstream retention requirements.

That would let the shared connector allocator distinguish consumable resources from replenishable ones and compose exact Trainer transactions across several actions.
