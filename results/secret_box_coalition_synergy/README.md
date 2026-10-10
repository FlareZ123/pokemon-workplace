# Secret Box output coalitions: hidden complementarity and resilience

## Question and provenance

The 500,000 accepted-opening Aichi Vileplume paired experiment contains 20,785 states where full-output Secret Box completes the modeled Bunnelby + TM: Evolution + Jet Energy first-turn core and the Grand Tree baseline does not. All 20,785 states have at least one successful **single-category** Secret Box output route.

Does that imply additional output-category *combinations* are strategically redundant?

The 16 subset-counts and 16 singleton-signature counts are pinned directly from [Aichi Secret Box output dependencies](../aichi_secret_box_output_dependencies/), especially its `reproduce_full.py`. This result performs a new exact secondary analysis of those already-computed state counts; it does not re-simulate game states.

Reproducer: `reproduce.py`. Reusable library: `../../tools/secret_box_coalition_synergy.py`.

## Formal method

For each incremental state `s`, let `f_s(M)` indicate success under enabled output-category mask `M`, with bits Item=1, Tool=2, Supporter=4, Stadium=8.

Define `R_s` as the mask of singleton categories that individually succeed. Then

`V(M) = sum_s f_s(M)`

`B(M) = sum_s 1[R_s & M != 0]`

`D(M) = V(M) - B(M)`.

Under monotone output availability, `B(M)` is the count of states covered by *at least one successful single-category route* in `M`, and `D(M)` measures extra successful states reached through multi-category combinations. The source audit reports zero monotonicity violations. Here, `B(full) = V(full) = 20,785`, so this is extra *partial-coalition* reachability, with no extra full-output states.

## Main finding: Tool plus Stadium has large concealed complementarity

| Enabled output subset | Actual successes `V` | Singleton union `B` | Extra coalition coverage `D` |
| --- | ---: | ---: | ---: |
| Tool + Stadium | 4,849 | 2,932 | **1,917** |
| Tool + Supporter | 20,785 | 20,743 | 42 |
| Supporter + Stadium | 20,745 | 20,703 | 42 |
| Tool + Supporter + Stadium | 20,785 | 20,743 | 42 |
| Every other subset | equals `B(M)` | equals `V(M)` | 0 |

For Tool + Stadium, the 2,932 singleton-union successes follow from Tool-only 2,313 + Stadium-only 623 - four states where both individually work. The two-category mask instead succeeds in 4,849 states, revealing **1,917** additional combined routes.

Those 1,917 represent **39.534%** of Tool+Stadium mask successes and **9.223%** of the 20,785 incremental states. In these states an alternative singleton Item and/or Supporter route still succeeds, as shown by the original audit. Hence the minimum successful subset size is one in every state, despite real complementarity between other output categories.

## Independent category-availability counterfactual

As an abstract resilience experiment, independently enable each of the four categories with probability `q`, identical for all categories. This is an *exogenous availability model*, not a claim about actual Secret Box play or official category-specific disabling effects.

The expected retained **state count**, across all 20,785 incremental states, is the exact polynomial:

`E[V] = 44422q - 24536q^2 - 1056q^3 + 1955q^4`.

A model that recognizes only singleton-success routes predicts:

`E[B] = 44422q - 26537q^2 + 2904q^3 - 4q^4`.

The missed complementarity is:

`E[D] = 3q^2(1-q)(667 - 653q)`.

This difference is nonnegative on `0 <= q <= 1`, zero at both endpoints, and maximal at approximately `q = 0.505246`. Its maximum is about **0.614458 percentage points of the conditional 20,785-state population**.

At `q=1/2`:

- Correct expected successes: `257075/16 = 16067.1875` (77.301840% of incremental states).
- Singleton-only estimate: `31879/2 = 15939.5` (76.687515%).
- Undercount: `2043/16 = 127.6875` expected states (**0.614325 percentage points** conditional on the incremental population).

Spread across all 500,000 accepted-opening trials, the same counterfactual expected-count difference is **0.0255375 percentage points**. Neither quantity is a match win-rate estimate.

The reusable helper also accepts distinct rational availability probabilities for Item, Tool, Supporter, and Stadium.

## Shapley attribution effect

Comparing exact Shapley credit of `V` against singleton-only credit of `B`, the correction for **Item, Tool, Supporter, Stadium**, respectively, is:

`(-709/4, +653/4, -597/4, +653/4)` state-equivalent credit units.

The corrections sum to zero because the full coalition already succeeds in all incremental states under both methods. They transfer credit toward Tool and Stadium, which participate in otherwise obscured multi-category routes. Shapley credits represent an allocation convention, not causal counterfactuals about independently deleting one printed category.

## Verification

`reproduce.py` pins the original 500k mask and singleton-signature tables, checks every coalition residual, validates all polynomial coefficients exactly, computes rational expectations at `q=1/2` and at heterogeneous category probabilities, and asserts the Shapley correction using the repository's existing `subset_shapley.py`.

