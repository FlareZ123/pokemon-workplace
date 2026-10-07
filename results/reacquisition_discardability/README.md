# Same-line reacquisition can make a required payload temporarily discardable

## Question

The Aichi Vileplume Secret Box result shows a first-turn line in which Secret Box can feed Guzma & Hala, and the temporal-discard result shows that later discard costs can be funded by cards generated after Secret Box.

Can a card that is itself required for the endpoint become a legal discard target because a later connector can search another copy of that same payload?

Yes.

This result adds a provenance-aware temporal hand-resource ledger and applies it to the concrete `Secret Box -> Guzma & Hala` structure.

Implementation: `tools/temporal_resource_ledger.py`  
Reproducer: `results/reacquisition_discardability/reproduce.py`

## Card-text basis

The bundled card pool gives:

- Secret Box (`sv6-163`): discard 3 other cards from hand, then search for an Item, Pokémon Tool, Supporter, and Stadium.
- Guzma & Hala (`sm12-193`): search for a Stadium; when played, the player may discard 2 other cards and, if they do, may also search for a Pokémon Tool and Special Energy.

The Aichi list contains two Technical Machine: Evolution, two Artazon, and two Jet Energy.

The Advanced Player's Rulebook says card instructions are followed in written order. It also says a restricted deck search may take fewer than the specified number of cards. The relevant implication here is temporal: Guzma & Hala's two-card discard is paid before its searched payload enters hand.

## Exact resource ledger

`temporal_resource_ledger.py` represents hand resources by:

- card class;
- provenance, such as initial hand or a specific earlier action;
- zone.

Each action can:

1. consume named cards from hand;
2. pay an exact discard cost with an exact provenance witness;
3. generate named cards into hand after the cost.

A sequence can impose final hand requirements. The solver enumerates legal discard choices and finds a witness minimizing the number of cards discarded from the initial hand.

This is a resource-accounting layer rather than a full physical card-state engine. An action's generated outputs must be validated against deck availability by the caller.

## Concrete two-action branch

The modeled Secret Box branch retrieves:

- Guzma & Hala;
- Tag Call;
- Technical Machine: Evolution;
- Artazon.

Guzma & Hala is then played and pays its two-card optional discard.

The first endpoint profile requires the final hand to contain:

- Technical Machine: Evolution;
- Artazon;
- Jet Energy.

The second profile also requires Tag Call, treating the Item output as an independent downstream demand rather than redundant side payload.

### Minimum initial filler stock

| Downstream requirements | G&H reacquires neither TM nor Artazon | Reacquires TM | Reacquires Artazon | Reacquires both |
| --- | ---: | ---: | ---: | ---: |
| TM + Artazon + Jet | 4 | **3** | **3** | **3** |
| Tag Call + TM + Artazon + Jet | 5 | 4 | 4 | **3** |

Every line still discards five cards in total: three to Secret Box and two to Guzma & Hala.

The difference is which cards need to exist as disposable stock before Secret Box starts.

## Witness: required payload becomes discard fodder

With only three initial filler cards, Secret Box spends all three. It then retrieves Guzma & Hala, Tag Call, TM: Evolution, and Artazon.

If Guzma & Hala can search another TM: Evolution, the second discard can use:

- Tag Call;
- the TM: Evolution just retrieved by Secret Box.

Guzma & Hala then searches a replacement TM: Evolution plus Jet Energy. The final hand still satisfies the TM + Artazon + Jet endpoint.

The first TM was strategically required by the endpoint, yet its current copy became discardable because the continuation guaranteed a replacement before the endpoint was checked.

Artazon has the symmetric property when another copy remains searchable.

## DCI interpretation

This gives a precise state transition that a static per-card discard score can miss.

A payload can move through three roles inside one line:

1. **required payload** when no replacement route exists;
2. **temporarily expendable payload** when a later connector can reacquire it;
3. **required payload again** after the replacement has been searched and the line approaches its endpoint.

