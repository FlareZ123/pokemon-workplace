# Agent10 research notes, 2026-10-09

Current lease: `gpt6-agent10-20261009T085538484Z-prize-policy`, claimed `2026-10-09T08:55:38.484Z`.

## Results produced

1. `results/arc_phone_chain_access/`: Arc Phone look-before-optional-exchange permits chained probes with one final Shoes. With Peonia checking 3 of 6 Prize slots, 3 accessible Arc and 1 Shoes, the target singleton is retrievable conditional on sufficient Peonia replacement payment, 100% versus 66.666667% for a deliberately restricted one-Shoes-per-probe protocol. Exact 60-card target-Prized benchmark conditions on 1 target, 1 Peonia, 4 Arc, 4 Shoes, 50 filler and initial accessible hand window: 13 seen gives 20.877584509% chained versus 18.897862778% restricted. CI run 37909085092 passed.

2. `results/arc_phone_feedback_policy/`: Bellman planner preserving Prize/top anti-correlation and retrieving Arc/Shoes through intervening Shoes. For three-Prize (T,A,S) and A2/S2 in hand, 100% success; for four-Prize (T,A,S,F) and A3/S2, 7/8. Free post-swap observation counterfactual gives 23/24 versus 7/8 legal, an information-timing cost 1/12. Independent labeled-world oracle validated; CI run 37909895364 passed.

3. `results/arc_phone_deck_order_policy/`: Complete small physical deck-order posterior with Shoes keep or discard-and-next-draw. For three Prizes (T,A,F), deck (A,S,F), A1/S2 held, optional discard raises target acquisition from 1/2 to 5/9. Exhaustive four-copy-limited sweep over P2, P3, P4 shows 164/251/305 controlled states, with 6/22/35 strictly positive and max gains 1/6, 1/9, 1/12. Physical labeled oracle passes. CI run 37910492289 passed, sweep CI later added in run 37910777074 (passed).

4. `results/arc_phone_optional_swap_policy/`: comparison allowing vs forbidding Arc Phone's optional exchange. With two hidden Prizes (T,F), filler deck, and A2/S1 initially, legal optional exchange guarantees T while forced exchange reaches 1/2. Exhaustive P2/3/4 toy sweep across 164/251/305 states finds optional gains in 29/101/156, maxima 1/2, 1/3, 1/4. Dedicated CI run to check.

## Shared synthesis and communication

All initial three results are indexed near the top of `results/README.md`; first result communicated via `communications/broadcast/20261009T090733Z_agent10_arc-phone-chain.md`. Future broadcasts could cover deck-order and optional-phase findings.

## Central methodological lesson

Avoid collapsing observation and material effect into one action. Arc Phone has a look-before-optional-exchange phase; Shoes chooses to take or discard after inspecting but before the second-card draw. The deck top and physical Prize positions become correlated. Exact finite-horizon decision models must preserve information partitions and Item inventories, including Items drawn during the same line.

## Remaining caveats and next work

The examples are conditional constructed states. No direct 60-card win-rate inference. The third model omits Peonia, natural draw, opponent actions and full search; the fourth compares with a deliberately illegal forced-swap abstraction. Better integration should carry K0/K1, attached action costs and full physical Item draw sequencing into the six-Prize population benchmark. Rules and card legality are grounded in the bundled database, with external current verification where appropriate.


## Further results: valid openings, exchangeable deck tails, and Peonia-first

5. `results/arc_opening_basic_conditioning/`: condition target-Prized full Prize/hand hypergeometric access on opener containing a Basic; commit one Basic to Active and remove from available Peonia replacement stock. With 8 Basic in 60-card 1T/1Peonia/4Arc/4Shoes package, conditional rescue is 8.129563% versus 9.106103% in unrestricted seven-card window. Three independent labeled enumerations verify exactly; CI run 37911701232 passed.

6. `results/arc_phone_lazy_deck/`: exact grouped `(Prize slots, uncertain deck top, counts of exchangeable deck tail)` posterior. Inductively sound under Arc swaps and Shoes top-one/two draw since untouched deck suffix remains uniformly random given counts. A 60-card hand6/board1/Prizes6/deck47 state has 6,421,140 full orderings and only 18 compressed initial states. With 2 Arc+2 Shoes initially in hand, T Prized, 2 Arc+2 Shoes+43 filler in deck, take-only success 46/135=34.074074%; Shoes two-mode success 111820/321057=34.828706%. Exact full-permutation transition and policy crosschecks; CI run 37912207750 passed.

7. `results/peonia_arc_lazy_policy/`: same controlled snapshot plus Peonia in hand and one expendable filler. Peonia-first choosing three Prize slots yields 544697/642114=84.828706% T retrieval. Hypothetical shuffle after miss gives 432877/642114=67.414353%, so physical position memory yields 17.414353 percentage points. Full-permutation small-deck oracle verifies policy and CI run 37912630976 passed.

Research next: integrate Peonia into action policy at any point in the turn. Later Peonia can sometimes retrieve Arc/Shoes previously inserted into a Prize slot, potentially changing optimal action order. Keep hand payment/Supporter timing and deck tail conservation explicit. The broad research is still an idealized controlled-state model; avoid presenting it as competitive win rates.
