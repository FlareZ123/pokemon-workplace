# Physical confluence of pure staged Bench contractions

## Question

Can a game-state search collapse a sequence of forced Bench-size reductions into a single direct contraction **without losing the full exact physical-card ledger**?

Within an explicit restricted transition class, yes. The result is a state-space quotient with an exact multiplicity, useful for avoiding redundant search branches. It does not assert that all game histories involving these Stadiums are equivalent.

- Implementation and exhaustive regression: `tools/bench_contraction_physical_confluence.py`.
- Lower-level physical transition: `tools/bench_contraction_batch_conservation.py`.
- [Passing GitHub Actions run 38132208735](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38132208735).

## Conditions

The property holds for a board with `n` distinct Benched Pokémon objects undergoing two *certain*, *monotone* capacity reductions `n -> a -> b`, with `0 <= b <= a <= n`.

Assumptions enforced by the test composition:

1. No actions, card draw, observations, player choices beyond the mandated discard selections, or triggered effects are resolved between contractions.
2. Removed entire Pokémon stacks and all of their attachments move to the same exchangeable discard zone under both contractions.
3. The Active Pokémon stays in place; no promotion or terminal game-resolution decision intervenes.
4. Each retained object, stack, attachment, and game-state field stays unchanged by the pure contraction transition.
5. The physical identity ledger uses its normal canonical sorted card-count and materialized-instance representations.

These are physical-transition assumptions. Actual Stadium play requires the surrounding turn/rules engine to authorize the specific capacity changes, including Stadium replacement and turn budget.

## Exact theorem

Let `B` be the set of `n` original Bench objects. A first chosen contraction retains `A subseteq B`, `|A| = a`. A second retains `S subseteq A`, `|S| = b`. For every fixed final `S`, the initial intermediate survivor `A` may include any `a-b` of the `n-b` discarded-at-end objects. Hence each final survivor set has precisely

`M(n,a,b) = C(n-b, a-b)`

distinct two-stage histories. Consequently,

`C(n,a) * C(a,b) = C(n,b) * C(n-b,a-b)`.

The final physical board retains exactly the same object IDs and attached cards as directly contracting from `n` to `b` and discarding `B \\ S`.

Each off-board card class has the same final count: every removed physical Pokémon-stack card and attachment makes exactly one transition to discard, independent of removal order. Exchangeable counts are canonicalized in `ZoneCountState`. Remaining exact materialized instances are sorted by ID in `IdentityLedger`. Thus the **entire** `StackBoardMaterialState` is equal to the direct-contraction state, beyond simply matching which Bench names survived.

The quotient should carry path multiplicity only when modeling **histories**. For policy optimization with a payoff determined solely by the final state and no intermediate effects, evaluate each final survivor set once.

## Quantitative state-space reduction

| Capacities | Two-step histories | Distinct terminal physical states | Histories per terminal state |
| --- | ---: | ---: | ---: |
| 5 -> 4 -> 3 | 20 | 10 | 2 |
| 5 -> 5 -> 3 | 10 | 10 | 1 |
| 5 -> 3 -> 2 | 30 | 10 | 3 |
| 8 -> 5 -> 3 | 560 | 56 | 10 |

The 5-occupant cases are directly covered by the reproducible physical state tests. The 8-occupant row is an exact combinatorial extension; it was not run through the 5-occupant physical fixture.

## Evidence from physical conservation engine

`bench_contraction_physical_confluence.py --self-test` passes:

- all **21** pairs `0 <= b <= a <= 5` from a starting five-Pokémon Bench, comparing **complete equality** of every two-step result against its direct-contraction counterpart;
- exact pairwise history multiplicity, and exhaustive coverage of direct terminal states;
- the evolved `Tarountula -> Spidops` object carrying Grass Energy and Muscle Band, with all four constituent physical cards routed to discard together if that object is selected;
- conservation of each card class across every tested staged sequence;
- a capacity-restoration countercheck: `5 -> 4 -> 5` leaves only four Benched Pokémon, so a capacity increase does not recover discarded objects;
- rejection of a claimed ascending second contraction in the monotone-census API.

The CI test was completed on GitHub Actions run **38132208735** with conclusion **success**.

## Relationship to prior research

- [bench_contraction_choice_space](../bench_contraction_choice_space/) proves the survivor-set path-count identity and shows strategy can select a different intermediate set when later information or payoffs matter.
- [bench_contraction_batch_conservation](../bench_contraction_batch_conservation/) verifies a single chosen physical contraction, including full evolution stacks and attached cards.
- This result tests their *composition*, giving an exact final **ledger-and-board** equality property over every monotone two-stage path on the existing materialized fixture.

## Limits and future work

The theorem must not be used to erase meaningful intermediate decision nodes. A Supporter, Ability, drawn card, unknown later contraction, attachment, triggered departure effect, or external state history can give two paths with equal final Bench occupancy different payoffs or legal continuations. A complete match engine must decide whether histories are observationally equivalent before applying this quotient.

A useful next test is a nonconfluence witness using a real source-specific triggered effect during the intermediate state, followed by an evaluation of which state and event-history fields must remain in the quotient key.
