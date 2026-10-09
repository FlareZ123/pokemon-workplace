# Optional Tag Call before G&H: material access and Prize-information upgrade

## Research question

Within the saved-late-Jirachi first-turn Aichi Vileplume access model, can an additional naturally held Tag Call be used before playing Guzma & Hala to make its discard payment safer and improve access to Redeemable Ticket or Town Map? How much of any gain comes from the TAG TEAM cards physically obtained, and how much comes from permitting a held setup resource to be discarded after the search has revealed the Prize composition?

This extends [aichi_jirachi_payment_frontier](../aichi_jirachi_payment_frontier/) and reuses the existing [Tag Call payment-fuel connector](../../tools/aichi_tagcall_payment_reachability.py).

**Reproduction:** tools/aichi_tagcall_information_preview.py, reproduce.py, run.py, and .github/workflows/validate-agent4-aichi-tagcall-preview.yml.

**Passing CI:** https://github.com/FlareZ123/pokemon-workplace/actions/runs/37977774112

## Window and legal represented action

The base preparer may begin a G&H route from a natural G&H in hand (K0), a Jirachi top-five find (still K0), or Tag Call searching the deck (K1). The optional intervention is considered **only** when G&H's pending payment is still pre-K1, late Jirachi Stellar Wish remains unused, and another Tag Call is retained in hand.

The supplemental Tag Call is played *before* G&H to search for up to two additional copies of G&H, which enter hand as discard candidates. The Item is consumed and this search reveals the remaining deck, thus permitting K1 deduction of the six initial Prize cards. G&H is then played, two cards are discarded if necessary, and its required Tool/Special Energy plus an optional Stadium are materialized before an unused late Stellar Wish examines the freshly shuffled top five.

An optional Tag Call may also serve other searches in real play. Here only the existing two-G&H acquisition line is represented. This isolates one concrete, physically grounded counterfactual route.

## Conservative guard and ablation

Baseline payment paths are restricted from discarding any already-held TM: Evolution, Jet Energy or Artazon. This is a **conservative guard against re-searching a possibly Prized essential resource** before G&H has exposed the deck. Other hidden-state-dependent endpoint choices remain optimistic; the guard is not a complete implementable K0 policy.

The optional action is evaluated in two stages:

1. **Material-only:** actually play Tag Call, obtain the additional G&H copies and build the new hand/deck; retain the same three-card protection guard on its G&H payments. This also physically thins the deck and creates discard material.
2. **Guard relaxation:** after Tag Call's full-deck search, allow discarding a held output where it is known that an accessible replacement exists. The model's selected payment remains per-world and endpoint-aware.

At every stage the player may decline the additional Tag Call, so the comparison uses the maximum of the base and optional routes. The ablation therefore splits the modeled uplift into an extra material-access component and an additional guard-relaxation component. The latter is **an information-enabled action-space effect**, subject to the limits of the simple guard, rather than an identified causal information premium.

## Fixed-seed 80,000 opening result

Seed 20261009; 68,960 accepted Basic-containing openers; 48,665 G&H-core offered; 6,017 late-Jirachi eligible; 3,659 of these late-Jirachi states are pre-K1. The extra Tag Call route is represented in **1,409** of those pre-K1/late-Jirachi/core states.

All aggregate percentages below divide by 68,960 accepted openings. The displayed event additionally conditions on the named endpoint and the optional Tag Call route being applicable, so these are **small marginal contributions**, not total endpoint success rates.

| Endpoint and Item assignment | Baseline guarded first reset | With optional Tag Call | Improvement (paired 95% CI) | Material-only part | Guard-relaxation part |
| --- | ---: | ---: | ---: | ---: | ---: |
| Dual Stage 2, one Ticket | 0.230761% | 0.237154% | +0.006393 ± 0.000495 pp | +0.005220 pp | +0.001173 pp |
| Dual Stage 2, two Tickets + one Map | 0.423264% | 0.433774% | **+0.010510 ± 0.000819 pp** | +0.008573 pp | +0.001937 pp |
| Dual Stage 2, three Tickets + one Map | 0.554710% | 0.568267% | +0.013557 ± 0.001075 pp | +0.011054 pp | +0.002503 pp |
| Item lock, two Tickets + one Map | 0.236192% | 0.242662% | +0.006470 ± 0.000639 pp | +0.005396 pp | +0.001074 pp |
| Item lock plus Pidgeot, two Tickets + one Map | 0.141903% | 0.145857% | +0.003954 ± 0.000498 pp | +0.003313 pp | +0.000640 pp |

For the dual-Stage-2, two-Ticket/one-Map comparison, the material-stage benefit occurs in 695 accepted states; the further guard-relaxation benefit is positive in 275. A strictly forced Tag Call line would be allowed to harm certain hands by consuming a connector, but the optional policy may decline it. In this sample the best optional path was never worse than the guarded comparator by construction.

The material effect comprises roughly four-fifths of the measured gain in this package, so merely labeling the entire +0.010510 pp as the **value of knowing Prizes** would be incorrect.

## Interpretation

An additional Tag Call can make a G&H discard less costly by obtaining redundant TAG TEAM Supporters as expendable resources. The corresponding deck search reveals Prizes before the critical discard deadline. It can also thin the deck and change the late Stellar Wish's target density. These channels matter separately.

The incremental first-reset access gain in this specific package is small relative to the broader 60-card game's variance and unknown matchup opportunity costs. It is not enough evidence to recommend changing the published Aichi list.

## Limits and next work

- The model represents only one optional Tag Call continuation, namely retrieval of additional G&H copies when available. It omits other TAG TEAM Supporter selections and alternative search paths.
- The baseline protection guard is a conservative proxy, not a complete K0-observation-consistent policy over all possible initial Prize compositions.
- The optional route is evaluated with actual sampled deck/Prize contents and the best endpoint-preserving payment in each state, so even the material-stage benefit remains an **optimistic existence estimate**.
- Late Jirachi's post-search top-five hit probability is calculated exactly for each state with a uniformly shuffled remaining deck. Later draw/recovery, opponent lock, Bench interactions and the value of spent Tag Call are unmodeled.
- Ticket/Map tech assignments replace four specific Supporter slots, whose competitive value outside this first-turn window is not included.

An exact K0 policy over visible observations could strengthen this experiment by choosing one payment for all hidden Prize worlds and measuring whether prior Tag Call actually changes that choice. The independent [Tool-thinning information theorem](../gnh_tool_thinning_information/) proves why this constraint matters.