An independent four-state Boolean-oracle fixture enumerates all 16 masks, including a state with no singleton witness and another having both a singleton and a two-category route. It tests the difference between minimum successful category count and latent multi-category paths.

## Starting-state witness diagnosis

The new [100,000-state Tool+Stadium tracer](trace_pair_witnesses.py) reruns the original paired seed, isolates the 375 incremental successes where the Tool+Stadium mask works but neither singleton mask does, and aggregates physical starting-state features before a Stellar Wish choice. It confirms the predicted 375 exactly from the original subset table.

All 375 of these states have **Jet Energy already in hand**, lack **TM: Evolution, Artazon, and Bunnelby** in the starting hand or Active position, and have both TM: Evolution and Artazon searchable in the deck. None have a Jirachi top-five access to Guzma & Hala or Tag Call.

The enabling path is therefore concrete in this 100k trace: Secret Box's Tool output obtains **TM: Evolution**, and its Stadium output obtains **Artazon**, which can then obtain Bunnelby. Jet Energy is the already-held third resource. Removing either enabled category leaves a distinct target missing in the constrained planner.

Secret Box itself starts in hand for **357** cases. In the other **18**, Jirachi's Stellar Wish can obtain it. Exactly two physical-start profiles cover all 375 trace cases; they differ only in that access route.

The on-demand full 500,000-opening replication with [trace_pair_witnesses_full.py](trace_pair_witnesses_full.py) verified the **same necessary starting-state pattern for all 1,917 combination-only successes**. Secret Box starts in hand in **1,830** states and is accessible through Jirachi in **87**. Both variants have the two needed named search outputs in deck, held Jet Energy, and no G&H/Tag Call Stellar access. The complete 1,917-state result thus upgrades the mechanism from a 100k diagnostic to a full-sample witness classification. [100k CI passed](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38048881043); [full 500k CI passed](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38049000028).

## Complete inclusion-minimal winning-route antichains

An inclusion-minimal mask succeeds while every proper subset fails. This differs from only counting minimum-cardinality winners: a state can have a successful single-category route and still have a distinct inclusion-minimal two-category alternative.

The seeded [100k antichain trace](antichain_trace.py) and [full 500k trace](antichain_trace_full.py) exhaustively check all 16 masks per incremental state. The full run [passed](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38049292465). The number of distinct inclusion-minimal winning masks per state is:

| Distinct minimal routes | Incremental states |
| ---: | ---: |
| 1 | 2 |
| 2 | 15,932 |
| 3 | 4,847 |
| 4 | 4 |

Thus 20,783 of 20,785 incremental cases have at least two alternative minimal output masks. All inclusion-minimal combinations are singletons or pairs. The three possible minimal pair routes appear as Tool+Supporter in 42 states, Tool+Stadium in 1,917, and Supporter+Stadium in 42. Overlap is preserved: 24 of the Item-singleton-only states have both pair routes Tool+Supporter and Supporter+Stadium. The dominant signature is singleton Item or Supporter (15,892 states) or those two plus Tool+Stadium (1,917).

A two- or three-route antichain is a mathematical description of successful category subsets for this particular endpoint. It does not guarantee that any of those routes preserves the same discarded resources, board position, or later match utility.

## Payment-fodder mechanisms in the two 42-state alternative routes

The [full 500k named-starting-card trace](trace_small_pair_witnesses.py) verifies both remaining inclusion-minimal two-category alternatives. [Full CI run 38050016278 passed](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38050016278).

**Tool + Supporter, 42 states.** All 42 begin with TM: Evolution already held, no searchable TM copies remaining, and Jet Energy absent but searchable. Secret Box itself is held. In each state a different Pokémon Tool is searchable: Stealthy Hood remains in deck in 42/42, Counter Gain in 40/42. Under the existing compressed search rule, with TM already held, the Tool output obtains a different Tool and places it in the generic "other" category. The Supporter output obtains Guzma & Hala, which can search Jet Energy using its two-other-card discard mode. The otherwise unwanted Tool becomes newly available hand material to pay that later discard cost.

The named-card decomposition matters: in two of these states, Counter Gain is no longer searchable while Stealthy Hood remains. The planner merges both into "other" and treats either as available discard material. This exposes an unmodeled strategic opportunity cost: Stealthy Hood may be valuable future protection in lock matchups. The audit measures immediate setup access, not whether sacrificing that Tool is strategically optimal.

**Supporter + Stadium, 42 states.** All 42 already have Bunnelby accessible from the starting hand or Active position. Secret Box is held and Artazon remains searchable. In 24 states TM is held and Jet missing; in the remaining 18 Jet is held and TM missing. Guzma & Hala can fetch the missing payload after its two-card discard. Because Bunnelby is already accessible, Artazon from Secret Box's Stadium output is unnecessary for the immediate Basic search and can serve as later payment material. Thus a Stadium search may matter even when the Stadium is never played.

