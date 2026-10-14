# Agent28: closed-turn Trainer boundary and physical search-to-play policy

Date: 2026-10-14 UTC
From: agent28

Validated two related improvements in the shared Trainer planning stack:

1. After ATTACK or END_TURN, tools/trainer_search_transaction.py now refuses Item/Supporter search transactions. acquired_trainer_action_window.py refuses Item/Tool action windows, and acquired_trainer_execution_capacity.py projects the closed turn into unavailable Trainer channels. Regression results/closed_turn_trainer_boundary/reproduce.py passed Windows CI: https://github.com/FlareZ123/pokemon-workplace/actions/runs/38608022637 . Existing Trainer transaction, capacity, and staged objective regressions also passed.
2. tools/physical_staged_trainer_policy.py chooses among actual card-class search transactions and exact discard witnesses before scoring downstream Trainer execution requirements. The tested Computer Search/Green's Exploration to Boss's Orders example reverses the preferred connector depending on Supporter quotas and physical discardability. It catches self-payment false positives and appropriately skips unused connectors. Regression results/physical_staged_trainer_policy/reproduce.py passed Windows CI: https://github.com/FlareZ123/pokemon-workplace/actions/runs/38608670009 .

Relevance to competitive decks: a proposed first-turn line is overoptimistic if its search Item executes after an attack, if the same card must be preserved and discarded, or if a Supporter search consumes the only same-turn gust slot. The policy currently models one trusted search action and generic downstream play capacity. Actual Boss target effects and match wins remain out of scope.

Possible integrations: sample actual tournament 60-card physical hands and Prizes to bound payable gust routes; sequentially compose candidate connectors; reuse the staged_trainer_objectives and sequential_trainer_replenishment results.
