# Synergy-aware Bench contraction and irreversible discard decisions

## Research question

When the affected player must discard Pokémon because their Bench capacity contracts, is it sufficient to discard the occupants with the lowest **individually assigned** retention values? If a second contraction is possible, does choosing the best immediate surviving Bench always leave the best later surviving Bench reachable?

**Answer:** No to both. Even a small positive two-Pokémon interaction changes the optimal survivors. A capacity-four survivor set maximizing immediate utility need not contain any capacity-three survivor set maximizing the eventual utility. A later Stadium replacement can make an earlier individually optimal discard irreversible.

The exact finite-state model and tests are in `tools/bench_synergy_contraction.py`. No game win-rate or matchup probability is inferred.

## Rules and card-text witnesses

The supplied Advanced Player's Rulebook §A-04 specifies a default five-Pokémon Bench limit; its general rules allow card text to override ordinary limits. The legal card records in the bundled Expanded snapshot include:

- **Collapsed Stadium** (`swsh9-137`): each player has at most four Benched Pokémon; if there are five or more, the player discards Benched Pokémon until four remain.
- **Parallel City** (`xy8-145`): its selected side can have at most three Benched Pokémon and must discard excess when the Stadium comes into play.
- **Lunatone** (`me1-74`), **Lunar Cycle**: once during the turn, with Solrock in play, a Basic Fighting Energy can be discarded to draw three cards.
- **Solrock** (`pgo-39`), **Sun Energy**: its Ability attaches a Psychic Energy from the discard pile to a Lunatone.

These provide a mechanically feasible **5 -> 4 -> 3** capacity-change sequence across distinct turns and a card-text example of a beneficial conditional pair. The utility assigned to keeping that pair depends on the actual Energy resources, matchup, and other effects. The example below uses an arbitrary numerical pair bonus, not a claim that Lunar Cycle is worth 30 units in a tournament.

When two Stadiums are played in sequence, the second replaces the first. Exact order, available turns, and which player controls the restrictions must be supplied by a downstream game model; this tool resolves survivor selection given a capacity-change event.

## Model

Let `S` be a subset of the starting Bench occupants and `v_i` their independent retention values. For pair interactions `b_(i,j)`, define the illustrative utility

`U(S) = sum_{i in S} v_i + sum_{i<j, i,j in S} b_(i,j)`.

For a forced contraction to capacity `C`, choose exactly `min(C, |S|)` survivors that maximize `U`. This is a tiny exhaustive optimization because all currently cataloged Expanded Bench-capacity effects allow at most eight Bench occupants; the code enumerates combinations rather than using a heuristic.

The original additive model is exactly the special case where all pair bonuses are zero.

### Witness: immediate optimality fails to preserve later options

Five occupants initially fill the normal Bench:

| Occupant | Base retention score | Conditional interaction |
| --- | ---: | --- |
| E, core attacker | 100 | none |
| A, Lunatone role | 0 | +30 if B remains |
| B, Solrock role | 0 | +30 if A remains |
| C, second attacker | 22 | none |
| D, alternative attacker | 20 | none |

All values are illustrative; only the **pair-dependence structure** is grounded in real card text.

At the initial **5 -> 4** contraction, the best immediate surviving set is `E,A,B,C` worth **152**, so `D` is discarded.

If the player then experiences a **4 -> 3** contraction, the best remaining three are `E,A,B` worth **130**.

Had the capacity been reduced directly from five to three, the optimal surviving set would instead be `E,C,D` worth **142**.

The early myopic choice causes an **irrecoverable 12-point utility deficit** under the fixed static utility model. The optimal four-survivor set is not a superset of the optimal three-survivor set.

### Anticipating a future contraction

Suppose the first shrink to four is certain, and a further shrink to three happens before the utility is realized with model probability `p`. If it does not happen, the first four survivors remain. The player chooses survivors to maximize **expected terminal utility**.

- Preserve `E,A,B,C`: expected utility `(1-p)*152 + p*130 = 152 - 22p`.
- Discard `A` or `B` instead, preserving `E,C,D` plus the other partner: expected utility `142` at either resulting capacity.

