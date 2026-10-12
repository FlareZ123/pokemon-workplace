# A playable Regidrago VSTAR experimental swap

## Deck identity

[Complete candidate 60-card manifest](regidrago_extra_dragapult_minus_vip.json). The reference is Haruku Yoshioka's published 2026 Aichi 10th-place Regidrago VSTAR deck at [Limitless](https://limitlesstcg.com/decks/list/26816). The candidate retains every original card and print except:

- **Dragapult ex** (`sv6-130`): 1 to 2.
- **Battle VIP Pass** (`swsh8-225`): 3 to 2.

The resulting list contains **21 Pokémon, 29 Trainers, 10 Energy**, 15 Basic Pokémon, and one ACE SPEC Prime Catcher. The attached validation compares all 36 print IDs with the published baseline and runs the repository's paper Expanded deck adjudicator as of 2026-10-12. This is an experimental candidate, with no tournament results.

## Why this exact swap?

Regidrago VSTAR's Apex Dragon copies attacks of Dragon Pokémon in the discard pile. Dragapult ex provides Phantom Dive. A second Dragapult helps avoid losing the only copy to Prizes, and a held Dragapult can itself be discarded to pay for Quick Ball or Mysterious Treasure while searching Regidrago V. Battle VIP Pass obtains Basics during the first turn without a discard requirement. The earlier [direct-loading frontier](../regidrago_payload_load_frontier/) found that removing the only Battle Compressor in exchange for the duplicate Dragapult sharply reduces early access to the intended discard pile. This variant preserves Compressor and both original discard-search Item counts.

## Exact opening comparison

Uniform deck shuffles, legal seven-card opening containing a Basic, six face-down Prizes, and one natural draw. A first-eight-card Regidrago V access event occurs when the Basic is already visible or can be found through an observed legal first-turn Item with a copy left in the deck. `D` is an **externally assumed number of expendable non-Basic cards among the other 35**. Quick Ball and Mysterious Treasure may be paid using one held Dragapult ex or one of those D cards. The search target must be Regidrago V, and the action still requires the target to remain in deck.

| Metric (conditional on accepted opening) | Published 3 VIP / 1 Dragapult | Candidate 2 VIP / 2 Dragapult |
| --- | ---: | ---: |
| Regidrago held or VIP fetch | 67.616195% | 62.304142% |
| Add held Dragapult as Item payment, D=0 | 70.297724% | 68.000861% |
| Add disposable cards, D=10 | 84.465282% | 82.168419% |
| Add disposable cards, D=20 | 87.538657% | 85.241794% |
| Any Item discard payment allowed | 87.919858% | 85.622995% |
| Unique successful paid-Dragapult Basic search, D=0 | 2.681529% | 5.696719% |

The Regidrago V access cost is **2.296863 percentage points** under these modeled discard policies. The duplicate Dragapult raises the probability of a unique Basic-fetch line that simultaneously discards the payload by **3.015190 points** in the D=0 case. Separately, the exact Item-loading model finds that simply adding the Dragapult while retaining the same Quick Ball, Treasure and Compressor counts increases early direct Dragapult-to-discard route availability from **16.845955% to 24.042923%**, a **7.196967-point** increase. These correlated events cannot be multiplied into a full setup probability.

## Evidence and limits

The arithmetic in `tools/regidrago_basic_search_frontier.py` enumerates all physical category hands and Regidrago Prize counts with exact rational probabilities. `reproduce.py` compares fourteen event metrics against an independently labeled, exhaustive physical-card oracle on four small decks. It checks the full candidate and exact print-specific Expanded eligibility using existing deck validation.

The model excludes Dedenne, Squawkabilly, draw Supporters, additional Item sequences, evolution and attachment timing, opponent locks, Bench capacity, and actual attack use. The Extra Dragapult variant has no measured head-to-head performance. Its value should be tested against the documented first-turn access loss and matchup-specific Phantom Dive needs. The published tournament deck remains the primary tested competitive reference.
