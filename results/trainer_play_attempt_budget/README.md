# Trainer play attempts: quota commits after a successful use

## Question

When a card effect intercepts a Supporter or Stadium before it is successfully used, should the once-per-turn quota be consumed at declaration time?

No for the concrete Quaking Fist interaction studied here.

Implementation: `tools/trainer_play_attempt_budget.py`  
Regression: `results/trainer_play_attempt_budget/reproduce.py`

## Concrete Expanded witness

Seismitoad `me55-84` / Quaking Fist is legal in the current bundled paper Expanded pool. Its English text says:

`During your opponent's next turn, whenever they try to use a Trainer card from their hand, they flip a coin. If tails, your opponent discards that Trainer card instead of using it.`

The distinction between **trying to use** and **using** is mechanically decisive.

## Official Supporter retry ruling

The official Japanese Pokémon Card Q&A asks what happens when a player under Quaking Fist tries to use a Supporter, flips tails, and discards it.

It rules that the player may then use another Supporter during the same turn, and the Quaking Fist coin is flipped again.

Official Q&A:
https://www.pokemon-card.com/rules/faq/search.php?page=33

A second current ruling makes the historical predicate explicit. After a Supporter attempt fails Quaking Fist, an attack that requires the player to have used a Supporter that turn does not receive its bonus because the failed card **does not count as having been used**.

Official Q&A:
https://www.pokemon-card.com/rules/faq/search.php?freeword=%E3%82%AB%E3%83%90%E3%83%AB%E3%83%89%E3%83%B3&regulation_faq_main_item1=all

## Official Stadium retry ruling

The same ruling family says that if a Stadium play attempt flips tails, the attempted Stadium is discarded and the player may still play another Stadium that turn. The Quaking Fist coin is flipped again.

It also resolves ordering when another Stadium is already in play: the Quaking Fist coin happens before the old Stadium would be discarded. On tails, the existing Stadium stays in play.

Official Q&A:
https://www.pokemon-card.com/rules/faq/search.php?freeword=%E3%82%B9%E3%82%BF%E3%82%B8%E3%82%A2%E3%83%A0%E3%82%92%E3%83%88%E3%83%A9%E3%83%83%E3%82%B7%E3%83%A5&regulation_faq_main_item1=XY

## Two-phase action model

The ordinary `TurnActionBudget` remains useful, but the play transaction needs two phases.

`begin_trainer_attempt()`:

- verifies the ordinary Supporter or Stadium quota is still available;
- checks the ordinary same-name Stadium restriction;
- moves the selected physical Trainer from hand into a pending attempt;
- does **not** consume the quota.

If Quaking Fist produces tails, `fail_quaking_fist_gate()` moves the pending card to discard. The quota and successful-use history remain unchanged.

If the gate passes, `pass_quaking_fist_gate()` consumes the canonical Supporter or Stadium quota and commits the ordinary play. For Stadiums, only the successful branch replaces the Stadium already in play.

This reproduces the official retry rulings.

## Why eager quota consumption is wrong

A planner that calls `budget.consume(SUPPORTER)` or `budget.consume(STADIUM_PLAY)` as soon as the card is announced cannot represent the official tails branch without rolling the quota back.

Rollback is especially fragile because other state changes can occur around a play attempt. A safer transition boundary is:

`attempt -> pre-use replacement / prevention gates -> commit successful use -> resolve card body`

That boundary also keeps historical predicates coherent. A failed Supporter attempt has a discarded physical card but zero successful Supporters used this turn.

## State distinction

The result separates:

- physical card movement;
- remaining ordinary quota;
- successful-use history;
- pending attempted play;
- existing Stadium state.

A discarded Trainer therefore does not imply that its ordinary action channel was consumed.

## Relation to existing canonical budget work

`turn_action_budget/` correctly models how many successful ordinary Supporter and Stadium uses remain.

This result adds the transactional seam around that budget. The budget should be committed when the play becomes a successful use, after effects such as Quaking Fist have had their pre-use interception window.

The same principle should be audited anywhere a card effect can replace, cancel, or prevent an action before the game considers it successfully performed.

## Limits

The model covers Supporter and Stadium quota behavior under this specific pre-use coin gate. It does not implement arbitrary Trainer bodies, Item semantics, or all replacement/prevention effects.

For Supporters, the successful branch sends the card directly to discard because the regression focuses on quota timing rather than Supporter body destinations. Card-specific destination replacement remains covered by other transaction work such as Gladion.

The result does not assume that every failed action in the game preserves its quota. That conclusion must be established per action grammar and ruling family.
