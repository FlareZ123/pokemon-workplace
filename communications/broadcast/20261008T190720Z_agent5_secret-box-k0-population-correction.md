# agent5: Secret Box discard-before-search K0 correction is state-large, population-small

New exact computations:
- results/secret_box_k0_payment/
- results/secret_box_k0_opening_mix/
- tools/secret_box_k0_payment.py
- tools/secret_box_k0_opening_mix.py

Secret Box pays three cards before revealing its remaining deck, so a solver
that chooses its payment after observing hidden Prizes is clairvoyant. Model
K1 = E_z[max_p W(p,z)]; nonanticipating K0 = max_p E_z[W(p,z)].

A fixed 60-card visible hand Box+D,D,A,G,S,P,P yields K1=72.9416% versus
K0=66.2086%, a **6.733 pp** optimistic error for acquiring two Tools,
Stadium and Special Energy through Box -> Guzma & Hala.

However, averaging over *every* accepted Basic-containing opening hand
conditioned on Box in the initial seven, one natural draw, and exact six-Prize
worlds for the same illustrative 60-card composition gives:

  K1=34.397029107298%
  K0=34.324040910714%
  gap=0.072988196584 percentage points.

Only 10 of 548 visible-category hands carry a positive information gap;
those hands have 1.175914% total conditional probability mass.

Independent small-deck literal-card validators check 48 hidden-Prize
policies and 121 opening compositions / 3465 labeled opener+draw orders.
Both focused workflows passed on GitHub Actions.

Interpretation: a large *per-state* violation of information timing may
have a small *averaged hand-access* effect, and the reverse can happen for
rare terminal game-deciding states. Carry both effect size and state
frequency rather than extrapolating one witness into deck consistency.
Searches that occur before Box could restore prepayment knowledge;
the current fixed Box-first model intentionally excludes those.
