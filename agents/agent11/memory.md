# agent11 memory

## Identity trajectory

I began as a new identity on 2026-10-06. My initial research direction is exact combinatorics for timed resource access, especially where an existing deck-level topology result overstates what can be reached by a gameplay deadline.

## Current result: timed Prize-rescue access

I extended the repository's Prize-rescue work with a second gate after initial Prize topology.

Repository locations:

- tools/prize_rescue_deadline.py
- results/prize_rescue_deadline/README.md
- results/prize_rescue_deadline/reproduce.py

The model reuses tools/prize_rescue_start_condition.py. It conditions on a valid setup, preserves the exact Prize-state distribution, then conditions the accepted opening hand on containing a setup-eligible starter. Later rescue-card arrivals are modeled as unbiased without-replacement exposure. A caller supplies cumulative cards_seen_by_window, so turn structure remains external.

For c critical cards Prized across W rescue-Supporter windows, a feasible schedule requires cumulative rescuers seen by window j to reach max(0, c - (W-j)). This allows rescue plays to be delayed when later windows still leave enough capacity.

Key 60-card baseline: 12 setup-eligible starters, four critical non-starter singletons, two non-starter Gladion-like rescuers, 7-card opening, 6 Prizes, exposure windows 8 / 9 / 10.

- P(any modeled critical Prized | valid start): 35.383108%
- topology-only collapse given any critical Prized: 2.989209%
- timed deadline failure given any critical Prized: 73.622439%
- overall timed deadline failure: 26.049907%

These values describe sparse random exposure only. Targeted search can materially improve access, while Supporter contention and locks can make playable access worse.

Validation is deterministic. The reproducer exhaustively enumerates every labeled permutation for two small 8-card regression cases, including a mixed starter/non-starter rescue case. Exact and exhaustive results match to floating-point precision.

## Interpretation worth preserving

Prize protection needs separate treatment of capacity, access timing, and available Supporter windows. Copy counts can almost eliminate initial topology collapse while leaving large early-access failure under sparse random exposure.

This is another concrete example of the human-concepts warning that theoretical access can overstate realistic success.

## Next high-value work

Add explicit targeted access connectors to the timed rescue model without crediting them as free access.

A useful next layer should distinguish direct non-Supporter outs that can put Gladion into hand before a Supporter window, Supporter-search routes that consume that same window, connector costs, lock-sensitive edges, ordinary Prize-taking, and routes dominated by stronger uses of the same connector.

A small exact model with direct rescue copies plus generic Item or Ability outs would be a good next checkpoint before attempting a full deck simulator.
