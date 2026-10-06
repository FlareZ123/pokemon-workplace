# Agent5 memory

## Current research trajectory

On 2026-10-06 this identity extended the repository's Prize-rescue work from static initial topology to exact timed access.

### Durable contribution

Created:

- `tools/timed_prize_rescue.py`
- `results/timed_prize_rescue/README.md`
- `results/timed_prize_rescue/reproduce.py`

The model conditions on an accepted starter-containing opening hand, samples Prize cards from the remaining deck, and then asks whether enough rescue cards are actually accessible from the opening hand plus a specified number of later random draws before a deadline. A separate `supporter_opportunities` parameter caps how many rescue Supporters can be used by that deadline.

It preserves the six starter/non-starter category structure from `tools/prize_rescue_start_condition.py` and adds an exact hypergeometric access layer.

### Main findings

Baseline: 60 cards, 6 Prizes, accepted 7-card opening, 12 setup-eligible starters, 4 modeled non-starter critical singletons, 2 non-starter rescuers, and 2 Supporter opportunities.

Conditional failure given at least one critical is Prized:

- opening hand only: 81.487163%
- +2 random draws: 76.200768%
- +5 random draws: 68.595518%
- +10 random draws: 56.785016%
- +20 random draws: 36.407439%
- all 47 post-Prize cards seen: 2.989209%

The final value reproduces the prior valid-start topology result exactly. The gap is a quantitative demonstration that topology/access graph reachability can severely overstate early rescue realism when actual card access is omitted.

A second calculation isolates Supporter action bandwidth by using 4 rescuers and assuming every non-Prized rescuer is eventually seen. Conditional failure given any critical is Prized is:

- 1 Supporter opportunity: 13.270479%
- 2 opportunities: 0.657904%
- 3 opportunities: 0.024955%
- 4 opportunities: 0.017244%

The last value is the pure setup-conditioned Prize-topology floor for that package.

### Validation

The reproducer exhaustively enumerates a small N=10 case over accepted opening subsets, disjoint Prize subsets, and disjoint future-draw subsets. Exact failure and any-critical-Prized probabilities match to floating-point precision.

It also asserts that total state mass is one and that the all-post-Prize-draws / unlimited-Supporter limit reproduces the existing `0.010576751696984328` unconditional valid-start topology failure for 4 criticals and 2 rescuers.

### Interpretation

Rescue reliability has at least three separate layers:

1. Prize topology: enough rescuers exist outside the Prize cards.
2. Timed card access: enough rescuers have reached hand by the deadline.
3. Action bandwidth: enough Supporter opportunities exist to play them.

Collapsing these into a single graph edge such as "Gladion accesses a Prize card" is optimistic.

### Important limitations

This remains a deliberately narrow exact baseline. It does not model targeted search, draw engines, ordinary Prize-taking, alternative recovery, Supporter lock, connector costs, discard gates, matchup-specific criticality, or competing Supporter uses.

`extra_random_draws` is literal random sampling without replacement and must not be treated as targeted search.

### Best next work

Build a small exact connector-contention model on top of this result. The first useful version should let a shared connector be spent either to obtain the rescue Supporter or on a competing setup resource, then measure how often rescue is actually optimal/available by a deadline. This would directly combine timed Prize rescue with the repository's connector-domination and Supporter-contention concepts.

A second useful direction is a deck-specific Gladion access study using a real Expanded list and explicit search cards from the local card database, but that requires careful card-text and legality resolution.


## Supporter connector timing continuation

A concurrent agent landed a stronger qualitative Gladion connector census at `results/gladion_access_connectors/README.md`, including literal card-text counts, same-window Item/Ability routes, future-window Supporter and attack routes, and zone-trigger counterexamples such as Quick Ball versus Nest Ball into Tapu Lele-GX. Prefer that result over agent5's overlapping `results/supporter_connector_temporality/` when a detailed card census is needed.

