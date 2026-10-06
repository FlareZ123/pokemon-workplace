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


## Connector timing and typed graph checkpoint

I added two related results after the timed-access baseline:

- tools/supporter_access_catalog.py
- results/gladion_access_connectors/README.md
- tools/typed_access_network.py
- results/typed_access_network/README.md
- results/typed_access_network/reproduce.py

The card-text census finds 37 Expanded-legal card names across 62 prints with literal deck -> Supporter-in-hand wording in the bundled snapshot. Source categories are 10 Pokémon Ability names, 20 attack names, 4 Item/ACE SPEC Item names, and 3 Supporter names. Team Rocket's Transceiver is restricted to Team Rocket Supporters, so it cannot find Gladion.

Important timing/zone distinctions:

- Call Bell, Secret Box, Computer Search, and Xtransceiver are representative same-window Item access routes to Gladion, with card-specific conditions/costs.
- Jirachi-EX, Tapu Lele-GX, Lumineon V, and Meowth ex are Basic Rule Box Pokémon whose Supporter-search Ability requires play from hand onto Bench. Quick Ball/Ultra Ball can search them into hand, then manual benching can fire the trigger. Nest Ball puts the Pokémon directly from deck onto Bench, so the hand-play trigger is absent.
- Battle Compressor -> Gladion to discard -> VS Seeker -> Gladion to hand is a deterministic two-Item same-window route when Items are usable.
- Pokégear 3.0, Random Receiver, Trainers' Mail, and Xtransceiver are stochastic and should not count as full deterministic outs.
- Attack-based Supporter searches reach a later turn because using an attack ends the turn.
- Supporter-based searches such as Misty's Favor, Steven, Skyla, Green's Exploration, Red's Challenge, Teammates, and Team Rocket's Petrel consume the current Supporter window. They can prepare Gladion for a later Supporter window but are not same-window Gladion outs.

The typed access engine formalizes four key regressions:
- Quick Ball -> Tapu Lele-GX -> Wonder Tag -> Gladion succeeds in the current window.
- Nest Ball -> Tapu Lele-GX does not fire Wonder Tag, so no Gladion line.
- Battle Compressor -> VS Seeker -> Gladion succeeds in the current window.
- Skyla -> Gladion fails in the current window but succeeds when one future Supporter window is allowed.

It also proves state-edge removal for Ability lock, a full Bench, and Item lock.

The typed engine is intentionally a small semantic scaffold, not a full TCG simulator. It currently hard-codes representative actions and uses BFS over immutable state.

## Next highest-value action after typed graph

Add an explicit attack boundary plus a representative attack-based Supporter search, then join the deterministic typed network to the exact timed-access probability model. The combined model should preserve deterministic targeted transitions, stochastic branches, random exposure, and Supporter-window consumption instead of treating all connector cards as equivalent outs.


## Clean direct-out combinatorics checkpoint

Added:

- tools/direct_rescue_outs.py
- results/direct_rescue_outs/README.md
- results/direct_rescue_outs/reproduce.py

This exact model follows accepted opening -> Prize cards -> later random exposure and conditions on at least one modeled critical non-starter being Prized. It adds O abstract "clean direct outs": non-starter cards already assumed playable before the current Supporter window, each able to search one real Gladion-like rescuer from deck to hand.

Access succeeds when a real rescuer is exposed, or when an out is exposed and a real rescuer remains in the searchable deck. This preserves the distinction between connector and target.

Baseline: 60 cards, 6 Prizes, 7-card accepted opening, 12 starters, 4 critical non-starter singletons, 2 real rescuers, 8 random non-Prize cards seen.
- P(any critical Prized | valid start) = 35.383108%.
- 0 clean outs: 24.265475% first-rescue access conditional on a critical Prized.
- 2 outs: 43.128752%.
- 4 outs: 57.765545%.
- 6 outs: 68.998807%.
- 8 outs: 77.517529%.

Treating outs as literal extra Gladion copies slightly overstates access because an out fails when all true Gladion copies are unavailable to search. At 8 cards seen the overstatement is 0.083261 pp for 1 out, 0.156779 pp for 2, 0.278397 pp for 4, and 0.442446 pp for 8.

The result is deliberately favorable to the connector. Concrete cards such as Secret Box, Computer Search, Call Bell, or Xtransceiver need separate state-specific AMR/cost/timing treatment.

The reproducer has an exhaustive labeled-permutation check on an 8-card regression case and matches the exact combinatorial result.

## Current next step

Integrate typed connector events with the multi-window timed-rescue model. The immediate design target is to preserve physical Gladion topology while letting a connector create a targeted arrival before a Supporter window, with route-specific conditions rather than increasing the Gladion count or cards_seen.
