# Simultaneous Knock Out redirection conflicts

## Question

When several Knock Out effects apply to the same physical Pokémon or attached
cards, can their destination programs be combined mechanically, or do some
states require effect-order semantics?

Implementation: `tools/knockout_redirection_conflicts.py`  
Regression: `results/knockout_redirection_conflicts/reproduce.py`

## Representation

Each KO effect contributes a partial map:

`physical instance -> destination zone`

The map contains only destinations the effect actually assigns. This is why the
route compiler preserves explicit discard instructions from text such as Lost
City's "(Discard all attached cards.)" while Huntail's Diver's Catch leaves
non-selected cards unassigned.

`destination_conflicts()` groups assignments by physical instance and reports
a conflict only when two or more effects assign different zones to the same
instance.

`merge_compatible_programs()` merges programs only when every shared instance
has the same destination.

The detector preserves effect provenance in each conflict row. It deliberately
does not decide which effect wins.

## Concrete conflicts

The regression reuses the same pending KO state as the executable-route result:
an evolved Honedge -> Doublade -> Aegislash stack with two Basic Water Energy,
one Double Colorless Energy, one Muscle Band, and a surviving Benched Bidoof.

It compares destination programs corresponding to the four current taxonomy
exemplars.

### Aegislash Durable Blade + Lost City

Durable Blade assigns the whole evolved Pokémon stack to hand.

Lost City assigns that same stack to the Lost Zone.

The detector reports exactly three conflicts, one for each physical Pokémon card
in the stack. Both effects assign attachments to discard, so the attachments are
compatible.

This case also reinforces that an evolved Pokémon cannot be represented as only
its top card for zone movement.

### Tyranitar-GX Lost Out + Lost City

Both effects assign the Pokémon stack to the Lost Zone, so those assignments are
compatible.

Lost Out assigns every attachment to the Lost Zone, while Lost City explicitly
assigns every attachment to discard.

The detector therefore reports exactly four conflicts: the two Basic Water
Energy cards, Double Colorless Energy, and Muscle Band.

This is the counterexample that makes explicit-default preservation necessary.
If Lost City's attachment instruction were stored merely as "no override", the
conflict would disappear from the model even though the card text assigns a
different destination.

### Huntail Diver's Catch + Lost City

Diver's Catch assigns the two selected Basic Water Energy instances to hand.

Lost City explicitly assigns those attachments to discard.

The detector reports exactly those two Energy instances. Huntail makes no
assignment to the Pokémon stack or to non-selected attachments, so it creates no
additional conflict there.

### Tyranitar-GX Lost Out + Huntail Diver's Catch

Lost Out assigns all attachments to the Lost Zone.

Diver's Catch assigns the selected Basic Water Energy to hand.

Again the detector reports exactly the two selected Water Energy instances.

## Relation to trigger ordering

The existing `knockout_phase_resolution` result establishes a separate rule
boundary: when several KO-triggered effects activate at the same time, the
current-turn player chooses their order.

The conflict detector identifies where that ordering can matter physically. A
same-destination overlap is semantics-free and can be merged. A same-instance
different-destination overlap cannot be collapsed into one unordered routing
map without losing information.

This result does not infer the final destination from trigger order. Doing that
correctly requires executing effects against evolving zone state, including the
possibility that an earlier effect has already moved the affected card.

## Finding

A KO destination model needs three different states of information:

1. **unassigned**: this effect does not say where the instance goes;
2. **assigned to the ordinary sink**: the effect explicitly says discard;
3. **assigned elsewhere**: hand, Lost Zone, or another destination.

Treating the first two as identical is safe for a single isolated effect and
unsafe for simultaneous effects.

The destination-program abstraction therefore provides a precise seam between
card semantics and physical execution. It can identify conflict surfaces before
a full arbitrary-trigger interpreter exists.

## Limits

The regression proves destination incompatibility, not the official outcome of
every co-triggering card combination.

Actual activation still depends on controller, damage source, Pokémon type,
Stadium state, optional choices, Ability suppression, and other semantic
conditions. Those remain upstream.

A future ordered-effect executor should consume the existing global KO trigger
order, apply one destination-changing effect at a time to the pending state, and
define what happens when a later effect refers to a card that an earlier effect
has already moved.
