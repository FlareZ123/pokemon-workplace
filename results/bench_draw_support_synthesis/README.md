# Bench-entry support: from accessible cards to executable target outcomes

A cross-study synthesis of conditional research on **Crobat V (Dark Asset)**, **Dedenne-GX (Dedechange)**, **Quick Ball**, starting Active selection, hidden Prize cards, and finite Bench capacity in paper Expanded.

This report maps the relationship among agent15's atomic calculations. Each link below provides independent reproductions and explicit assumptions. The synthesis distinguishes physical rules, exact mathematical findings, and hypothetical utilities. It does not estimate deck win rates.

## The main finding

A conventional access metric such as “one of the draw support Pokémon can be searched or benched” is insufficient to evaluate the final result. A correct line must represent **which zone the relevant target occupies after all hand mutations** and which resources were spent to reach it.

In particular:

- Crobat's Dark Asset draws to hand size six, so earlier legitimate hand plays and paid searches change its draw width. The physical Bench entry must happen from hand.
- Dedenne's Dedechange discards the existing hand before drawing six. If Crobat drew an indispensable singleton, immediately following with Dedenne can discard it. A stopping decision matters.
- Both support Pokémon become two-Prize liabilities occupying limited Bench slots. Gross card access alone has no built-in accounting for those costs.
- Search effects differ by when they change hidden information. Quick Ball reveals Prize **composition** by inspecting the deck, but an informed decision taken after paying Quick Ball cannot recover its spent card and discard payment.
- A target wanted in the discard pile can reverse the preferred use of Dedenne. Final-hand access and discard-pile access are different objectives.

These points are rules-anchored by the bundled card catalog and Advanced Player's Rulebook. Their numerical magnitudes below come from exact, *restricted* state models.

## The research chain

| Study | Question resolved | Principal bounded finding |
| --- | --- | --- |
| [Setup-role contention](../setup_trigger_role_contention/) | Does a support Pokémon in the opening hand remain usable for its hand-to-Bench trigger? | When the only starting Basic, the physical copy becomes Active and cannot fire that trigger without recovery |
| [Setup-conditioned trigger access](../bench_trigger_access/) | Does a Pokémon search put its target in the right zone? | Quick Ball-like hand search and Nest Ball-like direct Bench placement cannot be conflated |
| [Pickup and paid search ordering](../bench_quickball_payment_order/) | Can a used support provide later Quick Ball discard fuel? | Adaptive sequencing can outperform all-search-first by creating new discardable cards |
| [Single-target draw payload](../bench_draw_payload_order/) | Can Dedechange destroy a singleton that Dark Asset just found? | At h=5, Dedenne-only conditional 7/53 target retention versus conditional staged 9/53; forced follow-up Dedenne drops to 6/53 |
| [Multicopy target draw](../bench_draw_target_multiplicity/) | What if multiple interchangeable targets are acceptable? | Four target copies: Dede 44.2722%, staged 53.6409%, with lower marginal Bench pressure than one target |
| [Paid Quick Ball/Crobat sequence](../bench_quickball_crobat_dedenne/) | What changes when Crobat must be fetched using a physical discard payment? | At h=5 with C guaranteed live, Dede 79/598 versus paid stage 5/26 target retention, but Q/F consumed |
| [Opening material incidence](../bench_quickball_crobat_incidence/) | How common is the restricted physical opening and what can be executed immediately? | Only 0.507290815% of Basic-valid openings satisfy the specified D/Q/F/O event with Crobat still searchable. At the immediate h=7 hand, its material-weighted target-access delta is 0.011028061 pp |
| [Energy and Tool bootstrap](../bench_draw_energy_tool_bootstrap/) | Can the stronger h=5 draw width be obtained through legal non-draw actions? | Basic Energy plus Tool attachment establishes an executable h=5 line; the joint E/T, K/C-live weighted access increment is only 0.002047195 pp |
| [Target destination utility](../bench_draw_zone_policy/) | What if K is worth more in discard than in hand? | With H=1, G=2, C=0, optimal staged policy yields K in hand6/53, discarded3/53; if only hand is valuable, optimal yields hand9/53, discard0 |

The earlier general access work and the later payload experiments are complementary. Setup models determine **whether an action is available**. Destination models determine **what that action ultimately accomplishes**.

## Compare probabilities only within their conditioning

