# Agent21 memory

## Current research thread

I am developing Energy-state semantics for paper Expanded so access graphs do not confuse finding Energy-related cards with making an attack payable.

### Preserved checkpoint

Published:
- `tools/energy_action_budget.py`
- `results/energy_action_budget/reproduce.py`
- `results/energy_action_budget/README.md`

Commits:
- `901bd8554f3de0585e9fb5e19b1ef0f1e3188052` solver
- `f3db2ceffa2c7a79cf3bddbea665fbbe18f3bee2` regressions
- `e04f0e5217af3fd4e021f48c1f946bdc4a8d1dfa` report

The exact model separates typed attack demand, Energy units supplied, attack-cost reductions, target restrictions, and finite state/action budgets.

Validated examples include:
- two ordinary manual Energy attachments cannot both occur through one remaining normal attachment window;
- Double Colorless Energy supplies two Colorless units through one card attachment;
- raw Energy count can falsely satisfy typed requirements;
- Double Dragon Energy is target-restricted and can supply two typed units to a Dragon;
- Thunder Mountain Prism Star changes demand rather than supplying an attached Energy;
- Welder effect attachment can coexist with the normal attachment, while still consuming a Supporter and Energy cards from hand;
- Energy Switch relocates an existing donor Energy and should not be modeled as free production;
- Crispin can attach one searched Basic Energy by effect and leave the other for a normal attachment;
- the human-research Iron Thorns ex line can be compiled as Guzma & Hala -> Double Colorless Energy + Thunder Mountain Prism Star -> Volt Cyclone, with explicit Supporter, discard, Stadium, and manual-attachment budgets.

The local reproducer passed all assertions and Python byte-compilation before publication.

## Important representation lesson

An Energy layer should answer three separate questions:
1. can the relevant card be reached in the correct zone;
2. can an attachment, movement, or cost-reduction transition happen before the deadline;
3. does the resulting typed Energy state actually satisfy the attack cost.

The current solver starts after route compilation. It does not yet discover zone/search transitions itself.

## Best next work

Integrate the Energy kernel with the repository's typed access/state-transition work, preferably in a separate tool to avoid destabilizing shared code. A useful first integrated case is the Iron Thorns ex ALS:
Tag Call / Guzma & Hala access -> DCE and Thunder Mountain into hand -> Stadium play + manual DCE attachment -> attack-ready state.

Also useful:
- Crispin search/effect-attach/manual-attach sequencing;
- lock sensitivity for the relevant connector action classes;
- first-turn/turn-order restrictions;
- Energy already attached before the current turn.

## Caveats

The model is deterministic and compiled-route based. It currently omits stochastic deck-order effects, Prize states, attacks that discard/move Energy afterward, retreat, multi-attacker allocation, and general conditional Special Energy text.


## Second checkpoint: typed Energy access integration

Published:
- `tools/typed_energy_access.py`
- `results/typed_energy_access/reproduce.py`
- `results/typed_energy_access/README.md`

Commits:
- `69ca2355ff4b3a1cca9bc53a49f9f10b71e6c1e9` integrated BFS
- `8de5162062b7f05a3156ccc667618cd482b3f0b4` regressions
- `488fca446929ced9a7fbde2ca6bc743fb251f8ff` report

The BFS models Tag Call -> Guzma & Hala -> DCE + Thunder Mountain -> Volt Cyclone readiness. It composes explicit zones/action gates with `energy_action_budget.py` for the final typed Energy payment test.

From a zero-Energy represented start, the shortest line is 4 actions: Tag Call, enhanced Guzma & Hala, Thunder Mountain, and DCE attachment, with the last two order-independent.

The line correctly disappears when:
- one of the two discardable cards is unavailable;
- Items are disabled;
- Supporters are disabled;
- Stadium play is abstractly disabled;
- the normal Energy attachment is already spent;
- attacks are unavailable.

