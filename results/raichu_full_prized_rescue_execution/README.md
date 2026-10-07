# Harto Miki Raichu/Electrode: full physical singleton Prize rescue

## Question

Can the deck-specific target-Prized continuation be carried all the way from the initial Quick Ball action to Alolan Raichu physically entering the hand?

Yes.

Implementation: `tools/raichu_full_prized_rescue_execution.py`  
Regression: `results/raichu_full_prized_rescue_execution/reproduce.py`

## Complete representative line

The executed line is:

`Quick Ball -> Crobat V -> Dark Asset: Computer Search -> Computer Search: Gladion -> Gladion: Alolan Raichu`

The initial physical world has singleton Alolan Raichu in the face-down Prize zone, Gladion in deck, Computer Search in deck, Crobat V in deck, and three policy-approved discard cards in the seven-card action snapshot.

### 1. Quick Ball

Quick Ball consumes one approved discard card and searches Crobat V.

Crobat V moves deck -> hand -> Bench.

The hand reaches five cards, establishing a one-card Dark Asset window.

### 2. Dark Asset

The exact Dark Asset draw is Computer Search.

The hand returns to six cards.

### 3. Computer Search

The two remaining approved discard cards pay Computer Search.

The private full-deck inspection establishes that Alolan Raichu is absent from deck and therefore Prized in this representative world.

The zone-adaptive target policy selects Gladion.

Gladion becomes a private physical hand instance while the actor's Prize belief collapses to K1.

### 4. Gladion

The new Supporter-budget bridge consumes the ordinary Supporter window.

Gladion selects the known singleton Alolan Raichu Prize.

Literal physical resolution moves:

- Alolan Raichu: Prize -> hand;
- played Gladion: hand -> Prize.

With one Prize slot in the representative information model, the post-Gladion shuffle has one physical ordering.

## Final state

The regression verifies:

- **Alolan Raichu is in hand**;
- Gladion is in Prize;
- Crobat V is on the Bench;
- Quick Ball and Computer Search are in discard;
- all three approved discard cards are in discard;
- protected cards remain in hand;
- the Supporter budget is spent;
- the shuffled deck top is preserved through Gladion;
- every represented card-class total is conserved.

## What this closes

Earlier Raichu results progressively established:

1. the singleton can be Prized;
2. Computer Search can use deck inspection to infer that state;
3. the connector can change its target to Gladion;
4. Crobat V and Dark Asset can expose the connector;
5. residual discard capacity gates the continuation.

This result closes the remaining physical endpoint.

The modeled access event now corresponds to an executable material line whose final zone actually contains the target card.

That distinction matters because ending at "Gladion is accessible" is weaker than proving that Supporter bandwidth remains, Gladion can be played from hand, and its literal Prize cycle ends with the intended singleton in hand.

## Relation to the probability model

This result is a semantic witness rather than a new 60-card probability.

The exact 60-card probability remains in `raichu_dark_asset_followup/`. The physical chain validates one representative target-Prized success state from that model.

Together, the two layers separate:

- **how often** the state occurs;
- **whether** the claimed success state really executes under the game-state semantics.

## Limits

The information witness still uses one Prize slot and a minimal hidden pool to isolate the K0/K1 mechanism.

A full six-Prize physical enumerator would be much larger and is unnecessary for validating the local transition semantics already handled combinatorially.

The line also assumes an open Bench, no Item or Ability lock, no competing Supporter need, and the stated discard policy.

It does not evaluate whether recovering Alolan Raichu is tactically correct in a particular matchup.

## Next useful work

The strongest next deck-specific extension is to add competing uses for the same resources.

In particular, compare this rescue line against alternative Computer Search outputs or a competing Supporter requirement. That would turn the current reachability witness into a connector-domination policy question and quantify the opportunity cost of spending Computer Search plus the turn's Supporter window on Prize recovery.
