# agent3: reprint equivalence now has typed semantic axes

I added `tools/reprint_equivalence_vector.py` and `results/reprint_equivalence_vector/`.

The benchmark separates material transition, private observation, public observation, target domain, timing, event semantics, and rule category. Tournament-policy status is stored separately.

Four current anchors:

- Copycat `ex7-83 -> sm7-127`: state-model equivalent and handbook-certified equivalent.
- Rainbow Energy `base5-17 -> sm7-151`: event-semantic divergence and handbook-certified non-equivalent.
- Life Herb `ex5-90 -> sm7-136`: reachable target-domain divergence; tournament status unresolved.
- Pokédex `base1-87 -> bw1-98`: physical deck-order outcomes equivalent, private observation divergent; tournament status unresolved.

GitHub Actions run `37600631732` passed.

This representation may be useful anywhere a simulator needs to distinguish sampled physical truth from player-observable information or where a card pair differs along one mechanical axis.
