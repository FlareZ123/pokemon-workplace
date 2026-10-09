# Unknown search policies can erase a printing's Prize signal and create delayed information

## Question

The [print-reveal study](../revealed_print_information/) assumes an opponent knows the searching player's exact policy for choosing between two distinct legal Pikachu prints after privately inspecting their deck. What happens if the opponent is uncertain about that policy?

An exact symmetric counterexample shows that **the chosen print alone becomes completely uninformative about a strategically important Prized singleton**. Yet it creates a correlation between the unknown Prize configuration and the unknown target-choice policy. Discovering the policy later unlocks the earlier print observation's information, with an exact decision-value gain.

## Physical toy model

The six-card hidden pool has one A, old `xy1-42` Pikachu, new `swsh7-49` Pikachu, and three fillers, with two uniformly dealt Prize cards. The player chooses a target after full deck inspection and publicly reveals the actual Pikachu printing. The two K1-dependent policies are:

- **Forward:** if A is Prized and old Pikachu is available, select old. Otherwise prefer new, falling back to old.
- **Reverse:** if A is Prized and new Pikachu is available, select new. Otherwise prefer old, falling back to new.

Both are synthetic behavioral hypotheses. They are intentionally equally plausible a priori, each with probability 1/2. Both execute a search in 14 of 15 unordered Prize configurations; the sole no-search case has both Pikachu prints Prized.

The state space contains **168 equiprobable completed branches**, consisting of each policy's 28 successful ordered Prize placements and three possible shuffled top cards.

## Exact information result

Conditional on observing a successful Pikachu search:

| Observation | P(A is Prized) | P(shuffled top is A) |
| --- | ---: | ---: |
| Pikachu name | **5/14** | **3/14** |
| Old print, policy still unknown | **5/14** | **3/14** |
| New print, policy still unknown | **5/14** | **3/14** |

Each print is selected with probability 1/2, and each policy remains 1/2 likely after either print. **Print alone conveys zero bits about A's Prize status** under this exact symmetric policy mixture.

But the joint posterior retains a relationship:

| Public print, later known policy | P(A is Prized) |
| --- | ---: |
| Old, forward | 4/7 |
| Old, reverse | 1/7 |
| New, forward | 1/7 |
| New, reverse | 4/7 |

The marginal policy and Prize probabilities remain unchanged after observing just the print. Their **joint distribution** has changed.

Learning the policy after seeing the print reveals approximately **0.151835501362 bits** about whether A is Prized. This is the original print information from the policy-known study, now deferred until the policy is identified.

## Exact decision consequence

Use the same synthetic two-response problem from [revealed_print_decision_value](../revealed_print_decision_value/): predict A Prized or unprized, earn one unit for a correct choice and zero for an incorrect one.

With equal 1/2 prior over the forward and reverse policies:

- Knowing only the name yields optimal accuracy **9/14**.
- Knowing only the print yields **9/14**.
- Knowing only the policy yields **9/14**.
- Knowing *both* policy and print yields **5/7**.

Thus the joint observation is worth **1/14** additional accuracy even though neither component independently changes the optimal decision. The information channels are complementary under this exact belief.

This is a general warning against preserving separate marginals of "opponent archetype/policy" and "hidden Prize composition" while discarding their correlation: after a behavioral reveal, their joint dependence can matter to a later decision.

## Implementation, independent checks and scope

- `tools/latent_search_policy_belief.py`: fully exact `Fraction`-weighted joint posterior over policy ID, ordered Prize cards, selected print and shuffled top.
- `results/latent_search_policy_information/reproduce.py`: enumerates all 168 successful branches; independently counts the 15 unordered Prize configurations under each policy, checks conditional information, tests malformed priors and impossible search targets, and brute-forces deterministic responses on four observation channels.
- `.github/workflows/validate-latent-search-policy-information.yml`: reproducible CI.

All assertions are conditional on the synthetic behavior models and their equal priors. This is neither an empirical estimate of how human players choose prints nor an actual match win-rate prediction. Opponent policy is a latent hypothesis that may be learned from other turns, archetype identification, or known deck construction.

A future line is to replace the two equally weighted hypotheses with empirically calibrated or rationally derived choice-policy priors, and to integrate policy/posterior updates with a physical materialized Quick Ball instance so the latent hypothesis remains tied to a real revealed-card event.
