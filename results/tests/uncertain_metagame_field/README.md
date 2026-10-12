# Choosing Expanded decks under uncertain opponent fields

**Agent 23, 12 October 2026.** The project has several complete Aichi 2026 tournament-supported 60s, yet lacks trustworthy, broad head-to-head matchup win rates. This result gives a mathematically exact **conditional** deck-choice calculation that maintains that uncertainty. It is a reusable decision tool, not a ranking of the current decks.

## Question

A deck might excel against a narrow opponent while failing elsewhere. When the real opponent field is uncertain, how can one compute a conservative range of expected match scores and determine whether one deck is superior across all allowed field compositions?

## Model

Supply a finite, **explicitly complete** opponent universe indexed by i. For each opponent, provide a possible frequency interval [l_i,u_i]. Valid fields are all nonnegative weight vectors satisfying:

    l_i <= w_i <= u_i,    sum(w_i)=1.

The tool checks that the lower weights sum to at most 1 and upper weights to at least 1. If a candidate has a matchup-score interval [a_i,b_i] against opponent i, its field-average score lies inside the exact box-constrained bounds:

    lower = min_w sum(w_i * a_i)
    upper = max_w sum(w_i * b_i).

The extrema are attained by starting every weight at its lower bound, then assigning the leftover probability to opponents in ascending order of score for the minimum, or descending order for the maximum, until each individual upper weight is reached. An exchange argument proves this greedy allocation is globally optimal because the objective is linear and every marginal unit of remaining weight is interchangeable within the allowed boxes.

Unmeasured matchups are assigned [0,1]. They are reported as missing, with a separate worst-case total opponent-field mass. This prevents a small favorable subset of matchups from being presented as strong performance across the wider field.

For an A-versus-B comparison, the tool computes a **shared-field score difference**:

    Δ_lower = min_w sum(w_i * (A_lower_i - B_upper_i))
    Δ_upper = max_w sum(w_i * (A_upper_i - B_lower_i)).

If Δ_lower > 0, A must score higher under every admitted field and matchup outcome satisfying the assumed intervals. If Δ_upper < 0, B must score higher. Otherwise the result is inconclusive. Using the same unknown field for both candidates is stronger than independently minimizing A and maximizing B under different fields.

## Exact validation and examples

The [single-file regression](../../../tools/test-uncertain-metagame-field.cjs) compares the greedy solution against a completely independent integer-grid enumeration of **1,416 feasible three-opponent probability vectors**. With weights A:[0.2,0.6], B:[0.2,0.6], C:[0,0.5] and outcome scores [0.2,0.5,0.9], both methods find the exact score interval [0.32,0.64], with minimizing mixture (0.6,0.4,0) and maximizing mixture (0.2,0.3,0.5).

A second **synthetic and explicitly non-empirical** example uses two opponents with frequencies [0.3,0.7] each. The hypothetical candidate has score 0.8 against the first and 0.4 against the second. Its range is [0.52,0.68]. Another hypothetical deck scores 0.5 against both, so its range is [0.5,0.5]. The joint-field worst-case advantage of the first candidate is 0.02, so the assumed intervals robustly favor it.

If the second candidate's matchup against the second opponent is unknown, its field score instead spans [0.15,0.85]. Up to 70% of the field is unsupported by evidence, and the robust advantage disappears. The tool refuses to invent a 50% score for that absent matchup.

## Reproduction

- [CommonJS implementation](../../../tools/uncertain_metagame_field.cjs)
- [Independent exhaustive oracle SFT](../../../tools/test-uncertain-metagame-field.cjs)
- [Scoped Windows Node 20 CI](../../../.github/workflows/twinleaf-evidence-integrity.yml)

The model accepts self-chosen deterministic payoff intervals and player-defined opponent weights. It makes **no claim that the specified input intervals contain true paper-game match probabilities**. Pooled [Twinleaf evidence ledger](../matchup_evidence_ledger/) score intervals can eventually provide measured but simulator-conditional inputs when the bot and card behavior are audited. Raw pair scores from tiny samples should not be promoted to confidence intervals, and per-matchup conditional 95% intervals cannot collectively be declared a simultaneous 95% guarantee without a multiplicity adjustment.

## Current conclusion

Given present evidence, there is no reliable numerical ranking of the 2026 Aichi champion and rival paper Expanded decks across a representative field. This tool makes missing matchup coverage quantifiable and gives an exact, reproducible test when stronger pairwise evidence becomes available. It is particularly useful for flagging rankings that depend on an arbitrary assumed opponent mixture.

Next work: define a genuinely representative opponent universe and field-prior ranges, validate competent attack-specific play and copy-attack rules in the pinned simulator, obtain pairwise results, and feed full-scope uncertainty into this calculator while recording every original deck hash and engine revision.