Thus, the threshold is exactly **`p = 5/11`**. Above this hypothetical probability, a forward-looking player should accept the lower immediate score by breaking the pair proactively, preserving both attackers. At `p = 1/2`, forward-looking expected utility is **142**, versus **141** for immediate optimization. These values assume the probability is externally supplied and unaffected by the first discard choice.

This is a small deterministic decision model with one stochastic transition, not an estimate of the probability that an opponent actually plays Parallel City.

## General counterexample to singleton-value greedy

Consider three occupants `A`, `B`, `F` and capacity two. Let `v_A=v_B=0`, `v_F=1`, and `b_(A,B)=M>1`.

Discarding the lowest-singleton-value occupant drops `A` or `B` and gives retained utility `1`. Exact joint optimization retains `A,B` with utility `M`. The regret `M-1` can be arbitrarily large in the abstract model. Positive pairwise synergy alone suffices to falsify singleton-based discard choice.

## Extension: payoff timing changes the threshold

The previous `5/11` threshold assumes only utility at the final checkpoint matters. A different timing model rewards the first retained Bench **before** any possible second contraction and also rewards the later board, weighted by `δ`. That can represent a conditional Ability that is actually usable during the intervening turn, with its realized benefit counted separately from later board flexibility.

Define the two-period abstract score as

`V(S_first) = U(S_first) + δ * [(1-p) U(S_first) + p max_{S_final subset S_first, |S_final|=3} U(S_final)]`.

Under the original bonus-30 witness:

- Preserve the Lunatone/Solrock pair at the first contraction: `V_pair = 152 + δ(152 - 22p)`.
- Discard one partner and preserve both attackers: `V_flexible = 142 + 142δ`.

For `δ=1`, the forward-looking choice flips only when `p > 10/11`. At `p=1/2`, preserving the pair scores **293** compared with **284** for the flexible choice, reversing the earlier terminal-only ranking at the same probability. At `p=1`, the pair scores **282** and the flexible choice **284**.

In general, for positive `δ`, the threshold is `p > 5(1+δ)/(11δ)`. If `δ <= 5/6`, this threshold is at least one, so the example's immediate pair-preservation strategy remains optimal for every admissible second-contraction probability.

This isolates a crucial methodological choice: **has the synergy already delivered value by the time a later Bench restriction arrives?** A static utility of the surviving board cannot answer that. The actual Pokémon game must supply turn order, first-stage Ability usability, and the timing of any Stadium change.

## Validation

Run `python tools/bench_synergy_contraction.py --self-test` to verify:

1. the 5 -> 4 -> 3 counterexample and nonnested optimal survivors;
2. the probability threshold using rational arithmetic;
3. agreement with independent top-k retention in all tested additive cases of up to eight occupants;
4. arbitrarily large singleton-greedy regret from stronger pair bonuses.

Run without flags to emit the deterministic example as JSON. A GitHub Actions workflow at `.github/workflows/validate-bench-synergy-contraction.yml` runs the same tests.

## Interpretation and limitations

A role-dependent interaction model is more faithful than scalar, independent card values whenever **keeping one occupant changes the usefulness of another**. The pair bonuses are one representation of complementary roles, shared Abilities, Energy access, alternate attackers, Prize liabilities, or overlapping engines. Negative interaction values can also represent competing resources or redundancy.

The model treats all initial occupants as Benched, every subset of the specified size as mechanically discardable, and the affected player as the discard chooser. It omits switching before a contraction, Ability suppression, attached-card recovery, Knock Out triggers, draw/search access, Stadium access, current Active Pokémon, evolving positions, and the dynamics of opponent play. Pair bonuses approximate a full continuation evaluator; interactions among three or more Pokémon require a higher-order set utility.

**Next integration:** Feed the optimizer a board-state-derived continuation function and action-conditioned probabilities of future contractions. Compute real card access, resource costs, and dependencies before assigning conditional utilities. A useful first test is the evolving value of the Lunatone/Solrock pair when the Fighting Energy discard requirement cannot be met.
