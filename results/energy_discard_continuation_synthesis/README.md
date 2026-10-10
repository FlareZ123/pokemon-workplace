# Continuation-aware Energy payments: evidence synthesis

**Scope:** paper Pokémon TCG Expanded, Black & White onward, using supplied card snapshots and Advanced Player's Rulebook; source-specific witness with Regidrago VSTAR, Salamence ex, and Double Dragon Energy.

## Main conclusion

For a copied attack with a generic two-Energy discard, **minimizing the number of physical Energy cards discarded is insufficient to preserve future attack options**. Physical card identity, currently provided Energy types/units, next attack costs, recovery resources, and opponent's response all belong to the continuation state.

The strongest concrete witness: Regidrago VSTAR (`swsh12-136`) with DDE (`xy6-97`), Basic Grass and two Basic Fire copies uses Apex Dragon to copy Salamence ex's (`sv9-114`) Dragon Impact, doing 300 damage and discarding two Energy. A one-card payment discards DDE and leaves Basic Grass/Fire/Fire, which **does not currently pay** Apex Dragon's Grass/Grass/Fire cost. Three distinct two-Basic payments retain DDE and one Basic (Grass or Fire), which **do** pay the next Apex Dragon cost before other actions.

This is an **Energy-readiness and action-opportunity** result, not a theorem that all real matches favor two-card discards.

## Source and rules grounding

