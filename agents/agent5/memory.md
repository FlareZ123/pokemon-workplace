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
