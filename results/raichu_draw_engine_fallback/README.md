# Harto Raichu: draw-engine fallback after Quick Ball

## Question

The exact Harto Raichu sequencing work reaches **48.690299111%** same-turn Alolan Raichu access in the modeled observable branch by using a visible Ultra Ball or Computer Search first when available, then a hosted Forest Seal Stone line, then the established observation-consistent Quick Ball payment policy.

That Quick Ball continuation still treated failure to find a deck-resident Crobat V as terminal and did not let the player choose Dedenne-GX or Squawkabilly ex after the search establishes K1.

This result adds those real draw engines while preserving their different hand and timing semantics.

Implementation: `tools/raichu_draw_engine_fallback.py`  
Card-semantic compiler: `tools/raichu_draw_engine_profiles.py`  
Seeded CI regression: `results/raichu_draw_engine_fallback/reproduce.py`  
Preserved research run: `results/raichu_draw_engine_fallback/five_million_seed_20261008.json`

## Deck refinement

The preceding exact model grouped several setup Basics into an undifferentiated starter bucket. This simulation splits the actual draw engines out explicitly:

- 2 Crobat V;
- 2 Dedenne-GX;
- 1 Squawkabilly ex.

The remaining modeled package keeps:

- 1 Alolan Raichu;
- 2 Gladion;
- 3 Ultra Ball;
- 1 Computer Search;
- 1 Forest Seal Stone;
- 2 Quick Ball;
- 11 conservative disposable non-starters;
- Giratina as one disposable starter;
- 10 other setup-eligible Basics;
- 23 other cards.

The 16-card setup-Basic total therefore remains unchanged.

## Card-grounded engine semantics

The existing card compiler verifies the bundled legal prints and gives three materially different profiles:

| Engine | Ability | Modeled transition after Quick Ball |
| --- | --- | --- |
| Crobat V | Dark Asset | preserve residual hand, draw until 6 |
| Dedenne-GX | Dedechange | discard residual hand, draw 6 |
| Squawkabilly ex | Squawk and Seize | discard residual hand, draw 6, first turn only |

Crobat V is also a legal Forest Seal Stone host. Dedenne-GX and Squawkabilly ex are not Pokémon V.

A searched Crobat V therefore draws one card in the inherited seven-card action snapshot. A searched Dedenne-GX or Squawkabilly ex replaces the residual five-card hand with a fresh six-card sample.

## Method

A full exact enumeration over the refined 60-card state space was attempted first. The local exact calculation exceeded the available execution window, so this checkpoint is explicitly a **simulation result**, not an exact probability.

The preserved run uses **5,000,000** uniformly randomized 60-card orders with seed **20261008**. Each order supplies:

1. the seven-card opening;
2. six Prize cards;
3. one ordinary draw.

Invalid openings are rejected, preserving the same valid-opening conditioning as the exact baseline.

The simulation is paired. The old Crobat-only continuation and the expanded engine-choice continuation are evaluated on the same sampled hidden state. This makes their difference substantially lower-variance than comparing two independent simulations.

After the initial state is sampled, the draw following each candidate engine is **integrated exactly** with multivariate hypergeometric enumeration over the remaining deck composition. No second Monte Carlo draw is used for the one-, two-, or six-card engine exposure.

The reported calibrated endpoint adds the simulated paired gain to the already validated exact combined-visible baseline of **48.690299111%**. The confidence interval is therefore the sampling interval for the incremental gain translated onto that fixed exact baseline.

## Continuation policy

The existing visible sequencing remains unchanged:

1. if Ultra Ball or Computer Search is already visible, use that deterministic direct-first line;
2. otherwise, if Forest Seal Stone is visible with a Crobat V host, use the hosted Star Alchemy line;
3. otherwise, use Quick Ball and the validated five-clause K0 discard policy.

Once Quick Ball is paid, its deck inspection establishes K1. The expanded continuation then chooses the locally best modeled option among:

- immediate residual Gladion / Ultra Ball / Computer Search / Forest Seal access;
- held or searched Crobat V;
- held or searched Dedenne-GX;
- on the first turn, held, searched, or already-in-play Squawkabilly ex.

A visible Crobat V may be benched before a hand-reset engine to provide a Forest Seal Stone host. Bench capacity is outside this local model.

## Main result

The 5,000,000-state run produced 4,503,832 valid openings and 163,231 states in the observable branch.

| Quantity | Estimate |
| --- | ---: |
| Paired old-policy sample | 48.557116% |
| Paired expanded policy, later turn | 60.778588% |
| Paired expanded policy, first turn | 60.967121% |
| Increment from draw-engine choice, later turn | **+12.221472 pp** |
| 95% CI for later-turn increment | **+12.158824 to +12.284120 pp** |
| Increment from draw-engine choice, first turn | **+12.410005 pp** |
| 95% CI for first-turn increment | **+12.347324 to +12.472685 pp** |
| Extra first-turn value attributable to Squawk availability | **+0.188533 pp** |
| 95% CI for Squawk timing increment | **+0.178696 to +0.198369 pp** |

Using the exact **48.690299111%** existing baseline as a control-variate anchor gives:

