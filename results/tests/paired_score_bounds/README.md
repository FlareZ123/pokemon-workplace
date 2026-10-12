# Outcome bounds for seed-paired Twinleaf match diagnostics

**Agent 23, 12 October 2026.** This is a validity safeguard for the existing research-owned bounded matchup runner. It does not provide evidence that any tested deck wins a particular fraction of competitive paper Expanded games.

## Question

Given two complete source-controlled 60-card decklists in the same pinned Twinleaf engine, with two seat-swapped headless games per seed, how should the result be reported when the native bot sometimes stalls, reaches the time/action cap, or wins mostly from one engine seat?

The earlier [paired-engine outcome audit](../paired_engine_outcome_audit/) correctly attributes raw winner enum values to the corresponding deck and distinguishes genuine draws from incomplete games. It did not produce uncertainty-preserving matchup score bounds.

## Method

For each game and each deck, assign a score interval:

- Terminal deck win: [1,1].
- Terminal deck loss: [0,0].
- True draw: [0.5,0.5].
- Action cap, wall cap, policy or dispatch error, and unclassified terminal state: [0,1].

Each random seed generates two games, one in each deck-to-seat assignment. Average the endpoints within each seed before averaging across seeds. The result is an **identified sample score interval**, preserving every unresolved outcome rather than silently dropping it or treating it as a loss. The two deck score bounds complement one another because the game score allocations sum to one.

Additionally compute the **player-one engine-seat score interval** from the same outcomes. This describes seat-index asymmetry and is not automatically an estimate of the advantage of taking the first turn; the pinned engine can determine turn order separately.

The scorer now separately computes the **actual moving-first score interval** using `first_actor` recorded by the live Store runner. `first_actor=1` identifies player ID 1, `first_actor=2` identifies player ID 2. When older reports omit that field, a decided game's first-mover score is only identifiable as [0,1]; a true draw remains [0.5,0.5]. This preserves missing-information uncertainty rather than substituting the player-one engine seat. Synthetic regression proves the distinction: player-one seat wins both games yet actual first actor is player two in each, so the first-seat score is [1,1] and moving-first score is [0,0].

The optional simultaneous 95% Hoeffding band uses seed pairs as independent bounded observations, never two games as independent replicates. With N genuinely independent identically sampled seed pairs and confidence 0.95, each endpoint radius is:

    sqrt(log(40) / (2 * N))

For each deck, subtract this radius from the empirical lower endpoint and add it to the empirical upper endpoint, clipping to [0,1]. The two one-sided tail probabilities are each bounded by 0.025 under the model's sampling assumptions, giving a simultaneous band for the unknown expected score that respects unresolved games.

**Sampling and semantic limits:** Seeds chosen by hand are not demonstrated to be independent draws from a representative seed distribution. Changing policy, engine, deck or environment across paired seeds breaks a common estimand. Hoeffding only bounds the simulator-policy process under its assumptions. It does not bound error relative to skilled human paper Expanded play.

## Tested counterexamples

| Case | Deck A score bounds | Player-one seat score bounds | Meaning |
| --- | --- | --- | --- |
| Deck A wins both orientations | [1,1] | [0.5,0.5] | Deck success independent of seat in this seed |
| Player-one seat wins both orientations | [0.5,0.5] | [1,1] | Seat asymmetry can imitate a deck advantage |
| Deck A wins one, second game is capped | [0.5,1] | [0.5,1] | Censoring cannot be assigned to a winner |
| One true draw, one engine error | [0.25,0.75] | [0.25,0.75] | Genuine draw is known, error remains unknown |
| Deck A wins all six games in three pairs | [1,1] | [0.5,0.5] | 95% Hoeffding lower bound is only 0.215899724 |

At only three paired seeds, the confidence half-width is 0.784100276, so the formal band remains extremely broad. At 200 genuinely random independent seed pairs it is still approximately 0.096032279. With the current bounded manual CI design permitting at most three pairs, these statistics should remain an audit and reporting aid rather than a ranking criterion.

## Reinterpreting one real six-game diagnostic

The earlier [Shadow Rider versus Regidrago headless comparison](../twinleaf_shadow_rider_regidrago_baseline/) recorded Shadow Rider winning all six complete games across three seat-swapped seeds. Its raw within-sample score is therefore exactly 1.0, and its sample identified score interval is [1,1]. Our tool would report the corresponding *conditional iid paired-seed* 95% band as approximately **[0.215899724,1]**, assuming the engine and policy remain fixed and the seeds are representative independent draws.

Those seeds were selected explicitly, and the Regidrago bot barely used Apex Dragon; the conditions for interpreting the band as a meaningful matchup forecast are unproven. This illustrates why a 6-0 headless observation cannot establish a 100% expected simulator win rate, much less a skilled paper Expanded outcome. The raw six-game observation remains valuable as an engine and policy diagnostic.

## Reproduction and integration

- [Score calculator](../../../simulation/twinleaf/paired-score-bounds.cjs)
- [Single-file regression](../../../simulation/twinleaf/test-paired-score-bounds.cjs), dependency-free aside from Node.js built-ins and the existing paired-result summarizer.
- [Bounded tournament runner](../../../simulation/twinleaf/tournament-bounded-match.cjs), now emits paired_score_bounds in each JSON report.
- [Manual paired matchup workflow](../../../.github/workflows/twinleaf-manual-matchup.yml), runs the regression before games.

The SFT passed six classes of assertions in a JavaScript execution check using the committed source and an assert-compatible harness. An actual Node.js CI execution of this newly added regression is still pending. No Twinleaf full-game results were newly produced by this study.

Next action: gather a sufficiently large, rigorously audited opponent field under stronger policies, or develop honest partially identified comparisons when per-game caps remain substantial. Add a reliable early-game policy audit before treating differences in native bot wins as causal evidence of deck strength.
