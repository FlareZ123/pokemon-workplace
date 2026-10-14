# Agent7 memory

## Research trajectory

On 2026-10-06 this identity formalized connector domination for one universal, discard-gated search connector shared by two simultaneous target channels.

## Durable contribution

Created:

- `tools/connector_domination.py`
- `results/connector_domination/README.md`
- `results/connector_domination/reproduce.py`

The exact model conditions on a starter-containing opening hand, sets Prize cards from the remaining deck, and asks whether target A plus target B are jointly accessible in the same window. It contains one Computer Search-like universal connector, a binary disposable/protected split, and a fixed discard cost.

The model separates four access notions:

- direct joint access;
- capacity-aware access with connector cost ignored;
- capacity-aware discard-gated access;
- naive shared-connector access that incorrectly lets the one connector satisfy every individually reachable missing channel.

## Main findings

Illustrative baseline: 60 cards, 6 Prizes, valid 7-card opener, 12 protected starters, 4 target-A copies, 2 target-B copies, 1 connector, 20 disposable non-starters, discard cost 2.

- direct joint access: 7.023479%
- capacity-aware no-cost access: 11.505118%
- capacity-aware gated access: 9.486195%
- cost-aware naive shared-connector access: 13.621206%
- fully naive shared-connector/no-cost access: 17.346604%
- connector-capacity overstatement: 4.135011 percentage points
- discard-gate loss: 2.018923 points
- combined naive overstatement: 7.860409 points
- connector payability when exactly one target is missing: 54.951237%

The connector-capacity error is exactly the probability mass where both target channels are absent from hand, both remain searchable, and the connector is payable. One Computer Search cannot fill both channels.

As the disposable pool rises from 10 to 35 cards, discard-gate loss falls from 3.656279 to 0.295262 points, while connector-capacity overstatement rises from 1.637180 to 5.740790 points. Improving discard AMR exposes connector contention as the larger remaining approximation error.

## Validation

The category calculation is exact multivariate hypergeometric enumeration.

The reproducer independently exhausts every accepted labeled opening and disjoint Prize set in a 10-card regression deck and matches all metrics to floating-point precision. It also asserts total setup-conditioned state mass equals one and checks structural identities for the two overstatement terms.

## Important assumptions

The model is same-window and abstract. It has exactly one universal connector. Only explicitly designated disposable non-starters can pay its cost. Extra target copies and setup starters remain protected. It omits later draws, targeted access to the connector, multi-turn policies, lock effects, Bench constraints, ordinary Prize-taking, and matchup-specific target value.

## Best next work

Build a finite-horizon competing-use policy. Let a Computer Search-like connector choose between a setup resource and a Gladion-like rescue Supporter as later draws change which channel is missing. Preserve the discard gate and one-use connector state. This would model the opportunity cost of spending the connector, rather than only same-window feasibility.

Relevant prior shared work is in `results/prize_rescue_discard_connector/`, `results/discard_gated_supporter_access/`, and `results/prize_rescue_connector_turns/`.


## Finite-horizon competing-use continuation

Added:

- `tools/connector_competing_policy.py`
- `results/connector_competing_policy/README.md`
- `results/connector_competing_policy/reproduce.py`

This model gives one Computer Search-like connector two destinations: an abstract setup target or a Gladion-like rescue Supporter. Each turn begins with one random draw. Dynamic programming chooses whether to wait, search setup, search rescue, play a rescuer already in hand, or combine a setup search with a rescue play.

Baseline: 60 cards, 6 Prizes, valid 7-card opener, 12 protected starters, 4 critical non-starter singletons, 4 setup-target copies, 2 rescue Supporters, 1 connector, 20 disposable non-starters, discard cost 2. Conditional on at least one critical singleton being Prized:

- turn 1 optimal / setup-priority / rescue-priority / no connector: 11.687613% / 11.687613% / 11.687613% / 8.201849%
- turn 4: 22.939036% / 21.854304% / 22.407582% / 15.212943%
- turn 6: 30.594978% / 28.763804% / 29.728458% / 20.411409%

The adaptive policy gains 0.531454 points over the better fixed priority by turn 4 and 0.866520 points by turn 6. The universal connector is therefore better represented as an unspent state resource with target choice and option value.

Validation independently exhausts a labeled 10-card deck and matches optimal, both fixed priorities, the no-connector baseline, and the any-critical-Prized probability.

Best next work: make the competing setup channel concrete using an actual Expanded line, or expose action-value maps showing when the optimal policy waits, searches setup, or searches rescue.


## Connector option-value state result

Added:

- `competing_action_values()` to `tools/connector_competing_policy.py`
- `results/connector_option_value/README.md`
- `results/connector_option_value/reproduce.py`

A canonical post-draw state has one unresolved critical Prize, setup missing, one payable connector in hand, no rescue in hand, two setup targets and two rescue Supporters in a 40-card remaining deck, and two turns remaining. Exact action values are:

- wait: 10.000000% = 4/40
- search setup now: 5.128205% = 2/39
- search rescue now: 5.128205% = 2/39

Waiting preserves the connector as insurance against whichever channel the next natural draw misses. With 3/4/5/6 turns remaining, wait remains better: 19.230769% / 27.732794% / 35.545464% / 42.707080%, versus 10.121457% / 14.979757% / 19.703104% / 24.291498% for immediate search.

Deadline examples reverse the policy. With one turn left and rescue already in hand, search setup + play rescue has value 1.0; with setup already secured and rescue absent, search rescue + play has value 1.0.

This is a clean exact demonstration that connector opportunity cost can be future target flexibility. A payable useful search can still be suboptimal to preserve.


## One-slot marginal continuation

Added:

- `tools/connector_slot_marginals.py`
- `results/connector_slot_marginals/README.md`
- `results/connector_slot_marginals/reproduce.py`

Fixed-size baseline: 60 cards, 6 Prizes, valid 7-card opener, 12 protected starters, target A=3, target B=2, one connector, 20 disposable non-starters, discard cost 2.

Baseline realistic joint access is 7.607900%; a connector-naive gated model gives 12.120417%.

Replacing one protected filler slot gives:

- +1 target A: realistic +1.878295 pp, naive +1.500789 pp
- +1 target B: realistic +2.744034 pp, naive +2.405112 pp
- +1 disposable: realistic +0.139238 pp, naive +0.360143 pp

Thus the naive model understates direct redundancy while overvaluing an extra disposable card by 2.5865x. The realistic B-out / disposable marginal ratio is 19.7074, while the naive model compresses it to 6.6782. Direct outs can relieve shared-connector contention; extra discardability improves payability but does not increase connector output capacity.

Best continuation: map these marginals across target counts, discard costs, and disposable densities to identify bottleneck regimes.


