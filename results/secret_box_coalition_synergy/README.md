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

The trace is a reproducible state-level diagnostic complementing the full-sample count inference. It does not assert that all 1,917 full-sample synergy states have the same profile without running a matching full-sample trace. [GitHub Actions run 38048881043](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38048881043) passed both exact attribution and the witness tracer.

## Limits and next questions

The underlying Aichi planner models a compressed first-turn core, not complete games, lock matchups, physical category failure rates, or the later value of discarded cards. Output masks change category availability while preserving other planner abstractions. The sample is seeded, its state counts are fixed, and the polynomial describes a hypothetical overlay on those states.

A next step is to distinguish *why* the Tool+Stadium routes work in each of the 1,917 states: Jet already held, board/Bunnelby requirements, Tool selection, and alternative acquisition. That requires instrumenting state-level witnesses rather than inferring the mechanism solely from aggregate mask counts. Another extension is to derive correlated-category availability from actual card/text constraints instead of assuming independent `q`.
