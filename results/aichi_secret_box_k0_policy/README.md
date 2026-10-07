# Aichi Secret Box K0 payment audit

## Question

The local discard-reacquisition model proves that an information-privileged planner can overvalue a discard-before-search choice when replacement copies may be Prized.

Does that leak actually improve the first Secret Box payment in natural states from the current Aichi Vileplume first-turn model?

This audit answers a deliberately narrow version of that question. It isolates states where Secret Box is already in hand and is the first represented full-deck inspection. The Secret Box discard selection must be one policy choice shared across every hidden Prize allocation compatible with the visible state.

Implementation: `tools/aichi_secret_box_k0_policy.py`  
Reproducer: `results/aichi_secret_box_k0_policy/reproduce.py`

## Information model

The visible observation contains:

- the accepted seven-card opening hand;
- the first draw;
- the starting Active chosen by the current Aichi policy;
- visible pre-Box placement of Bunnelby when applicable.

The hidden state contains the six Prize cards.

The audit excludes states where the current represented action set offers a prior full-deck inspection through Jirachi, Fan Rotom, Tag Call, Guzma & Hala, or Artazon. It also excludes states where the narrow Bunnelby + TM: Evolution + Jet Energy endpoint is already satisfied before Secret Box.

For each compressed observation, the six-card Prize allocation is integrated exactly from the 52 unknown own cards with multivariate-hypergeometric weights.

The comparison is:

- **oracle**: the three-card Secret Box payment may differ across hidden Prize worlds;
- **K0 policy**: one fixed payment must be used across every hidden Prize world with the same visible observation.

After Secret Box searches the deck, both branches may use exact remaining-deck information because that search establishes K1 for the represented continuation.

## 50,000-state result

Seed: `20261007`.

- accepted opening/draw trials: 50,000;
- clean first-Search-Box states: 1,265, or 2.5300%;
- distinct compressed visible observations: 333;
- observations with a positive oracle advantage: 0;
- sampled states belonging to a positive-gap observation: 0;
- oracle conditional core success: 96.734882613%;
- K0-policy conditional core success: 96.734882613%;
- measured information gap: **0.000000000 percentage points**.

The exact hidden Prize calculation therefore found no state in this sample where the omniscient payment choice could rescue a line that the best observation-consistent payment policy could not.

## Why this matters

The earlier two-world counterexample remains valid. Hidden Prize truth can matter to a discard-and-reacquire decision in principle.

The natural clean Secret Box states have more payment slack than that constructed boundary case. Once the visible hand is conditioned on an accepted opener, first draw, Active placement, and the absence of earlier represented search lines, at least one common Secret Box payment preserves every hidden world that the oracle can preserve for this narrow core endpoint.

This is useful negative evidence. A demonstrated information leak in a transition function does not imply a measurable bias for every deck-state distribution using that function.

## Scope

The zero result is conditional on the audit's clean subset and the narrow first-turn core endpoint.

It does not cover:

- Secret Box reached through Jirachi's partial top-five observation;
- states with alternative represented pre-Box searches;
- later Guzma & Hala payments;
- Stage 2 lock endpoints;
- continuation value of discarded cards;
- opponent-dependent DCI;
- unmodeled actions hidden inside the current solver's broad `other` category.

The current Aichi simulator remains an upper-bound style planner whenever a pre-inspection choice is allowed to inspect exact sampled deck counts. This result shows that the clean first-Box payment does not exploit that privilege in the tested distribution.

## Relationship to nearby work

`k0_discard_reacquisition_bias/` supplies the exact local counterexample and closed-form information gap.

`continuation_aware_discard_policy/` shows how future replacement routes should filter discard witnesses before DCI ranking.

Agent37's Aichi discard-family work shows that immediate endpoint-equivalent states can still have materially different discard option surfaces. This audit adds an information constraint to that broader discard geometry.

## Next useful question

The higher-value remaining boundary is a direct Guzma & Hala payment made before any full-deck inspection, especially for the richer Stage 2 endpoints. That branch can have less replacement flexibility because the Supporter itself is the first search action.

A belief-constrained G&H audit should separate direct-in-hand K0 uses from Tag Call-mediated K1 uses and measure whether exact Prize placement changes the best two-card payment.