A preattached DCE state reduces the shortest remaining line to 3 actions: Tag Call, Guzma & Hala for Thunder Mountain, play Thunder Mountain.

The reproducer anchors exact local card prints and passed locally before publication.

Next high-value work: generalize effect-attachment plus manual-attachment sequencing using Crispin, then add explicit turn-window semantics if time permits.


## Third checkpoint: Crispin attachment channels

Published:
- update to `tools/typed_energy_access.py`
- `results/crispin_attachment_channels/reproduce.py`
- `results/crispin_attachment_channels/README.md`

Commits:
- `13854edb1d599594824f7701defe850d2421f0ba` Crispin transitions
- `6461b77bacc7f4e41b1027e6bea867770006718c` regression
- `c34733c0f208c9c6f25d901a1ae45bb7dac4a277` report

Executable case uses Bagon `dv1-6` Dragon Claw at Fire + Water and Crispin `sv7-133`. From Bagon Active with no Energy, Crispin in hand, Fire+Water in deck, and both Supporter/manual-attachment bandwidth free, the shortest line is two actions:
1. Crispin attaches one Energy by effect and puts the other in hand.
2. The normal attachment attaches the second Energy.

The final attached units are R+W and the Energy kernel confirms Dragon Claw is payable.

Key conclusion: effect attachment and the normal once-per-turn attachment need separate state channels. The line fails when the manual attachment is spent/disabled or the Supporter window is spent/disabled.

Next: explicit turn-window refresh semantics for Supporter/manual-attachment budgets and attack availability, or a broader generic Energy-card compiler.


## 2026-10-12 incarnation: earliest attack turn and printed opening gates

Lease claimed 2026-10-12T18:41:53.846Z, run `gpt6-chat-agent21-20261012T184153846Z` (original timestamp authoritative; do not refresh).

Added `tools/energy_turn_windows.py` and `results/tests/energy_turn_windows/{reproduce.py,README.md}`. It wraps prior deterministic typed Energy setup actions in an earliest-own-turn Dijkstra search, integrating existing `TurnActionBudget` under the legacy Energy access booleans. Going second the represented Tag Call/Guzma & Hala/DCE/Thunder Mountain Iron Thorns attack is own turn 1 (4 actions), and Bagon/Crispin RW is own turn 1 (2 actions). The same card zones going first need own turn 2 (5/3 actions including an inert-opponent turn transition). Source-scoped locks persist; ordinary Supporter, Stadium and manual attachment quotas reset; attached Energy stays. CI run `38293544137` passed.

Added `tools/opening_attack_permissions.py` and `results/tests/energy_turn_windows/opening_attack_regressions.py`. Audited 51 Expanded-labeled English attack prints in the bundled card snapshot, strictly partitioned into 21 first-player first-turn attack exceptions, 12 second-first-only attacks, eight second-first-banned, ten second-first-bonus. Source-specific exception important: Pheromosa-GX Fast Raid exemption does not authorize its Cruel Spike sibling. Scream Tail ex's Scream Supporter lock is available only own turn one when going second. Terapagos ex Unified Beatdown cannot be used first own turn going second. CI run `38294041743` passed both tests. Broadcast `communications/broadcast/20261012T1857Z_agent21_opening_attack_gates.md`.

Limits: known zones, inert opponent between own turns, no draws, Prize uncertainty, card-sourced opponent locks, or match-win-rate outputs. Opening attack corpus uses bundled English `legalities.expanded` flags and must not be treated as complete tournament legality. New tests go under `results/tests/` per 2026-10-12 deck-first maintainer directive; do not expand root `results/README.md` with atomic tests.

Next useful tasks: source-bind first-turn exception profiles into attack-specific physical action gates after exact print/attack authentication; add opponent-turn transitions and top-deck/Prize beliefs; connect Energy/payment sequencing to tournament 2026 Raichu-Electrode and tournament Shadow Rider candidate plans rather than producing only graph connectivity metrics.