Discardability therefore depends on future reachable substitutions, not only on the card's intrinsic importance or the current hand.

The exact copy in hand can be expendable while the card class remains required.

## Relation to temporal resource replenishment

`temporal_resource_replenishment/` establishes the generic ordered-resource rule: an earlier action can produce discard stock that a later action consumes. This result refines that abstraction at card-class resolution. The produced resource has an identity, can itself be required by the endpoint, and can become expendable only because a later search restores the same requirement.

The distinction matters for compiling exact Trainer transactions into temporal resource profiles. Raw hand production is too coarse when some generated cards must be retained and others are replaceable only under a live search route.

## Relation to connector output capacity

The second table also links reacquisition to the concrete Secret Box dependency result.

If Tag Call is redundant after Secret Box already found Guzma & Hala, one side output plus one reacquirable payload is enough to fund Guzma & Hala's two-card discard with zero additional initial stock.

If Tag Call is independently required, that side output is no longer expendable. One reacquisition channel is then insufficient; both TM and Artazon must be replaceable to preserve the three-card initial-stock floor.

This is another reason physical output count is not the same as independent downstream demand capacity.

## Raw Aichi copy-availability probe

The deterministic witness assumes the replacement copy exists in deck.

A separate seeded 200,000-state probe uses the Secret Box variant of the published Aichi list and the same accepted-opening, Active-choice, Prize, first-draw, and Stellar-Wish access structure as the existing Secret Box work. It conditions only on raw first-turn Secret Box access; it does not require the full ALS to succeed.

Among 27,552 states with represented Secret Box access:

- 23,665 (85.8921%) still had both copies of at least one of TM: Evolution or Artazon in deck before Secret Box searched;
- 10,082 (36.5926%) had both copies of both cards still in deck;
- 3,887 (14.1079%) had neither pair fully intact.

Having both copies in deck is a sufficient condition for the exact `Box searches payload -> G&H discards it -> G&H searches the second copy` cycle. It is not necessary for every possible reacquisition line, because a payload already in hand can create other configurations.

The probe is therefore a structural prevalence check rather than a probability that optimal play should use the discard/reacquisition cycle.

## Modeling consequence

A temporal discard policy needs more than a scalar discard-capacity budget.

For each candidate discard, the planner should ask whether the card class is still required and whether another legal route can restore that requirement before its deadline.

A useful execution layer should therefore preserve:

- exact card class;
- provenance;
- timing of costs and generated resources;
- final or intermediate retention requirements;
- later reacquisition channels;
- zone availability for the replacement copy.

This lets a policy recognize transiently high discardability without globally declaring an important card disposable.

## Validation

The reproducer asserts the exact minimum-initial-stock matrix above and emits exact discard witnesses with provenance.

The 200,000-state Aichi probe is deterministic under seed `20261007` and asserts the recorded counts. Two independent 500,000-state spot checks with different seeds put the `either TM or Artazon pair intact` conditional rate at 85.66% and 85.81%, consistent with the seeded regression.

## Limitations

The ledger does not model the deck as a conserved physical zone. Its generated outputs are action specifications, so a higher-level planner must prove those targets are actually searchable.

The Aichi probe tests only a sufficient copy-availability condition and only raw Secret Box access. It does not condition on incremental Secret-Box-only success, matchup value, Prize knowledge after search, or whether discarding and reacquiring the payload is strategically superior to another legal line.

The final requirements are hand-resource requirements. A full turn planner still needs board placement, Bench capacity, Active positioning, Supporter quota, lock state, and the two TM: Evolution attacks.

## Next useful work

Integrate the temporal ledger with `trainer_search_transaction.py` and the typed search-target allocator so searched outputs are removed from a conserved deck state rather than declared by the caller. That would make transient discardability executable inside the canonical search and zone layers and would let copy depletion automatically disable a reacquisition witness.
