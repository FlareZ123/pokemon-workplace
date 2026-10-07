# Board-derived Retreat execution

## Question

Can the repository execute a Retreat while deriving the represented
board-dependent facts that were previously supplied as disconnected booleans,
unit snapshots, or cost values?

## Composition

`tools/board_derived_retreat.py` provides one higher-level attempt boundary.

It performs these steps in order:

1. discard holder-restricted Special Energy whose attachment is no longer
   legal;
2. refresh state-dependent unit counts on surviving Special Energy;
3. derive Retreat Cost effects from attached Special Energy;
4. derive represented active Pokémon Tool Retreat effects on both boards;
5. combine those effects with any still-external Retreat Cost modifiers;
6. calculate the effective Retreat Cost;
7. derive Scoop-Up Block from the opponent's exact represented board;
8. execute the conserved physical Retreat payment and Energy-destination
   transaction.

The returned object preserves the normalized pre-Retreat state, effective cost,
modifier provenance, active Scoop-Up Block sources, and the optional transaction
result.

## Commit semantics

Attachment validity and provider refresh describe the current game state before
the Retreat action. They therefore remain reflected in the returned
normalization even if the requested Retreat itself is illegal.

This matters for a stale Triple Acceleration Energy on a Basic holder. The card
self-discards during normalization. A request to spend it on Retreat Cost 3 is
then rejected, while the card remains correctly in discard.

Destination conflicts stay under the existing immutable transaction contract:
an unresolved replacement conflict does not spend the Retreat action.

Rescue Board exposes a separate information boundary. If remaining HP is not
supplied, the Tool layer reports its low-HP condition as unresolved and the
higher-level attempt does not execute a Retreat at a potentially wrong cost.

## Regression

The regression composes four previously separate witnesses:

- stale Triple Acceleration Energy self-discards before payment;
- Ignition Energy on a Stage 1 holder refreshes from one unit to three and pays
  Retreat Cost 3;
- Mystery Energy on a Psychic holder reduces base Retreat Cost 2 to zero, while
  an external +2 modifier restores the effective cost to 2;
- Air Balloon is derived from the attached Tool and makes base Retreat Cost 2
  free;
- Rescue Board with unknown remaining HP stops at an explicit unresolved
  condition, while a supplied 30 HP state derives no Retreat Cost;
- a damaged Dashing Pouch holder facing an enabled opposing Mr. Mime
  `sm9-66` derives Scoop-Up Block from the opponent board and sends the paid
  Double Colorless Energy to discard.

## Architectural implication

A Retreat action is increasingly well represented as a typed state program
rather than a function of one integer cost and one list of Energy IDs.

The remaining external modifier tuple is now concentrated in Ability, Stadium,
and attack-applied effects plus Tool conditions whose required state is absent.
Source-aware derivation for those effects is the next boundary before the
integer cost can become fully canonical.
