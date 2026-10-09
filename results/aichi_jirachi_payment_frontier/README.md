# Aichi G&H payments and late Stellar Wish Item access

## Question and method

Can Guzma & Hala's optional two-card discard payment change the probability of accessing a Redeemable Ticket or Town Map through a saved Jirachi Stellar Wish? This combines the existing legal G&H payment enumerator with the prior deferred-Stellar Wish policy in the 60-card published-Aichi counterfactual.

Files:
- Model: tools/aichi_jirachi_payment_frontier.py
- Exact fixtures: results/aichi_jirachi_payment_frontier/reproduce.py
- Fixed sample: results/aichi_jirachi_payment_frontier/run.py
- Workflow: .github/workflows/validate-agent4-aichi-jirachi-payment.yml
- Passing run: https://github.com/FlareZ123/pokemon-workplace/actions/runs/37975496982

The first and second Ticket-reset **access windows** are evaluated after the modeled G&H setup endpoint. Every possible two-card discard payment is enumerated, and an endpoint-preserving payment is selected separately for each tech package. This is a hindsight-feasibility upper bound before K1 information.

## Exact mechanism: replacement Tool search thins a deck

G&H shuffles the deck after searching. For a remaining deck of N cards with K Ticket/Map targets, a saved Stellar Wish sees one or more targets in its top five with probability

\[
p(N,K) = 1-\frac{\binom{N-K}{\min(5,N)}}{\binom{N}{\min(5,N)}}.
\]

Paying with a *held* Tool and re-searching another copy from the deck can preserve the required Tool/Energy while removing one additional non-Ticket from the deck. The increased target density can make payment-aware late-Wish access slightly greater than the nominal no-payment calculation.

Exact tested witness: held TM: Evolution, Faba, Gladion and Pidgey; remaining deck includes a second TM, Jet Energy, Artazon, one Ticket and five other cards. Pay Faba + Gladion, search Jet and Artazon, and retain seven remaining deck cards: Ticket is accessible with probability **5/7**. Alternatively pay Faba + the held TM, retrieve a replacement TM plus Jet and Artazon, and retain six deck cards: Ticket is accessible with probability **5/6**. Both post-search hands contain TM and Jet. The fixture proves this legal action-state phenomenon. It does not justify discarding a held TM at K0 when the other copy may be Prized.

## Fixed-seed 80,000-start study

Seed 20261009; **68,960** accepted ordinary-Basic openings, **48,665** offered core G&H routes, **6,017** eligible late Jirachi uses after the deferred-connector policy. Endpoint-ready optimistic and payment-feasible counts coincided: dual Stage 2 **28,962**; Item lock **25,077**; Item lock plus Pidgeot **16,361**.

All table probabilities are on the accepted-opening denominator. Paired CI half-widths reflect uncertainty from Monte Carlo starting-order sampling, conditional on this model.

| Endpoint and package | Reset window | Nominal late Wish | Payment-aware late Wish | Paired difference |
| --- | --- | ---: | ---: | ---: |
| Dual Stage 2, one Ticket | First | 5.743505% | 5.748785% | +0.005280 pp |
| Dual Stage 2, two Tickets + one Map | First | 10.710198% | 10.718730% | **+0.008532 ± 0.000504 pp** |
| Dual Stage 2, two Tickets + one Map | Second | 0.070430% | 0.070578% | +0.000148 ± 0.000048 pp |
| Item lock, three Tickets + one Map | Second | 0.112425% | 0.111121% | -0.001303 ± 0.002843 pp |
| Item lock + Pidgeot, one Ticket | First | 2.868293% | 2.870422% | +0.002129 ± 0.000195 pp |

The largest shown first-window uplift is under one hundredth of a percentage point. Payment can also harm second-reset availability, although the shown negative estimate has a CI spanning zero.

## Interpretation and limitations

This measures **Item access**, not Prize reset success or win probability. Most accepted starts do not meet the endpoint prerequisites. The best discard payment can differ by goal and can make choices based on hidden Prize information that an actual K0 player lacks. G&H reveals the deck during search **after** its optional discard payment. Consequently, re-searching a discarded held Tool can be dangerously optimistic without prior K1 information.

The model assumes a uniform shuffled deck after G&H, a maximum of one Item acquisition via unused Stellar Wish, a specific natural-or-deferred early Jirachi policy, and no later opponent interaction or Item lock. It excludes longer-term DCI, displaced tech-slot value, Bench contention after setup, and subsequent turns.

The regression exhaustively validates the hypergeometric top-five formula on labeled decks of size 1 through 10, validates both reset gates, and checks a physical named Tool-replacement witness. CI output and all package comparisons are available in the linked CI logs.


## Payment-time Prize information partition

The subsequent provenance audit distinguishes **represented** routes that
actually consumed Tag Call to obtain G&H, thereby searching the deck before
the optional G&H payment, from routes with G&H naturally held or obtained
by an early Jirachi top-five observation. The latter routes do not establish
complete deck/Prize knowledge until G&H searches, after its payment.

Within the same 80,000-start sample, **18,498** of the **48,665**
core-ready states had a prior Tag Call full-deck search. Of **6,017**
late-Stellar-eligible states, **2,358** had a prior full-deck search.

The dual Stage-2, two-Ticket/one-Map package's **+0.008532 pp**
first-reset difference decomposes on the accepted-opening denominator into:

- **+0.003411473 pp** from prior-K1 states (474 positive states);
- **+0.005120407 pp** from pre-K1 states (751 positive states).

For its second-reset gate, the split is **+0.000060038 pp prior-K1**
and **+0.000088141 pp pre-K1**.

This partition does **not** turn the hindsight oracle into an observation-valid
strategy. The pre-K1 improvement may disappear or reverse when the
payment must be chosen without knowing whether a backup Tool is Prized.
The exact reversal in
[the K0/K1 Tool-thinning theorem](../gnh_tool_thinning_information/)
shows how this can happen. Optional extra prepayment Tag Call use when
G&H is already held is outside the represented preparer.

Regression and 80,000-start provenance audit both passed
[CI run 37976302686](https://github.com/FlareZ123/pokemon-workplace/actions/runs/37976302686).
