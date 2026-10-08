# Goal closure: natural target draw and searched target are separate winning branches

## The projection problem

The preceding [exact Teleport discard access bound](../teleport_discard_access_bound/)
required Ultra Ball to **search** a designated Basic Pokémon that remained
in the deck. That captures one particular play path. It undercounts the
larger Bench objective when the designated Pokémon is instead drawn
naturally and held in hand.

The required gameplay goal in the bounded state is:

1. pay Ultra Ball's discard cost using Sky Field and one other approved card;
2. activate a live Gothitelle's Teleport Room to put Sky Field into play;
3. Bench a fixed first Basic already held and the designated second Basic,
   whether the second was drawn naturally or found with Ultra Ball.

For a naturally held second Basic, Ultra Ball's restricted deck search can
choose zero Pokémon. The Item still makes a physical state change by its
mandatory two-card discard and is legally executable.

- Mathematics: [`tools/teleport_discard_goal_closure.py`](../../tools/teleport_discard_goal_closure.py)
- Physical adaptation: [`tools/teleport_discard_payload_line.py`](../../tools/teleport_discard_payload_line.py)
- Regression: [`reproduce.py`](reproduce.py)
- Passing CI: [run 37772427463](https://github.com/FlareZ123/pokemon-workplace/actions/runs/37772427463)

## Canonical correction identified during the investigation

The general `trainer_search_transaction._validated_retrieval_branch`
previously rejected zero-target search whenever the Trainer did not discard
its entire hand. That incorrectly classified a mandatory-cost Trainer as
a free no-op when its searched output was intentionally empty. The shared
validator now rejects a zero-result retrieval **only when** the selected
branch has no other represented physical state change (no entire-hand
discard, no required/paid optional discard). The canonical
`_execute_transaction` layer already used the correct
`discard_cost == 0` physical-change check.

The supporting rulebook provides both necessary clauses:

- I-H, deck searches with type-restricted targets may choose fewer than
  specified, including none; only unrestricted any-card searches require
  the specified count.
- I-B-01, Item actions require a legal state change; Ultra Ball's mandatory
  discard payment changes physical hand/discard zones.

This correction was regression-tested by the physical held-target witness
and the repository's general Trainer-search transaction CI. The broader
consequence is that a failed or deliberately empty restricted search may be
a meaningful *payment transport* action.

## Exact disjoint partition

Let the original unknown pool contain N cards. Prize selection removes p;
a later hand sample reveals h. There is one designated target T, U Ultra
Ball copies, S Sky Field copies, and D approved other discard candidates.
Categories are disjoint.

The original path-only formula counts:

```text
P(target in deck AND U/S/D in hand)
  = (N-p-h)/N * IE(N-1, h; U, S, D)
```

where `IE(M,k; U,S,D)` denotes exact inclusion-exclusion probability
of at least one card from each disjoint group among k cards sampled
uniformly without replacement from M.

The natural-target branch is:

```text
P(target in hand AND U/S/D in hand)
  = h/N * IE(N-1, h-1; U, S, D)
```

Their events are disjoint. The **goal-level probability** is their sum,
assuming either target location leads to the executed Bench objective.

### K0, six random Prizes

Example: N=46, p=6, h=5, U=4, S=2, D=16, T=1.

| Branch | Exact fraction | Percent |
| --- | --- | ---: |
| T remains in deck and is searched | 7280/174537 | 4.171035% |
| T already in sampled hand | 2080/685377 | 0.303483% |
| **Combined goal-level access** | 419120/9366819 | **4.474518%** |

The path-only abstraction excludes 0.303483 percentage points of valid
goal-level successes in this precise state. This added branch is small
because only five cards are seen and the hand must also contain three
other disjoint classes.

### K1, all designated card groups unprized

Condition on a known 40-card non-Prize pool before drawing the next five,
with all four Ultra Ball, both Sky Field, 16 approved discards and T present.

| Branch | Percent |
| --- | ---: |
| T remains in deck for Ultra Ball | 6.793838% |
| T naturally drawn alongside U/S/D | 0.515495% |
| **Goal-level access** | **7.309334%** |

The K1 probabilities condition on this specific Prize configuration,
rather than integrating over random Prizes. Prizing T makes both branches
zero in the isolated model.

## Verification

The symbolic probabilities are checked against exhaustive enumeration
of every Prize subset and every hand subset from three small labeled pools.
The regression physically executes the naturally held branch using the
canonical Ultra Ball retrieval transaction with a zero-target choice, exact
two-card payment, the physical Stadium-copy bridge, Teleport Room, and both
required Bench entries. Every represented card-class total is conserved.
Discarding the wrong two cards blocks the second Bench entry.

CI run `37772427463` passed after fixing the shared zero-target validator.
An earlier failed run is preserved as evidence of the specific previously
blocked semantics.

## Strategic interpretation

Measuring a route's success by whether a *specific search action* retrieves
its designated target can underestimate the value of a line whose actual
objective is to put that target into play. A natural draw can bypass the
search output while preserving the other purpose of the search card,
especially when its payment is being used to change a card's zone.

This underscores the need to define the objective before optimizing a
connector: search-route completion, card-in-hand access, Bench materialization,
and game-level utility are distinct targets.

## Limits

All previous model assumptions remain: Gothitelle is already established
and live, four Bench slots are occupied under Collapsed, ordinary Stadium
play has been spent, another required Basic is already held, and the
specified Ultra Ball + Sky Field payment is the only considered capacity
recovery channel. Neither the Stage 2 setup probability nor opponent
responses are modeled. A naturally held T still counts only when the
three-card U/S/D hand pattern occurs; there may be additional unmodeled
paths for which no Ultra Ball is necessary.
