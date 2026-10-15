# Shadow Rider anti-Path / Thorns counter: Stadium-cut sensitivity

## Why this matters

The [source-aware anti-Path/Thorns launch model](../shadow_rider_paid_search_allocation/) tests a hypothetical Aichi champion Shadow Rider 60 with one Canceling Cologne and one Flutter Mane. The prior 60-card grouping obtains these two slots by cutting two of the original deck's **three Stadium** copies, leaving only one Stadium plus its original Field Blower as Path answers. Which remaining Stadium is kept was not named by the grouped model.

The resulting 7.327398814% conditional early-launch access is highly sensitive to that assumed cut package. This study asks what changes if the champion keeps one or both additional Stadiums, using an equal number of unspecified *other Trainer* slots instead. It is a resource-allocation sensitivity, **not a recommendation to cut unknown tactical Trainers**.

## Exact 60-card comparison

All three scenarios retain one hypothetical `swsh10-136` Canceling Cologne, one `sv5-78` Flutter Mane, 4 Mysterious Treasure, 4 Fog Crystal, one Quick Ball, one Forest Seal Stone, 11 Basic Psychic Energy, the original Pokémon counts plus Flutter, and one `sm2-125` Field Blower. The Path-answer category represents that Blower plus each retained replacement Stadium. It assumes the retained Stadiums can replace opposing Path to the Peak.

| Stadiums kept from original three | Stadiums cut | Other Trainers cut | Path-answer cards including Field Blower | Restricted launch access | Flutter-feasible access |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 2 | 0 | 2 | **7.327398814%** | 3.617383668% |
| 2 | 1 | 1 | 3 | **8.041497019%** | 3.937586761% |
| 3 | 0 | 2 | 4 | **8.688630294%** | 4.224959455% |

Retaining a second original Stadium increases this restricted access endpoint by **0.714098205 percentage points** over the two-Stadium-cut baseline. Retaining all three increases it by **1.361231480 points** over baseline, with a further **0.647133275-point** improvement beyond the two-Stadium case.

The full exclusive source decomposition (Cologne-only / Flutter-only / both) is:

| Stadiums kept | Cologne-only | Flutter-only | Both |
| ---: | ---: | ---: | ---: |
| 1 | 3.710015146% | 3.199759737% | 0.417623931% |
| 2 | 4.103910258% | 3.473660940% | 0.463925820% |
| 3 | 4.463670840% | 3.718136716% | 0.506822739% |

The experiment preserves original 60-card size by exactly swapping one Stadium source class against one other-Trainer class at each step. It does not choose which other Trainer would actually leave. A concrete playable counterfactual list must specify that cut and evaluate its lost effects.

## Exact method and validation

The [reproducer](reproduce.py) imports the existing full 60-card paid-search and shared-Fog/Prize solver and the [turn-boundary source partition](../shadow_rider_thorns_continuation/). It preserves the original accepted-seven, first natural draw, and six-Prize weighting, then changes only the grouped Path-answer and otherwise-unmodeled Trainer counts. Exact integer fractions, launch-source inclusion/exclusion and source-print assertions are checked in all scenarios.

An independent labeled-card miniature-deck enumeration compares the grouped evaluator for the original Path-answer count and the full two-Stadium-restoration count. The original route partition itself passed a separate 83,720-world oracle and [Windows CI regression](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38727538806). This sensitivity model has its own [manual-only workflow](../../../.github/workflows/validate-shadow-rider-path-cut-sensitivity.yml) to avoid repeatedly spending CI on an exact multimillion-state calculation.

Reproduce from repository root using `python -m results.tests.shadow_rider_path_cut_sensitivity.reproduce`.

## Strategic interpretation and limitations

A Stadium copy is valuable here because it answers Path directly and, depending on which Stadium is retained, may also influence later Max Geist cost or Bench capacity. However, the grouped solver treats all Path-answer copies as interchangeable **for the initial Stadium-removal gate**; the choice between Dimension Valley and Sky Field is strategically consequential after that first turn. The alternative cut slots also include potentially essential draw, gust, recovery, search, or disruptive Trainers, whose lost value the restricted model does not estimate.

All percentages are **K1-style information-privileged first-turn card-access probabilities conditional on the stipulated opposing Path + Active Iron Thorns board**. They exclude nonanticipatory decisions, actual action sequencing, opponent attacks, second-turn Flutter survival, sufficient Energy in hand to charge, pivots, damage and match results. As shown in the continuation audit, a Cologne-only launch generally loses its Underworld Door window once Cologne expires. This study establishes a cut sensitivity worth testing, with no claim that a more Stadium-heavy 60 wins more matches.

**Next:** choose and print-validate actual alternative Trainer cuts, model the lost effects and competing Stadium functions, and test sustained charging/damage against an opposing Thorns turn before recommending any swap to the published champion.
