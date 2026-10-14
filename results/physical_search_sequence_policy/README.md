# Bounded exact physical search sequencing

## Question

Can a search planner discover and execute an ordered two-connector route when the second Trainer is itself retrieved by the first, and the second's optional discard cost is paid by other outputs produced during the first search?

The existing hand-written Secret Box -> Guzma & Hala regression established that such a line is possible. This study tests whether a reusable planner can discover the sequence without being given its legal order.

## Implementation

tools/physical_search_sequence_policy.py performs bounded ordered exploration over trusted exact search actions. Every step calls the canonical execute_trainer_retrieval_transaction on the evolving exchangeable card-class state. It enumerates fresh discard witnesses *after* the played Trainer is removed from hand. Search targets are physically depleted from the deck, and previously generated cards can be used to pay later costs. It never double-uses a provided option; multiple physical uses must be supplied separately. A no-action choice and each intermediate prefix are scored too.

The objective is generic downstream Trainer-play capacity in declared turn windows. The optimization maximizes completed objectives, then prefers fewer discarded cards and fewer used connectors.

## Representative print-checked chain

The fixture verifies Secret Box (sv6-163), an Item ACE SPEC with a three-other-card payment, and Guzma & Hala (sm12-193), a Supporter with an optional two-other-card payment.

The starting hand contains Secret Box plus exactly three disposable cards. Deck targets are a search Item, search Tool, Guzma & Hala, Stadium, second Tool, second Stadium, and Special Energy. The option list deliberately presents Guzma & Hala before Secret Box. The planner must discover that Guzma & Hala is unavailable until searched.

1. Secret Box spends the three starting fodder cards and searches an Item, Tool, Guzma & Hala, and Stadium.
2. Retrieved Guzma & Hala plays as this turn's Supporter, spending the newly generated Item and Stadium as its two discard payments. The first Tool is protected from discard.
3. Guzma & Hala retrieves its Stadium, Tool, and Special Energy, leaving both distinct Tools in hand for a *generic* two-Tool execution goal.

| Controlled case | Maximum generic Tool executions |
| --- | ---: |
| Only one search action permitted | 1 / 2 |
| Two ordered physical actions allowed | 2 / 2 |
| Only two initial fodder cards | 0 / 2 |
| Supporter play locked | 1 / 2 |
| Tool play locked | 0 / 2 |
| Turn already ended | 0 / 2 |

The successful route spends five cards in discard payments while only three disposable cards were in the initial hand. It conserves every physical card class and preserves the first Tool.

## Interpretation and limitations

This is a deterministic exact-state execution result. The planned Tool objectives require card-specific valid attachment targets and Bench space that the generic scheduler does not check; they must not be read as actual completed Tool attachments. The second Tool has value only if it serves a real game plan. It is a search-policy infrastructure result, with no simulation of opposing play or match-win measurement.

The execution options have already been compiled and narrowed to their trusted target domains. The planner does not exhaustively generate all legal retrieval options itself; caller-supplied options describe a finite candidate action family. An extension should generate candidates from verified source text and physical Prize/hand state, then compare reachable attack or lock endpoints rather than mere Trainer play bandwidth.

Run results/physical_search_sequence_policy/reproduce.py or manually dispatch .github/workflows/validate-physical-search-sequence-policy.yml. The focused workflow also runs the original single-action and sequential-replenishment regressions.
