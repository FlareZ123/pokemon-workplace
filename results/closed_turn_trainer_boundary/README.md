# Closed-turn Trainer execution boundary

## Question

Can a search Item or an already-held Item/Tool still execute after an attack, when the canonical turn-action budget has already ended the turn?

Under the rulebook's attack resolution, an attack ends the attacking player's turn. The general Trainer action window is therefore closed, independently of whether Item or Tool play was previously locked. A subsequent extra turn is a new window, not a continuation of the spent turn.

## Discovered implementation gap

Before this correction, the conservative Item/Supporter search transaction checked the Item lock channel but not the budget's \`turn_ended\` state. The acquired-Trainer action-window bridge likewise checked Item/Tool channels without checking whether the turn was over. The finite-capacity projection inherited the same problem: its Supporter and Stadium quotas were zero after turn end, but it could still count Item or Tool plays.

This creates false positive action sequences for setup-and-attack optimizers, including any line mistakenly scheduling more Item search after its attack.

## Fix

- \`tools/trainer_search_transaction.py\` rejects any new search transaction when \`state.budget.turn_ended\` is true.
- \`tools/acquired_trainer_action_window.py\` reports a closed play window for held Trainers after the turn ends, even when the underlying lock channel is open.
- \`tools/acquired_trainer_execution_capacity.py\` projects a closed turn into four unavailable Trainer subtype play channels, while preserving the original state and unrelated channel properties.

## Regression

\`reproduce.py\` uses the bundled actual Secret Box multi-output search profile and its three-other-card payment. The same frozen hand and deck permit the transaction before attacking and reject it after either ATTACK or END_TURN. Existing held Item and Pokémon Tool copies remain physically in hand but have no same-turn execution window. A fresh explicit next-turn window permits both again.

The regression composes the existing exact retrieval transaction, finite-capacity scheduler, action budget, and acquired-card bridge. It verifies per-card zone conservation on the successful turn and checks that the ended-turn correction applies to four Trainer channels.

## Limits

This is a deterministic legality and execution-window regression, not a full match simulation. It does not cover attempts interrupted during Trainer play, card-specific Tool targets, Stadium same-name rules, effect-based turn-end exceptions, or complete attack resolution. The finite-capacity scheduler still assumes trusted future turn-window inputs.

Run the focused and existing related regressions with the manual GitHub Actions workflow \`.github/workflows/validate-closed-turn-trainer-boundary.yml\`.
