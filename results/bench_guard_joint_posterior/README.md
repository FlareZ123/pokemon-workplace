# Joint probability of intermediate Ability prerequisites after Bench contraction

## Research question

Given a final Bench after two forced contractions, can the probability that **two distinct named-Ability guards** were jointly present at an intermediate stage be computed as the product of their separate availability probabilities?

**No in general.** Joint availability is determined by the union of prerequisite Pokémon. Missing prerequisites compete for limited temporary Bench space. Their indicators may be negatively or positively correlated, depending on overlap and the known final survivors.

Implementation: `tools/bench_guard_joint_posterior.py`.  
[Windows CI 38133713699 passed](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38133713699).

## Controlled stochastic experiment

Start with `n` distinct original Bench occupants. The Bench is forcibly contracted to `a` survivors, then to `b` final survivors (`0<=b<=a<=n`). Each stage selects a uniformly random survivor subset. No abilities, energy, card draws or other gameplay actions intervene; this is an exact combinatorial availability model under a **hypothetical** random-discard policy.

Let `S` be a particular final survivor set. Two intermediate Ability-prerequisite sets are `G_1` and `G_2`.

An Ability guard is available at the intermediate stage if all of its required original Pokémon objects are present. For conditional probabilities, define `g_i = |G_i \\ S|` and `g_{12}=|(G_1 union G_2) \\ S|`.

From the single-guard exact posterior `F(g)=C(n-b-g,a-b-g)/C(n-b,a-b)`, we obtain:

- `P(E_1 | S)=F(g_1)`;
- `P(E_2 | S)=F(g_2)`;
- `P(E_1 and E_2 | S)=F(g_{12})`;
- `Cov(1_{E_1},1_{E_2} | S)=F(g_{12})-F(g_1)F(g_2)`.

The independent-product error is `F(g_1)F(g_2)-F(g_{12})`. Positive values mean the product **overstates** joint reachability; negative values mean it **understates** it.

The unconditional joint probability at intermediate stage is `C(n-|G_1 union G_2|,a-|G_1 union G_2|)/C(n,a)`.

## Eight-occupant disjoint-source example

The supplied Expanded card pool provides the named prerequisites of:

- Lunatone `me1-74` Lunar Cycle and Solrock, two distinct objects;
- Regigigas `swsh10-130` Ancient Wisdom, requiring five other named Regi Pokémon in addition to its source, six distinct objects.

These **eight** prerequisite objects are disjoint in the modeled initial Bench. Suppose the first contraction changes the Bench from eight to seven. Exactly one of the eight is discarded.

- The two-object Lunatone guard remains whole if the discarded Pokémon belongs to the six-object Regigigas guard, probability `6/8=3/4`.
- The six-object Regigigas guard remains whole if the discarded Pokémon belongs to the two-object Lunatone guard, probability `2/8=1/4`.
- Both guards can never be present together after one of their combined eight objects was discarded: joint probability **zero**.

Their two event indicators are perfectly anticorrelated in this controlled experiment. An independent marginal product would falsely assign `(3/4)(1/4)=3/16=18.75%` to joint reachability.

Condition on an additional contraction to five final survivors `S` containing **one** Lunatone-guard object and **four** Regigigas-guard objects. Among the three objects missing from the final Bench, the intermediate stage retained two. Jointly,

`P(E_L|S)=2/3,` `P(E_R|S)=1/3,` `P(E_L and E_R|S)=0.`

The independence product would then overstate joint eligibility by `2/9`, or about 22.22 percentage points.

These are mathematically exact under the stipulated uniform survival process. They do not imply the decks reliably establish eight prerequisites, nor do they quantify how often an actual game has these boards.

## Overlap can reverse the direction of the error

Take the abstract five-to-four-to-three contraction with guard sets `G_1={0,1}` and `G_2={1,2}`. They share object `1`. Observe final `S={0,2,3}`.

Exactly two intermediate sets can lead to `S`: one temporarily includes object `1`, the other includes object `4`. If object `1` was present, **both guards** were satisfied; otherwise neither was.

Thus `P(E_1|S)=1/2`, `P(E_2|S)=1/2`, and `P(E_1 and E_2|S)=1/2`. The product of marginals is only `1/4`, an **underestimate by 25 percentage points**.

The overlap example is a mathematical guard grammar witness, not a claim that this exact pair of printed Abilities exists.

## Independent validation

The code exhaustively tests every ordered pair of possible guard subsets for original Bench sizes `n=0,...,5`, all `0<=b<=a<=n`, and every corresponding final survivor set `S`. It independently enumerates the actual `a`-object intermediate sets containing `S` and counts each guard and their joint availability.

All **128,397** parameter cases matched the three exact posterior formulas, using rational fractions throughout. It separately tests the source-backed eight-object disjoint guard example and the overlapping positive-correlation example.

[Windows-hosted GitHub Actions run 38133713699 succeeded](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38133713699).

## Optimization and modeling implications

An access hypergraph that treats several named-Ability requirements as independent probabilities may invent attainable combinations or systematically distort their modeled likelihood. Correct computation requires the union of simultaneously needed source/prerequisite objects and the finite intermediate Bench capacity.

The formula complements [bench_multi_guard_action_equivalence](../bench_multi_guard_action_equivalence/), which establishes the exact joint feasibility of multiple action subsets, and [bench_guard_history_posterior](../bench_guard_history_posterior/), which supplies the conditional single-guard probability.

The main limitation is the uniform subset policy. With strategically chosen discards, temporary Ability use, changing resources or observed opponent actions, the conditional intermediate-state distribution is no longer uniform. It must be computed from the actual action policy and observations. The formula is a sound reference oracle only for the controlled distribution it states.
