# Harto Miki Raichu/Electrode: Dark Asset continuation versus discard density

## Question

How sensitive is the newly modeled post-Dark-Asset connector continuation to the size of the conservative disposable-card pool?

This matters because the continuation needs two separate payments in sequence. Quick Ball or Ultra Ball first searches Crobat V, then a connector exposed by Dark Asset may need another two-card discard payment.

Implementation source: `tools/raichu_dark_asset_followup.py`  
Sensitivity regression: `results/raichu_dark_asset_followup_sensitivity/reproduce.py`

## Method

The sweep preserves the same Harto-style 60-card structure and 16 setup-eligible Basics used by the preceding Dark Asset result.

The total conservative disposable pool varies from 4 to 24 cards.

One disposable copy remains the Giratina-like setup starter in every row. The remaining disposable copies are non-starters. The other 13 protected setup starters stay fixed, so legal-opening conditioning remains comparable across the sweep.

Every row uses:

- seven-card accepted opening;
- six Prize cards;
- one later ordinary draw;
- two Crobat V;
- two Quick Ball;
- three Ultra Ball;
- one Computer Search;
- one Forest Seal Stone;
- two Gladion;
- singleton target;
- Quick Ball cost 1;
- Ultra Ball and Computer Search cost 2.

## Exact result

| Conservative disposable pool | First-order Dark Asset | Bounded continuation | Follow-up gain | Quick share of gain |
| ---: | ---: | ---: | ---: | ---: |
| 4 | 21.337239% | 21.340892% | +0.003653 pp | 99.63% |
| 8 | 27.840140% | 27.882207% | +0.042067 pp | 98.19% |
| 12 | 35.092509% | 35.225031% | +0.132521 pp | 96.82% |
| 16 | 41.593945% | 41.859458% | +0.265512 pp | 95.54% |
| 20 | 46.664827% | 47.082760% | +0.417934 pp | 94.37% |
| 24 | 50.177285% | 50.741198% | +0.563913 pp | 93.34% |

The incremental continuation value rises monotonically across this sweep.

## Finding 1: second-order connector value is strongly DCI-regime dependent

At the strict four-card disposable pool, Dark Asset can still improve direct access, but the new connector-after-draw layer contributes only **0.003653 percentage points**.

At the 12-card baseline, the same semantic layer contributes **0.132521 points**.

At 24 conservative disposable cards, it contributes **0.563913 points**.

The newly exposed connector therefore has little practical value in low-discard-capacity states even though the search graph contains the same edges.

This is a clean Active Move Realism effect. The graph topology is fixed while residual payment feasibility changes.

## Finding 2: the residual gate compounds earlier discard costs

The first-order Dark Asset result already benefits when the initial search-to-Crobat action is payable.

The bounded continuation asks for more.

For the dominant Quick Ball branch:

- one acceptable discard pays Quick Ball;
- two acceptable cards must still remain if Dark Asset exposes Ultra Ball or Computer Search.

The follow-up therefore crosses a three-card initial threshold under the conservative binary policy.

As the disposable pool becomes denser, more opening states cross that threshold and the new layer activates more often.

This explains why the continuation gain grows faster than a simple "one more out" interpretation would suggest.

## Finding 3: Quick Ball stays dominant, but Ultra's share grows with slack

Quick Ball accounts for 99.63% of the incremental gain at four disposable cards and 93.34% at 24.

Ultra Ball's share rises from 0.37% to 6.66% across the same sweep.

The mechanism is straightforward.

Quick Ball spends one card before Dark Asset and therefore preserves more residual payment capacity.

Ultra Ball spends two cards before Dark Asset. Its two-card draw-to-six window can expose useful combinations, but the branch increasingly needs larger disposable slack to convert those draws into another cost-two connector.

The deeper draw becomes more relevant as the payment constraint relaxes.

## Finding 4: target-Prized access rises more gradually

Conditional target-Prized bounded access rises from:

- 29.299803% at a four-card disposable pool;
- 35.678624% at the 12-card baseline;
- 42.418164% at 24.

The Prized-target branch has direct Gladion states that do not need a discard payment, so its total access is less tightly coupled to the residual connector gate than the target-in-deck side.

The second-order Computer Search -> Gladion route is still gated by two residual discards.

## Interpretation

A draw engine's continuation value should be conditioned on the resource state left by the action that reached the draw engine.

The relevant state is richer than:

`Dark Asset draws N`

For these lines it is closer to:

`search cost paid -> residual acceptable-discard multiset -> Dark Asset width -> connector identity drawn -> connector cost payable -> zone-dependent output`

This reinforces the repository's broader conclusion that access and action feasibility need separate state variables.

## Validation

The deterministic CI sweep freezes the exact incremental values for all six disposable-pool settings and asserts monotonicity.

The 12-card row reproduces the previously validated baseline exactly:

- first-order Dark Asset 35.092509%;
- bounded continuation 35.225031%;
- increment +0.132521 pp.

The underlying bounded model already has an independent labeled-card physical regression.

## Limits

The pool-size sweep changes only a binary conservative discard-policy category.

It does not assign graded DCI values, distinguish which Special Energy copies should be preserved in a particular matchup, or model the future value lost by spending three cards across the two-connector sequence.

A larger disposable pool therefore means "more cards currently allowed by this policy," not "more truly free cards."

## Next useful work

A stronger continuation would replace the binary pool with a small ranked discard policy.

For example, separate:

- cards actively preferred in discard;
- low-cost expendable cards;
- conditional Energy discards;
- protected singleton or combo resources.

The planner could then optimize the two sequential payments jointly instead of treating every allowed card as equivalent.