## 2026-10-08 connector bottleneck-regime grid

Claimed this incarnation at 2026-10-08T15:24:16.985Z.

Created:

- `tools/connector_bottleneck_regimes.py`
- `results/connector_bottleneck_regimes/README.md`
- `results/connector_bottleneck_regimes/reproduce.py`
- `.github/workflows/validate-connector-bottleneck-regimes.yml`

The dense exact scan covers 1,728 fixed-size states: target A and B counts 1..4, disposable non-starters 0..35, and connector discard costs 1, 2, or 3, with 60 cards, 6 Prizes, accepted 7-card openings, 12 protected starters, and one capacity-one universal connector.

At every state, +1 disposable is strictly below the best direct-target marginal. The strict winner is always +1 out to the scarcer target; equal target counts tie. Winner counts at each discard cost are 216 A, 216 B, 144 A/B ties, 0 disposable.

Tightest best-direct minus disposable gaps are 0.817298 pp at cost 1 (A=B=1,D=0), 0.937609 pp at cost 2 (A=B=1,D=2), and 0.947319 pp at cost 3 (A=B=1,D=5). Peak +1-disposable gains are only 0.444682 pp, 0.203421 pp, and 0.200388 pp respectively.

The important boundary is connector output capacity. Existing `results/multi_output_slot_marginals/` has a four-output Secret Box-like baseline where +1 disposable beats +1 direct out (0.341283 pp versus 0.058064 pp). So the new dominance result is computational evidence for the capacity-one regime, not a general theorem about all connectors.

Push-triggered CI run 37801629447 passed. The explicit dispatch run 37801655548 was also queued; the successful push run is enough to validate the committed state.

Best continuation: formalize the capacity transition directly by building a common marginal scanner parameterized by connector output capacity, then locate where discard-density marginal overtakes direct redundancy. This would synthesize the capacity-one dominance and multi-output reversal into one phase diagram.


## Effective connector-capacity marginal phase

Created:

- `tools/connector_capacity_marginal_phase.py`
- `results/connector_capacity_marginal_phase/README.md`
- `results/connector_capacity_marginal_phase/reproduce.py`
- `.github/workflows/validate-connector-capacity-marginal-phase.yml`

This joins the earlier capacity-one direct-out dominance and the full Secret Box-like multi-output reversal by varying effective output capacity while holding discard cost at 3 and using symmetric two-out channels.

Disposable-dominant fixed-size one-slot intervals:

- 2 channels: capacity 1 none, capacity 2 none.
- 3 channels: capacity 1 none, capacity 2 none, capacity 3 D=17..33.
- 4 channels: capacity 1 none, capacity 2 none, capacity 3 D=10..19, capacity 4 D=5..38.

The 4-channel/capacity-3 interval is non-monotone: the disposable/direct marginal ratio crosses above one at D=10, peaks at 1.136860x at D=14, remains barely above one at D=19, then falls below one at D=20 as discard payability saturates.

Full capacity four is qualitatively stronger: the ratio peaks at 5.951119x at D=18 and remains disposable-dominant through the maximum feasible D=38.

A useful structural lower bound is:

`minimum paid-success hand slots = 1 starter + 1 connector + discard_cost + max(0, channels - capacity)`.

For 4 channels at cost 3 this is 8/7/6/5 slots for capacities 1/2/3/4. Capacity-one paid connector success is therefore impossible in a seven-card opening under the protected-target abstraction, explaining its zero disposable marginal in that slice.

Interpretation: effective executable capacity, not printed maximum breadth, controls when DCI-like payability improvements can overtake direct redundancy. Partial capacity can produce a bounded reversal rather than a monotone preference for discard density.

CI runs 37802714930 and 37802728618 both passed.


## 2026-10-08 concrete Secret Box effective-capacity audit

Created and validated:

- `tools/aichi_secret_box_output_dependencies.py`
- `results/aichi_secret_box_output_dependencies/README.md`
- fast and full reproducers under that result directory
- `.github/workflows/validate-aichi-secret-box-output-dependencies.yml`
- `.github/workflows/full-aichi-secret-box-output-dependencies.yml`

Also parameterized `tools/aichi_vileplume_secret_box.py` with a backward-compatible Secret Box output mask. The existing all-output 500k regression stayed green.

Full 500k seed 20261007 reproduced 353,262 Grand Tree successes, 374,047 full Secret Box successes, and 20,785 incremental successes.

Key result: every incremental state has a successful one-category Secret Box witness. Item-only retains 20,783/20,785 = 99.990378% of incremental states; Supporter-only 20,703 = 99.605485%; Tool-only 2,313 = 11.128217%; Stadium-only 623 = 2.997354%.

The two Item-only failures have zero Tag Call left in deck. Prior paired work shows no incremental state begins with Tag Call in hand, so all four Tag Call copies are Prized in those two states. Direct Supporter output rescues them. Full-output ablation therefore makes Supporter indispensable in exactly two states and every other output category indispensable in zero.

Supporter-only fails in 82 states, but raw deck Guzma & Hala counts there are 2 copies in 5 states, 3 in 24, and 4 in 53. So Supporter-only failure is not G&H Prize depletion. It reflects downstream payment/routing differences.

Singleton route-count distribution: exactly 1 working category in 44 states, 2 in 17,849, 3 in 2,888, 4 in 4. Singleton signatures: Item only 42; Supporter only 2; Item+Tool 40; Item+Supporter 17,809; Item+Tool+Supporter 2,269; Item+Supporter+Stadium 619; all four 4.

The dominant concrete mechanism is `Secret Box -> Item -> Tag Call -> Guzma & Hala`, so printed four-category breadth greatly overstates immediate category usage for this endpoint, while counting Secret Box as capacity one also misses the downstream fan-out.

Full pinned regression run 37805240852 passed.

Created `results/composed_connector_fanout/` to formalize the mechanism with the temporal resource solver. The Item chain `Box -> Tag Call -> G&H -> Artazon` satisfies Bunnelby + TM Evolution + Jet demand from four abstract payment units because Tag Call replenishes one unit before G&H. Direct Supporter route requires five. Removing Tag Call's second-card production also raises the Item route threshold from four to five. Supporter-window zero makes the chain fail. CI runs 37805002503 and 37805018267 passed.

Important modeling consequence: distinguish printed output count, immediate category use, and state-valid terminal fan-out. Compile connector chains into terminal profiles carrying payment, action-window, and ordering costs before mapping a real card into an abstract capacity regime.

Potential next action: use all 16 subset success counts to compute redundancy-aware output attribution (e.g. Shapley values). Full counts already imply approximate access credit Item 46.92%, Supporter 46.77%, Tool 4.53%, Stadium 1.78%.


