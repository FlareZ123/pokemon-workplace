# Exact intermediate Bench-guard posterior from final survivors

## Research question

Suppose two forced Bench contractions choose their discarded Pokémon uniformly at random. A later observer or state-search algorithm knows the final Bench survivors but has forgotten which Pokémon were present at the intermediate stage. What is the exact probability that all prerequisites for a specified Ability were simultaneously present in that stage?

The probability depends on how many prerequisite Pokémon survive to the final stage. It is an exact combinatorial conditional distribution, and it can restore correct probability weights after merging intermediate histories.

Implementation: `tools/bench_guard_history_posterior.py`.  
[Windows CI 38133534623 succeeded](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38133534623).

## Clearly specified probability model

There are `n` distinct original Bench objects. A first forced contraction chooses a survivor set `A` of size `a` uniformly from all `C(n,a)` choices. A second chooses final survivors `S subseteq A` of size `b` uniformly from all `C(a,b)` choices, with `0 <= b <= a <= n`.

A set `G` of `d` prerequisite original Bench objects enables an optional intermediate action iff every member of `G` belongs to `A`.

Only Bench-choice randomness is modeled. This is an intentionally hypothetical **uniform discard policy**. Competitive players choose discards strategically, and a real match may involve additional actions, information and lock effects. No empirical frequency or win rate is asserted.

## Exact conditional formula

Condition on a particular observed final survivor set `S`, of size `b`.

Every first-stage survivor set `A` containing `S` is equally likely. The number of such intermediate sets is `C(n-b,a-b)`.

Write `r=|G intersect S|` and `g=d-r`, the number of required objects **absent from the final Bench**. To have been present at the intermediate stage, those `g` objects must have been among the `a-b` original objects retained temporarily and discarded only by the second contraction.

Thus the number of eligible intermediate sets given `S` is `C(n-b-g,a-b-g)`. The exact posterior is

`P(G subseteq A | S) = C(n-b-g,a-b-g) / C(n-b,a-b)`.

The zero-binomial convention handles `g>a-b`, in which case the event is impossible.

An equivalent expression is

`P(G subseteq A | S) = C(a-b,g)/C(n-b,g)`

for valid nonnegative parameters, with the usual zero convention.

The original physical action-path multiplicity `C(n-b,a-b)` therefore becomes the denominator of the conditional belief rather than merely a search-space reduction factor.

## Source-grounded Lunatone/Solrock example

Use a five-occupant Bench with Lunatone `me1-74` and Solrock `pgo-39` as two named prerequisites for Lunar Cycle. First contract from five to four, then to three.

Each final survivor set has two possible preceding four-Pokémon intermediate Bench sets.

| `r`, prerequisite Pokémon in final `S` | Number of final survivor sets | Eligible intermediate histories per final set | Posterior guard available |
| ---: | ---: | ---: | ---: |
| 2 | 3 | 2 of 2 | 1 |
| 1 | 6 | 1 of 2 | 1/2 |
| 0 | 1 | 0 of 2 | 0 |
| **Total** | **10** | **12 of 20 overall** | **3/5 marginal** |

The source-backed Ability can require a Basic Fighting Energy payment and draw three cards; this experiment only assigns probability to its **named-Pokémon prerequisite availability**, assuming payment and legal use would be possible if the guard survived.

In a controlled policy that always uses the action when it is available, the probability of using it is exactly `3/5`. If the action is instead used with probability `p=1/2` whenever eligible, independently of the particular intermediate survivor choice, the unconditional probability of use is `3/10`. These are policy-dependent model probabilities.

## Recovering weighted terminal outcomes

Every final survivor set `S` occurs with probability `1/C(n,b)` under the stipulated two uniform choices. If the action is used with conditional probability `p` when its prerequisites were present at the intermediate stage, then

`P(S, action used) = [1/C(n,b)] * p * P(G subseteq A | S)`

and

`P(S, action skipped) = [1/C(n,b)] * (1-p*P(G subseteq A | S))`.

Summing across all `S` recovers

`P(action used) = p * C(n-d,a-d)/C(n,a)`.

The action-execution outcome is assumed to be a fixed distinguishable off-board change, as in the earlier action-equivalence experiments. Full deck-draw stochasticity and card-effect text would require further branching within each action-used state.

## Eight-slot example

For the six-object Regigigas `swsh10-130` Ancient Wisdom prerequisite family under the abstract geometry `8 -> 7 -> 5`, suppose the complete six-object named guard is initially on the Bench.

The final five-slot Bench may contain `r` members of the six-element guard. The posterior that *all six* were present at the intermediate seven-slot stage is:

| Guard objects remaining finally | Guard-enabled posterior |
| ---: | ---: |
| 5 | 2/3 |
| 4 | 1/3 |
| 3 | 0 |

Marginalizing over final sets gives `P(guard at intermediate)=C(2,1)/C(8,7)=1/4`.

The real Regigigas Ability requires an Energy recovery destination and additional legal action conditions. These percentages describe only the hypothetical random Bench subset process.

## Independent exact validation

The regression enumerates all `0<=b<=a<=n` for `n=0,...,8`, every guard cardinality `0<=d<=n`, and every distinct final survivor set `S` of the required size. It independently counts all intermediate `a`-object sets that contain `S` and which also contain the guard, then compares these exact counts to the closed-form binomial counts.

All **18,943** independent case comparisons passed. Exact `fractions.Fraction` arithmetic avoids floating-point normalization drift.

Additional assertions cover both the five-to-four-to-three Lunar Cycle example and eight-to-seven-to-five Regigigas example, invalid parameters, endpoint joint-probability normalization, and marginal use probabilities for `p=1` and `p=1/2`. [Windows run 38133534623 succeeded](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38133534623).

## Interpretation and limitations

This creates an exact probability-preserving quotient for the stated randomized policy, whereas previous results established only *reachability* and equality of physical successor states. A simulator that merges intermediate states while retaining stochastic outcome weights can use this posterior instead of assigning uniform probability to distinct final state/action combinations.

When the player conditions discard choices on desired Abilities, Energy, hidden cards, matchup, or turn plans, the intermediate histories have different weights. The displayed uniform posterior then becomes invalid. Any learned or game-theoretic policy must supply its own transition weights, and observations of actual discarded cards may eliminate uncertainty entirely.

Related analyses:
- [Bench physical confluence](../bench_contraction_physical_confluence/).
- [Physical optional Lunar Cycle census](../bench_contraction_action_equivalence/).
- [Single-action guard quotient](../bench_intermediate_guard_equivalence/).
