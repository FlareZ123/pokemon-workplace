# Dynamic Special Energy providers in Retreat execution

## Question

Can the conserved Retreat transaction reevaluate every current Special Energy
family whose card text explicitly changes the number of Energy units it
provides?

## Result

Yes, for the six families identified by the reproducible dynamic-unit catalog.

`tools/retreat_dynamic_energy_units.py` now uses exact print identity plus
current represented state to refresh the Active Pokemon's attached Energy before
Retreat payment is validated.

The implemented families are:

- **Ignition Energy**: 1 unit normally, 3 on an Evolution Pokemon;
- **Twin Energy**: 2 units normally, 1 on Pokemon V or Pokemon-GX;
- **Neo Upper Energy**: 1 unit normally, 2 on a Stage 2 Pokemon;
- **Counter Energy**: 1 unit normally, 2 while behind on Prizes on a holder that
  is not Pokemon-GX or Pokemon-EX;
- **Reversal Energy**: 1 unit normally, 3 while behind on Prizes on an Evolution
  Pokemon without a Rule Box;
- **Super Boost Energy Prism Star**: 1 unit normally, 4 when 3 or more Stage 2
  Pokemon are in play.

The regression imports the dynamic-unit catalog and asserts that the exact
10-print catalog is equal to the implementation registry. A newly discovered
dynamic-count print therefore cannot silently fall outside the represented
surface.

## State inputs

Holder and board traits are derived from `BoardPokemon.tags` using an explicit
small vocabulary for Stage, Pokemon V/GX/EX, and Rule Box state.

Counter Energy and Reversal Energy also depend on relative Prize counts.
`RetreatEnergyProviderContext` carries those two counts. If Prize counts are
unknown, those two families preserve their existing represented snapshot rather
than guessing which provider mode is active.

Super Boost Energy derives its Stage 2 count directly from the represented
board.

For Retreat, the adapter resolves only **unit count**. It returns Colorless
symbols because Energy type is irrelevant to paying a numeric Retreat Cost.
Attack-payment type semantics remain a separate layer.

## Regression witnesses

The test suite deliberately starts several cards with stale snapshots in both
directions.

Examples:

- Twin Energy represented as one unit on a Basic holder is refreshed to two and
  can pay Retreat Cost 2;
- the same card represented as two units on a Pokemon V is refreshed to one and
  cannot pay Retreat Cost 2;
- Reversal Energy becomes three units only in the behind-on-Prizes,
  non-Rule-Box Evolution state;
- Super Boost Energy with three represented Stage 2 Pokemon becomes four units,
  pays Retreat Cost 4 with one physical card, and then follows its Prism Star
  destination to the Lost Zone.

## Strategic implication

A Retreat planner cannot safely cache `EnergyAttachment.units` across game
state transitions.

The payment witness is a set of physical cards, while Energy quantity is a
function of the current state. That function can change after evolution, Prize
changes, or board development without changing the physical attachment itself.

The execution order should therefore be:

1. preserve attached physical card identity;
2. derive current provider state;
3. enumerate legal physical payment witnesses;
4. resolve destination effects for the selected cards.

## Limits

The tag vocabulary is an explicit local contract and is not yet generated from
card print metadata. Incomplete holder tags can therefore still misrepresent a
provider condition.

This result covers unit-count changes. Conditional attachment legality remains
separate. Cards such as Double Dragon Energy, Triple Acceleration Energy,
Rapid Strike Energy, and other holder-restricted Special Energy may need to be
discarded when a holder stops satisfying their attachment condition even if
their nominal unit count is fixed.
