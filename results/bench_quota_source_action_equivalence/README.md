# Exact Bench-history equivalence with a live Supporter quota source

## Question

When a Bench-dependent Ability temporarily raises the per-turn Supporter limit, how many additional action-resource states can be reached through two staged Bench contractions, including paths where the quota source is **discarded after** its extra Supporter use?

An exact formula and independent exhaustive enumeration show that transient increased action capacity can create legal histories whose final board no longer contains the source that permitted them.

Implementation: `tools/bench_quota_source_action_equivalence.py`.  
[Windows CI run 38133327769 passed](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38133327769).

## Printed rule witness and scope

Magnezone `bw8-46` is an Expanded-legal Stage 2 Pokémon in the bundled card pool. Its **Dual Brains** Ability says:

> During your turn, you may play 2 Supporter cards.

The provided Advanced Player's Rulebook ordinarily permits one Supporter per turn. The repository's earlier [action_quota_effects](../action_quota_effects/) result establishes a separate current limit and already-used count: once two Supporters have legally been played under Dual Brains, Magnezone leaving play returns the current limit to one, but the historical usage of two remains.

This investigation isolates that geometry. A designated original Bench object represents an unsuppressed active Magnezone source. Every other intervening legal requirement is externally supplied. Two or three **abstract** distinct Supporter transactions are each assumed to have a separately permitted, nontrivial, independently distinguishable off-board effect. They consume the same Supporter-use quota, and each optional transaction may require named original Bench objects still in play. The experiment does not simulate actual Supporter effect text, physical Trainer card movement, deck search, turn opening or setup, or Magnezone's Stage 2 evolution sequence.

## Closed-form model

Start with `n` distinct Benched objects, one designated Magnezone object `M`, and capacity reductions `n -> a -> b`, `0 <= b <= a <= n`. The source may be discarded at either stage.

For each action subset `U`:

- `|U|=0` or `1`: the normal Supporter limit suffices. Require the union `G_U` of all selected actions' original Bench prerequisites.
- `|U|=2`: the action subset requires `G_U union {M}` to coexist at the intermediate stage; only live Magnezone grants the necessary second Supporter use.
- `|U|>2`: prohibited because Dual Brains supplies at most two uses.

Let `d_U` be the size of the applicable union. The exact annotated history count for subset `U` is

`H_U = C(n-d_U,a-d_U) C(a,b)`.

The count of *distinct final survivor sets* reachable with that action subset is

`R_U = sum_{r=max(0,b+d_U-a)}^{min(d_U,b)} C(d_U,r)C(n-d_U,b-r)`

when `d_U <= a`, else zero.

The complete terminal-state quotient is `Q = sum_{U, |U|<=2} R_U`, when the action-resource effects are distinguishable by selected subset. This count retains the temporary grant through the action window: Magnezone only needs to be present at the **intermediate** stage, regardless of whether the player discards it during the second contraction.

## Five-to-four-to-three witness

Take `n=5`, `a=4`, `b=3` and two abstract resource-ready Supporter transactions whose effects require no other Bench object.

| Action subset | Annotated histories | Distinct complete terminal states |
| --- | ---: | ---: |
| No Supporter | 20 | 10 |
| Only Supporter A | 20 | 10 |
| Only Supporter B | 20 | 10 |
| Both, requiring Magnezone at intermediate stage | 16 | 10 |
| **Total** | **76** | **40** |

Under the ordinary one-Supporter limit, the final full-state count is **30**. A live Magnezone grant adds **10** distinguishable terminal resource-state classes, even though some histories that used both Supporters subsequently discard Magnezone.

For example, let Magnezone occupy initial Bench object 0. A first contraction to four retains it and discards object 4. Both abstract Supporters are played while Dual Brains permits two. A second contraction discards Magnezone, leaving original objects 1,2,3. The legal action history records two Supporter uses even though the final source is absent.

Alternatively, if the first contraction discards Magnezone, a second Supporter is unavailable under the default quota, potentially reaching the *same* final Bench with a different action/resource history. A simulator that derives previous Supporter usage from the *final* source's presence loses this distinction.

## Validation

The standalone code checks every ordered pair of guard subsets, every designated source object and every `0<=b<=a<=n` with `n=1,...,5`, for **125,004 parameter configurations**.

Its independent oracle enumerates all actual intermediate and final survivor subsets, computes the *live* Supporter-use limit from whether the specified source remains at the intermediate stage, enumerates zero, one or two chosen supported transactions, and forms exact `(final-survivor tuple, used-transaction subset)` signatures. The calculated history counts and full-state quotient match in every case.

Additional tests cover:

- source discarded during the second contraction after the second Supporter action;
- source discarded during the first contraction, preventing a second Supporter use;
- three alternative Supporter transactions, where Magnezone permits any pair but no triple;
- rejected invalid capacity order and invalid source identity.

[Windows-hosted CI 38133327769](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38133327769) completed successfully.

## Relation to earlier work

- [Action quota effects](../action_quota_effects/) establishes the general changing-limit / historical-usage state representation and card-text Magnezone witness.
- [Bench multiple-guard action equivalence](../bench_multi_guard_action_equivalence/) contributes action-prerequisite union feasibility. The quota-source model adds Magnezone to the union **only for action subsets that exceed the ordinary one-use limit**.
- [Bench physical confluence](../bench_contraction_physical_confluence/) proves pure-discard mergeability when no intervening action changes resources.
- [Bench intermediate-action counterexample](../bench_contraction_intermediate_action/) demonstrates a specific physical discard/draw action before its source is removed.

## Limits and future integration

The result is a conditional, abstract action-availability count. It assumes the selected Supporters all have relevant payable and nontrivial effects and that no prohibitions, turn ends, changing hand contents or other resource contention block them. Only one continuous Magnezone source is modeled; Ability locks or another source could change current quota. The published `TurnActionBudget` and `derive_action_quotas` should own actual usage transitions in a future fully materialized match model.

State-space cardinality is neither action probability nor matchup win rate. Different histories leading to the same final state may carry different decision probabilities and private observations, which must be represented separately if required.
