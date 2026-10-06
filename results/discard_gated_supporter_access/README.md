# Discard-gated Supporter access: exact AMR correction

## Question

If an Item can search a target Supporter during the current Supporter window, how much does a realistic discard requirement reduce the access probability compared with a raw graph edge?

This result connects the repository's discard-gate work to the typed Supporter-access work. It isolates a Computer Search-like or Secret Box-like connector that preserves the Supporter play while requiring disposable cards in hand.

Implementation: `tools/discard_gated_supporter_access.py`  
Reproducer and exhaustive validation: `results/discard_gated_supporter_access/reproduce.py`

## Relation to prior work

`results/discard_cost_amr/` established an exact hypergeometric baseline for discard-gated actions in a sampled hand. It showed that card presence can substantially exceed practical payability when the hand contains too few acceptable discard targets.

`results/supporter_outs_timing/` showed a different source of overstatement: a connector can reach a target Supporter while consuming the Supporter action required to play it.

The present result holds timing favorable. The connector is assumed to preserve the Supporter play. It then measures the access lost solely because the connector's discard cost cannot be paid from the modeled hand.

## Model

The deck is partitioned into:

- target Supporters;
- copies of a discard-gated connector;
- non-starter cards currently acceptable to discard;
- setup-eligible starters, all treated as protected from discard;
- protected non-starters.

The model:

1. conditions the seven-card opening hand on containing at least one setup-eligible starter;
2. sets Prize cards from the remaining deck;
3. optionally samples later random draws;
4. checks whether the target Supporter is already accessible;
5. if the target is absent from hand, checks whether a connector is accessible and a target copy remains in the searchable deck;
6. applies the discard gate.

The binary disposable/protected partition follows the narrow DCI abstraction used by the earlier discard model. It is state-dependent by construction: the caller chooses how many non-starters are acceptable to discard in the modeled state.

Setup starters are deliberately protected in this first integration. This avoids treating the Pokémon required to satisfy setup as generic discard fodder.

## Access definitions

**Direct target access** means at least one target Supporter is in the accessible hand.

**Naive access** means direct target access, or a connector is in hand while a target remains in the deck. This is the reachability-graph answer if the discard cost is ignored.

**Gated access** additionally requires enough modeled disposable cards in hand to pay the connector's discard cost.

**Gate overstatement** is the probability mass where naive access says the line exists and the discard-aware model says the connector cannot be paid.

## Illustrative baseline

Use:

- 60 cards;
- 6 Prize cards;
- a valid 7-card opening;
- 12 protected setup-eligible starters;
- 2 copies of the target Supporter;
- 1 discard-gated connector;
- no additional random draws before the access check.

Raw reachability is the same in every row because the connector count and target count are fixed:

`P(naive current-window access) = 29.837458%`

Direct target access is:

`P(target already in hand) = 20.931886%`

The connector is therefore uniquely needed in 8.905572% of accepted starts under this composition.

| Disposable non-starters | Discard cost | Gated access | Naive overstatement | Payable given connector route is needed |
| ---: | ---: | ---: | ---: | ---: |
| 10 | 2 | 23.126607% | 6.710851% | 24.645% |
| 10 | 3 | 21.332333% | 8.505124% | 4.480% |
| 15 | 2 | 25.004046% | 4.833411% | 45.727% |
| 15 | 3 | 22.195621% | 7.641837% | 14.188% |
| 20 | 2 | 26.735410% | 3.102048% | 65.167334% |
| 20 | 3 | 23.525132% | 6.312326% | 29.119362% |
| 25 | 2 | 28.092546% | 1.744912% | 80.407% |
| 25 | 3 | 25.138757% | 4.698701% | 47.236% |
| 30 | 2 | 29.007500% | 0.829958% | 90.680% |
| 30 | 3 | 26.779627% | 3.057831% | 65.664% |
| 35 | 2 | 29.525047% | 0.312411% | 96.492% |
| 35 | 3 | 28.187314% | 1.650144% | 81.471% |

The payability percentages above are conditional on a state where the target is not already in hand, the connector is in hand, and at least one target remains in the deck.

## Finding 1: a favorable timing class can still have low AMR

With 20 disposable non-starters, the two-card connector is payable in 65.17% of connector-dependent states. The three-card connector is payable in only 29.12%.

Both connectors are temporally capable of finding and then playing the target Supporter in the same window. Their realistic access differs because the hand-cost channel differs.

This is a direct quantitative example of why temporal typing and DCI need to coexist. An edge can be correctly classified as same-window and still be unavailable in many actual hands.

## Finding 2: raw access can hide a large cost difference

At 20 disposable non-starters:

- raw graph access: 29.837458%;
- cost-two gated access: 26.735410%;
- cost-three gated access: 23.525132%.

A reachability graph that treats both as deterministic one-card outs assigns them the same access value. The exact gate model separates them by 3.210278 percentage points of total current-window access in this composition.

The difference is larger when the disposable pool is smaller.

## Finding 3: discardability density matters more for higher costs

At 10 disposable non-starters, a three-card connector is payable in only a small fraction of connector-dependent states. At 35 disposable non-starters, it becomes usable in a large majority of those states.

This aligns with the human-developed DCI idea: card identities alone do not determine whether a discard cost is realistic. The current state's disposable-card distribution does.

The scalar "number of disposable cards" remains a coarse abstraction. A real hand can contain cards with different strategic discard costs, matchup dependence, and future value.

## Computer Search and Secret Box interpretation

Computer Search discards two cards and searches for any card. Secret Box discards three cards and can search a Supporter together with other Trainer categories.

For the narrow question "can this card produce a target Supporter in the current window?", the modeled timing is similar and the discard costs differ.

That does not make Secret Box a strictly worse connector. Its multi-axis search can satisfy several needs at once, which can justify the extra discard cost. This result isolates only target-Supporter access and therefore intentionally excludes the additional value of the other cards Secret Box can obtain.

Likewise, Computer Search may have a strategically superior competing target. The existence of a payable Gladion line does not establish that spending Computer Search on Gladion is optimal.

## Validation

The reported calculations are exact; no Monte Carlo sampling is used.

The reproducer independently exhausts a small 10-card deck over:

- every accepted opening-hand subset;
- every disjoint Prize subset;
- every disjoint future-draw subset.

It compares direct access, naive access, gated access, overstatement, connector-needed probability, and conditional connector payability. All values match the category-based exact model to floating-point precision. The total state mass is also asserted to be one.

## Limitations

The model deliberately isolates one binary discard gate.

It does not model:

- graded DCI values;
- specific card identities among the disposable pool;
- cards that become disposable only after another action;
- cards that should be discarded proactively;
- multiple competing discard effects;
- setup Pokémon leaving the opening hand in a way that changes a more detailed hand model;
- targeted search for the connector;
- stochastic connectors;
- Bench requirements;
- lock effects;
- Supporter contention after the target is obtained;
- multi-axis value from Secret Box;
- competing uses of Computer Search;
- ordinary Prize-taking or full gameplay.

The connector is assumed to search deterministically once its cost is paid.

## Next useful work

The strongest next extension is to insert the discard gate into `tools/prize_rescue_connector_turns.py`.

That model can distinguish:

- a preserving connector that is in hand but currently unpayable;
- a preserving connector that becomes payable after later draws;
- a connector whose payment discards resources that would otherwise matter.

The first version can keep the disposable/protected split binary. A later version can replace it with a state-dependent DCI policy or explicit card classes.
