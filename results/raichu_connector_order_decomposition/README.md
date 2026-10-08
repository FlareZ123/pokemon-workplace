# Harto Raichu: why connector order gains 15.5 points

## Question

The visible-connector sequencing result raises same-turn Alolan Raichu access by 15.495412 percentage points when a visible Ultra Ball or Computer Search is used before Quick Ball.

Where does that gain come from?

Implementation: `tools/raichu_connector_order_decomposition.py`  
Reproducer: `results/raichu_connector_order_decomposition/reproduce.py`

## Mechanism

In the modeled branch, Quick Ball, at least one Gladion, and at least one conservative disposable are already visible.

When Ultra Ball or Computer Search is also visible, the direct-first line can pay its two-card discard cost with:

`Quick Ball + one conservative disposable`

The weaker connector itself becomes payment for the stronger connector.

Quick-Ball-first has a different resource geometry:

1. play Quick Ball;
2. discard one card for Quick Ball;
3. search Crobat V;
4. if Raichu is in deck, still find and pay a later connector;
5. if Raichu is Prized, preserve or recover Gladion.

The exact K0 payment rule often discards Gladion in connector-rich, low-disposable observations because doing so preserves the remaining discard stock for Ultra Ball or Computer Search.

The direct-first line eliminates that tradeoff. Quick Ball itself is one unit of the two-card payment, so Gladion can stay in hand while only one conservative disposable is consumed.

## Exact decomposition

The total direct-first gain is **15.495411904 percentage points** over the original observation-consistent Quick-Ball-first policy.

| Quick Ball payment chosen by baseline | Hidden state after search | Gain contribution | Share of total gain |
| --- | --- | ---: | ---: |
| discard Gladion | Crobat V unavailable | 1.123935609 pp | 7.253345% |
| discard Gladion | Raichu in deck | **11.707847066 pp** | **75.556862%** |
| discard Gladion | Raichu Prized | **2.525800117 pp** | **16.300310%** |
| discard disposable | Crobat V unavailable | 0.137829112 pp | 0.889483% |
| discard disposable | Raichu in deck | **0** | **0%** |
| discard disposable | Raichu Prized | **0** | **0%** |

The six contributions sum exactly to the measured ordering gain up to floating-point accumulation.

## Finding 1: most of the gain is payment reordering

The largest contribution is the target-in-deck / discard-Gladion bucket at **75.56% of the total gain**.

Those are states where the baseline visible policy recognized that Ultra Ball or Computer Search mattered and sacrificed Gladion to preserve enough ordinary discard stock after Quick Ball.

Direct-first uses Quick Ball itself as discard stock instead. It can immediately search Raichu while preserving Gladion.

Another **16.30%** of the gain comes from target-Prized worlds under the same baseline payment choice. Direct-first preserves Gladion, learns the target is absent from deck through the search, then uses Gladion on the Prize cards.

Together, those two discard-Gladion buckets explain **91.857172%** of the total gain.

## Finding 2: when the baseline already preserves Gladion, ordering is usually tied

In every modeled direct-visible world where:

- the optimal K0 Quick Ball policy discards a conservative disposable; and
- Crobat V remains searchable,

the direct-first line adds **zero** same-turn Raichu-access probability.

This is a useful structural result. The stronger connector is not automatically better first.

Its local advantage appears specifically when playing the weaker connector first creates a payment or preservation conflict.

## Finding 3: Crobat dependence is a smaller independent effect

The remaining **8.142828%** of the gain comes from worlds where the Quick Ball -> Crobat line fails because no Crobat V remains in deck.

The direct-first line does not need Crobat V to reach the local endpoint.

This is separate from the payment-order effect.

## Strategic interpretation

This is a concrete form of **connector-as-payment domination**.

A card can be strategically valuable as an access edge and simultaneously become the cheapest payment for a stronger access edge.

That means discardability cannot be assigned independently of action order.

In this branch:

- Quick Ball is important when it is the selected first connector;
- the same Quick Ball becomes highly discardable when Ultra Ball or Computer Search already solves the target;
- preserving Gladion can be more valuable than preserving the weaker connector;
- the correct DCI-like ordering therefore changes with the chosen action sequence.

This strengthens the repository's broader connector-domination warning: compare complete resource-consuming lines, not isolated access edges.

## Validation

The decomposition re-enumerates the same exact opening, draw, Prize, and hidden-world model.

It imports the already-validated five-clause observation-consistent Quick Ball payment rule, then attributes the direct-first deficit by:

- the baseline payment chosen;
- Crobat V availability;
- Raichu's deck-versus-Prize state.

The regression also requires its total direct-visible mass and baseline success mass to match `raichu_visible_connector_sequencing/`.

Diagnostic CI run `37764704111` established the exact bucket values. The final regression pins those values with stable floating-point tolerances.

## Limits

The endpoint is still only same-turn Alolan Raichu access.

The model does not assign future value to:

- the discarded Quick Ball;
- the discarded disposable;
- preserved or consumed Computer Search;
- later Basic-Pokémon access;
- Crobat V board value;
- future Gladion value;
- lock interactions;
- Bench pressure;
- later-turn attacks and Energy development.

A full-game policy may prefer a locally lower-probability line because it preserves more future optionality.

## Next useful work

The next reusable abstraction is a **payment-substitution planner**.

For every candidate first action, it should enumerate which other visible connectors can legally serve as payment, then compare the resulting endpoint and future resource state.

That would generalize this Harto-specific phenomenon to Secret Box, Ultra Ball, Computer Search, Mysterious Treasure, and other discard-gated Expanded connectors.
