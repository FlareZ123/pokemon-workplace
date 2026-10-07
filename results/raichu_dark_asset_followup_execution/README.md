# Harto Miki Raichu/Electrode: physical bounded Dark Asset follow-up

## Question

The exact probability model attributes most of its bounded post-Dark-Asset gain to the Quick Ball branch.

Can one representative success and one representative failure be executed against conserved physical card state?

Yes.

Implementation: `tools/raichu_dark_asset_followup_execution.py`  
Regression: `results/raichu_dark_asset_followup_execution/reproduce.py`

## Success witness

The starting action snapshot has seven cards in hand:

- Quick Ball;
- three cards explicitly allowed by the discard policy;
- three protected cards.

The deck contains Crobat V, Ultra Ball, and Alolan Raichu.

The exact physical sequence is:

1. Quick Ball leaves hand and resolves.
2. One allowed card pays Quick Ball's discard cost.
3. Crobat V moves from deck to hand.
4. Crobat V moves from hand to the Bench, leaving five cards in hand.
5. Dark Asset's exact one-card draw is represented by moving Ultra Ball from deck to hand.
6. Two remaining allowed cards pay Ultra Ball's discard cost.
7. Alolan Raichu moves from deck to hand.

Final material state therefore contains:

- Quick Ball and Ultra Ball in discard;
- all three disposable cards in discard;
- Crobat V on the Bench;
- Alolan Raichu in hand;
- all three protected cards still in hand.

Every represented card-class total is conserved.

## Residual-payment failure witness

A matched starting snapshot contains only two allowed discard cards.

Quick Ball can still pay one and reach Crobat V. Dark Asset can still expose Ultra Ball.

One allowed card remains afterward.

The follow-up Ultra Ball needs two other cards and the protected policy refuses to spend the protected cards, so the bounded continuation is rejected.

This is the executable form of the threshold used in `raichu_dark_asset_followup`: the Quick Ball branch needs at least three initially acceptable discard cards for a newly drawn cost-two connector to remain playable.

## Strategic implication

The physical witness shows why a draw-engine hit cannot be scored independently of the path that produced the draw.

Ultra Ball is a successful Dark Asset draw only when the state after Quick Ball still supports Ultra Ball's payment.

The relevant state variable is therefore residual discard capacity after prior actions, together with the identities that policy permits spending.

This extends the deck-specific DCI chain from immediate connector payability into continuation feasibility:

`initial discard policy -> Quick Ball payment -> Crobat entry -> Dark Asset draw -> residual discard policy -> Ultra Ball payment -> target access`

## Validation boundary

The witness uses the shared canonical Trainer transaction for both Items. It inherits:

- the temporary resolving-Trainer zone;
- exact discard selection;
- Item-play channel checks;
- typed search-target consumption;
- deck-to-hand movement;
- final Trainer disposal;
- card-class conservation.

The prior `raichu_search_to_crobat_execution` bridge owns the Crobat Bench entry and Dark Asset draw width.

The only additional physical event introduced here is the exact Dark Asset draw of Ultra Ball, represented as one deck-to-hand move.

## Limits

This result validates one target-in-deck continuation. It does not represent the target-Prized Computer Search -> Gladion branch.

It also does not yet carry observer-relative deck/Prize beliefs through Quick Ball's revealed search and shuffle, model one-use Ability identity for Dark Asset, or score alternate uses for Ultra Ball and the three discard cards.

The success witness establishes mechanical reachability under the supplied policy. It does not claim that spending all three disposable cards is strategically optimal in a real game.

## Next useful work

The remaining high-value physical branch is the target-Prized continuation:

`Quick Ball -> Crobat V -> Dark Asset draws Computer Search -> Computer Search -> Gladion`

The repository already contains `computer_search_private_transaction.py`, which carries exact payment, K1 inspection, private target selection, shuffle, observer-relative beliefs, and conservation. Composing that transaction with the search-to-Crobat bridge would connect the Raichu K0/K1 result to the physical information-state machinery.