- Regidrago VSTAR (`swsh12-136`): Apex Dragon Grass/Grass/Fire; Legacy Star recovers up to two cards from discard after discarding top seven, and uses the once-per-game VSTAR Power.
- Salamence ex (`sv9-114`): Dragon Impact does 300 and discards two Energy from the attacking Pokémon.
- DDE (`xy6-97`): provides two Energy units of every type while attached to a Dragon Pokémon; one physical card can satisfy two Energy-unit requirements.
- The supplied Advanced Player's Rulebook v3.4 explains copy attacks, multi-unit Energy discard through the Ignition Energy example, typed Energy provision and physical Energy-card categories.
- Enhanced Hammer (`sv6-148`): discards an opposing Special Energy; Temple of Sinnoh (`swsh10-155`): suppresses Special Energy effects and forces Colorless provision.
- [Official 2025 Expanded strategy example](https://www.pokemon.com/uk/features/a-deep-dive-into-the-2025-pokemon-tcg-expanded-format) includes a Regidrago list with one Salamence ex, four DDE, three Basic Grass and two Basic Fire, corroborating archetype relevance, without proving any opening or attack frequency.

These are card/rulebook facts. The payment outputs and type-population counts below are exact computations under fixed assumptions.

## Evidence ladder

| Evidence level | Result and scope | Reproducer |
| --- | --- | --- |
| Constructive physical-card witness | Four distinct **irredundant** generic two-unit payments; one-card DDE option loses next Apex readiness, all three two-Basic payments preserve | [base result](../energy_discard_continuation_frontier/), `tools/energy_discard_continuation_frontier.py` |
| Reproducibility check | Independent bitmask oracle over 2,904 synthetic payment configurations; exact print checks for the witness | `results/energy_discard_continuation_frontier/reproduce.py` |
| Type-multiset generalization | 165 possible three-Basic type multisets with DDE, 81 initially Apex-ready, 80 one-card reversals | [base result](../energy_discard_continuation_frontier/) |
| Weighted hypothetical Basic supply | For `g` Grass, `f` Fire, `o` other Basic copies, conditional reversal `1-C(g,2)f/[C(g+f+o,3)-C(o,3)]` | [weighted result](../energy_discard_continuation_weighted/), `tools/energy_discard_continuation_weighted.py` |
| Source-list card-count bridge | In published 2025 example list with g=3, f=2, o=0, 4 of 10 uniformly sampled three-Basic mixes reverse the one-card preference | [weighted result](../energy_discard_continuation_weighted/) |
| Colored cost generalization | 165 three-colored next-attack cost multisets × 165 Basic mixes = 27,225 pairs; 15,228 reversals among 15,393 initially ready | [cost theorem](../energy_discard_colored_cost_theorem/), `tools/energy_discard_colored_cost_theorem.py` |
| Colorless-cost extension | 220 three-symbol next-cost multisets × 165 Basic mixes = 36,300 pairs; 23,328 reversals among 24,468 initially ready | [Colorless extension](../energy_discard_colored_cost_theorem/COLORLESS_EXTENSION.md), `tools/energy_discard_colorless_cost_extension.py` |
| Opponent-response ablation | Enhanced Hammer and Temple of Sinnoh neutralize immediate next-Apex readiness after the DDE-preserving payments, with no intervening restorative actions | [disruption result](../energy_discard_continuation_disruption/), `tools/energy_discard_continuation_disruption.py` |
| Printed recovery line | Once-per-game Legacy Star can retrieve discarded DDE on a later turn; restoring its attachment consumes the VSTAR Power and normal hand attachment | [Legacy Star extension](../energy_discard_continuation_disruption/LEGACY_STAR_RECOVERY.md), `tools/energy_discard_legacy_star_recovery.py` |

The exact type-signature counts are **unweighted artificial configuration counts**. They must not be used as tournament frequencies. The published example-list's 4/10 is a hypothetical *uniform Basic attachment selection* from known card counts, and likewise is not an in-game rate.

## Strategic hierarchy for comparing payments

A decision model should preserve at least five distinct dimensions.

1. **Mechanical payment validity:** what exactly can the attack discard in its current phase? Energy *cards* versus Energy *units*, fixed counts, typed restrictions, current Special Energy effects, and whether a chosen physical subset can satisfy the clause.
2. **Immediate downstream readiness:** can the remaining attached units pay a future attack, and can the user survive until that turn? Colorless attack-cost symbols accept any Energy type; explicit typed Energy-discard instructions require type matching and must not share the wildcard logic.
3. **Restoration capacity:** which missing resources can be re-established through Legacy Star, an attachment, Supporter, Trainer, draw, or recovery? Which one-use and once-per-turn opportunities does that cost?
4. **Opponent response:** can opposing Items or Stadiums suppress DDE before its next use? Do alternative states offer more recoverable Basic Energy material if the opponent can always counter Special Energy?
5. **Game objective:** can that future attack lead to a meaningful KO, Prize path or lock? Does recovery contend with more important VSTAR, Supporter or attachment actions?

This is a precise instance of the supplied human prior-research ideas about **Active Move Realism**, **Discard Capable Index**, **Supporter contention**, and **connector domination**. The priority should be evaluated from actual state transitions and resulting strategic payoff, rather than assigning a permanently low cost to physical-card discards.

## Remaining gaps

**Rule-level:** This work enumerates *irredundant* payments sufficient for the generic two-Energy clause. It does not claim to exhaust every legal multi-card overpayment pattern under sequential effect resolution; additional overpayment rules would need explicit source/ruling verification. The existence of the four constructed payments and the continuation comparison remains sufficient for the proof.

**Game-state modeling:** All provider profiles are assumed currently active, except for explicit Temple response. The environment lacks full dynamic Special Energy suppression and full physical Energy-card identity transitions with simultaneous event/replacement effects.

**Strategy:** No opponent turn sequence, stadium counterplay, surprise Item lock, damage resolution, prize exchange, draw distribution or actual policy search is simulated. The symbolic opportunity-cost expression in the disruption result is a toy preference boundary with unknown values.

**Research next:** Connect these state-preserving payments to the central Energy-route action budget and a physical post-attack zone-transition model. Use exact card-specific source rules and a short full-turn continuation simulation to quantify action opportunity costs, then compare against minimum-card-only pruning on reproducible controlled fixtures.

## Reproduction map

The repository-root Python entry points are:

`python -m results.energy_discard_continuation_frontier.reproduce`

`python -m tools.energy_discard_continuation_weighted`

`python -m tools.energy_discard_colored_cost_theorem`

`python -m tools.energy_discard_colorless_cost_extension`

`python -m tools.energy_discard_continuation_disruption`

`python -m tools.energy_discard_legacy_star_recovery`

The tools use the repository's bundled `resources/` snapshot. The local independent exact enumerations for the base, weighted, and cost-multiset analyses were run and verified. The remaining reproducer scripts embed state and print assertions but do not constitute a full gameplay engine.


## Causal provider control: flexible types, rather than two-unit capacity alone

A matched ablation in [Double Dragon versus Double Colorless Energy](../energy_discard_special_provider_ablation/) holds one two-unit Special Energy card and three Basic Energy cards fixed, replacing DDE with DCE.

For **every** three-symbol attack cost drawn from the nine Basic Energy types plus Colorless, the three Basics alone can already pay the cost whenever the DCE-plus-Basics state can pay it. This is because DCE adds only Colorless units, whereas any three Basic Energy units can fill Colorless requirements after the colored requirements have been met.

Consequently:

`ready(DCE + 3 Basics, cost) == ready(3 Basics, cost)`.

And the precise set of DDE states where the Special Energy's flexible types create additional attack readiness is

`ready(DDE + 3 Basics, cost) and not ready(3 Basics, cost)`.

This is **exactly** the set where discarding DDE as one physical two-Energy payment loses that readiness. The independent exhaustive verification found **23,328 such pairs** out of 36,300 cost/mix pairs, versus **zero** minimum-card DCE continuation reversals among states initially ready with DCE. The difference isolates Energy **type flexibility** as the mechanism and reinforces why totals of physical cards or Energy units alone are insufficient.

Source prints: DDE `xy6-97`; DCE `bw4-92`. The ablation is controlled and counterfactual; the DCE version of a specific DDE-enabled attack state may have been unable to launch the attack in the first place.
