# Value of public setup information for matchup-dependent decisions

## Question

When mulligans reveal information before the first normal turn, how much can that evidence improve an actual matchup-dependent choice?

This result converts the setup evidence models into a finite Bayesian decision problem.

Implementation: `tools/setup_information_value.py`

Reproducer: `results/setup_information_value/reproduce.py`

## Decision model

Let candidate matchups or deck constructions be `c`, prior probabilities be `P(c)`, observable setup outcomes be `o`, and available actions be `a`.

Each action has utility `U(a,c)`. Before observing setup evidence:

`V0 = max_a sum_c P(c) U(a,c)`.

After observing setup evidence:

`V1 = sum_o max_a sum_c P(c) P(o|c) U(a,c)`.

The setup value of information is `V1 - V0`.

Utilities can later be supplied by matchup-conditioned DCI, AMR, ALS success, Prize race, damage, or richer simulation. The examples use transparent synthetic utilities to isolate the contribution from information.

## Finding 1: mulligan count improves a Basic-density line choice by 20.49 points

Compare equal-prior candidates with four forced Basics versus twelve forced Basics. Suppose the action is to choose the line corresponding to the correct candidate, with utility 1 for a correct choice and 0 for an incorrect choice.

Before setup evidence, expected correctness is 50%.

Three observable count bins are sufficient for the Bayes-optimal decision in this example:

- after 0 mulligans, choose the 12-Basic candidate;
- after 1 mulligan, choose the 4-Basic candidate;
- after 2 or more mulligans, choose the 4-Basic candidate.

Expected correctness becomes **70.492684077%**, a gain of **20.492684077 percentage points**.

## Finding 2: diagnostic exposure improves a same-Basic-count choice by 6.33 points

Compare equal-prior candidates that both contain four forced Basics. One has four copies of a non-Basic diagnostic and the other has two.

Mulligan count cannot distinguish these candidates because their Basic counts are equal.

Using only whether the diagnostic was exposed at least once before setup succeeds raises expected correct selection from 50% to **56.330816307%**, a gain of **6.330816307 percentage points**.

This isolates the decision value of public card-content evidence from the value of mulligan-count evidence.

## Finding 3: posterior movement can have zero strategic value

The tool also accepts arbitrary action utilities.

In one example, preserving a matchup tech is optimal under the prior and remains optimal after both possible diagnostic-exposure observations. The posterior changes, while the value of information is exactly zero because the best action never changes.

In a second example, the utility boundary lies between the two posteriors. The optimal policy preserves the tech after a diagnostic is exposed and spends it after no diagnostic is exposed. The same public evidence then has positive decision value of **1.375393666 percentage points** under the supplied normalized utilities.

This separates evidence strength from practical usefulness.

## Strategic implication

A simulator should value public setup information through the decisions it changes. Matchup-dependent DCI, AMR, discrete tech preservation, lock planning, and ALS branches can become downstream actions in this framework.

A useful state representation therefore needs both a belief state and decision boundaries. Evidence is strategically important when it shifts the posterior far enough to change the preferred action.

## Validation and limits

The reproducer checks every reported result from exact hypergeometric and geometric setup probabilities. Each observation space is finite and sums to one for every candidate, so these values have no Monte Carlo error or truncated tail.

The action utilities are illustrative. Practical values require matchup-specific evidence from simulation or game-state analysis. Optional-starter policy censorship from `setup_transcript_bayes` is a natural next input to this decision layer.