Three superficially similar numeric claims refer to substantially different populations:

1. **Both supports held (h=5):** one K among 53 locations; adding conditional Crobat yields +2/53 = 3.773585 percentage points final-hand reach versus conditional Dedenne.
2. **Quick Ball paid, Crobat guaranteed live (h=5):** K among 52 possible non-Crobat positions; QB removes Crobat before draws, making the gain +18/299 = 6.020067 percentage points. This benchmark presupposes the ability to reduce hand size to five.
3. **Immediately executable first-turn baseline (h=7):** the same paid continuation draws only one Dark Asset card, conditional gain 2.173913 percentage points. Its named opening and live-Crobat event occurs in only 0.507290815% of accepted openings. Their exact composition product gives 0.011028061 percentage points of restricted whole-opening target-access contribution.

The Energy/Tool bootstrap then adds extra named-card requirements to establish h=5 **legally**, so the material event becomes rarer. Its joint probability must account for a natural draw that might complete a Tool/Energy requirement instead of revealing the target. Treating that draw and target placement as independent would be wrong.

Neither the small whole-opening contributions nor the large conditional differences are universal deck-building values. They refer to the **specific paths tested**, exclude alternative connectors, and ignore matchup-dependent prize trades.

## A precise information lesson

Two information states can end with the same Prize composition knowledge and still differ in resources spent:

- If an **earlier** deck search already proved K is Prized, a K-only policy can avoid searching for Crobat with Quick Ball.
- If Quick Ball itself first reveals that K is Prized, QB and its discard payment have already been consumed; subsequent Bench entries can still be avoided.

The single-target paid-search model records QB on 51/52 K0 continuation states and on 45/52 states when equivalent Prize composition information was available earlier. The six-of-52 savings are pure action-timing information value *before charging the earlier inspection*. The calculation grants no information about which face-down Prize position contains K.

## Strategic interpretation

This research supports separating several kinds of state-dependent card value:

**Card location and intended role.** K in hand may be valuable for hand attachment, play, or preservation. The same K in discard may be valuable for an attack-copy payload. A label like “K accessed” conceals the relevant distinction.

**Connector payment and intervention time.** QB searches a Basic only after its other-card discard. Searching Crobat changes deck composition, gives additional Prize information, and changes hand size. These effects happen in a fixed temporal order, and the same search connector could have another competing purpose.

**Bench debt.** A support Bench entry is persistent under normal rules. Two support entries need two vacancies or a separate pickup/release line. The earliest model treats Bench as a strict capacity gate, while the zone-policy model adds a hypothetical cost per two-Prize occupant.

**Stopping options.** A player should sometimes decline an otherwise legal Dedechange once a strategically protected K is in hand. If a discarded K is strategically desirable, taking the Dedechange branch may instead be appropriate. The full optimal policy depends on all protected cards, targets, Bench exposure, and the opponent.

## Reproducibility and evidence

All core results are exact rational computations. Validation includes independent physically labeled opening/Prize/draw enumeration, hand/deck/Bench/discard conservation tests, post-search K shuffle-location enumeration, and finite-state policy checks. Dedicated Windows GitHub Actions workflows confirm:

- [Single-target + K1](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38063917796)
- [Multiplicity](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38064155241)
- [Paid Quick Ball](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38064651663)
- [Whole-opening direct certificate](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38065158418)
- [Energy + Tool bootstrap](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38065490161)
- [Destination-aware policies](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38065838569)

The calculations are deterministic and reproduce without stochastic sampling. Underlying source files and assumptions are linked in the atomic reports.

## Next research priorities

Most of the uncertainty now lies in bridging the exact restricted policies to authentic competitive states:

- Put real Item/Ability-lock, Bench occupancy, hand mutation, and opponent threats into the same action engine.
- Charge the opportunity cost of expending Quick Ball, Basic Energy attachment, Tool slot, and support Pokémon that the opponent might gust or Knock Out.
- Handle multiple target functions with heterogeneous values, where some cards are protected and others intentionally discarded.
- Replace named-line incidence and target-only rewards with full board development, Prize-race progression and matchup-dependent attack requirements.
- Independently audit card-print effective text and legality whenever moving from abstract role classes to concrete decklists.

Until these extensions exist, the framework is best used as a collection of verified **counterexamples to naive consistency heuristics** and as a set of executable test cases for future simulators.
