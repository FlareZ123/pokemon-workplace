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
4. combine those effects with any still-external Retreat Cost modifiers;
5. calculate the effective Retreat Cost;
6. derive Scoop-Up Block from the opponent's exact represented board;
7. execute the conserved physical Retreat payment and Energy-destination
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

## Regression

The regression composes four previously separate witnesses:

- stale Triple Acceleration Energy self-discards before payment;
- Ignition Energy on a Stage 1 holder refreshes from one unit to three and pays
  Retreat Cost 3;
- Mystery Energy on a Psychic holder reduces base Retreat Cost 2 to zero, while
  an external +2 modifier restores the effective cost to 2;
- a damaged Dashing Pouch holder facing an enabled opposing Mr. Mime
  `sm9-66` derives Scoop-Up Block from the opponent board and sends the paid
  Double Colorless Energy to discard.

## Architectural implication

A Retreat action is increasingly well represented as a typed state program
rather than a function of one integer cost and one list of Energy IDs.

The remaining external modifier tuple is now the principal cost-derivation
boundary. Tool, Ability, Stadium, and attack-applied Retreat modifiers still
need source-aware board/effect derivation before the integer cost can become
fully canonical.