## 2026-10-10 incarnation: coalition resilience and latent synergy

Claimed agent7 on 2026-10-10T11:26:13.941Z, verified commit e22bae29cc63a1c777166d0798174666444e3462.

Extended the 500,000-state Aichi Secret Box 16-mask audit into exact per-coalition synergy analysis using existing singleton-signature counts. Created \`tools/secret_box_coalition_synergy.py\`, \`results/secret_box_coalition_synergy/\`, and CI regression.

Every incremental state has a working singleton output route, but a Tool+Stadium-only mask succeeds in 4,849 states versus only 2,932 covered by a successful Tool or Stadium singleton. The 1,917 additional cases (9.223% of all incremental cases) are **latent multi-category synergy** hidden by the minimum-cardinality-one statistic. Tool+Supporter and Supporter+Stadium each have 42 additional cases beyond singleton unions. The original all-four state-count remains 20,785.

With each category independently available with probability \`q\`, uniform extra expected coverage is \`3*q**2*(1-q)*(667-653*q)\`; at \`q=1/2\`, the singleton-only model understates access by \`2043/16\` expected states, or 0.614325 conditional percentage points. This is a hypothetical category-availability overlay, not a game win rate. Shapley correction from additional coalition paths reallocates -709/4 Item, +653/4 Tool, -597/4 Supporter, +653/4 Stadium credit units; total is zero because the full coalition was already successful under both models.

Validated exact rational polynomials, 16-mask residuals, micro-oracle independent exhaustive enumeration, and heterogeneous category availability locally. The results reuse the original 500k seeded tables; no new expensive simulation.

Next useful investigation: instrument the Aichi planner to extract state-level Tool+Stadium witnesses and determine which board and hand conditions explain the 1,917 paths. Distinguish card acquisition from payment, and assess whether the compressed category mask misses path-local opportunity costs.

Follow-up 100k-seed witness trace: `results/secret_box_coalition_synergy/trace_pair_witnesses.py` isolates exactly 375 Tool+Stadium-only alternative states; all have Jet Energy already in hand, no TM: Evolution, Artazon or Bunnelby initially in hand/Active, both TM and Artazon searchable, and no Jirachi G&H/Tag Call access. Secret Box initially held in 357 and available by Stellar Wish in 18. Therefore the mechanism on this sample is Box Tool -> TM and Box Stadium -> Artazon -> Bunnelby while Jet is already held. Full sample has 1,917 inferred such extra successes; extrapolation of the diagnostic profile beyond 100k is a hypothesis until traced. GitHub Actions run `38048881043` passed both reproducible analyses. Updated result README fixes incorrectly escaped Markdown backticks and records this distinction.

Full 500,000-state witness trace (`results/secret_box_coalition_synergy/trace_pair_witnesses_full.py`, on-demand Actions run `38049000028`, **passed**) confirms all 1,917 latent Tool+Stadium-only successes have the SAME necessary resource pattern: Jet Energy already in opening/draw hand; TM Evolution, Artazon and Bunnelby initially absent from hand/Active; TM and Artazon searchable; no Jirachi access to G&H/Tag Call. Box is in hand 1,830 times or accessible from Jirachi top-five 87 times. This full population evidence supersedes the earlier 100k-only extrapolation caveat. Future work: statewise inclusion-minimal winning antichains and cross-pair overlap; assess consequences for Shapley and constrained category availability.

## Further 2026-10-10 findings: full antichains and sharp category-dependence bounds

Full 500k inclusion-minimal successful output-mask antichain audit `results/secret_box_coalition_synergy/antichain_trace_full.py` passed CI run `38049292465`. Distinct minimal-route counts across 20,785 incremental states: exactly 1 route in 2 states, exactly 2 in 15,932, exactly 3 in 4,847, and exactly 4 in 4. All winning minimal masks have sizes 1 or 2. Minimal pairs: Tool+Supporter=42; Tool+Stadium=1,917; Supporter+Stadium=42 (can coexist).

Exact `results/secret_box_coalition_synergy/correlation_bounds.py` proves sharp arbitrary-correlation bounds for the singleton-or undercount under equal marginal category availability q: 0 <= E[D] <= 1917 min(q,1-q). Simple pointwise dual certificates: D<=42*1(Tool)+1875*1(Stadium) and D<=1917*1(Item absent); tight explicit q-piecewise joint distributions. At q=1/2, independent undercount 2043/16 states, max permitted by correlated marginals 1917/2 states (4.611499 conditional pp); min 0. CI run `38049440514` passed. These are abstract exogenous-category availability counterfactuals and neither card-rule claims nor tournament rates. README now includes proof, witness distributions, and full antichain profile summary.

Next: investigate both 42-state pair routes with exact physical opening-state diagnostics, then pursue causal sequence instrumentation or more realistic correlated lock/payability mechanisms.

## 2026-10-10: exact 42-state payment-fodder routes and Jet equivalence

`results/secret_box_coalition_synergy/trace_small_pair_witnesses.py` full 500k seeded regression CI `38050016278` passes. All 42 Tool+Supporter inclusion-minimal pair states: TM: Evolution already in hand and not searchable from deck; Jet absent from hand but searchable; Secret Box held; G&H and Tag Call absent initially; a non-TM Tool (Stealthy Hood in all42, Counter Gain in40) remains searchable. The compressed Box Tool output therefore materializes `other` payment stock, allowing the Box Supporter -> Guzma & Hala full discard route to Jet. Two states have no Counter Gain in remaining deck, raising the possibility that the only Tool offered for this payment is strategically valuable Stealthy Hood. The current simplified model treats both interchangeably.

All 42 Supporter+Stadium pair states: Bunnelby already held or Active; Box held; Artazon searchable; 24 have TM and lack Jet, 18 have Jet and lack TM. Box Stadium Artazon can serve as G&H payment material while G&H retrieves the missing terminal resource, rather than using the Artazon effect. Pair6 and pair12 overlap in 24 states. These are physical starting-state diagnostics and causal implications of the constrained action set, not full sequence traces.

`results/secret_box_coalition_synergy/trace_jet_output_equivalence_full.py` in same full CI verifies exact state-wise match between Jet initially held and Tool+Stadium-only success among all 20,785 incremental cases: 4,849 true/true; 15,936 false/false; zero discordances.

Important mistake corrected during diagnostics: `_raw_state` yields physically named Counter dictionaries, whereas `_compress_deck` yields abstract keys `tool_other`, `supporter_other`, etc. First tracer patch used those abstract keys on raw Counter and printed misleading zero counts; corrected to physically named `TOOL_OTHER`, `SUPPORTER_OTHER`, `TAG_TEAM_OTHER` sets. Full corrected CI above passed. Future identity should preserve this distinction.

## 2026-10-10: sample-vs-universal output portfolio counterexamples (major correction)

New [`results/secret_box_coalition_synergy/global_portfolio.py`] exact count audit: 100k incremental prefix global minimal output-set portfolios (Item) or (Tool+Supporter), 500k prefix (Item+Supporter) or (Tool+Supporter). CI run `38050425832` passed. This is only empirical sampled coverage, NOT universal.

Breakthrough: three *constructive physically legal permutation fixtures*, implemented by `results/secret_box_coalition_synergy/constructive_global_witnesses.py` with detailed result at `results/secret_box_global_witnesses/README.md`, demonstrate **all FOUR Secret Box output categories individually indispensable for universal coverage over possible accepted openings**, under the CURRENT compressed first-turn-core Aichi planner. CI run `38050810040` passed. All three have Grand Tree baseline fail, full Box succeed, and every winning output mask contains specified bits:
(1) 4 Tag Call Prized, missing Jet: bit Supporter4 required; winning masks [4,5,6,7,12,13,14,15].
(2) 4 Guzma & Hala Prized, Jet held, TM and Bunnelby missing: Tool2+Stadium8 required, winning masks [10,11,14,15].
(3) Prizes 3 Stealthy Hood +1 Counter Gain+2 Artazon, TM Evolution×2+Bunnelby held, Jet missing: Item1 required via Tag Call -> G&H plus Bellelba payment; winning masks [1,3,5,7,9,11,13,15]. Their OR required bits is 15, so no proper subset preserves every possible full-Box-only modeled success, despite sample-complete two-category sets. Note rarity: the exact six-prize set in #3 has unconditioned probability 1/C(60,6)=1/50,063,860, less than 0.01 expected events in500k unconditioned shuffles. All fixtures are legal actual 60-card permutations and tested by original planner. Relevance to deck optimizers: hard-constrained zero-failure claims need exhaustive or adversarial coverage, since Monte Carlo misses rare Prize states.

Broadcast message sent under `communications/broadcast/2026-10-10T1212Z_agent7_secret_box_four_output_necessity.md`. Results/README.md prepended main theorem.

Additional note: rare four-Tag-Call prize event combinatorics initially mistaken (treated opening as coming from 54 fixed nonTagCall nonPrize cards and assumed the other two Prizes contained no Basics). Correct conditional-on-all-four-prized opening samples uniformly from the **56 nonTagCall** cards because two other Prize identities are random. `rare_tagcall_prize_tail.py` corrected expected value assertion to `246321/7805903600` conditional on valid 7-card opener with14 Basics. The first on-demand CI `38050516296` failed this hardcoded assertion; fixed in commit `cb2e1cb`, rerun pending. Important to distinguish forced all-six nonBasic Prize exact event (opening pool54) from four fixed Prize cards (opening pool56). 

## 2026-10-10: quantified exact rare-Prize incidence and positive-measure Item payment family

Reusable exact conditional probability helper `tools/accepted_opening_prize_probabilities.py`; `results/secret_box_coalition_synergy/exact_prize_tail_validation.py` proves via exact formula and independent 8-card exhaustive brute-force oracle. Given 60 cards and 14 Basic Pokémon, six Prizes, valid seven-card opening:
- Any specified four nonBasic physically distinct cards all Prized: `246321/7805903600` ≈0.00003155573174 (15.7779 expected events in 500k accepted openings).
- Any specified six nonBasic cards all Prized: `1195/57598385152` ≈2.07471e-8 (0.01037 expected in500k). Unconditioned six-card exact event probability `1/C(60,6)`.
- In original 500k seed, `rare_tagcall_prize_tail.py` recounts 21 openings with four TagCall Prized, two with accessible Box, and exactly two incremental Item-only failures, reconciling with original mask audit. Important: fixed4 Prize event's other2 Prizes are random; opener uniformly in remaining56 cards, not fixed54. Targeted CI run `38051300162` passed before latest Item-specific extension. Subsequent targeted run `38051418649` passed with extension (check logs if necessary). Old full sequential workflow `38050516296` failed erroneous rational assertion, and later `38050967090` failed literal escaped-newline indentation; these are superseded by corrected scripts and targeted green CI.

`results/secret_box_global_witnesses/importance_sample_prize_tails.py` and full100k wrapper, CI `38051488314` PASSED. Uniform accepted opening sampler conditioned on each forced Prize layout; counts:
- 4 TagCall Prized: 100,000 conditional starts, 7,873 incremental, 6,063 require Supporter. Joint rarity estimated 1.913224 per million valid openings.
- 4 G&H Prized: 100k conditional, 3,048 incremental, 1,283 require Tool **AND** Stadium. Estimated 0.404860 per million valid openings.
- All 3 Hood+CounterGain+2Artazon Prized: 100k conditional, 1,765 incremental, 13 require Item. Estimated 0.000002697 per million valid openings (extraordinarily small, high relative estimation uncertainty). Results are conditional simulated setup incidence, not tournament win rates.
For all six Prize case, `results/secret_box_global_witnesses/stratified_item_payment_tail.py` forces opening Oddish+ACE+Bunnelby+TM Evo twice, and two filler+first draw cards from physical35 generic card pool. The exact event probability conditional on valid opener is `1/18281877053440`. In 5,000 stratified Monte Carlo states, all required Item. More decisively `results/secret_box_global_witnesses/exhaustive_item_payment_family.py` checks all `C(35,2)*33 =19635` unordered filler-pairs plus draw, two opposite opener orders for each = 39,270 scenario/planner checks; all baseline fail, fullBox and Item-only succeed, mask14 no-Item fails. CI `38051738170` PASSED. This is a rigorously validated positive-mass counterexample *family*, not an exact total Item-required probability. Key nuance: exact family probability includes the defined specific five opening cards and filler set, and exhaustive test only two opposing physical opening orders, though other orders likely functionally equivalent; do not overclaim exact enumeration of every opening permutation.
New [`results/secret_box_global_witnesses/README.md`] quantitative section and `results/README.md` top entry capture full implications and CI links.

Next research options: use importance sampler to test other adversarial support constraints and quantify conditional route sensitivities; build per-source payment DCI-aware resource planner to distinguish Hood discard from Counter Gain; or exact subset-cover combinatorial procedure beyond these fixtures.


## 2026-10-10 22:58Z incarnation: exact universal Secret Box omission-loss incidence

Run ID: gpt6-agent7-20261010T225801035Z-box-payment. Claim commit 3bf5001a2f4b7296f49d65f0e0a962af7086d3fe. Do not refresh this lease; use its original timestamp for the 70-minute release check.

New code and results:
- results/secret_box_global_witnesses/exact_portfolio_lower_bounds.py
- results/secret_box_global_witnesses/relaxed_prize_pair_lower_bounds.py
- results/secret_box_global_witnesses/README.md, new appended theorem sections
- .github/workflows/validate-secret-box-exact-portfolio-lower-bounds.yml
- .github/workflows/validate-secret-box-relaxed-prize-pair-bounds.yml

Both validation runs PASSED: 38093543413 and 38093703503.

**Finding:** full-output Secret Box versus Grand Tree Aichi going-second core: all four output categories are individually necessary for universal correctness over physical valid opening states. Earlier constructive 60-position permutations showed existence. This incarnation derived exact positive-mass *families* under accepted Basic-open conditioning, and verified a large part of each with the same solver. A conservative eleven-card nonBasic generic filler stock (Guzma×2 + Cassius/Karen/Plumeria/Gladion/Faba/Lusamine/Peonia/Team Yell's Cheer/Bellelba) supports:
- Four Tag Calls in Prize; opener Oddish + Box + 5 fillers; first draw sixth filler; remaining two Prize cards may vary unless they exhaust a required two-copy TM, Jet, Artazon, or Bunnelby: 1,172 eligible two-card Prize layouts, aggregate first-draw weight 6,744; exact lower bound 843/48561235923200 ≈ 1.73595252e-11 valid starts needing Supporter.
- Four Guzma & Hala in Prize; opener Oddish + Box + Jet + 4 fillers; draw fifth filler; extra Prizes arbitrary except pairs exhausting TM, Artazon, Bunnelby: 1,173 eligible Prize layouts, aggregate first-draw weight 7,875; exact lower bound 225/7769797747712 ≈ 2.89582827e-11 needing both Tool and Stadium.
- All three Hood+Counter Gain+two Artazon in Prize, opener Oddish+Box+Bunnelby+both TM + two generic (35-wide) fillers; draw third filler: exact family probability 1/4570469263360 ≈ 2.18795914e-13 requiring Item. This improves previous 1/18281877053440 4-fold by admitting either physical Oddish and either physical Bunnelby. Existing 39,270 planner tests covered generic filler stock for one physical copy of each; model observes named card counts, so copy substitutions preserve outcomes.

The three Prize patterns are mutually disjoint, hence for any fixed output subset M a distribution-free lower bound on the first-turn-core loss vs full outputs is the sum of these appropriate family masses:
S * 1[Supporter omitted] + T * 1[Tool or Stadium omitted] + I * 1[Item omitted].
The proof counts real physical identities in uniformly shuffled 60 cards conditional on a valid seven-card Basic opener, six Prizes, and one natural draw. Pair-exclusion count is a closed-form weighted sum; the scripts check it by physical Prize-pair enumeration and replay.

**Limitations:** extremely small lower bounds and immediate-core endpoint, not actual omission-loss totals or tournament win rates. Generic filler source cards may have large downstream strategic value, omitted from the solver. The relaxed Prize script replays all eligible Prize pairs for one canonical filler arrangement; the earlier script checks all conservative 11-stock opening/draw fillers for a fixed Prize layout; the union across both dimensions is established by the named/compressed structural argument, not literally by the cross-product solver. No random sampling is needed for the exact probability calculations. Secret Box's cost is paid before the first deck search, and these witness hands contain plenty of visible generic payment material, avoiding a K0 clairvoyance artifact.

Next useful work: construct a more complete exact *enumeration* over physical opening filler allocations and Prize pairs, grouping by compressed hand/deck signature to avoid millions of duplicate DFS states; independently confirm the cross-product invariance theorem. Or build a DCI-aware side-cost model of discarding Stealthy Hood versus Counter Gain and measure which alternative backup category paths remain strategically prudent.


### 2026-10-10 same incarnation: physical DCI transition and zero-variance rare Item incidence

Further commits:
- results/secret_box_global_witnesses/grouped_cross_product_certificate.py, CI 38093867316 PASSED: exhaustive grouped opener/filler/extra-Prize/draw cross-product verification with exact physical multiplicities. Previous relaxation proof now fully checked, no possible independence gap.
- results/secret_box_global_witnesses/discard_gate_recycling_bounds.py, CI 38094108463 PASSED: hypothetical d=0..11 safe discard stock exact sensitivity for S (4 Tag Call prized) and T (4 G&H prized) events, physical Prize-pair and labeled filler enumeration. For d3 S=59/33385849697200, T=75/42733887612416; for d11 original S=843/48561235923200, T=225/7769797747712. With three initially safe fillers, Box can discard them, fetch TM + G&H + Artazon, then G&H can discard freshly searched TM and Artazon if a duplicate of each survives in deck, and recover another TM+Artazon+Jet. This makes Box output search a financing route for subsequent costs without K0 clairvoyance, rather than only direct terminal payload retrieval. Real supporter discardability remains matchup-dependent.
- results/secret_box_global_witnesses/named_recycling_transactions.py, CI 38094322482 PASSED: physical 60-instance conservation/zone transitions; Box pre-cost3 and G&H second cost2, protected fillers untouched. Explicit duplicate availability cases validate 3 safe (both duplicates), 4 safe (one replacement), 5 safe (neither). Strengthens prior compressed safe-resource certificate with named action sequencing.
- results/secret_box_global_witnesses/exact_six_prize_item_necessity.py, CI 38094565530 PASSED: complete exact conditional necessity probability for Item output given fixed six-prize all3 Hood+Counter Gain+Artazon2 = 35,905,391,051 / 243,063,372,123,000 ≈0.0001477202868428502, i.e. 0.01477202868%. Exact Prize event given valid opener = 1195/57598385152. Combined probability for all accepted starts = 35,905,391,051 / 11,715,529,476,053,936,332,800 ≈3.064768956826847e-12. Replaces high-noise 13/100k conditional MC (exact prediction 14.772/100k). About 14x earlier constructive physical Item lower-bound family and is a subset of total possible Item-indispensable states, not total outcome difference.
- Exact algorithm groups 54 unprized physical cards into 13 categories, enumerates 20,401 valid grouped opening vectors with weighted draw/Active and Jirachi top-five exact presence masks, totaling 1,147,468 test branches. Sum accepted-start weights equals combinatorial formula. Important observation: ZERO Item-required cases in fixed-Prize stratum obtain Box only via Jirachi Stellar Wish; all already held Box. Among conditional Item-required outcomes, ~5.905% were Jirachi Active with Box already held; ~94.095% started other Active. Narrow model result, not a general rule.
- results/secret_box_global_witnesses/item_exact_projection_oracle.py, CI 38094613227 PASSED: compressed exact outcome Boolean matches source planner on 12,000 physically sampled 60-card permutations conditional same6 forced Prizes. Every one agrees, two Item-required in independent sample.
- results/secret_box_global_witnesses/README.md appended proof, probabilities, caveats; exact code pinned rational values and zero Stellar-only regression.

Next valuable investigations:
1. Build further full exact global distribution over other Prize layouts with targeted stratification, to quantify total Item output indispensability rather than only one forced all-six event. Larger search.
2. Examine whether Stellar Wish Box-only inability follows from general AMR/hand-size capacity theorem under all-other-Tools/Artazon Prized.
3. Quantify protected-card loss with two-turn continuation objective or valued protected filler utility; current d threshold is hypothetical.
4. Integrate finding prominently into top-level results/README.md and send focused broadcast after exact run.


### 2026-10-10 continuation: falsification of all-six-only Item necessity

Key new falsification: Item output can be indispensable even if one Artazon is **unprized and actually held**, when Artazon is reserved for Bunnelby via Bench search and both TM copies are held. A concrete exact physical state:
- Prizes: Stealthy Hood ×3, Counter Gain, Artazon, Guzma & Hala.
- Starting seven: Oddish Active, ACE Secret Box, TM Evolution, Artazon, Pidgeotto, Gloom, Herdier.
- First draw: second TM Evolution.
- Pay Box with Pidgeotto+Gloom+Herdier, leaving TM×2+Artazon. No spare Tool or Stadium search because four other Tools Prized and second Artazon Prized; must preserve Artazon for Bench Bunnelby and one TM. Box Item can fetch Tag Call, Tag Call obtains two additional TAG TEAM Supporters (Bellelba and G&H, or two G&H if Bellelba itself Prized). Extra TAG TEAM plus redundant TM pay G&H optional two-card cost to get Jet. No-Item cannot pay. G&H Supporter output of Box is unnecessary because Tag Call can fetch it; Item-only mask works.

New code:
- results/secret_box_global_witnesses/one_artazon_item_family.py, CI 38095153924 PASSED. Validates 102 physical Prize layouts (all four non-TM Tools Prized, one of 2 Artazon, any one of 51 permissible sixth Prize cards excluding both TM, ACE and remaining Artazon) across representative all 3×3×3 generic filler group profiles and two TM opening/draw allocations. Generic filler stock=26 (other supporters 10 + special energies3 + ignored nonBasic13). Counts exact 2,444,000 physical prize/opening/first-draw configurations, conditional valid-opening mass **5/734379410688 ≈6.80846974633e−12**. This strict family is disjoint from all-six Tool/Artazon prized exact event.
- results/secret_box_global_witnesses/five_prize_item_frontier.py, CI 38095207971 PASSED: broaden to two disjoint fixed-five-Prize configurations (all4 otherTools+oneArt, or 3 of4 otherTools+bothArt) with sixth Prize any other category and enumerate *all* Basic-valid non-Jirachi-start grouped 7-card openers and first draws weighted by physical multiplicities, Ace Box held. Exact missing-Item and incremental-vs-GrandTree probability for the union **506271/2136694380620800 ≈2.3694123249058526e−10**. This is an exact subset (Jirachi starting Active excluded), much stronger than 6.808e−12 constructed family.
- Disjoint with all-six priced exact 3.0647689568e−12 => confirmed global Item-indispensability lower bound **2811797384387/11715529476053936332800 ≈2.400060014474121e−10** among valid starts. Both families are finite physical instances under uniform shuffle, not actual game win frequencies.
- The first draft of five_prize_item_frontier.py intentionally asserted zero Item necessity outside all-six and CI 38094988069 FAILED with the genuine counterexample above. This hypothesis was falsified and the script corrected to an exact weighted census. CI 38095207971 PASSED. This is an important negative research result.
- results/secret_box_global_witnesses/five_prize_physical_projection_oracle.py, CI 38095395920 PASSED: 28,000 independent complete physical 60-card states conditional on two forced five-Prize sets and random sixth. Compared grouped model's baseline/15/14 Boolean outcomes to original physical _raw_state and Jirachi top-five observations on each actual permutation; every check agreed. One incremental Item-positive case in the sampled one-Artazon family, zero in one-other-Tool, as expected under rare-event sampling.
- results/secret_box_global_witnesses/complete_five_prize_item_frontier.py: extends exact five-Prize census to Jirachi Active + next-five Trainer presence masks, including Artazon and Box as Stellar targets. Workflow validate-complete-five-prize-item-frontier.yml CI run 38095352937 still in progress as of 23:33Z. Expected to pin nonJirachi component to above exact rational; continue validating and archive final results after pass.
- README new appended section documents 102 physical Prize family. Broadcast communications/broadcast/20261010T2330Z_agent7_item-artazon-payment-collision.md shared broader lesson.
- Top-level results/README.md already prepended a summary of earlier exact lower bounds and one six-Prize Item event. Update after inclusive five-Prize CI to surface 2026-10-10 latest evidence prominently.

Main methodological lesson: availability of a card in hand does not imply it is safely spendable. The held unprized Artazon's assigned Bench-search duty prevents it from paying G&H, so Item acts as an indirect two-card payment source via Tag Call. This invalidated a tempting simple scarcity threshold and illustrates nonfungible resource roles and connector contention.

## 2026-10-12 incarnation: first playable tournament deck references, exact Radiant launcher

Claimed lease at 2026-10-12T10:52:32.423Z using CAS on `agents/agent7/.lease.json`, commit `ad0a47c8d39860b56086a328e61dfff23db1da14`. The prior unfinished complete-five-Prize Secret Box CI 38095352937 was confirmed successful; the old agent7 result remains intact.

The top-level results index had grown very large while never linking a complete human-usable 60-card deck. To address the primary research objective, created `results/competitive_deck_baselines/` with complete exact-print English lists:
- 2026 Aichi Vileplume Control runner-up: 26 Pokémon / 28 Trainers / 6 Energy, 14 starting Basics, original Grand Tree ACE SPEC. Print choices checked against the directly imported published list counts in `tools/aichi_vileplume_als.py`.
- 2026 Aichi champion Shadow Rider Calyrex (Yasunori Kato, May 10): 18 Pokémon / 31 Trainers / 11 Energy, 14 starting Basics, Unfair Stamp ACE SPEC and Radiant Eternatus. Original event source https://www.limitlesstcg.com/tournaments/566/decklists. This is a complete real-event benchmark with 33 selected English print IDs.

`reproduce.py` and `shadow_rider_reproduce.py` run `tools.deck_legality_proof.adjudicate_deck` as of 2026-10-12 and assert all exact prints eligible under bundled current Expanded snapshot. The proof does not decide regional rule variants or provide match win rates. CI workflow `.github/workflows/validate-playable-deck-baselines.yml` ran both on Windows successfully in run 38240101196. Both lists are indexed prominently in `results/README.md`.

New independent exact analytic model: `results/shadow_rider_radiant_launch/` has `reproduce.py` and README; matches the baseline's 1 Radiant Eternatus, 4 VMAX, 4 Mysterious Treasure, 13 other Basic, 38 filler. Exact 7-card valid Basic opening, six Prizes, and first natural draw going second. An alternate Basic MUST be in the opening to allow Radiant to enter the Bench, and two VMAX must remain searchable in the deck. Directly held Radiant launches two with 12.017840120% probability; Treasure-fetched Radiant adds 31.681322310%; combined 43.699162430%. Any Radiant access 45.025040638%. All percentages conditional on valid opening. Mathematically exact grouped hypergeometric enumeration, crosschecked with exhaustive 8925-labeled physical toy states and rational regressions; Windows CI successful run 38240760192. It counts mechanically possible one-discard Treasure, and omits value of discarded cards, Item lock, other search/draw, opponent mulligans, and later strategy.

Next high-value research: extend this Radiant model with legitimate competing use for Mysterious Treasure, and match/timing decision value of ending turn via Climactic Gate rather than attacking. Or build headless matchup tests against the Vileplume and Shadow Rider baselines, preserving actual Twinleaf supported subset. Do not interpret setup as win rate.

### Same incarnation: paired first-draw depletion, DCI and lock countermeasure

Added `results/shadow_rider_turn_order_launch/` (Windows CI run 38241339661 passed): exact same physical valid opening+Prize model with/without natural first draw. Two-VMAX Radiant access going first = 39.5787881589%, going second =43.6991624304%; gross improvement 4.3853588775%, **loss** 0.2649846061%, net +4.1203742714 percentage points. Every lost state involves drawing a VMAX from a deck that previously had exactly two available for Radiant search. Independent exhaustive 8,925 labeled toy physical state oracle matches both the joint and source-identity transition distribution. Drawing Radiant yields +0.9668960922 pp, drawing Treasure +3.4184627853 pp. Result is turn-one *ability-line access*, not optimal turn-order strategy.

Added `results/shadow_rider_discard_gate/` (Windows CI run 38241687329 passed). Exact hypergeometric DCI sensitivity: designate d of 38 other cards safe to discard, all other cards protected; probability safe hand conditional h other cards is 1-C(38-d,h)/C(38,h). At d=0/4/10/20/38, overall direct+paid Treasure two-VMAX access is 12.017840% / 24.757153% / 35.705070% / 42.343714% / 43.693497%. Even at d=38, h=0 Treasure-ready mass 0.0056658 pp cannot pay under strict one-class model. Independent 8,925 labeled toy oracle with 2/4 safe cards matches group exact. These are illustrative exogenous DCI assumptions, not actual player discard decisions.

Added `results/iron_thorns_shadow_rider_suppression/` (Windows CI initially failed due legit missing optional `rules` attribute on ordinary Pokémon; fixed via `card.get("rules") or ()`; run 38242177157 passed). Official Aichi sixth-place Iron Thorns ex list has exactly four Iron Thorns Basic; all accepted opening starts necessarily Active Iron Thorns. Active unnegated Initialization strips abilities from non-Future Rule Box targets: Radiant's Climactic Gate, Shadow Rider VMAX Underworld Door, Tapu Lele-GX Wonder Tag, Pidgeot ex Quick Search. Ordinary Vileplume Irritating Pollen, Fan Rotom Fan Call, and Jirachi Stellar Wish have no Rule Box, and persist. Radiant ability-mediated dual-VMAX launch rate is mechanically zero under active unnegated Initialization, even though it was 43.699% unblocked in narrow going-second model. Do not conflate this static lock counterfactual with complete-match outcome; opponent sixth-place published Japanese deck includes English-unreleased cards, and no full print legality was certified for it.

All four Radiant investigations synthesized into `results/README.md`. Source tournament link https://www.limitlesstcg.com/tournaments/566/decklists.
Next: build decision policies against opponent lock, or source-specific strategic discard alternatives. Avoid duplicating other agents' lock kernels: agent50 owns typed lock and attacker bot work.


## 2026-10-12 incarnation: English Aichi Iron Thorns deck and discard realism

Claimed agent7 lease at 2026-10-12T18:34:13.218Z, run id gpt6-agent7-20261012T183413218Z-connector-research. Never refresh the original timestamp. Lease CAS claim commit 487320b15a2a45a1a71cf940d8862034dda1fc2a. Orderly release threshold: 2026-10-12T19:44:13.218Z UTC, using actual clock at checkpoints.

Repository owner replaced results/README.md around 18:30Z with a directive to make a deck-first concise index, progressively organize tests under results/tests/ and decks under results/decks/. Agent2 owns that curation effort; avoid editing the top-level results README until coordinated. Broadcast communications/broadcast/20261012T1835Z_agent2_deck-first-results-maintainer-directive.md.

New complete experimental 60-card English-print adaptation of Kazuma Kashi's Aichi 2026 6th-place Iron Thorns ex list at results/decks/iron_thorns_aichi_english/. Original Japanese-only Palace Book, Palace Belt and Player's Ceremony were replaced with one extra Trainers' Mail, one extra Handheld Fan, and one extra Double Colorless Energy. Retains 57 original copies by name/count. Composition 4 Pokemon, 47 Trainers, 9 Energy, 4 starting Iron Thorns Basics, 1 Megaton Blower ACE SPEC. Manifest holds exact English print IDs, published source URL, three explicit substitution rationales; test validates strict 60-card construction, current bundled Expanded print eligibility and named attack-resource rates. Commit ced3a7fcd25c012f91a8a753ba5fcb69dfd0aef3 and Windows CI PASS 38292730598. These are source-data verified, playable snapshot candidates, not a demonstrated improvement in game wins.

First compare used existing tools/iron_thorns_gnh_side_payload.py under exact accepted 7-card opener + six Prize + first draw: theoretical Thunder Mountain + DCE line access 33.781505711% with original one DCE and 38.080679951% with two, +4.299174240 percentage points. Original named model assumes G&H two-card discard is always acceptable. Some alternative work valuable later includes Trading Trainer's Mail and Japanese-only draw card roles versus DCE speed.

Follow-up G&H discard sensitivity merged via PR #14, squash commit 9b26d68a1798c06ae041390f5f5e12d8e2335de2, dedicated branch agent7/iron-thorns-discard-gate-20261012. New reusable tools/iron_thorns_gnh_discard_gate.py and independent chronological physical card regression results/decks/iron_thorns_aichi_english/discard_gate_reproduce.py; detailed results/decks/iron_thorns_aichi_english/discard_payability.md and deck README synthesis; expanded Windows workflow. CI PASS on branch run 38293890630, 3 exhaustive labeled physical toy configurations with 13,608 / 25,200 / 47,880 opening-Prize-draw worlds, all exact category masses matched; original one/three-DCE envelopes reproduced and strict/spare policy ordering checked. Production model analytically reorders natural draw before Prize sampling conditional opening, mathematically equivalent under random shuffle.

The DCI model partitions other filler into hypothetical safe and protected cards. Any direct Mountain+DCE hand or no-optional-discard G&H Mountain search works. Paid G&H DCE search requires two safe cards (strict) or additionally unused G&H/Tag Call held (spare). With 12 safe (illustratively 4 Crushing Hammer, 4 Trainers' Mail, 2 Enhanced Hammer, 2 Camping Gear), 1-DCE strict=16.293835803%, 2-DCE strict=20.953810534%, 2-DCE spare=23.149686991%, 2-DCE ideal=38.080679951%. 12 safe status is hypothetical; cards can have large competing utility, not realistic universal DCI. 2-DCE strict gain +4.659974731pp over 1-DCE strict. At safe 0/6/12/19/30/48 the two-DCE strict rates are 9.234391/12.954847/20.953811/29.529449/36.568688/38.080141%. These are **named opening resource access** and not actual first-turn attack or match win rates. Other draws/search, supporter contention, locks, regional draw replacements, and opponents omitted.

Coordinated with Agent2 via communications/agent2/20261012T1844Z_agent7_iron_thorns_deck_first_candidate.md (commit 5fafa4200704e448522338e071187b2f6dcd143d), preserving agent2 ownership of deck-first results index. Strong next work: compare against a legal English draw-Stadium replacement for removed Player's Ceremony, across a two-turn continuation policy; or quantify Trainers' Mail's real top-four access in the exact 60 list, using actual paid-discard priorities. Avoid claiming objective competitive best without head-to-head evidence; Twinleaf headless adapter remains incomplete for competitive match simulation. For future checkout, source CI files at .github/workflows/validate-iron-thorns-aichi-english.yml.


### Same incarnation: full English Tropical Beach alternative and exact attack/fallback frontier

Created second fully-specified paper Expanded candidate at results/decks/iron_thorns_aichi_beach/ with manifest, README 60-card print table, source proof, dedicated test and frontier.md. It differs from agent7 two-DCE variant only +1 Tropical Beach (bwp-BW28)/-1 Double Colorless Energy (sm2-166), so 4 Pokémon / 48 Trainers / 8 Energy. Japanese-only Player's Ceremony becomes an extra legal English Tropical Beach, while other two prior substitutions are retained. Exact print eligibility bundled snapshot PASS, one ACE SPEC, four Iron starters.

Reusable tool tools/iron_thorns_beach_frontier.py models the choice between named immediate attack package (strict 12 hypothetical safe G&H discard targets) and conditional failure with a held/searchable Tropical Beach end-turn draw available. Model exactly partitions 7-card Basic-valid opener, six Prizes, first normal draw going second; when G&H optional discard needed for DCE, strict requires two designated safe cards. Fallback access can be held Beach or G&H/Tag Call to Beach in deck. Attack takes priority to produce disjoint events. Independent exhaustive labeled toy oracle in results/decks/iron_thorns_aichi_beach/frontier_reproduce.py matched 13,608 / 25,200 / 47,880 worlds; model attack values independently equal tools/iron_thorns_gnh_discard_gate.py.

At strict s12, 2-DCE 1-Beach: attack 20.953810534%, failed-attack Beach fallback 27.046350616%, union 48.000161150%. Alternative 1-DCE 2-Beach: attack 16.293835803%, fallback 39.657753910%, union 55.951589713%. Extra DCE +4.659974731pp immediate, extra Beach +12.611403294pp fallback. With stylized score Attack=1, fallback=v, two-Beach wins when v>exact 41265224571587/111677083922987 = 0.3695048538341463. This is not an empirical utility ratio, win rate, or reason to rank decks; opponent also gains Beach and future draw contents not modeled. Sensitivity s=0,6,12,19,30 reproduced in frontier.md.

Files merged via PR #15, squash commit e7772ff16263c63ebdcc0ee62f5b03494b3e5f12. Windows workflow .github/workflows/validate-iron-thorns-beach-frontier.yml CI PASS final run 38294748963 and initial 38294596755. Both deck READMEs cross-linked, direct results/test scripts in per-deck structure according to owner's deck-first directive.

Next high-value work: evaluate an explicit real-card two-turn continuation after Beach draw (whether missing Tag Call, G&H, Mountain, DCE can be found) while preserving opponent-benefit limitation, or study how Trainers' Mail can retrieve Supporter/Stadium and whether its four-card top lookup can change the named first-turn resource endpoint. Avoid assuming Beach fallback value equal to attack.


## 2026-10-14 incarnation: one-Mail physical opening frontier

Claimed 2026-10-14T17:35:30.427Z, run_id gpt6-agent7-20261014T173530427Z-iron-thorns. Research on the two complete legal English Aichi Iron Thorns variants (2 DCE/1 Beach versus 1 DCE/2 Beach). Added tools/iron_thorns_mail_frontier.py, results/tests/iron_thorns_mail_frontier/{README.md,reproduce.py}, Windows .github/workflows/validate-iron-thorns-mail-frontier.yml. PR #16 squash merged to main commit 33adacf0dc6dda55ae19ff508a1ca81fb40422db; Windows CI run 38609587845 SUCCESS.

Paired 300,000 valid opening hands per list, same 18 physical slot draws, RNG seed 20261014: two-DCE strict attack 20.910667% baseline -> 24.179000% with one Mail, +3.268333pp; two-Beach 16.275333% -> 18.736000%, +2.460667pp. Beach fallback after one-Mail choice 31.069000% vs 44.982333%. Baseline physically sampled rates matched preceding exact study within 0.2pp. Prior hypothetical 12 safe includes 4 unplayed Mail +4 Crushing Hammer +2 Enhanced Hammer +2 Camping Gear. Played Mail ceases to be a G&H discard. The Mail selection policy is oracle-perfect regarding hidden deck/Prize status and can choose to skip Mail, **so results are a restricted-action optimistic envelope**, not realistic K0 or match-win probabilities. This caveat matters significantly because seeing top four requires committing the Mail Item action. Agent2 received a synthesis message in communications/agent2/20261014T1750Z_agent7_iron_thorns_mail_frontier.md.

Next best priority: build explicit K0 hand-visible pre-commitment and posterior selection to quantify the clairvoyance gap, then two-turn Beach draw and opponent reuse. No need to edit results/README.md without coordination with agent2.
