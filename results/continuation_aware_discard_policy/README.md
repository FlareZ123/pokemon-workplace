# Continuation-aware discard policy

## Question

Can discard legality be derived from future conserved replacement routes instead of freezing a current required card as permanently protected?

Yes.

This result adds a generic policy seam:

`state -> exact discard witness -> legal continuation -> endpoint check -> DCI ranking`

Implementation: `tools/continuation_discard_policy.py`  
Reproducer: `results/continuation_aware_discard_policy/reproduce.py`

## Representation

`continuation_feasible_discards()` first enumerates exact mechanical discard selections from the current hand.

For each selection, a caller-supplied continuation generator executes future game actions using the repository's normal transition layers. The filter keeps only selections whose resulting state satisfies the declared endpoint requirements.

The filter does not guess future mechanics. In this regression the continuation generator enumerates every typed Guzma & Hala retrieval and executes each through `trainer_search_transaction.py`, including its resolving-Supporter state, exact two-card discard, Supporter quota, and conserved deck-to-hand movement.

After feasibility has been established, `rank_continuation_discards()` can apply additive DCI-style desirability. Scalar DCI therefore remains an objective over future-valid witnesses instead of defining legality itself.

## Concrete Secret Box state

The reproducer first executes Secret Box from a three-filler opening.

Secret Box retrieves:

- Tag Call;
- TM: Evolution;
- Guzma & Hala;
- Artazon.

The next decision is Guzma & Hala's two-card discard. The current hand contains Tag Call, TM: Evolution, and Artazon as the three candidate payloads.

The endpoint requires:

- one TM: Evolution;
- one Artazon;
- one Jet Energy.

The look-ahead policy receives no manually selected reacquisition mode. It enumerates all legal Guzma & Hala retrieval vectors from the exact remaining deck and discovers which discard pairs have at least one endpoint-satisfying continuation.

## Replacement-channel result

The future-feasible discard pairs change exactly with physical replacement availability:

| Copies before Secret Box | Replacement copies after Secret Box | Future-feasible two-card discards |
| --- | --- | --- |
| 2 TM, 2 Artazon | TM and Artazon | Tag+TM, Tag+Artazon, TM+Artazon |
| 2 TM, 1 Artazon | TM only | Tag+TM |
| 1 TM, 2 Artazon | Artazon only | Tag+Artazon |
| 1 TM, 1 Artazon | none | none |

These classifications are derived from exact continuations. The policy is not told that TM or Artazon is expendable.

When Tag Call is added to the endpoint requirements and both replacement channels are live, only `TM + Artazon` remains a safe two-card discard. The continuation must restore both payload classes so Tag Call can remain in hand.

## DCI ranking after future feasibility

With both replacement channels available, assign illustrative discard desirability:

- TM: Evolution = 1.0;
- Tag Call = 0.8;
- Artazon = 0.1.

All three discard pairs are future-feasible for the smaller endpoint. The DCI ranking selects `Tag Call + TM: Evolution` with additive score 1.8.

If the replacement TM is removed from the deck, that same pair disappears from the legal witness family before ranking.

This gives DCI a stronger state-dependent interpretation: the score can rank a current copy highly only after future replacement reachability has been established.

## Finding

Discardability is a continuation property.

The current hand alone is insufficient to classify a required copy. Two states can have the same hand but different safe discard sets because the deck contains different replacement copies or because the endpoint retains different obligations.

A practical planner can therefore derive transient DCI behavior by:

1. enumerating exact current discard choices;
2. exploring legal continuations up to the relevant deadline;
3. rejecting choices whose continuations cannot restore required resources;
4. ranking the surviving choices with tactical or heuristic value.

This directly implements the replacement logic previously supplied manually in the reacquisition experiments.

## Limits

The generic policy seam accepts a continuation generator supplied by the caller. The current result uses one future Supporter action and one endpoint deadline.

It does not yet perform unbounded search over arbitrary action graphs, opponent responses, hidden Prize uncertainty, or multi-turn policies.

The additive DCI example is illustrative. Future-value interactions can still require non-additive objectives after feasibility filtering.

## Next useful work

A bounded action-graph planner can supply the continuation generator automatically.

Useful extensions include:

- depth-limited same-turn search over typed Trainer actions;
- deadline-aware continuation across turn boundaries;
- belief-weighted replacement reachability when a replacement copy may be Prized;
- connector opportunity cost, so preserving the only search connector can outweigh an otherwise legal payload replacement.