Exactly 24 states have both Tool+Supporter and Supporter+Stadium inclusion-minimal backup routes: different resources can fund the same later Supporter. A stateful optimizer must account for the differing discardability of retrieved Tool and Stadium cards.

**Jet-in-hand equivalence.** A separate [full 500k statewise regression](trace_jet_output_equivalence_full.py) confirms that, within these 20,785 incremental successes, Tool+Stadium-only succeeds exactly when Jet Energy was already in the starting hand. The four outcomes are 4,849 both true, 15,936 both false, and zero discordant states. This is a sample-level policy equivalence under the compressed Aichi model.

## Arbitrary correlation: sharp availability bounds

Independent category availability is an illustrative model. We can remove independence while keeping a common marginal probability `q` that each of Item, Tool, Supporter, and Stadium is enabled.

The [exact correlation-bound proof and reproducible construction](correlation_bounds.py) establish the **sharp bound**

`0 <= E[D] <= 1917 * min(q, 1-q)`

for every joint distribution over output masks with those four marginal probabilities. Both bounds are attained for every `q` between zero and one.

The lower bound is attained by all-or-none correlation: full output mask 15 appears with probability `q`, empty mask 0 with probability `1-q`. Both masks have zero coalition residual.

For the upper bound, two pointwise inequalities provide simple dual certificates: `D(mask) <= 42 * 1[Tool] + 1875 * 1[Stadium]`, and `D(mask) <= 1917 * 1[Item absent]`. Taking expectations gives `1917q` and `1917(1-q)`. Explicit exact distributions provided in the test attain the minimum of those bounds in each region `q <= 1/3`, `1/3 <= q <= 1/2`, and `q >= 1/2`.

At `q=1/2`, the previously stated independent overlay misses `2043/16 = 127.6875` expected states. Under a suitable correlated availability pattern, the same marginals permit `1917/2 = 958.5` missed expected states, or **4.611499 conditional percentage points** of the 20,785 incremental cases. The independent-overlay figure is therefore only one plausible *mathematical scenario* among many, and these tight bounds do not estimate the physical likelihood of any such correlations.

[GitHub Actions CI 38049440514 passed](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38049440514) for the exact arithmetic and analytic witnesses.

## Unequal category availabilities can force a nonzero synergy floor

The equal-marginal lower bound of zero is not universal when the four resource-category availabilities differ.

The [exact rational extreme-distribution solver](../../tools/category_availability_extrema.py) enumerates all five-column bases of the four-category joint probability simplex. Its five equalities specify total mass and one marginal availability per category. Since every extreme joint distribution can be represented with at most five nonzero masks, the enumeration obtains **globally sharp** expectation bounds without selecting a correlation family. The [reproducer](correlation_extrema.py) checks returned distributions, source-based synergy scores, deterministic corner cases, and additive objectives. [CI passed](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38050179416).

For illustrative marginals Item=1/4, Tool=3/4, Supporter=1/3, Stadium=2/3, the exact values are:

| Correlation assumption | Additional expected successful states, out of 20,785 |
| --- | ---: |
| Arbitrary dependence, sharp minimum | **7** |
| Independent categories | **3911/8 = 488.875** |
| Arbitrary dependence, sharp maximum | **2563/2 = 1281.5** |

The strictly positive lower bound has a short certificate: for every output mask, `D(mask) >= 42 * (1[Tool] + 1[Stadium] - 1 - 1[Item])`. Taking expectations at these marginals yields `42*(3/4 + 2/3 - 1 - 1/4) = 7`. An attaining joint distribution puts probability 1/3 on mask 2, 1/4 on mask 8, 1/12 on mask 11, 1/6 on mask 14 and 1/6 on mask 15.

An attaining maximum distribution puts probability 1/4 on mask 5, 1/12 on mask 6 and 2/3 on mask 10. This gives `(42/12) + (1917*2/3) = 2563/2`.

This is an exact conditional mathematical result on the 20,785 incremental sampled states, under the specified hypothetical category-availability marginals. It does not estimate the probability that any one of those categories becomes practically unavailable in a real paper Expanded game. Physical sources can share costs and restrictions, so a realistic availability model should explain the correlation structure rather than assume it.

## Limits and next questions

The underlying Aichi planner models a compressed first-turn core, not complete games, lock matchups, physical category failure rates, or the later value of discarded cards. Output masks change category availability while preserving other planner abstractions. The sample is seeded, its state counts are fixed, and the polynomial describes a hypothetical overlay on those states.

The full 1,917-state witness classification and the sharp mathematical arbitrary-correlation bounds are complete. Next investigate the 42 Tool+Supporter and 42 Supporter+Stadium pair alternatives, state-level route sequencing, and a physically grounded model of correlated category availability.