| Calibrated local endpoint | Estimate | 95% CI |
| --- | ---: | ---: |
| Later turn | **60.911771%** | 60.849123% to 60.974419% |
| First turn | **61.100304%** | 61.037623% to 61.162985% |

These are estimates for the narrow same-turn "Alolan Raichu enters hand" endpoint under the modeled branch. They are not full-deck game-consistency estimates.

## Where the gain comes from

First-turn gain attribution sums to the full **+12.410005 pp** increment:

| Best continuation route in the paired state | Gain contribution |
| --- | ---: |
| Search Dedenne-GX from deck | **+11.553599 pp** |
| Search Squawkabilly ex from deck | +0.476264 pp |
| Immediate K1 continuation after Quick Ball | +0.282422 pp |
| Dedenne-GX already in hand | +0.080799 pp |
| Squawkabilly ex already in hand | +0.011234 pp |
| Squawkabilly ex already in play | +0.005069 pp |
| Crobat V already in hand | +0.000617 pp |
| Search Crobat V from deck | +0.000000 pp |

Searching Dedenne-GX accounts for about **93.10%** of the first-turn incremental gain.

On later turns, where Squawk and Seize is unavailable, searching Dedenne-GX still contributes **+11.553599 pp** of the **+12.221472 pp** total gain.

The reset engine therefore dominates the missing continuation in this local access problem. Crobat's one-card draw after being searched adds essentially no new access beyond what the preceding exact model already captured.

## Information value without Crobat

A smaller **+0.282422 pp** component comes from "immediate K1" states.

This exposes a previous modeling artifact. Quick Ball can inspect the deck even when the best continuation does not use a Crobat V. Once the search reveals that the singleton Raichu is absent, residual Gladion or another already-visible connector can become sufficient.

The search action therefore has information value separable from the value of the Pokémon it eventually selects.

## Squawkabilly is mostly redundant for this endpoint

Making Squawk and Seize legal on the first turn adds only about **0.1885 pp** beyond the later-turn engine policy.

That should not be read as a general judgment about Squawkabilly ex. In this exact deck package, two Dedenne-GX copies already provide a broadly available six-card reset. The singleton Squawkabilly therefore adds mostly overlapping local access for this endpoint.

## Validation

The seeded reproducer:

- recompiles and checks the Crobat V, Dedenne-GX, Squawkabilly ex, and Forest Seal Stone card semantics;
- verifies the refined deck partition sums to 60 cards and 16 setup Basics;
- runs a paired 1,000,000-state simulation with the same seed;
- checks the simulated observable branch against the preceding exact branch mass;
- checks that the paired baseline is consistent with the exact combined-visible baseline;
- pins broad intervals around the new paired gains and Squawk timing increment;
- requires gain attribution to sum to each paired gain;
- requires searched Dedenne-GX to remain the dominant incremental route.

The full 5,000,000-state JSON is preserved separately so the research estimate does not depend on the smaller CI sample.

## Limitations

This remains a bounded local ALS model.

It does not model:

- multiple sequential reset engines in the same turn;
- Quick Ball or other newly drawn search cards after the reset;
- Battle Compressor;
- Pikachu / Ditto Prism Star evolution setup;
- Electrode-GX and Energy-loading requirements;
- Bench capacity;
- lock effects or Ability suppression;
- VSTAR Power having been spent on another line;
- opponent interaction;
- future-turn resource value after Dedechange or Squawk and Seize destroys the hand.

The reset effects can discard strategically valuable cards. This result credits only the immediate Raichu-access endpoint, so it does not estimate the full strategic cost of that hand destruction.

The active-selection abstraction also preserves the earlier Crobat-first setup convention instead of optimizing the starting Active Pokémon.

## Interpretation

This result strengthens two broader repository themes.

First, theoretical connector access must be evaluated as an executable line with payment, information state, and downstream hand transition. A one-card Crobat draw and a six-card Dedenne reset are materially different even though Quick Ball reaches both Pokémon.

Second, a search can remain valuable when its searched target is not the endpoint. Quick Ball both changes the deck composition and establishes K1, then the engine choice is made with that new information.

## Next work

The next high-value step is to broaden the **first action** family again.

This result optimizes the engine only after Quick Ball. If Dedenne-GX or Squawkabilly ex is already visible, using its reset before Quick Ball can preserve the Quick Ball and its payment, while giving up the K1 information obtained by searching first.

A whole-action planner should compare those visible reset-first lines against:

- direct Ultra Ball / Computer Search first;
- hosted Forest Seal Stone first;
- Quick Ball -> K1 -> best engine;
- and the future resource cost of destroying the hand.


## Subsequent sequencing result

The follow-up `pre_reset_search_dominance/` resolves the simplest visible reset-first comparison inside this same state projection.

Because constrained deck searches may intentionally take zero cards, a legal Quick Ball can be used before an immediately planned Dedechange or Squawk and Seize reset. Quick Ball and its payment would otherwise be discarded by that reset. With zero search output and the same fresh-draw witness, the projected material state after the reset is identical while the Quick Ball line has gained K1 information.

Therefore the naive reset-first line does not improve this local endpoint under the current assumptions. Future work should focus on states that break that equivalence, such as known top-deck order, discard-timing triggers, lock changes, or future value assigned to Quick Ball itself.
