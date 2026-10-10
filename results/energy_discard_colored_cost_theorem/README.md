# A general three-colored-Energy continuation theorem

## Question

Does the Regidrago VSTAR / Dragon Impact minimum-card discard reversal rely on Regidrago's specific Grass/Grass/Fire attack cost?

**No.** In the bounded Energy model below, the reversal extends to every three-unit attack cost composed of *colored* Energy requirements. The exact count depends only on the number of distinct required colors.

## Controlled model and notation

A Dragon Pokémon has exactly four attached cards: one active Double Dragon Energy (provides two Energy units of any type) and three single-unit Basic Energy cards. Its current attack requires discarding two generic Energy units. The next desired attack costs exactly three colored Energy units drawn from the nine Basic Energy types in the paper Expanded card pool. Colorless requirements, Energy-restriction effects, state-dependent provider deactivation, and alternative attacking methods are excluded.

An **irredundant** payment either discards DDE alone (one card) or discards two Basic Energy cards (retaining DDE and one Basic). Only attacks initially Energy-ready are considered.

Let `d` denote the number of distinct required colors, from one to three. The multiset of three Basic Energy types is unordered, and there are `C(9+3-1,3)=165` such multisets.

Initial readiness holds if and only if at least one of the three Basics provides a color present in the three-colored attack cost. DDE can then supply the two other required typed units. This gives

`I(d) = C(11,3) - C(11-d,3)`.

The payment discarding DDE leaves exactly the three Basics, so it preserves the next attack precisely if those Basics have **exactly** the attack's three-color cost multiset. There is one such attachment-type multiset per cost.

Every initially ready mix admits a two-Basic payment retaining one Basic whose color participates in the attack cost, and DDE supplies the other two requirements. Hence the one-card payment loses the next attack but a two-card payment preserves it in `I(d)-1` of the `I(d)` ready type compositions.

## Exhaustive computational result

| Distinct required colors | Three-color cost example | Initially ready Basic type mixtures | Continuation reversals | Exception |
| --- | --- | ---: | ---: | ---: |
| 1 | Grass/Grass/Grass | 45 | 44 | 1 |
| 2 | Grass/Grass/Fire | 81 | 80 | 1 |
| 3 | Grass/Fire/Water | 109 | 108 | 1 |

The program `tools/energy_discard_colored_cost_theorem.py` enumerates all **165** three-colored attack-cost multisets and all **165** three-Basic attachment-type multisets, for **27,225 pairs**. The implementation uses the existing exact typed Energy matching solver as a separate check of each readiness predicate and payment outcome. All assertions passed locally.

There are nine all-same-type demands, 72 demands with exactly two different types, and 84 with three different types. Across their 27,225 cost/mix pairs, 15,393 begin Energy-ready. Among those, 15,228 have the continuation reversal, while 165 preserve readiness after the one-card DDE payment.

Run `python -m tools.energy_discard_colored_cost_theorem` at the repository root.

## Strategic meaning

A local optimization objective minimizing *physical Energy-card loss* may systematically prune the continuation-preserving choice, even when the next attack's exact typed cost is known. Where such a future attack is strategically valuable, the remaining Energy type profile is essential to action ranking.

This is a state-space theorem under explicit resource constraints. The 27,225 pairs and group proportions are unweighted type-composition counts. They carry **no tournament, deck construction, or gameplay-frequency implication**.

The result extends the constructive printed-card example in [energy_discard_continuation_frontier](../energy_discard_continuation_frontier/) and its card-multiplicity weighting in [energy_discard_continuation_weighted](../energy_discard_continuation_weighted/). The game rules for two-unit discard and every-type Energy are documented in the bundled Advanced Player's Rulebook and Double Dragon Energy text (`xy6-97`).

## Limits and scope

This study counts guaranteed attacks whose costs contain exactly three colored requirements. Colorless cost symbols are wildcards; the formula would need a separate case and **must not** be applied unchanged. It assumes DDE remains active when retained on the same Dragon Pokémon. It omits normal attachment opportunities, recovery, prize taking, and opponent turns. Real strategy may prefer the lower physical-card payment for unrelated objectives despite losing immediate next-attack readiness.
