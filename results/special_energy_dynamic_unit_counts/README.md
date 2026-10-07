# State-dependent Special Energy unit counts

## Question

How large is the stale-provider risk exposed by the Ignition Energy Retreat
witness? Which effectively legal paper Expanded Special Energy cards explicitly
state more than one possible Energy-unit count?

## Method

`tools/special_energy_unit_count_catalog.py` scans Special Energy cards in
Expanded-legal sets, applies the repository's effective-legality overlay, and
extracts explicit provider counts from card text.

The parser recognizes two evidence forms:

- repeated Energy words such as `ColorlessColorlessColorless Energy`;
- numeric provider wording such as `provides only 3 Energy at a time`.

A print enters the catalog only when its text explicitly contains at least two
different unit counts. Type-only changes that remain one unit are excluded.

## Result

The current repository card pool contains **10 print rows across 6 distinct
Special Energy names** with explicit state-dependent unit counts:

- **Twin Energy**: 1 or 2 units, depending on whether the holder is a Pokemon V
  or Pokemon-GX;
- **Counter Energy**: 1 or 2 units, depending on Prize state and whether the
  holder is Pokemon-GX or Pokemon-EX;
- **Neo Upper Energy**: 1 or 2 units, depending on whether the holder is Stage 2;
- **Ignition Energy**: 1 or 3 units, depending on whether the holder is an
  Evolution Pokemon;
- **Reversal Energy**: 1 or 3 units, depending on Prize state, Evolution status,
  and Rule Box status;
- **Super Boost Energy Prism Star**: 1 or 4 units under its Stage 2 board
  condition.

By print profile:

- 5 prints expose {1, 2};
- 4 prints expose {1, 3};
- 1 print exposes {1, 4}.

The exact print IDs are locked by the regression so later card-pool changes are
visible rather than silently changing the research baseline.

## Interpretation

This is a direct state-modeling hazard for Retreat.

A physical Energy card can stay attached while the facts that determine how
many Energy units it provides change. Those facts include:

- holder evolution or Rule Box state;
- holder Pokemon category;
- remaining Prize counts;
- wider board composition.

A stored `EnergyAttachment.units` tuple is therefore safe only as a cache of
current provider state. It is not immutable physical-card identity.

The Ignition Energy result demonstrates both error directions: a stale low
count can erase a legal Retreat, while a stale high count can create an illegal
Retreat. The same failure mode is structurally available to the other five
families.

## Boundary of the catalog

This is a **unit-count** audit. It deliberately excludes Special Energy whose
provided type changes while the number of units remains constant, such as Prism
Energy or Luminous Energy.

It also excludes cards whose unit count is fixed while attachment legality is
conditional, such as Double Dragon Energy or Triple Acceleration Energy.
Those create a different state transition: the physical Energy may need to be
discarded when the holder stops satisfying its attachment condition.

## Next modeling step

A stronger Retreat payment layer should represent an attached Energy card by
physical identity plus a provider function evaluated from current game state.
The six families here define the minimum current dynamic-count surface that such
a function must cover.