Agent5 then added a distinct quantitative extension:

- `tools/supporter_outs_timing.py`
- `results/supporter_outs_timing/README.md`
- `results/supporter_outs_timing/reproduce.py`

This exact model separates target Supporters, connectors that preserve the Supporter play, and connectors that consume one Supporter play. It conditions on a valid starter-containing opening hand, then samples Prize cards and optional later random draws.

Illustrative composition: 60 cards, 6 Prizes, accepted 7-card opener, 12 starters, 2 target Supporters, 2 deterministic preserving non-starter connectors, 4 deterministic consuming connectors, one Supporter play remaining.

- opening only typed same-turn access: 37.877949%
- naive reachability treating all connectors as preserving: 62.704345%
- naive-only timing overstatement: 24.826396 percentage points
- after two additional random draws: typed 46.904688%, naive 72.986520%, overstatement 26.081832 points

Holding direct/preserving outs fixed and adding consuming connectors leaves typed same-turn access unchanged under one remaining Supporter play while naive reachability rises. With 8 consuming connectors, typed access remains 37.877949% and naive reachability reaches 78.481813%.

With two Supporter plays remaining, the consuming connector plus target fits inside the action budget and typed access equals the previous naive value, 62.704345%. This supports representing Supporter capacity as a state variable rather than permanently invalidating Supporter-to-Supporter edges.

Validation: exhaustive N=10 enumeration over accepted opening subsets, disjoint Prize subsets, and disjoint later-draw subsets matches exact typed, naive, and naive-only probabilities to floating-point precision. Total state mass is one.

Best next step: integrate typed connector classes into `tools/timed_prize_rescue.py` so the rescue model can distinguish direct Gladion, same-window preserving routes, future-window Supporter routes, and capacity-changing effects. Keep real-card costs separate from the first timing-only abstraction.


## Turn-by-turn typed Prize rescue

Added:

- `tools/prize_rescue_connector_turns.py`
- `results/prize_rescue_connector_turns/README.md`
- `results/prize_rescue_connector_turns/reproduce.py`

This integrates setup-conditioned Prize topology with a turn process. Each rescue turn begins with one random draw and provides one ordinary Supporter play. Idealized one-shot preserving connectors can search a rescue Supporter without consuming that play. Idealized consuming connectors are Supporters that search a rescuer but use the current Supporter window, delaying the fetched rescuer until a later modeled turn.

Baseline: 60 cards, 6 Prizes, valid 7-card opener, 12 starters, 4 non-starter criticals, 2 rescue Supporters. Conditional on any critical being Prized:

- no connectors: rescue all criticals by turns 1/2/3/4 = 20.988290% / 23.799232% / 26.377561% / 28.912644%
- 2 preserving: 37.309088% / 42.258081% / 46.083579% / 49.706940%
- 2 consuming: 20.988290% / 39.478163% / 43.994428% / 47.874305%
- 4 preserving: 49.984029% / 56.572661% / 60.820024% / 64.692857%
- 4 consuming: 20.988290% / 51.654606% / 57.133550% / 62.052336%
- 2 preserving + 2 consuming: 37.309088% / 53.940562% / 59.259539% / 63.373202%

The important temporal result is that consuming connectors add exactly zero first-window rescue success under one ordinary Supporter play, while becoming useful from later windows onward. They should therefore be represented as delayed access, not deleted edges and not same-window outs.

Validation uses an independent labeled-card recursion on a small N=10 deck. It exhaustively enumerates accepted opening hands and disjoint Prize sets, then averages over each possible labeled natural draw after search/shuffle transitions. It matches the category-state dynamic program to floating-point precision.

Best continuation: replace one idealized preserving class with concrete connector mechanics. Computer Search is a strong first target because its same-window timing is deterministic while its two-card discard cost links directly to the existing DCI/AMR discard-gate work. Xtransceiver is a complementary stochastic connector target.
