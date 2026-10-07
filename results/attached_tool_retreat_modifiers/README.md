# Board-derived Pokémon Tool Retreat modifiers

## Question

How much of the attached Pokémon Tool Retreat-Cost surface can be derived from
the existing board-object state rather than supplied as an external modifier?

## Result

`tools/attached_tool_retreat_modifiers.py` derives exact-print Tool effects for
20 current prints spanning:

- Air Balloon;
- Float Stone;
- U-Turn Board;
- Escape Board;
- Big Air Balloon;
- Future Booster Energy Capsule;
- Rescue Board;
- Gravity Gemstone;
- Snow Leaf Badge.

The derivation respects the existing `tool_effect_enabled` board state, so
suppressed Tools contribute no modifier.

## Conditional geometry

Several effects require holder context:

- Big Air Balloon needs a Stage 2 holder;
- Future Booster Energy Capsule needs a Future holder;
- Snow Leaf Badge needs a Pokémon V whose name contains Leafeon or Glaceon;
- Gravity Gemstone applies +1 while its holder is Active and affects both
  Active Pokémon.

The resolver therefore checks an opposing Active Gravity Gemstone as well as the
Tool on the retreating Active.

## Rescue Board information boundary

Rescue Board always reduces Retreat Cost by one and additionally makes the
holder have no Retreat Cost when its remaining HP is 30 or less.

The board-object kernel stores damage counters without storing printed/current
HP, so remaining HP is not derivable from that object alone. The resolver
accepts `active_remaining_hp` when a higher layer knows it.

If the value is omitted, the base -1 modifier is returned together with an
explicit unresolved low-HP condition. Callers can see that the result is not
exact instead of silently treating the conditional no-cost branch as false.

## Regression

The regression checks:

- Air Balloon base 3 -> 1;
- Float Stone base 4 -> 0;
- Escape Board base 2 -> 1;
- Stage 2 Big Air Balloon -> no Retreat Cost;
- Future Booster on a Future holder -> no Retreat Cost;
- Rescue Board unknown HP -> -1 plus unresolved condition;
- Rescue Board at 30 HP -> no Retreat Cost;
- one Gravity Gemstone on each Active turns base 1 into 3;
- Leafeon V with Snow Leaf Badge -> no Retreat Cost;
- a suppressed Air Balloon leaves base 3 unchanged.

## Architectural implication

Tool suppression and positional effects make Retreat Cost a cross-board
derivation problem.

The remaining-HP gap also identifies a concrete state variable that the
board-object kernel must eventually expose if it is to own exact Rescue Board
semantics.
