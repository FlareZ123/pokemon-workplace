# Minimum Prize information for a Guzma & Hala payment

## Research question

The [52-card G&H information frontier](../gnh_large_unseen_information_frontier/) values hypothetical full Prize knowledge before committing the optional two-card Guzma & Hala discard. Which *subset* of known Prize identities is enough for the same decision quality?

The paid action can retrieve a spare Technical Machine: Evolution and a spare Jet Energy in addition to Artazon. The kept action retrieves Artazon but preserves its two otherwise disposable hand cards. Both actions assume an unused eligible Jirachi Stellar Wish later inspects five shuffled cards for one Ticket-role Item. The discard cost is an **invented scalar continuation penalty**, not a calibrated gameplay value.

## Physical information model

There are 52 unseen physical cards, including Artazon, a spare TM, a spare Jet, one Ticket target, and 48 other identities. Six are uniformly Prized. For every hidden Prize configuration, the player can commit to **pay** or **keep** before G&H searches. The deck searches following payment can use actual deck knowledge; payment itself cannot.

An information signal names some of the four distinguished cards and states whether each is Prized. Policy choices may depend on this signal only. We independently enumerate the sixteen exact hypergeometric Prize patterns and optimize the conditional expected success-minus-cost payoff in each signal group.

The policy value is `sum_signal max(sum_world mass * keep, sum_world mass * (pay - cost))`. An empty signal reproduces K0; observing all four reproduces free-information K1. The signal is a mathematical counterfactual. A real Tag Call or another deck search changes physical state and incurs action costs.

## Exact result at the K0 indifference threshold

For `U=52, P=6, s=5`, the mean additional Ticket access from a paid search is `10/2499`. Set the hypothetical penalty to this value.

| Prize identities revealed before payment | Additional payoff over K0 | Regret against all-four K1 |
| --- | ---: | ---: |
| None | 0 pp | 0.078203 pp |
| Artazon | 0 pp | 0.078203 pp |
| Ticket | 0.046172 pp | 0.032031 pp |
| TM alone (or Jet alone) | 0.022624 pp | 0.055579 pp |
| TM and Jet | 0.040722 pp | 0.037481 pp |
| TM and Ticket (or Jet and Ticket) | 0.064270 pp | 0.013933 pp |
| **TM, Jet and Ticket** | **0.078203 pp** | **0 pp** |
| All four named cards | 0.078203 pp | 0 pp |

Exact K0 value is `5/51`; full-information value is `25989/262990`; their difference is `617/788970`. Among ordinary signals revealing named individual Prize statuses, **TM, Jet and Ticket are the unique minimal sufficient three-card subset**. At the stated cost the optimal post-signal policy is simple: pay only when all three are unprized. Artazon's Prize status cannot reverse the choice.

For this fixed 52/6/5 geometry, the full-information decision remains unchanged throughout the *open* penalty interval `1/396 < penalty < 5/1012`, approximately `0.002525 < penalty < 0.004941`. The lower endpoint is the maximum physical Ticket gain when exactly one of the two spares is obtainable; the upper endpoint is the minimum gain when both are obtainable. At penalty `1/405`, the Artazon Prize flag becomes decision-relevant again, confirming that the sufficiency result depends on utility.

The conditional named-status signal can be compressed to the single Boolean event “Ticket and both spares are in deck”, but a player normally learns it through a fuller search. This is a sufficient *decision statistic*, not a free legal source of information.

## Verification and limitations

[Exact grouped solver](../../tools/gnh_partial_prize_observability.py) and [single-file test](reproduce.py) compare 864 partial-observation policies against a separate physical-label oracle that explicitly enumerates Prize combinations and every small-game Stellar Wish subset. Tests also verify monotonic value of refining signals, K0/K1 regression equivalence, minimum sufficient named signals, and a counterexample at another discard penalty.

This result is limited to the fixed conditional hand and card composition. It omits acquiring or paying Tag Call, prior searches, actual Aichi opening distributions, matchup-valued discarded cards, Bench restrictions, lock effects and match-winning objectives. No deck-strength claim follows from these exact option values.

**Next research:** build a feasible observation-state partition for actual Aichi opening hands and compare pre-K1 and post-Tag-Call payment policies, accounting for Tag Call's material searches and opportunity cost.
