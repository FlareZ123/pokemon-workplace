# Harto Miki Raichu/Electrode: physical Prized-target Computer Search continuation

## Question

The bounded Dark Asset model has a small target-Prized branch where Quick Ball searches Crobat V, Dark Asset exposes Computer Search, and Computer Search changes its output to Gladion after the deck inspection establishes that Alolan Raichu is Prized.

Can that K0 -> K1 -> zone-adaptive output switch be executed through the repository's physical information-state machinery?

Yes.

Implementation: `tools/raichu_dark_asset_computer_followup_execution.py`  
Regression: `results/raichu_dark_asset_computer_followup_execution/reproduce.py`

## Representative physical world

The action snapshot begins with seven cards in hand, including Quick Ball, three policy-approved discard cards, and protected cards.

The hidden material state contains:

- Crobat V in deck;
- Computer Search in deck;
- Gladion in deck;
- one filler in deck;
- singleton Alolan Raichu in the single face-down Prize slot.

The one-Prize prior assigns equal pre-search probability to Alolan Raichu, Gladion, or filler being Prized. The actor and observer therefore begin from the same public uncertainty.

## Executed line

The exact line is:

`Quick Ball -> discard 1 -> Crobat V -> Bench -> Dark Asset: Computer Search -> discard 2 -> inspect deck -> Gladion`

The first part uses the physical search-to-Crobat bridge:

- Quick Ball pays one exact discard;
- Crobat V moves deck -> hand -> Bench;
- the physical hand falls to five;
- Dark Asset has a one-card draw-to-six window.

The witness makes that exact draw Computer Search.

Computer Search then uses the dedicated private-search transaction:

- Computer Search leaves hand for the resolving-Trainer zone;
- the two remaining policy-approved cards pay its cost;
- full deck inspection establishes K1 for the actor;
- because Alolan Raichu is absent from deck and physically in Prize, the zone-adaptive policy selects Gladion;
- Gladion becomes a private materialized hand instance;
- the remaining filler is materialized as the shuffled top;
- Computer Search moves to discard;
- card-class totals remain conserved.

## Information result

The actor's post-search belief assigns:

- **P(Alolan Raichu is the Prize) = 1**;
- **P(Gladion is the Prize) = 0**.

The observer knows the selection policy and sees the Computer Search action and shuffle, but does not see the private target identity. The observer therefore remains uncertain about the Prize composition.

The same physical truth is shared while information differs by observer.

This is the executable version of the earlier zone-adaptive Computer Search result. The value comes from coupling private full-deck inspection, K1 inference about the singleton target, a state-dependent choice of search output, and a Prize-recovery card useful in the inferred branch.

## Residual-payment gate

The matched failure witness begins with only two policy-approved discard cards.

Quick Ball spends one.

Dark Asset can still draw Computer Search, but only one allowed payment card remains. Computer Search's exact two-card cost cannot be paid without violating the protection policy, so the continuation is rejected.

This confirms that the target-Prized information advantage remains downstream of the same residual DCI gate as the target-in-deck Ultra Ball continuation.

## Why this matters

The K0/K1 abstraction is useful only if the simulator connects information to legal action choice.

Here, Computer Search does more than produce a generic universal-search edge. Its own resolution reveals enough private deck information to change what the player should retrieve.

A faithful state transition therefore carries material state, with Gladion leaving deck for hand, together with epistemic state, where the actor learns the exact Prize composition while the opponent does not.

## Validation boundary

The Computer Search transaction is inherited from `computer_search_private_transaction.py`, including Item-play gating, exact two-card discard selection, private target movement, actor-specific K1, observer-marginalized hidden target identity, shuffle-top materialization, and conservation.

The new bridge only composes that transaction with the already-validated Quick Ball -> Crobat V -> Dark Asset state.

## Limits

The representative information model deliberately uses one Prize slot and a three-card deck-plus-Prize pool so the K0/K1 transition is transparent and independently auditable.

It proves the interaction semantics. It does not reproduce the full six-Prize probability from the Harto model.

The witness also stops with Gladion in hand. It does not spend the Supporter action to exchange Gladion with the Prized Alolan Raichu.

The next exact physical step is therefore a Gladion transition that preserves its literal Prize destination and the Supporter budget.

## Next useful work

Compose this result with the repository's literal Gladion physical Prize transition.

That would execute the full target-Prized material chain:

`Quick Ball -> Crobat V -> Dark Asset -> Computer Search -> K1 -> Gladion -> Alolan Raichu to hand`

and would verify that the correct physical Gladion destination is preserved instead of treating Gladion as an ordinary discarded Supporter.
