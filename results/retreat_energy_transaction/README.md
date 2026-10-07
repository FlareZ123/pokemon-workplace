# Conserved Retreat Energy transaction

## Question

Can one immutable transaction compose:

- the canonical per-turn Retreat quota;
- exact physical Retreat Cost payment;
- Active-to-Bench movement;
- Special Condition and temporary-effect clearing;
- Dashing Pouch destination replacement;
- Scoop-Up Block's hand prohibition;
- Prism Star discard replacement;
- aggregate Energy-zone conservation?

## Result

Yes, for the currently supported destination rules.

Implementation: `tools/retreat_energy_transaction.py`  
Regression: `results/retreat_energy_transaction/reproduce.py`

The transaction begins from one `UnifiedState` that owns the authoritative
`TurnActionBudget` and one `EnergyBoardState` that owns physical Energy
attachments plus aggregate zone counts. The board's legacy `retreat_used`
boolean must mirror the canonical budget.

Mechanical Retreat is first evaluated on an immutable candidate through
`retreat_with_canonical_budget()`. Only after a legal payment and board
movement exist does the transaction analyze the destination of each selected
physical Energy card.

## Dashing Pouch witness

The bundled card pool contains Dashing Pouch `sm4-92`:

> If the Pokemon this card is attached to discards Energy for its Retreat Cost,
> put that Energy into your hand instead of the discard pile.

The official Japanese Dashing Pouch Q&A separately confirms that a Pokemon with
Retreat Cost 2 and two attached Double Colorless Energy cards may return both
DCE cards to hand and retreat.

The regression starts from exactly that two-DCE geometry. Selecting both DCE
copies:

- consumes one canonical Retreat use;
- removes both physical Energy instances from the outgoing Active;
- swaps the Active with the chosen Benched Pokemon;
- clears Poisoned and a temporary attack effect from the outgoing Pokemon;
- keeps Dashing Pouch attached to that Pokemon;
- moves both DCE card-class copies from `attached` to `hand`;
- dematerializes both board-level Energy instance IDs.

Selecting only one DCE from the same starting state is also legal for Retreat
Cost 2. It returns one DCE to hand and leaves the other physically attached.
The two payment witnesses therefore reach different conserved continuation
states.

## Scoop-Up Block boundary

The existing destination analysis is reused rather than reimplemented.

When the outgoing holder is damaged and opposing Scoop-Up Block is active,
Dashing Pouch's hand route is prohibited. The same one-DCE payment enters
`discard` instead.

This demonstrates that payment selection and destination selection are separate
stages. The physical cards selected for payment are known before replacement
rules determine their final zones.

## Unresolved Prism Star conflict stays uncommitted

The repository deliberately has no claimed authority for Dashing Pouch plus a
Prism Star Energy when both hand and Lost Zone replacement proposals remain
live.

The composed transaction preserves that evidence boundary. It can evaluate the
mechanically legal Retreat on an immutable candidate, detect the unresolved
destination conflict, and return the original state with:

- zero canonical Retreat uses spent;
- original board topology;
- original attached Energy counts;
- an explicit conflict record.

If Scoop-Up Block removes the hand proposal for a damaged holder, the remaining
Prism Star route deterministically sends the selected Energy to the Lost Zone
and the transaction commits.

## Architectural implication

A successful Retreat is an ordered state program:

1. verify turn quota and Retreat permission;
2. validate an exact physical Energy payment witness;
3. construct the board movement and clear outgoing-Active transient state;
4. resolve per-card destination replacements and prohibitions;
5. move aggregate card classes from `attached` to their final zones;
6. consume the canonical Retreat use only in the committed state.

The immutable candidate step is important. A simulator should not spend the
Retreat action or move a physical card while a replacement conflict is still
unresolved.

## Limits

The transaction accepts already-resolved upstream facts for opposing Scoop-Up
Block activity and which selected Energy instances are Prism Star cards.
Continuous Ability suppression, opponent-board geometry, and Prism Star
identification from exact print metadata remain outside this adapter.

The Dashing Pouch plus Prism Star conflict intentionally stays unresolved until
stronger rules authority is available.
