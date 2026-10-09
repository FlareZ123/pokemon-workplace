# Pokémon TCG Expanded research map

This directory contains accumulated research on paper Pokémon TCG Expanded, Black & White onward. This page is a human-readable map of the strongest recurring findings and the detailed results that support them. It is intentionally selective rather than exhaustive.

**Opponent mulligan-bonus externality:** [opponent_bonus_assembly/](opponent_bonus_assembly/) derives exact conditional multi-group assembly probabilities after opponent bonus draws. The marginal increase from successive draws initially rises for two required four-copy groups (but can peak immediately if both groups are Basics) and induces a non-monotone optimal setup policy in an abstract 60-card benchmark: reject optional-only no-key hands at 0–1 mulligans, keep at 2–5, reject from 6 onward. The adaptive gain over the best stationary benchmark is only 0.000876371 normalized utility, and all game-line values are uncalibrated. Exhaustive small-deck and Bellman checks pass.

## Current high-level picture

Across several independent investigations, the same methodological conclusion keeps recurring:

> **Theoretical access is weaker than executable access.**

A card or line can be reachable in a search graph while still failing because of connector output capacity, discardability, Supporter timing, Bench space, Energy-attachment bandwidth, target restrictions, Prize dependencies, lock geometry, or information arriving after the relevant decision deadline.

The repository therefore increasingly favors **typed, resource-constrained state transitions** over untyped card-association graphs.

**Three-support pickup threshold:** [bench_multi_trigger_access/](bench_multi_trigger_access/) generalizes joint activation to up to five singleton supports; with n entries and q transient slots, at least n-q successful pickups are needed. The verified three-support toy benchmark gives 7.5272% nominal access versus 0.1056% typed coin-weighted access with one slot; an independent oracle checks 309,120 small-deck outcomes and the implementation reproduces the preceding n=2 baseline exactly. These are conditional access results before actual discard payments and support-Ability hand effects.

**Pickup-package slot frontier:** [bench_pickup_package_frontier/](bench_pickup_package_frontier/) exhaustively enumerates 49 eight-slot packages combining Nest Ball, Super Scoop Up, one optional Scoop Up Cyclone and discard-payment filler. In a fixed A1/O3/Quick Ball4 toy deck, the best restricted single-support trigger access is 35.7871% with four Nest Balls, three coin pickups and one Scoop Up Cyclone, compared with 34.4109% for the best package without the ACE SPEC. The +1.3762-point increase omits all alternative ACE SPEC opportunity costs and has passed exact CI.

**Paid pickup-replay and Nest Ball roles:** [bench_trigger_paid_replay/](bench_trigger_paid_replay/) integrates Quick Ball's actual other-card discard payment, Nest Ball direct-to-Bench target replay, backup-Basic rescue of a forced Active, and stochastic pickup timing. A 60-card toy's optimal access is 34.4109% versus 41.6405% under free search. Ablation partitions four Nest Balls' +9.8122 pp contribution into +5.1960 pp discard stock, +1.1506 pp backup Basic search, and +3.4657 pp support pickup replay. Independent 8,925-world labeling, ten physical witnesses and exact role partition pass CI. All figures exclude actual support Ability hand changes and opposing action.

**Nest Ball pickup replay:** [bench_trigger_pickup_replay/](bench_trigger_pickup_replay/) shows that a Basic placed by direct-to-Bench search can later be scooped into hand and manually rebenched for a hand-origin Ability trigger. Combined with recovery of the forced starting Active, this raises an exact toy model's trigger access from 35.0383% to 41.6405%, partitioned into +3.1365 points Active rescue and +3.4657 points Bench-origin replay. An independent 8,925-world oracle and CI verify the decomposition; search discard costs and actual Ability payloads remain upstream.

**Starting Active rescue:** [bench_active_trigger_rescue/](bench_active_trigger_rescue/) quantifies when a support Basic forced into the opening Active role can subsequently trigger its from-hand Bench Ability by first establishing a backup Basic, scooping the Active, and replaying it from hand. Direct-from-deck-to-Bench search Items can enable the backup without directly triggering the support. An exact 60-card model recovers +3.1365 percentage points over the no-recovery baseline in one four-coin-pickup scenario. The result passes an independent 8,925-world labeled oracle and prior-kernel crosschecks.

**Adaptive Quick Ball payment:** [bench_quickball_payment_order/](bench_quickball_payment_order/) integrates paid Basic search, pickup Items, transient Bench capacity and discardability changes after a support triggers. In one exact 60-card access model, requiring Quick Ball searches before either support enters the Bench yields 1.5087% joint success; optimizing action order yields 3.5143%. A previously triggered, scooped support becomes discard payment for the next search. The model has an independent 10,500-world exhaustive oracle and passing CI. The result is conditional and excludes actual draw/discard Ability payloads and starting Active recovery.

**Two simultaneous support-trigger access:** [bench_double_trigger_release/](bench_double_trigger_release/) joins accepted-opening Active roles, Prize availability, one-use hand-search connectors, one transactional Bench slot, and Super Scoop Up coin outcomes in a single exact state model. In one idealized 60-card scenario, nominal two-trigger access is 20.8678% while typed, coin-weighted joint feasibility is 2.4541%; an independent labeled oracle validates 8,880 small-deck paths. This is an access benchmark before real connector payments or support Ability hand changes.

**Secret Box downstream search and information timing:** [secret_box_gnh_tool_pipeline/](secret_box_gnh_tool_pipeline/) proves in a conserving Box-first state model that the Supporter output can obtain Guzma & Hala for a second Tool search, with newly searched Item and Stadium cards serving as payment; the minimal upfront discard stock shifts from three to five depending on target preservation and Stadium redundancy. [secret_box_k0_payment/](secret_box_k0_payment/) proves that Box's mandatory discard happens before first-search Prize information arrives, yielding a 6.733-point clairvoyance overstatement in one exact 60-card hidden-state witness. [secret_box_k0_opening_mix/](secret_box_k0_opening_mix/) weighs that policy error across all accepted opening categories and one natural draw in the illustrative deck: the acquisition probability changes from 34.3970% (clairvoyant) to 34.3240% (information-respecting), an **0.073-point average difference**. These exact results distinguish search-output reuse, hidden-information admissibility, and the frequency of affected states. The endpoint is in-hand acquisition, not a full legal ALS execution or win-rate estimate.

 [secret_box_k0_sensitivity/](secret_box_k0_sensitivity/) maps 27 exact deck-composition variations and proves that the pre-search information penalty can be nonmonotonic as discardability or Stadium/Item redundancy changes. [secret_box_k0_bench_bootstrap/](secret_box_k0_bench_bootstrap/) enforces distinct Tool-holder capacity, lowering the illustrative K0 joint endpoint from 34.3240% to 15.0745% when two visible eligible Basics are required. [secret_box_nest_ball_bootstrap/](secret_box_nest_ball_bootstrap/) and [secret_box_nest_ball_k0/](secret_box_nest_ball_k0/) compile the Box Item output as Nest Ball's actual Bench search, recovering 9.0704 percentage points of joint K0 success while paying the cost of removing Nest Ball from the hand. Independent labeled-card regressions cover card payments, hidden Prize worlds, and split Basic-count openings. All estimates remain conditional abstractions rather than a full board/attack or tournament model.


[physical_state_conservation/](physical_state_conservation/) now provides a higher-level synthesis of the identity hierarchy, materialization lifetime, physical-card conservation law, Knock Out phase boundaries, destination routing, and promotion-order results developed across the state-kernel work.

**Cross-agent gust synthesis:** [cross_agent_gust_oracles/](cross_agent_gust_oracles/) reconciles independent agent20 and agent44 tactical solvers, confirming 5,238 typed Boss/Serena states, 6,570 Boss/Counter states and 1,460 fixed-target source-order values. The two source-priority tallies use distinct denominators, so the audit documents both board-level and board-plus-target-level claims. [gust_tactical_synthesis/](gust_tactical_synthesis/) integrates card text and errata, typed target restrictions, Prize and lock deadlines, opponent promotion, own-side switching, stochastic acquisition, and an execution contract. It separates rules facts, mathematically exact bounded results, and additional assumptions that must be validated before matchup or deck-building recommendations. 

**Tactical Prize racing:** [gust_prize_minimax/](gust_prize_minimax/) gives an exact adversarial-promotion six-Prize endgame model. Across 146 structural board classes, 41 exhibit increasing marginal benefit from the second gust, and forcing a single gust on turn one loses attack tempo in 55. This introduces terminal tactical utility and optional timing into the otherwise access-oriented evaluation of gust Supporters. [stochastic_gust_draw/](stochastic_gust_draw/) integrates finite random draws and proves an exact deadline-access formula: on the 1/1,3,3 witness board, two hidden gust copies in an N-card deck have expected attack count 4 - 4/C(N,2), while one copy in hand and one hidden gives 4 - 5/N. [durable_gust_minimax/](durable_gust_minimax/) extends the opponent-promotion model to one- and two-hit KO targets with damage persisting across switches; in 390 structural classes, 107 have increasing second-gust marginal value and 141 penalize mandatory immediate gust use. [defender_escape_gust/](defender_escape_gust/) introduces a finite opposing switch budget between non-KO hits: one defender escape eliminates the two-gust gain in 79/390 classes, while increasing second-gust marginal cases rise from 107 to 157. [typed_retreat_gust/](typed_retreat_gust/) replaces free escapes with target-specific Retreat Cost, attached Energy-card payment, and Item-lock-gated Switch tokens. Giving single-unit retreat Energy to three-Prize targets reduces the two-gust benefit in 70/390 toy boards, versus just 6/390 when the same Energy goes only to one-Prize targets. [counter_catcher_prize_timing/](counter_catcher_prize_timing/) shows a new form of conditional gust failure: Counter Catcher's eligibility can expire after taking Prizes. When the opponent has three Prizes left, 76/146 simplified board classes need one or two more attacks with two available Counter Catchers than with two unconditional Boss effects. [gust_lock_deadlines/](gust_lock_deadlines/) tests the source-order policy against exogenous Item and Supporter lock deadlines. A persistent turn-2 Supporter lock reverses the previously Counter-first priority in up to 100/146 board classes, whereas a turn-2 Item lock favors Counter-first in 100/146; 4,380 exact game states are independently checked. [mixed_gust_prize_minimax/](mixed_gust_prize_minimax/) solves the two-card allocation problem between conditional Counter Catcher and unrestricted Boss. The mixed pair matches two Bosses on all 146 bounded boards when the opponent has 1..3 Prizes left, but loses on six boards when the opponent has 4..5. In all 730 initial scenarios, spending Catcher before Boss when a gust is already chosen is weakly optimal; the priority rule does not justify playing a gust when natural attacking is better. [pokemon_catcher_coin_minimax/](pokemon_catcher_coin_minimax/) models official Pokémon Catcher coin-flip errata with within-turn Item retries; among 146 toy boards, two stochastic Catchers beat one guaranteed Boss gust in 41 classes, tie in 48 and lose in 57. [stochastic_typed_gust_draw/](stochastic_typed_gust_draw/) carries Boss+Serena and Boss+Counter into a finite without-replacement draw model. On one reciprocal witness, Counter's two-attack route requires the unique Counter-then-Boss first-two draw order, worth 1/[N(N-1)]; on the other, Serena's improvement occurs when both gust cards appear in the first three draws, worth 6/[N(N-1)]. The exact rational game tree verifies how an all-in-hand tactical one-attack advantage can be heavily diluted by access timing. [gust_source_incomparability/](gust_source_incomparability/) unifies Serena's V-only target geometry with Counter Catcher's Prize threshold: at opponent remaining Prizes 4..5, Boss + Counter is faster in 114/1,212 typed structural boards, while Boss + Serena is faster in a different 32, establishing strict incomparability between the two restricted gust sources under the one-hit-KO model. [target_restricted_gust_minimax/](target_restricted_gust_minimax/) shows that typed target eligibility is a separate source of gust value loss: in 126 of 1,212 abstract boards, Boss + Serena needs one or two more attacks than two Bosses, even though 71 losing boards contain at least one Pokemon V. One constructed board with four V targets still loses the two-attack route because both decisive three-Prize targets are non-V TAG TEAM Pokemon-GX. [paired_gust_live_lock_execution/](paired_gust_live_lock_execution/) closes the board-to-restriction-to-physical-action loop: Active Stoutland's Sentinel blocks Guzma, Prime Catcher Item gust moves Stoutland to Bench and reopens Supporters, and a subsequent physically paid Guzma can target Stoutland and reactivate Sentinel. Passive Vileplume Item lock or an empty opposing Bench blocks that local unlock line. The adapter recomputes restrictions from actual Active positions and causal Ability-lock state after each source action. [paired_gust_source_permissions/](paired_gust_source_permissions/) validates physical Prime/Cross/Guzma/Giovanni plays through the exact current-legal print metadata and the source-scoped action restriction projector. In 24 source-by-lock cases, Spiritomb's ACE SPEC lock blocks Prime while leaving Cross Switcher available; Item, Supporter, and Trainer-wide locks select different source sets, with 11 accepted conserving transactions. [paired_switch_identity_bridge/](paired_switch_identity_bridge/) extends the physical two-sided action to materialized hand and discard identities. It moves actual played Prime/Guzma/Giovanni or both distinct Cross Switcher copies into discard, conserves the card ledger and checks attached Energy and Tool bindings, with 384 positive/negative action contexts under CI. [paired_switch_physical_transaction/](paired_switch_physical_transaction/) composes the audited opponent-first or own-first Trainer programs with conserved physical board-object switches and ordinary Supporter quota. Its 384-state regression verifies that attached Energy and Tools, damage, Active status cleanup and card-class usage remain consistent while resolving Prime, Cross Switcher, Guzma and Team Rocket's Giovanni. [paired_switch_order_catalog/](paired_switch_order_catalog/) audits eleven legal prints of Prime Catcher, Cross Switcher, Guzma, and Team Rocket's Giovanni. The first three switch the opponent before requiring their own switch; Team Rocket's Giovanni switches its own eligible Pokemon first. The effect-order distinction changes which half can still resolve when one player's Bench lacks a valid target. [prime_catcher_order_geometry/](prime_catcher_order_geometry/) finds a sequencing discontinuity in Prime Catcher: if the opponent is legally gusted and the player's Bench is empty, the impossible own switch leaves the current attacker Active. Placing one unready support Pokemon on that Bench before Prime forces a self-switch and can destroy the same-turn KO. Exact 63-profile Bench census and 376-state action-sequence regression document the effect. [trainer_gust_catalog/](trainer_gust_catalog/) audits 75 eligible Trainer switch-text prints across 22 names, separates actual player-selected gusts from opponent-controlled switches, and normalizes three historical Pokémon Catcher prints whose raw text predates the erratum. [typed_gust_target_minimax/](typed_gust_target_minimax/) applies Boss versus Serena target-scope restrictions: two Serena gust modes require more attacks than two unrestricted gusts on 208/582 structural V/non-V boards. [counter_catcher_prize_race/](counter_catcher_prize_race/) adds an exogenous opposing Prize clock and shows that an opponent taking Prizes can reopen a formerly expired Counter Catcher window, though the race deadline may still prevent victory. [prize_refill_gust/](prize_refill_gust/) enumerates hand, deck, six Prizes and natural draws, showing that three Prizes taken from a high-value KO can deliver another Boss in time for the next gust. Its four-Boss toy two-attack success probability rises from 10.3171% without Prize recovery to 16.1067% when recovered gusts are usable. [k0_prize_gust_information/](k0_prize_gust_information/) quantifies when first-deck-search information changes this endgame policy: with 2–4 Boss copies in a 60-card toy deck, K1 exact Prize composition improves expected attacks in only four of 146 structural boards; the policy gain requires enabling Prize-recovered Boss and can change whether an already-held Boss should be spent now. [serena_draw_option/](serena_draw_option/) implements Serena's alternate discard-and-draw-to-five Supporter mode alongside target-restricted gust, with exact hypergeometric future Boss access. [serena_discard_capability/](serena_discard_capability/) demonstrates state-dependent discard acceptability: retaining redundant Serena copies in hand can prevent deeper draw-to-five access, worsening attack-turn expectations despite their nominal Supporter strength.

**Cross-model tactical synthesis:** [gust_option_value_synthesis/](gust_option_value_synthesis/) connects thirteen validated paper Expanded gust studies into a decision framework spanning opponent promotion, current errata, target restrictions, card payment, timing, Prize-card recovery, hidden information, and alternate Supporter modes. Its key limitation is that all component states are conditional abstractions rather than measured tournament position frequencies.

## 1. Connector realism: access, payment, output capacity, and opportunity cost

The connector results formalize several distinct reasons a search route can be less useful than its graph connectivity suggests.

- [connector_domination/](connector_domination/) shows that one universal one-card search cannot satisfy two independently missing channels at once. In its Computer Search-like baseline, correcting only discard cost still leaves a material overstatement if the shared connector is allowed to repair multiple missing targets simultaneously.
- [competing_connector_policy/](competing_connector_policy/) extends that shared-resource problem across turns. In its illustrative three-turn cost-2 baseline, state-contingent allocation between Prize rescue and a setup target reaches 12.303622% joint success versus 9.848039% for the stronger single-purpose policy, showing measurable option value from retaining target choice until more state information arrives.
- [competing_connector_deadlines/](competing_connector_deadlines/) adds expiring objective windows. With rescue due by turn 4 in the same abstract cost-2 regime, moving setup's deadline from turn 4 to turn 1 lowers flexible joint success from 15.114299% to 10.758838% and shrinks flexible allocation's gain over the best single-purpose policy from 3.055764 to 1.939474 percentage points.
- [connector_output_capacity/](connector_output_capacity/) compares a cost-2, capacity-1 connector with a cost-3, capacity-2 connector. The ranking changes as the disposable-card pool changes, so connector strength depends jointly on output capacity and state-dependent discardability.
- [discard_gated_supporter_access/](discard_gated_supporter_access/) and [discard_cost_amr/](discard_cost_amr/) quantify discard costs as real access gates rather than flavor text.
- [temporal_resource_replenishment/](temporal_resource_replenishment/) generalizes shared-resource allocation to ordered actions that can replenish resources. A Box-like cost-3 action that produces two later discard units can feed a cost-2 downstream connector from only three units of starting stock, so feasibility depends on action order and intermediate state updates.
- [temporal_discard_replenishment/](temporal_discard_replenishment/) anchors that effect in the Aichi Vileplume Secret Box line. In its seeded 100,000-state regression, all 4,175 Secret-Box-only successes had a continuation where later Guzma & Hala discards were paid entirely by cards generated after Secret Box, separating five-card discard throughput from three-card initial discard stock in those witnessed lines.
- [prize_rescue_xtransceiver/](prize_rescue_xtransceiver/) keeps Xtransceiver's coin flip inside the exact turn-by-turn rescue transition. Four copies raise first-window conditional rescue from 20.988290% to 36.853866%, while treating those same copies as certain-hit connectors would claim 49.984029%; same-turn retry bandwidth is most valuable when the rescue deadline expires immediately.
- [literal_gladion_projection/](literal_gladion_projection/) preserves Gladion's literal self-shuffle into the Prize zone and proves a narrow projection theorem: for the isolated objective of recovering all initially critical Prizes, the literal value is exactly equal to the earlier consumed-rescuer abstraction. A labeled physical-card enumerator validates the equivalence, while the result documents the richer interactions that can break it.
- [gladion_vs_seeker_destination/](gladion_vs_seeker_destination/) quantifies why physical Gladion destination matters once VS Seeker is available; an incorrect discard transition can create extra rescue uses.
- [compressor_vs_seeker_gladion/](compressor_vs_seeker_gladion/) adds provenance-aware Battle Compressor -> VS Seeker -> Gladion access and validates the two-Item complementarity with a labeled physical-card enumerator.
- [resource_constrained_connectors/](resource_constrained_connectors/), [compound_connector_constraints/](compound_connector_constraints/), [shared_connector_contention/](shared_connector_contention/), and [multi_channel_connector/](multi_channel_connector/) extend the same principle to multiple resources and competing channels.
- [connector_option_value/](connector_option_value/), [connector_marginal_regime/](connector_marginal_regime/), and [connector_slot_marginals/](connector_slot_marginals/) study how the value of an additional connector changes with the surrounding resource regime.
- [connector_capacity_option_value/](connector_capacity_option_value/) extends option value to multi-output search. In symmetric states with one more missing channel than connector capacity, preserving the connector until after natural draws can outperform eager allocation sharply; with five channels, capacity four, and four future draws, exact success is 70.0131% versus 21.2698% for eager use.
- [connector_capacity_deadlines/](connector_capacity_deadlines/) adds a deadline per target channel. In the same capacity-slack family, making one channel due before the next draw forces immediate connector commitment and collapses the optimal value to the eager-use value; in the five-channel, capacity-four, four-draw state this cuts success from 70.0131% to 21.2698%.
- [connector_slot_collision_option/](connector_slot_collision_option/) replaces interchangeable capacity with typed physical output slots. A Secret Box-shaped Item/Tool/Supporter/Stadium connector facing Item/Tool/Tool/Supporter demand has nominal capacity four but immediate matching size three; with one future draw, adaptive preservation succeeds 10.000000% versus 5.405405% for eager use.
- [connector_slot_deadlines/](connector_slot_deadlines/) combines typed slot geometry with target deadlines. Two Tool-only targets due in the current window are impossible for a one-Tool-output connector even when its nominal output count equals total demand; the all-urgent Item/Tool/Tool/Supporter example falls from the scalar model's apparent 100% feasibility to exact typed feasibility of 0%.
- [multi_output_slot_marginals/](multi_output_slot_marginals/) shows that the capacity-one slot ordering does not generalize to Secret Box-like multi-output search. With four distinct required channels, two outs per channel, and 20 currently disposable cards, +1 disposable gains 0.341283 percentage points of exact joint access versus 0.058064 points for +1 direct out, because crossing the discard gate can activate several outputs at once.
- [raichu_prize_access/](raichu_prize_access/) applies those ideas to Harto Miki's 2024 Aichi Raichu/Electrode list. After cross-classifying Giratina as both a setup starter and a discard candidate, and materializing the mandatory Active Pokemon, its direct Alolan Raichu package reaches the singleton in 30.578700% of valid-start states after one later random draw. Computer Search's zone-adaptive Gladion fallback adds 4.502243 percentage points within Raichu-Prized states.
- [raichu_forest_seal_access/](raichu_forest_seal_access/) adds the list's Forest Seal Stone layer while preserving its Pokemon V gate. Direct-ready typed access rises to 33.139533%, while an ungated universal-search abstraction claims 40.261571%. Omitting the Crobat V prerequisite therefore overstates this narrow access objective by 7.122039 percentage points.
- [raichu_search_to_seal_access/](raichu_search_to_seal_access/) lets Quick Ball and Ultra Ball complete Forest Seal Stone's Crobat V gate. Typed access rises to 34.466609%; Quick Ball supplies most of the +1.327077-point gain because its one-card discard threshold is reachable more often than Ultra Ball's two-card threshold.
- [raichu_dark_asset_search/](raichu_dark_asset_search/) adds first-order Crobat V Dark Asset after search-to-Crobat. Access rises to 35.092509%, exposing a cost-to-draw coupling: Quick Ball leaves a one-card draw-to-six window while Ultra Ball leaves a two-card window.
- [raichu_dark_asset_followup/](raichu_dark_asset_followup/) permits one further Ultra Ball or Computer Search action after Dark Asset while preserving residual discard capacity and Prize-aware target choice. Exact access reaches 35.225031%, a further +0.132521 points; 96.82% of that increment comes through the Quick Ball branch.
- [raichu_search_to_crobat_execution/](raichu_search_to_crobat_execution/) replays the Quick Ball and Ultra Ball search-to-Crobat witnesses through the canonical exact-discard Trainer transaction and typed Bench kernel. The seven-card snapshot physically leaves five cards after Quick Ball -> Crobat and four after Ultra Ball -> Crobat, confirming Dark Asset draw widths of one and two; a full Bench preserves the successful search but blocks the draw-engine continuation.
- [raichu_dark_asset_followup_execution/](raichu_dark_asset_followup_execution/) executes the dominant target-in-deck bounded continuation: Quick Ball spends one of three approved discard cards, Crobat V draws Ultra Ball, and the two residual approved cards fund Ultra Ball -> Alolan Raichu. Starting with only two approved discards leaves the second connector unpayable.
- [raichu_dark_asset_computer_followup_execution/](raichu_dark_asset_computer_followup_execution/) executes the complementary target-Prized branch through the observer-relative Computer Search transaction. Full-deck inspection collapses the actor to K1, the zone-adaptive policy selects Gladion when Alolan Raichu is physically Prized, the opponent remains uncertain about the private target, and the same residual two-card payment gate still applies.
- [gladion_supporter_physical_transaction/](gladion_supporter_physical_transaction/) couples literal Gladion Prize cycling to the canonical Supporter budget. The selected Prize moves to hand, played Gladion moves into Prize, the remaining Prize topology is shuffled, and Supporter lock or exhausted quota rejects the action.
- [raichu_full_prized_rescue_execution/](raichu_full_prized_rescue_execution/) closes the representative target-Prized material chain: Quick Ball -> Crobat V -> Dark Asset -> Computer Search -> K1 -> Gladion -> Alolan Raichu. The final state has Alolan Raichu in hand, Gladion in Prize, Crobat V on the Bench, the ordinary Supporter window spent, and all represented card totals conserved.
- [raichu_dark_asset_followup_sensitivity/](raichu_dark_asset_followup_sensitivity/) shows the second-order continuation is strongly discard-regime dependent. Its gain rises monotonically from 0.003653 percentage points with four conservative disposable cards to 0.563913 points with 24; Quick Ball supplies 99.63% to 93.34% of that gain across the sweep.
- [raichu_continuation_discard_policy/](raichu_continuation_discard_policy/) executes exact Quick Ball discard candidates through the full physical Prize-rescue continuation before DCI ranking. A required future piece is mechanically discardable and even given the highest illustrative local DCI, yet it is filtered out because discarding it destroys the joint endpoint; ranking then chooses the highest-scored continuation-safe witness.
- [raichu_belief_weighted_discard/](raichu_belief_weighted_discard/) extends that policy across K0 Prize uncertainty. In a representative seven-card Harto snapshot with Alolan Raichu absent from eight observed opening/draw cards, discarding visible Gladion preserves the target endpoint in 46/52 = 88.461538% of hidden target-zone worlds, while three ordinary discards remain safe in all worlds. Exact K1 releases Gladion only when Raichu is known to remain in deck, turning discardability into a belief-dependent feasible set rather than a fixed scalar score.
- [raichu_two_gladion_belief_discard/](raichu_two_gladion_belief_discard/) restores Harto's actual second Gladion under the same K0 snapshot. The visible Gladion becomes safely discardable in 98.868778% of hidden Prize worlds; the remaining 1.131222% failure set is exactly the joint event where both Alolan Raichu and the backup Gladion are Prized. This gives multi-Prize collapse a direct belief-dependent DCI interpretation.
- [raichu_backup_gladion_timing/](raichu_backup_gladion_timing/) separates that redundancy from timely access after Quick Ball establishes K1 and shows Alolan Raichu is Prized. Conditional on the search succeeding, the backup Gladion is outside Prizes in 45/50 = 90% of unresolved worlds, while one Dark Asset exposure reaches it in only 1/50 = 2%; a ready deterministic preserving connector can recover the 90% topology ceiling. Existence outside Prizes and deadline access are therefore distinct layers of discard safety.
- [raichu_backup_gladion_forest_seal_execution/](raichu_backup_gladion_forest_seal_execution/) physically realizes that deterministic ceiling with Forest Seal Stone. Crobat V can attach the Tool, use Star Alchemy for the deck-resident backup Gladion without spending the Supporter window, then Gladion literally rescues Prized Alolan Raichu. The route is rejected under Tool lock, an occupied Tool slot, spent VSTAR Power, Ability suppression, Tool-effect suppression, a non-V holder, or a Prized backup.
- [raichu_backup_connector_race/](raichu_backup_connector_race/) exactly combines a one-card Dark Asset exposure with hidden Computer Search and Forest Seal Stone in the same post-search K1 state. Direct backup draw is 2.000000%; each live deterministic connector adds 1.795918 points because the backup must occupy one of the other 44 deck positions; both gates together reach 5.591837%, still 84.408163 points below the 90% backup-in-deck topology ceiling.

- [trainer_search_profile_compiler/](trainer_search_profile_compiler/), [typed_search_target_allocator/](typed_search_target_allocator/), and [trainer_search_typed_integration/](trainer_search_typed_integration/) form a conservative card-text-to-action path for a validated multi-output Trainer search subset. The compiler emits text-level output/cost metadata, the typed allocator maps all 23 current output labels onto physical searchable-copy pools including Sabrina & Brycen's distinct-type constraint, and the state adapter carries locks, discard costs, Supporter/Stadium bandwidth, target multiplicity, and semantic target matching into the shared resource solver. One broad Trainer search can satisfy a narrower Item need when an Item target exists, while two connector copies still cannot reuse one singleton target.

- [trainer_search_materialization/](trainer_search_materialization/) carries the typed Trainer-search planner's exact target-cost witness into the conserved physical zone ledger. Its Secret Box regression moves four distinct searched target classes from deck to hand, while a two-Arven witness moves exactly two copies from one shared target pool and rejects reuse of a stale witness after the physical state changes.

**Working synthesis:** connector evaluation should preserve at least search eligibility, output multiplicity, payment costs, action-window costs, and competing uses of the same connector.

## 2. Prize cards: beliefs, cut sets, rescue timing, and information value

The Prize work has moved beyond a binary K0/K1 flag toward explicit belief states and decision timing.

- [prize_belief_states/](prize_belief_states/), [prize_belief_kernel/](prize_belief_kernel/), and [prize_belief_decision/](prize_belief_decision/) represent uncertainty over Prize compositions directly. Exact information can lose value, regain value after a hidden Prize mutation, and lose value again after re-inspection.
- [prize_dependency_cutsets/](prize_dependency_cutsets/) treats minimal correlated Prize failures as cut sets. Alternative lines can be structurally resilient while a shared singleton connector can create a size-1 failure cut.
- [prize_information_value/](prize_information_value/), [prize_information_actions/](prize_information_actions/), [partial_prize_information/](partial_prize_information/), and [prize_conditioning_layers/](prize_conditioning_layers/) separate information quantity from the action cost and timing required to obtain it.
- [prize_position_belief/](prize_position_belief/) proves that exact Prize composition can still be insufficient for position-sensitive effects. With one known target among six face-down Prizes, unknown position mapping gives a best chosen-slot hit probability of 1/6, while the same exact composition with a known target position gives certainty; an E-35 face-down shuffle preserves composition while erasing that positional advantage.
- [peonia_arc_position/](peonia_arc_position/) turns that state distinction into a concrete Peonia -> Arc Phone policy. With one known singleton among six Prizes and three Peonia selections, preserved physical positions raise target hand-or-topdeck access from a 58.333333% shuffle counterfactual to 66.666667%; Trekking Shoes provides a same-turn hand endpoint when available.
- [prize_top_draw_belief/](prize_top_draw_belief/) composes the Arc Phone joint top/Prize posterior with a later top-card draw. Observing the drawn top identity conditions the untouched Prize posterior, preserving cross-zone anti-correlation that independent marginals lose.
- [repeated_prize_probe/](repeated_prize_probe/) shows that physical-position memory compounds across repeated probes. After a three-slot Peonia miss, three distinct Arc Phone/Trekking Shoes probes cover every remaining target position, while a composition-only recurrence that forgets failed slots values the isolated sequence at only 71.064815%.
- [information_material_separation/](information_material_separation/) shows that exact Prize information and material card access are distinct outputs. A deck search can reveal the full remaining deck even if the intended downstream connector fails, while a later search can be materially important but informationally redundant.
- [prize_rescue_deadline/](prize_rescue_deadline/), [timed_prize_rescue/](timed_prize_rescue/), [prize_rescue_connector_turns/](prize_rescue_connector_turns/), and related rescue results model whether information and recovery arrive before the strategic deadline.
- [prize_ticket_reinspection/](prize_ticket_reinspection/) extends Prize-to-deck recovery to consecutive Redeemable Ticket resets. Under a known initial Prize state, repeated blind Tickets leave marginal terminal searchability unchanged. With non-shuffling reinspection and stop-on-success, a three-Ticket upper-bound witness rises from 75.86% to 100%; an intervening deck shuffle reduces that ceiling to 98.67%. Exact rational dynamic programs are independently exhaustively validated against physical-card permutations.
- [aichi_repeated_ticket_access/](aichi_repeated_ticket_access/) calibrates the theoretical repeated-Ticket gains on 400,000 paired orders of the published 2026 Aichi Vileplume first-turn line. One naturally accessed Ticket raises the represented dual-Stage-2 endpoint by 1.562 pp and two Tickets by 2.964 pp, but reinspection plus the actual second reset contributes only another 0.00348 pp in the tested two-Ticket/one-Town-Map package. It isolates the difference between copy-count access and repeated action execution while leaving later-game deck-slot opportunity costs unresolved.
- [aichi_jirachi_ticket_search/](aichi_jirachi_ticket_search/) adds Jirachi Stellar Wish to the same Aichi first-turn access problem and explicitly models the shuffle after searching five cards. Preserving an unused Jirachi Ability by spending a naturally held Guzma & Hala or Tag Call connector roughly doubles the opportunities for post-G&H Trainer selection in a 300,000-start sample. The corresponding two-Ticket/one-Map dual-Stage-2 access lift from the late Wish rises from +0.13035 to +0.25180 percentage points, with explicit hand/deck movement tests and conditional sequencing limitations.
- [prize_zone_recovery/](prize_zone_recovery/) shows that recovery destination is itself a state variable: moving a Prize payload to hand does not restore a deck-search target, while full Prize resets have zero blind marginal searchability gain in the modeled setup but positive value when exact Prize information lets the player reset only bad states.

**Working synthesis:** Prize reasoning is a belief-state control problem. The relevant quantity is the value of information or rescue under the current posterior and remaining action windows, not a permanent bonus for having searched the deck earlier.

## 3. Bench space is a hard state resource

[bench_capacity_geometry/](bench_capacity_geometry/) establishes a reusable representation of Bench feasibility.

Important distinctions include:

- current Bench occupancy;
- effective Bench capacity from active effects;
- temporary peak occupancy during a line;
- persistent **Bench debt** from one-shot support Pokémon;
- forced contraction when capacity falls;
- continuation value of the Pokémon the affected player chooses to discard.

A route can begin and end within the legal Bench limit while still being impossible because an intermediate step needs one extra slot. A capacity restriction can also clean up stale support Pokémon for the affected player, so smaller Bench capacity is not a fixed-value disruption independent of board composition.

Related work includes [bench_capacity_effects/](bench_capacity_effects/), [bench_capacity_lock_interactions/](bench_capacity_lock_interactions/), [bench_capacity_transition/](bench_capacity_transition/), [bench_release_catalog/](bench_release_catalog/), [bench_trigger_access/](bench_trigger_access/), and [typed_bench_state_kernel/](typed_bench_state_kernel/).

[interturn_bench_debt_policy/](interturn_bench_debt_policy/) adds a cross-turn action-budget coupling: a spent Crobat V on the fifth Bench slot can be removed by AZ when Bench entry is the only future need, but ordinary one-Supporter bandwidth cannot both use AZ and play another required Supporter on that same turn. A two-Supporter quota restores the line. In the exact four-out toy draw layer, a 4->5 draw improvement has a 16.769152% break-even probability for this future Supporter/Bench collision.

[typed_bench_release_execution/](typed_bench_release_execution/) generalizes that Bench-debt release across action classes. A Supporter release still collides with another required Supporter at ordinary quota, a deterministic Item release works unless Item-locked, an attack release cannot free a full Bench early enough for a same-turn new entrant because the attack ends the turn, and a ready Ability release can work before the remaining actions. Super Scoop Up gives a stochastic middle case: in the same 4->5 draw toy layer, one available attempt raises the break-even collision rate from 16.769152% to 33.538304%, while two raise it to 67.076608%.

[bench_release_deadline_geometry/](bench_release_deadline_geometry/) adds earliest-entry time and deadline. Attack release misses a current-turn Bench deadline but can preload an empty slot for a Pokémon that only becomes available next turn, and the next-turn Supporter quota is fresh. That same attack release still fails when the current turn independently needs a different attack, while Item release can preserve the attack window.

[interturn_bench_slack_exposure/](interturn_bench_slack_exposure/) shows that preloaded slack itself is exposed during the opponent window. After a release leaves occupancy 4 under capacity 5, Collapsed Stadium can reduce capacity to 4, force zero discards, and still erase the reserved slot entirely. Immediate materialization avoids that specific future-entry failure when the required entrant is retained through contraction, at the cost of sacrificing other board value.

[bench_capacity_restoration_bootstrap/](bench_capacity_restoration_bootstrap/) adds recoverability and bootstrap thresholds. A full four-of-four Collapsed Stadium Bench cannot use Pumpkin Pit/Snow Sink to unlock itself because those removers must legally enter the Bench before discarding the Stadium. Direct Stadium replacement can restore capacity from zero slack. Area Zero Underdepths is sequence-sensitive: with no Tera initially in play, replacing Collapsed reopens only the fifth slot; using that slot for the Tera activates capacity eight, while using it for an ordinary entrant first strands the Tera and blocks the expansion.

[bench_restoration_out_marginals/](bench_restoration_out_marginals/) quantifies the same bootstrap discontinuity. In its 40-card/five-seen toy state with two direct restorers and two Bench-triggered removers, zero slack has only two live outs and 23.717949% unlock access; one slack activates all four and reaches 42.707080%. Adding one remover copy is worth 0 pp at zero slack and 7.957350 pp at one slack under symmetric draw access.

[bench_restore_prize_conditioning/](bench_restore_prize_conditioning/) adds six random Prizes from a 46-card unknown pool and cross-validates the grouped states against `PrizeBelief`. K0 expected access is 20.772947% at zero slack and 37.941600% at one slack. Under K1, one direct restorer Prized drops zero-slack access to 12.5%, while one remover Prized leaves it at 23.717949%; at one slack those two Prize identities become symmetric live-out losses.

[bench_teleport_capacity_bridge/](bench_teleport_capacity_bridge/) composes the physical Gothitelle Teleport Room discard-to-Stadium channel with Bench limits and ordinary Stadium-play quota. From a full four-of-four Collapsed Stadium board, a live Active Gothitelle can remove the Stadium to reopen one slot even without a discard-pile replacement; Sky Field from discard expands to eight, while Area Zero requires Tera-first entry. Teleport preserves spent Stadium-play bandwidth, and the CI regression verifies mandatory replacement, timing/lock gates, and all 15 four-of-six contraction choices.

[teleport_discard_payload_line/](teleport_discard_payload_line/) composes an exact Ultra Ball two-card discard/search with physical Stadium entry. With Stadium quota already exhausted and Sky Field initially in hand, discarding Sky Field through Ultra Ball before using a live Teleport Room opens eight Bench slots and admits two required entrants; discarding two other cards or spending Teleport first permits only one. The counted Trainer and physical Stadium zone copies are synchronized, and the CI regression verifies class-total conservation and Item-lock/Roadblock negative branches.

[teleport_discard_access_bound/](teleport_discard_access_bound/) gives exact K0/K1 hypergeometric bounds for the discard-fed Teleport channel. In an illustrative 46-card unseen pool with six random Prizes, five cards subsequently seen, four Ultra Ball, two Sky Field, 16 approved other discard cards and one required searchable singleton, the conditioned board-state line is accessible in 4.171035% of draws; an access-only count that skips the additional discard requirement claims 5.325892%. A fully enumerated small-population regression independently verifies the symbolic formula. These probabilities exclude Gothitelle setup cost and alternative winning lines.

[teleport_discard_goal_closure/](teleport_discard_goal_closure/) corrects the searched-target-only metric to count the same goal when the singleton Pokémon is naturally drawn. In the 46-card unseen-pool K0 example, the additional hand-target branch raises the bounded goal access from 4.171035% to 4.474518%; under K1 with all required groups unprized, from 6.793838% to 7.309334%. Physical reproduction uncovered and repaired a canonical Trainer validator that rejected an otherwise legal zero-result restricted search even when mandatory two-card discard had changed state; general Trainer and goal-specific CI pass.

[teleport_connector_comparison/](teleport_connector_comparison/) shows a typed search-versus-payment ranking reversal using physical Quick Ball-to-Sky Field-to-Teleport Room execution. In the 46-card conditional K0 example, four Quick Ball copies give 5.804898% goal access for a Basic target versus Ultra Ball's 4.474518%; for Evolution card-in-hand access Quick Ball yields only 0.479006% versus Ultra Ball's 4.474518%. The SFT checks both Items' legality and exact texts, conserves physical zones, and matches independent exhaustive Prize/hand enumeration.

[teleport_same_pool_policy/](teleport_same_pool_policy/) combines Quick Ball and Ultra Ball in one explicit 46-card unknown pool and calculates the overlapping access-policy union exactly. For the bounded Basic-target goal, Quick-only covers 5.804898%, Ultra-only 4.474518%, and adaptive choice 9.285497%. For an Evolution target requiring hand access, the adaptive policy reaches 5.400934% by allowing Quick Ball to become Ultra Ball's second discard; even with no independently approved other discard, this dependent channel retains 1.920335% access. Exact small-state enumeration and a physical Quick+Sky discarded for Ultra-to-Stage-1 search pass CI.

[gothitelle_natural_setup_window/](gothitelle_natural_setup_window/) calibrates the major existing-Stage-2 assumption in the Teleport studies. For an illustrative 60-card list with three Gothita, two Gothitelle, four Rare Candy, and eight other Basics, 4.694346% of legally accepted opening hands naturally provide turn-two Rare Candy evolution readiness without any search or extra draw. An exact opening/Prize/turn-one/turn-two model matches independent labeled enumeration and demonstrates random-Prize marginal invariance in the no-search setting; it is not a competitive deck's optimized setup probability.

[gothitelle_quick_ball_first_turn/](gothitelle_quick_ball_first_turn/) extends exact turn-two Gothitelle/Rare Candy timing to one first-turn Quick Ball search for missing Gothita, with mandatory other-card discard and random-Prize searchability. In an illustrative 60-card list (Gothita 3, Gothitelle 2, Rare Candy 4, other Basics 8, Quick Ball 4, approved discard cards 12), turn-two readiness conditional on a legal opener rises from 4.694346% natural-only to 6.547707% with the targeted search, a 1.853361-percentage-point gain. Independent labeled enumeration and a Prize-sensitive negative test passed CI.

[gothitelle_teleport_two_turn_bridge/](gothitelle_teleport_two_turn_bridge/) tests a two-turn physical setup: first-turn Quick Ball discards Sky Field while searching Gothita, then the established Gothita evolves into Gothitelle through Rare Candy on turn two, and Teleport Room places that same Sky Field from discard into play. With Collapsed Stadium already in play and Ninetales's Barrier Shrine preventing hand-played Stadiums, two extra Basics enter after Teleport; paying junk for Quick instead leaves only one slot. The model conserves all tracked cards, respects the evolution window and tests the unlocked direct-play alternative; CI passed.

## 4. Energy readiness requires typed supply and action bandwidth

Energy access is another area where raw card counts collapse important distinctions.

- [energy_action_budget/](energy_action_budget/) separates typed Energy demand, Energy units supplied, cost reduction, target restrictions, and finite action resources such as the normal Energy attachment.
- [crispin_attachment_channels/](crispin_attachment_channels/) verifies that attachment by a Supporter effect and the ordinary once-per-turn attachment are independent channels. Crispin can attach one Energy by effect, put another into hand, and still leave the normal attachment available.
- [typed_energy_access/](typed_energy_access/) moves these distinctions into explicit state transitions.
- [multi_unit_energy_semantics/](multi_unit_energy_semantics/) and [apex_dragon_special_energy_burden/](apex_dragon_special_energy_burden/) address multi-unit and Special Energy behavior.
- [energy_identity_semantics/](energy_identity_semantics/) separates physical card name/category from current Energy type and unit provision. Its rulebook-backed Charizard/Meganium regression represents a Basic Grass Energy card that currently provides two Fire Energy without becoming Basic Fire Energy.

Concrete implications include:

- two Energy cards in hand can still require two turns if both need the same manual-attachment channel;
- one Double Colorless Energy card can provide two Colorless units with one manual attachment;
- Double Colorless Energy cannot satisfy two typed requirements such as two Fire symbols;
- Double Dragon Energy can satisfy typed demand only on a legal Dragon target;
- Energy type and Energy card category are separate semantics: a Special Energy that provides Psychic Energy does not become a Basic Psychic Energy card, which changes effects such as Photon Geyser's Basic-Energy-only discard;
- attack-cost reduction is a demand transformation, not another attached Energy card.

## 5. Lock effects need activation geometry and interaction state

[lock_interaction_matrix/](lock_interaction_matrix/) catalogs resource-denial effects and models more than the denied card class.

A useful lock state includes:

- denied or suppressed dimensions;
- activation geometry, especially Active-dependent versus persistent effects;
- target scope;
- conditions;
- persistence.

Multiple locks can compete for the single Active Spot, so a model that stores only desired denial dimensions can propose mechanically impossible combinations. Attack-applied locks can behave differently because they may persist after the attacker leaves the Active Spot. The catalog also finds a lock-handoff pattern such as Beheeyem's Mysterious Noise, where the attack applies Item denial while the attacker vacates play and frees the Active Spot for another source.

Related typed state work appears in [typed_lock_state_kernel/](typed_lock_state_kernel/) and [bench_capacity_lock_interactions/](bench_capacity_lock_interactions/).

[ability_lock_dependency_graph/](ability_lock_dependency_graph/) composes continuous Ability-lock sources through an explicit source-suppression dependency graph. Acyclic source hierarchies resolve mechanically, while a history-free snapshot retains cyclic strongly connected components as unresolved.

[ability_lock_setup_precedence/](ability_lock_setup_precedence/) adds official setup-order evidence for one such cycle. Empoleon V's Emperor's Eyes and Wobbuffet's Bide Barricade form reciprocal suppression edges, yet the official Japanese Q&A gives the first player's Ability precedence. The same physical board therefore has different effective lock states depending on first-player ownership.

[ability_lock_established_precedence/](ability_lock_established_precedence/) adds a dynamic official ruling. Tool-attached Garbodor initially suppresses Ting-Lu ex through Garbotoxin. When Garbodor later receives damage and Cursed Land would create the reverse edge, the official ruling preserves Garbotoxin because Ting-Lu's Ability is already absent at that event boundary. The implementation carries the previous resolved source into this verified transition while leaving other newly cyclic pairs unresolved.

[ability_lock_causal_state/](ability_lock_causal_state/) consolidates these verified precedence facts behind one causal state owner. It recomputes source geometry after each event, preserves an already verified cyclic winner while that source graph is unchanged, returns to ordinary snapshot resolution when the graph becomes acyclic, and leaves unsupported new cycles unresolved.

[protected_paired_switch_execution/](protected_paired_switch_execution/) integrates printed conditional paired-switch order with source-dependent Pokémon immunity. Benched Axew's Unnerve prevents Prime Catcher, Cross Switcher and Guzma from executing their opening opponent switch, blocking the dependent own switch. Team Rocket's Giovanni performs its own eligible switch first and therefore spends its Supporter and records one physical board transition even when the later opponent target is protected. Active Togekiss and Diancie establish opposite Item-versus-Supporter target eligibility. The compiler assumes static immunity across the transaction; dynamic Ability suppression requires a separate intervening resolution.

[gust_source_mix_minimax/](gust_source_mix_minimax/) compares typed Item and Supporter gust inventories under static effect-immunity with an exact defender-promotion minimax and a separate Boolean feasibility verifier. A mixed pair beats both homogeneous two-card pairs in 330 of 10,107 abstract boards (up to two fewer attacks), while it is worse than the better homogeneous pair in 991. One-Prize Active + Greninja V-UNION (Item immune) + Poncho-equipped VMAX (Supporter immune) yields 2-attack mixed and 3-attack homogeneous endgames. These are abstract geometry counts, not match frequencies.

[trainer_effect_gust_protection/](trainer_effect_gust_protection/) compiles six real Pokémon Ability prints and Leafy Camo Poncho into source-typed Trainer-play effect protection on exact Bench targets. It constructs a **crossed access matrix**: Togekiss Active blocks Prime Catcher Item gust yet leaves Guzma Supporter gust available, while Diancie Active reverses the result for a Benched Basic. The conservative checker includes provider positioning, suppressed Abilities, disabled Tools, card-source action class, and exclusion of attack-copied Supporter effects. Its tactical target permissions are separate from successful permission to play the source Trainer.

[dizzying_wind_attempt_event/](dizzying_wind_attempt_event/) reproduces the official Venomoth Dizzying Wind case where a failed Supporter is discarded yet the player can try another Supporter in the same turn. It reuses the pre-use gate in trainer_play_attempt_budget and preserves the failed physical attempt in the causal journal separately from committed plays. The Japanese official Q&A also confirms one coin flip for two simultaneous Poké Drawer+ Items and coin timing before Ultra Ball discard costs, giving direct support for an analogous but unverified one-coin Cross Switcher hypothesis.

[trainer_play_reactivity_catalog/](trainer_play_reactivity_catalog/) audits the bundled English Expanded card texts that react to Item, Supporter, or Trainer plays. In a bounded “whenever ... plays” phrase census, 32 eligible print records across 24 names occur: 31 use “prevent all effects of that card” and one, Phantom Forces Venomoth’s Dizzying Wind, introduces a coin-flip cancellation. The simultaneous two-Item Cross Switcher versus Venomoth flip multiplicity is flagged as a card-specific unanswered ruling rather than guessed. The dataset supplies target-protection candidates for future gust execution engines.

[play_occurrence_identity_separation/](play_occurrence_identity_separation/) refines the physical-card evidence model and corrects the overly conservative initial interpretation of [partial_play_history/](partial_play_history/): a successful named Prime Catcher action proves a physical Item play **occurred** even if exact source card instance IDs are unmaterialized. An opaque source witness stores the known card name, type, and required copy count, while absence of a physical source ID remains an independent provenance gap. Queries now return true for known opaque occurrences, false for excluded named actions under complete occurrence coverage, and unknown only across genuinely unclassified actions.

[partial_play_history/](partial_play_history/) introduces explicit event-capture coverage: a successful Item action with an unmaterialized source produces an **unknown** Item-play query rather than a false negative. Materialized hand-to-discard source proofs yield positive queries; verified negatives are available only when the entire submitted journal has complete provenance. Both variants can have identical physical boards and Ability-lock states. The result preserves the stronger caveat that callers must still submit all mechanically relevant actions.

[paired_switch_item_play_batch/](paired_switch_item_play_batch/) resolves a source-count versus effect-count mismatch: one Cross Switcher action spends two distinct physical Item cards even when only one opponent switch resolves. A new simultaneous play batch records both conserving hand-to-discard source identities at the first causal boundary, separately from the one-or-two switch boundaries. Prime/Cross occupy all four combinations of one/two physical Items and one/two switch boundaries under available Bench geometry.

[paired_switch_event_journal/](paired_switch_event_journal/) composes the physical Guzma, Prime Catcher, and Team Rocket's Giovanni switch transactions with the causal event journal, preserving switch microsteps in card-text order. A two-sided Guzma creates two lock refreshes and exactly one committed Supporter play. Prime with no own Bench executes only its opponent switch; Giovanni executes its own eligible Team Rocket switch before the opponent's. The regression compares replay against the original physical transaction and rejects inconsistent supplier events.

[causal_event_journal/](causal_event_journal/) joins that continuous lock-state owner to physical Trainer-play provenance in an immutable replayable event log. It constructs two identical final boards with the same actual Supporter-play history but different effective Ability-lock resolution because Wobbuffet left and re-entered the Active Spot in only one history. This demonstrates that even a complete Trainer-play log cannot substitute for mechanically ordered movement and source-geometry boundaries. The regression uses the actual ordinary and forced Supporter producers and rejects stale, duplicate, or corrupted journal transitions.

[ability_lock_precedence_quota_bridge/](ability_lock_precedence_quota_bridge/) shows the downstream consequence. On the same Empoleon V + Dual Brains Magnezone versus Wobbuffet board, changing only first-player ownership changes the derived Supporter quota from 2 to 1 because Bide Barricade either remains suppressed or suppresses Magnezone.

[ability_lock_canonical_budget/](ability_lock_canonical_budget/) completes the ownership chain into the canonical turn budget. A resolved causal lock state supplies only the effective suppression overlay; `refresh_canonical_action_quotas` derives the live grants and writes them into the existing `UnifiedState.turn_budget`. An unresolved lock state publishes no quota refresh.

**Working synthesis:** continuous lock state can depend on causal precedence in addition to board geometry. A simulator should preserve the event or setup fact that established precedence instead of forcing every suppression cycle into a timeless fixed point. Downstream derived state should consume that effective overlay rather than independently re-evaluating lock history.


[source_scoped_action_restrictions/](source_scoped_action_restrictions/) generalizes the Dream Ball / Vileplume source-zone observation into a conservative direct action-restriction compiler. The current legal snapshot yields **106 print-level restrictions across 63 card names**. Every compiled prohibition in this family names hand as its source, while the action predicate also preserves card class, attachment/evolution mode, Defending-Pokémon target scope where required, and Team Rocket's Arbok's printed exception. Vileplume therefore blocks an Item from hand while a Prize-pending Dream Ball remains legal.

**Working synthesis:** play permission needs a source-zone predicate. Broad hand-action booleans remain useful compatibility projections, while transaction-level legality should retain source zone and target semantics.


[source_scoped_channel_projection/](source_scoped_channel_projection/) measures when that compatibility projection is exact. Of the 106 audited restrictions, **92 (86.792453%)** can be encoded exactly by the existing hand-action channels. Fourteen retain typed residual predicates because they depend on ACE SPEC identity, Pokémon-with-Ability identity, evolution mode, Defending-Pokémon targeting, Energy target scope, a printed exception, or an unresolved exclusive lock branch. The bridge applies coarse channels only to hand-sourced attempts, so Vileplume can project to `item_play=False` without deleting Prize-pending Dream Ball.

**Working synthesis:** compact permission channels are safest as verified projections from richer state. A hybrid channel-plus-residual representation preserves a fast common case while exposing the semantic cases that need transaction-level predicates.


Echoing Madness and Allergy Storm are explicit branch-sensitive counterexamples to unioning all printed lock dimensions. Their compiled profiles remain unresolved until player choice or coin outcome selects one branch.


[source_scoped_trainer_transaction/](source_scoped_trainer_transaction/) applies that hybrid permission state to the established Item/Supporter search transaction engine. Exact print metadata supplies ACE SPEC and other selector tags, temporary channel projection gates ordinary hand actions, and residual predicates handle narrow selectors. The adapter restores base channels after execution so active restrictions remain the upstream state owner. A live CI regression verifies Vileplume blocking Secret Box, Sealing Scream identifying Secret Box as ACE SPEC, Arven remaining legal under Item-only lock, and Dark Moon-GX blocking Arven.

**Working synthesis:** transaction executors can consume lock legality as an external derived gate. This preserves one owner for action mechanics and one owner for active restriction state, reducing stale duplicated lock flags.


[source_scoped_restriction_activation/](source_scoped_restriction_activation/) adds activation and duration state for the same 106 restrictions: 77 are attack-applied and 29 are continuous Abilities with distinct board requirements. It also preserves attack coin, choice, and prerequisite gates plus the unique longer Frigid Breath window.

**Working synthesis:** continuous Ability restrictions should be derived from live source geometry and effective Abilities. Attack-applied restrictions should become temporal state after their application gate succeeds.


[continuous_source_scoped_restrictions/](continuous_source_scoped_restrictions/) executes the 29 continuous Ability profiles from effective Ability state plus local board geometry.

[attack_source_scoped_restrictions/](attack_source_scoped_restrictions/) resolves all 77 attack application gates into a concrete restriction or no effect.

[attack_restriction_turn_windows/](attack_restriction_turn_windows/) gives those concrete attack effects player-relative lifetimes and verifies extra-turn behavior with the shared turn scheduler.

[active_source_scoped_restrictions/](active_source_scoped_restrictions/) aggregates every currently live continuous and temporal restriction affecting one player immediately before permission projection. [active_source_trainer_transaction/](active_source_trainer_transaction/) feeds that aggregate into the established Trainer transaction engine.

[board_derived_continuous_restrictions/](board_derived_continuous_restrictions/) removes caller-authored continuous-lock booleans at the physical-state boundary. It derives source presence, Active position, Tool attachment, Stadium presence, relative Pokémon counts, and effective Ability state from canonical boards plus the resolved causal Ability-lock overlay. It validates that the overlay still matches the supplied board/Stadium state and rejects unresolved suppression cycles.

[board_derived_trainer_transaction/](board_derived_trainer_transaction/) carries the same ownership chain through real Trainer execution. The regression shows Secret Box closing under live Vileplume, reopening when Garbotoxin suppresses Vileplume, closing again under Stealthy Hood protection, and reopening under Jamming Tower while a Psyduck Headache temporal window independently blocks Arven.

**Working synthesis:** source-scoped hand denial now has separate owners for printed restriction semantics, activation geometry, causal Ability suppression, attack-gate materialization, temporal lifetime, current-board aggregation, attempted-action legality, and transaction mechanics. Derived permission state should be recomputed at the action boundary from canonical board and temporal state rather than persisted as stale lock flags.






## 6. Attack semantics require identity, execution body, and timing

[attack_copy_semantics/](attack_copy_semantics/) shows that copied attacks should be represented as nested execution rather than replacement of the outer attack object.

The minimum useful representation keeps separate:

- declared attack identity;
- currently executing copied attack body;
- ordered copy stack;
- eligibility predicate on each copy-selection edge;
- global use constraints;
- actor and zone state used to interpret phrases such as “your discard pile”.

This supports edge-local restrictions in nested copy lines such as Mimikyu Copycat -> Regidrago VSTAR Apex Dragon -> Dialga-GX Timeless-GX.

Other timing and attack-structure work includes [copied_attack_partial_resolution/](copied_attack_partial_resolution/), [attack_discard_dependency_grammar/](attack_discard_dependency_grammar/), [before_damage_timing_geometry/](before_damage_timing_geometry/), and [attack_retreat_lock_geometry/](attack_retreat_lock_geometry/).

[attack_copy_damage_bridge/](attack_copy_damage_bridge/) and [attack_copy_reaction_bridge/](attack_copy_reaction_bridge/) extend that execution stack through ordered board damage and the rulebook's damaged-by-attack reaction phase. A copied Timeless-GX can create a pending extra-turn directive while damage or a Strong Bash-like reflection still creates Knock Outs. The turn scheduler is therefore gated behind the full attack-ending phase order: outer copy continuation, board damage/effects, damaged-by-attack reactions, Knock Out processing, then turn handoff.

[attack_copy_physical_ko_bridge/](attack_copy_physical_ko_bridge/) then replays copied damage directly on the stack-bearing physical board. Its Haughty Order -> Phantom Dive witness carries a 200-HP Active and 60-HP Bench target into one pending simultaneous-KO batch, keeps their Tool/Energy attachments present for the trigger window, and conserves all physical card classes through atomic disposal and survivor promotion.

[attack_copy_terminal_bridge/](attack_copy_terminal_bridge/) gates pending copy-created turn effects behind the complete post-KO Prize window, terminal check, and replacement-Active phase. A Haughty Order -> Timeless-GX line that removes the opponent's final Pokémon ends the game without starting the extra turn; a continuing line remains blocked until the surviving Bench Pokémon is promoted, after which the canonical scheduler may apply Timeless-GX.

[simple_attack_board_semantics/](simple_attack_board_semantics/) adds a conservative card-data compiler for fixed/effect-only damage, seven exact damage-counter templates, and unconditional extra-turn clauses. [copy_attack_profile_damage_bridge/](copy_attack_profile_damage_bridge/) then preserves a crucial copy invariant: Weakness/Resistance uses the copying Pokémon's current type, not the selected source card's type. A Colorless Team Rocket's Persian ex copying Dragon-type Phantom Dive therefore deals 200 rather than 400 into a Dragon-weak Dratini unless Persian itself currently has Dragon type.

[attack_copy_outer_control/](attack_copy_outer_control/) separates six previously refused copy signatures into two execution stages: Nightcap has a declaration gate, while Skill Thief and four coin-gated attacks control whether the copy body executes after the attack has begun. [attack_copy_controlled_execution/](attack_copy_controlled_execution/) preserves the compiler's existing safety boundary with guarded definitions, then executes directly declared controlled attacks explicitly. A failed Nightcap gate never enters attack resolution; a failed Skill Thief or tails coin branch still records the declared outer attack; missing stochastic input remains an unresolved branch rather than an assumed outcome.

[physical_attack_position_source_bridge/](physical_attack_position_source_bridge/) carries exact attack-source self-switch, forced-switch, and targeted-gust effects onto the conserved physical board after copied damage. Tapu Fini-GX Aqua Ring shows that a step-5 self-pivot can move the original attacker to the Bench before a step-6 Poison Point reaction, clearing its Special Conditions and making the later condition inapplicable while preserving its Energy. Bayleef Push Down shows that a zero-HP Active can be switched to the Bench before the end-of-attack Knock Out check, so the later KO batch removes it without a second promotion. Clefairy Follow Me preserves the distinct attack-effect immunity target geometry of targeted gust versus forced switch. CI run 37802391672 passed.

[physical_attack_healing_source_bridge/](physical_attack_healing_source_bridge/) resolves exact copied self-healing bodies onto the physical Pokémon that actually executes the copied attack. A Haughty Order -> Maractus Mega Drain regression starts the copying attacker at four damage counters, heals it to two during the attack-effect step, then lets the defender's Spiky Energy reaction restore two counters in the later damaged-by-attack window. Elgyem Calm Mind verifies that an effect-only copied attack can heal the actor even with no damage record. The shared whole-attack coverage inventory now types all 293 exact self-healing rows and all 270 exact position-effect rows instead of leaving them under the generic source-specific fallback.

[physical_attack_energy_disruption_source_bridge/](physical_attack_energy_disruption_source_bridge/) adds exact copied one-Energy discard to the same physical phase model. Haughty Order -> Duraludon Hyper Beam demonstrates a step-5/step-6 dependency: discarding the defending Active's Spiky Energy suppresses its later damaged-by-attack backlash, while discarding another Energy leaves Spiky attached and places two counters on the original attacker. This matches the rulebook's analogous Gastro Acid timing example, where an effect removed during step 5 is absent when step-6 reactions are evaluated. The whole-attack inventory now types 191 exact Energy-disruption attack rows as well.

## 7. Setup is an information process as well as a legality process

The setup research models opening acceptance, optional starters, mulligans, and the public information revealed before the first normal turn.

- [setup_mulligan_policy/](setup_mulligan_policy/) studies how optional setup choices change opening and Prize priors.
- [setup_hand_value_policy/](setup_hand_value_policy/) turns those optional-only choices into an exact hand-state decision rule. With a constant cost per failed mulligan, the optimal stationary policy is a terminal-value threshold; the same keep rule also changes K0 Prize priors for non-starter cards that influence the decision.
- [setup_count_dependent_policy/](setup_count_dependent_policy/) extends the setup decision to nonlinear marginal mulligan costs. The exact backward recursion can either loosen or tighten the optional-hand standard after previous mulligans, so the count alone does not determine the direction of policy change.
- [talonflame_setup_policy_case/](talonflame_setup_policy_case/) applies the hand-state model to a historical Gardevoir/Talonflame list. A Talonflame-only opener has direct Brigette/Ultra Ball Ralts access 56.70% of the time; including the Skyla -> Ultra Ball connector raises modeled search coverage to 62.79%, and going second an Energy-powered Aero Blitz route raises total modeled line coverage to 94.87%. The case also separates Supporter contention from Ultra Ball discard payment.
- [setup_transcript_bayes/](setup_transcript_bayes/) shows that revealed mulligans are policy-censored samples. An opponent observing a mulligan sees information about both deck composition and the player's keep policy.
- [setup_information_value/](setup_information_value/), [mulligan_information_leakage/](mulligan_information_leakage/), and [setup_entry_payload_capacity/](setup_entry_payload_capacity/) extend the setup-state representation.
- [setup_trigger_role_contention/](setup_trigger_role_contention/) and [setup_bench_policy/](setup_bench_policy/) connect setup choices to later board constraints.

**Working synthesis:** archetype inference from mulligans should condition on the policy that generated the revealed transcript rather than treating revealed cards as an unbiased sample of non-Basic cards.

## 8. Archetype-Line-Specifics can be measured directly

[aichi_vileplume_als/](aichi_vileplume_als/) models the 2026 Aichi Open League runner-up Vileplume Control line built around:

`Tag Call -> Guzma & Hala -> Artazon + TM: Evolution + Jet Energy -> Bunnelby with Ω Barrage`

In the reported 500,000 accepted-opening simulation, the modeled Guzma & Hala route reached:

- Guzma & Hala access: 71.7356%;
- the Bunnelby double-Evolution core: 69.5594%;
- Pidgeot ex Stage 2: 59.5132%;
- Stoutland Stage 2: 48.5640%;
- Vileplume Item lock: 36.3388%.

The current broader modeled planner reaches the same core in 70.7090% of a deterministic 100,000-state regression after the Active-Bunnelby correction. That remains a modest increment over the named route and preserves the usefulness of the ALS abstraction within its stated scope.

[aichi_prize_supporter_information/](aichi_prize_supporter_information/) adds the list's singleton Gladion and Peonia to that first-turn core while preserving Supporter contention and Prize destinations. Across five matched 100,000-state blocks, state-aware Gladion adds 0.2964 percentage points, blind three-Prize Peonia adds 0.2010 points, and their union adds 0.4784 points. A separate K0/K1 audit shows that Tag Call or Fan Rotom pre-Supporter searches expose only 0.07275 points of the 0.29850-point state-aware Gladion ceiling in four matched blocks, making information timing a material part of Prize-recovery AMR.

[aichi_vileplume_secret_box/](aichi_vileplume_secret_box/) audits a concrete multi-output connector change in the same deck. Replacing Grand Tree with Secret Box raises the narrow first-turn core from 70.6524% to 74.8094% in a 500,000-state paired run (+4.1570 pp), while 76.67% of the incremental successes still route through `Secret Box -> Guzma & Hala -> Jet Energy`. This shows why physical output count and independent demand capacity must be represented separately.

[temporal_discard_replenishment/](temporal_discard_replenishment/) follows that route through its discard payments. Its provenance-aware 100,000-state regression shows that every Secret-Box-only success has at least one continuation where the later Guzma & Hala cost uses only cards generated after Secret Box resolves. This makes discard throughput and pre-line discard stock separate state quantities.

## 9. Iron Thorns ex: composing access with attack readiness

[iron_thorns_integrated_als/](iron_thorns_integrated_als/) composes Item, Supporter, discard, Stadium, manual-attachment, Prize-zone, and typed-Energy constraints for the named Iron Thorns ex line rather than validating each segment independently.

The deterministic state search finds the five-action baseline:

`Tag Call -> Guzma & Hala -> Thunder Mountain + Double Colorless Energy -> play Stadium -> attach DCE -> Volt Cyclone`

and removes the line when any required action channel or searched resource is unavailable.

[iron_thorns_named_line_probability/](iron_thorns_named_line_probability/) then evaluates the narrow named route exactly against the three published 2026 Aichi Iron Thorns lists. Conditioned on a legal seven-card opening and the first draw going second, the route succeeds in **33.781505711%** of accepted starts for the one-DCE Kazuma and Kohei lists and **39.107850627%** for Ryoya's three-DCE list. These figures exclude Trainers' Mail and other broader access routes, so they are route probabilities rather than full attack probabilities.

The result is a concrete first composition of the repository's typed-access and typed-Energy layers. It also identifies Trainers' Mail as a high-value next transition because connector failure dominates the remaining narrow-route state mass.

[iron_thorns_trainers_mail/](iron_thorns_trainers_mail/) performs that next transition exactly. Recursive top-four Trainers' Mail search raises the narrow route to **38.821051379%** for Kazuma, **46.623420409%** for Ryoya, and **37.195582431%** for Kohei. The result keeps Mail's target restrictions and reshuffle behavior explicit and shows that connector density interacts with DCE payload density.

[aichi_regional_draw_engine/](aichi_regional_draw_engine/) adds the Japanese-only draw engines missing from the bundled English card snapshot. Palace Book, Palace Belt, and Player's Ceremony account for every unresolved copy in the three preserved Aichi Iron Thorns lists. Palace Belt and Player's Ceremony are typed Guzma & Hala outputs, so omitting them removes real search edges. In the exact accepted-opening + six-Prize + first-draw model, a Palace Book or Player's Ceremony end-turn draw option is ready in **51.6974395%** of Kazuma states, **66.4787229%** of Ryoya states, and **44.4343565%** of Kohei states; Kazuma and Kohei can assemble Palace Belt plus Player's Ceremony in **33.7815057%** and **38.0806800%** of modeled states before scoring the two-card discard's DCI or Tool contention.

[iron_thorns_regional_failure_continuation/](iron_thorns_regional_failure_continuation/) conditions those region-only draw cards on failure of the named first-turn attack. Palace Book or Player's Ceremony supplies an immediate end-turn draw continuation in **32.848860519%** of Kazuma failures, **47.927533358%** of Ryoya failures, and **22.579832374%** of Kohei failures. The G&H -> Ceremony pivot alone occupies 5.751596817%, 2.604983539%, and 6.478205899% of the full accepted-opening state space respectively.

[iron_thorns_regional_recovery_package/](iron_thorns_regional_recovery_package/) adds Palace Belt as a next-turn objective. Among named-line failures, Belt plus an immediate regional draw continuation is jointly reachable in **12.723906584%** of Kazuma failures and **13.537034018%** of Kohei failures. [iron_thorns_speed_recovery_line/](iron_thorns_speed_recovery_line/) then uses G&H's Special-Energy output as a third axis: Belt + Ceremony + Speed Lightning Energy is reachable in **10.576296530%** and **11.912415167%** of those failures, with a single G&H able to fetch all three missing pieces in about 4.7% and 4.6% of failures.

[trainers_mail_prize_belief/](trainers_mail_prize_belief/) isolates the information content of Mail misses. Starting from a missing singleton with six Prize slots and 46 deck cards, four consecutive top-four misses raise the Prize posterior from **11.5385%** to only **15.8025%**. A full deck search is qualitatively stronger because it collapses the deck-versus-Prize uncertainty and can support a precise G&H/Gladion pivot.

## 10. Legality and card identity must remain explicit

[regional_card_source/](regional_card_source/) separates semantic source coverage from tournament-legality proof. The same preserved Aichi Iron Thorns lists fully resolve under JP source scope after adding three provenance-bearing Japanese references, while international scope leaves exactly the known 3/4/3 region-only copies out of scope. Local exact matches, explicit aliases, regional external records, out-of-scope records, and true missing names remain distinct resolution states.

[expanded_legality_baseline/](expanded_legality_baseline/) demonstrates that the bundled database is a search resource rather than a complete legality oracle. The maintained baseline applies confirmed official ban updates missing from the snapshot.

[card_identity_resolution/](card_identity_resolution/) separates three identities:

1. exact print ID;
2. conservative gameplay variant;
3. deck-building card name.

This separation matters because legality is print-sensitive and card names can map to many distinct gameplay variants. In the bundled snapshot, 1,289 of 3,392 names map to more than one conservative gameplay fingerprint.

Any simulator, validator, optimizer, or card index should therefore avoid using card name as its only gameplay or legality key.

[deck_validator/](deck_validator/) turns that identity separation into a conservative 60-card validator. It aggregates the ordinary four-copy limit by card name while retaining exact-print legality and card-specific deck rules such as ACE SPEC, Radiant Pokémon, Prism Star, Pokémon Star, and print-conditional singleton text.

[set_fallback_legality_audit/](set_fallback_legality_audit/) localizes all 191 remaining set-level legality fallbacks to the two 30th Celebration set files. [reprint_equivalence_candidates/](reprint_equivalence_candidates/) then shows the opposite edge of the problem: 106 prints outside the direct Expanded-set universe exactly match legal gameplay fingerprints, while 4,260 outside-scope prints share a name with a legal card and require stronger semantic review.

The handbook's Copycat example is a concrete counterexample to exact-text identity as a complete reprint rule: the two database fingerprints differ even though official tournament guidance treats the effects as functionally identical. Reprint equivalence therefore needs an errata-aware semantic layer rather than a name lookup or raw-text equality test.

[reprint_errata_resolution/](reprint_errata_resolution/) now separates 116 exact current-semantic candidates, 39 historically bridged candidates, 44 name-wide errata candidates, 3 current-handbook semantic candidates, 50 known non-equivalent prints, and 4,008 unresolved semantic-review prints within the 4,260-print same-name pool. [reprint_positive_evidence/](reprint_positive_evidence/) propagates the Tournament Handbook's explicit Copycat equivalence only across the exact historical source fingerprint, resolving `ecard1-138`, `ex15-73`, and `ex7-83` against `sm7-127`. [reprint_divergence_predicates/](reprint_divergence_predicates/) adds a structured semantic-difference layer: five historical benchmark rows contain explicit `excluding ...` clauses, three Great Ball rows are superseded by current name-wide errata, and two Life Herb rows expose the reachable predicate `target is Pokémon-ex`. The current Scizor ex witness makes those two Life Herb printings known non-equivalent in present paper Expanded. [trainer_name_reuse_divergence/](trainer_name_reuse_divergence/) adds 16 further historical Trainer negatives across eight same-name families through concrete distinguishing states, including Master Ball's bounded top-seven access, Revive's historical damage placement, and Power Plant's entirely different Stadium function.

[pokedex_information_semantics/](pokedex_information_semantics/) proves that the two historical “up to 5” Pokédex printings and the later fixed-five wording have identical reachable physical deck-order outcomes while permitting different private-observation histories. [reprint_equivalence_vector/](reprint_equivalence_vector/) generalizes that boundary into explicit semantic axes for material transition, private and public observation, target domain, timing, event semantics, and rule category, with tournament-policy status carried separately. Its four audited benchmarks distinguish Copycat's certified equivalence, Rainbow Energy's certified event-semantic divergence, Life Herb's reachable target-domain divergence, and Pokédex's private-information divergence.

## 11. Cross-kernel composition needs one canonical physical state

[unified_state_kernel/](unified_state_kernel/) composes the repository's Bench, lock, typed-Energy, and Prize-belief kernels behind one immutable mechanical state with a single authoritative card-zone map.

The regression suite shows that the same Quick Ball -> Tapu Lele-GX -> Wonder Tag -> Gladion association path can fail independently because of Item lock, Supporter lock, Ability suppression, or a full Bench. It also preserves the distinction between Item and Tool play, synchronizes Bench contraction with card zones, and sends the current attached-Energy/reduction summary to the exact Energy solver.

For a represented state where Quick Ball and its discard are already in hand while singleton Tapu Lele-GX and Gladion are both in a 53-card unknown pool with six Prizes, belief-weighted mechanical reachability equals:

`C(51,6) / C(53,6) = 78.4470246734%`.

This matches the independent closed form exactly.

**Working synthesis:** probabilistic beliefs should weight mechanically valid physical states. Specialized subsystems should avoid owning competing copies of physical card location. The current unified kernel is still a scaffold; `board_object_kernel.py` now supplies per-Pokémon movement state, while conservation across exchangeable zone counts, materialized board objects, and hidden-state beliefs remains open.

## 12. Multi-copy zone state needs multiplicity before object identity

[multicopy_zone_state/](multicopy_zone_state/) shows that a single `card -> zone` value is not a canonical deck-state representation when repeated copies exist.

For exchangeable copies, the minimal stronger state is a zone-count vector. Four copies distributed across deck, hand, Prize, and discard already have `C(7,3) = 35` distinct count states, while one name-to-zone value has only four possible values. Ten exchangeable copies across five abstract zones have `C(14,4) = 1001` count states.

The result therefore separates two stages of identity:

- keep gameplay-equivalent copies aggregated by per-zone multiplicity while they remain exchangeable;
- materialize explicit board-object identity only when attachment topology, damage/evolution state, temporary effects, hidden-information distinctions, or other history makes copies non-exchangeable.

This provides a state-compression path for the unified kernel: replace the current unique-string zone scaffold with count-preserving card classes, then assign object identity only where mechanics require it. The new board-object kernel supplies that materialized side; the remaining gap is a conservation adapter between them.

## 13. Board objects preserve topology and physical copy identity

[board_object_kernel/](board_object_kernel/) models Active/Bench Pokémon as persistent objects whose Energy, Tool, damage, temporary effects, and Special Conditions follow the correct Pokémon through switching, retreat, evolution, and Bench contraction.

The kernel distinguishes normal retreat from effect-based switching, including once-per-turn retreat bandwidth and Special Condition / temporary-effect clearing. It also represents multi-unit Energy payments by physical attached cards.

A follow-up identity audit separates **physical instance ID** from **database print ID**. Two physical Double Colorless Energy copies may share one print ID while carrying distinct instance IDs on the board. This prevents the repository's print-level `card_id` concept from being misused as a unique game-object key.

Together with [multicopy_zone_state/](multicopy_zone_state/), this suggests a hybrid state representation: keep exchangeable off-board copies aggregated by class and zone, then materialize instance identity when attachment topology or persistent history makes copies non-exchangeable.

## 14. Energy conservation joins aggregate counts to board topology

[energy_board_conservation/](energy_board_conservation/) implements the first explicit conservation bridge between those layers.

Two exchangeable Double Colorless Energy copies can move from an aggregate hand count into separate physical board instances that share one print identity. When one copy is discarded to pay Retreat Cost, the same transition updates board topology, the instance-to-class index, and aggregate `attached` / `discard` counts.

The validator rejects states where board attachments and aggregate attached counts disagree.

**Working synthesis:** materialization and dematerialization should be first-class transitions. Aggregate multiplicity is efficient while copies are exchangeable, and physical instance identity becomes necessary when topology or history differentiates them. The boundary must enforce conservation.

## 15. Pokémon evolution stacks bind physical cards to board objects

[pokemon_stack_materialization/](pokemon_stack_materialization/) extends the same materialization boundary to Pokémon cards.

A persistent Pokémon board object can own several physical Pokémon-card instances through an `in_play` relation. The regression materializes a Bulbasaur and Ivysaur from exchangeable hand counts, evolves the same board object, and verifies that the identity ledger and physical evolution stack contain the same exact instance IDs while total card counts remain conserved.

This separates three facts that a simulator otherwise tends to conflate: the physical Pokémon cards in the stack, the persistent in-play Pokémon object, and that object's current Active or Bench position.

## 16. Devolution reverses stack materialization

[devolution_materialization/](devolution_materialization/) checks the reverse identity transition. The top Evolution card leaves the persistent stack and returns to an exchangeable zone count, while the lower-stage physical card remains bound to the same Pokémon object and total copy counts stay conserved.


## 17. Tool and Knock Out conservation completes another materialization path

[board_attachment_conservation/](board_attachment_conservation/) extends the identity-ledger / board-object bridge to Pokémon Tools and mechanical Knock Out removal.

A Tool now moves through one conserved path from an exchangeable hand count to a materialized physical attachment, stays bound to the same Pokémon object through evolution, and returns to an exchangeable discard count when that Pokémon is Knocked Out. A second Tool on the same Pokémon is rejected by the transition model.

The shared `board_object_kernel.knock_out()` transition returns the complete removed Pokémon object, including Energy and Tool attachments. This lets conservation adapters update zones without duplicating board-removal logic, including the terminal case where no Pokémon remains to promote.

**Working synthesis:** materialization boundaries should be explicit per physical relation. Evolution preserves attachment identity; Knock Out destroys that board relation and is therefore a natural dematerialization boundary for ordinary discard-pile state.

## 18. Exchangeable card classes need an explicit equivalence namespace

[card_class_namespace/](card_class_namespace/) separates exact-print identity, conservative local gameplay variants, prospective official functional-reprint classes, deck-building names, and custom research classes.

The reprint audit's official Copycat example shows why this matters: tournament-functional equivalence can cross two different local gameplay fingerprints. A bare `card_class` string can therefore change meaning silently across legality, simulation, and copy-limit code.

The namespaced key adapter lets the existing zone-count machinery state its chosen equivalence relation without imposing one universal card identity.


## 19. Whole-stack Knock Out conservation unifies stack and attachment disposal

[stack_knockout_conservation/](stack_knockout_conservation/) composes the exchangeable zone-count layer, the physical identity ledger, and the stack-bearing board-position kernel for one complete Knock Out disposal transition.

The regression materializes a Bulbasaur/Ivysaur evolution stack, Muscle Band, and Double Colorless Energy on one persistent Active Pokémon object. On Knock Out, both Pokémon-card instances and both attachments move to discard and dematerialize while the Benched Bidoof remains bound to the promoted object. A terminal second Knock Out leaves no board-bound instances. Per-class copy totals remain invariant throughout.

**Working synthesis:** a Knocked Out evolved Pokémon is one board-object disposal boundary with multiple conserved physical-card members. Updating only the top card, attachment flags, or aggregate counts independently is structurally unsafe because it can orphan lower-stage cards or physical attachments.

[stack_zone_exit_conservation/](stack_zone_exit_conservation/) extends the same conservation boundary to ordinary hand/deck exits. The full evolution stack follows the Pokémon, while attached cards use a separately resolved destination. This distinguishes Scoop Up Cyclone style hand routing, Cassius style deck routing, and AZ style split routing without creating another board authority. The adapter can defer dematerialization when an enclosing effect still needs exact moved-card identity.

[pokemon_zone_exit_catalog/](pokemon_zone_exit_catalog/) supplies a conservative legality-aware card-text island for those destination fields. On the current bundled snapshot it finds 146 effectively legal print effects across 73 names: 85 deck/deck routes, 49 hand/hand routes, and 12 hand/discard routes. It uses the repository's effective paper Expanded legality layer, so the stale database metadata on officially banned Apple Drop Flapple printings does not leak into the catalog. Timing is now explicit: 143 rows are direct effects, while Rescue Scarf, Splash Energy, and Celebi contribute three Knock Out-triggered routing rows that must stay inside the Knock Out phase pipeline.

[pokemon_zone_exit_target_geometry/](pokemon_zone_exit_target_geometry/) classifies all 143 direct rows into 12 conservative board-target families. The largest are 76 self exits and 26 one-of-your-Pokémon exits, while the catalog also exposes opponent Active, opponent Bench, variable-cardinality own-board, wide opposing-Bench, mixed self-plus-opponent, and both-Active geometry. Exact routing clauses are preserved separately from full effect text so unrelated conditions cannot contaminate the moved target.

[cross_player_zone_exit_resolution/](cross_player_zone_exit_resolution/) shows that replacement-Active ordering is transition-specific. Expanded-legal Spidops `sv2-18` shuffles both Active Pokémon and their attached cards into the deck, then explicitly gives the attacking player the first replacement choice. The adapter removes both Active objects into a conserved promotion-pending state before any replacement is chosen, gates promotion behind terminal-state evaluation, and exposes the first visible choice before the second. This differs from simultaneous Knock Out, where the player whose turn would be next chooses first.

[batch_zone_exit_conservation/](batch_zone_exit_conservation/) adds an atomic same-player multi-object transition for geometry such as Virizion-GX's any-number board return, wide opposing-Bench shuffles, and survivor-complement effects. It validates the complete target set first, routes every selected evolution stack and attachment, and returns promotion-pending state if the Active belonged to the batch. This prevents a sequential implementation from promoting an intermediate Pokémon that was already selected to leave later in the same effect.

[zone_exit_branching/](zone_exit_branching/) quantifies the action-space consequence. On full six-Pokémon boards, coarse singleton geometry reaches at most six target sets, Shiftry's three-survivor complement has 10, and Virizion-GX's any-number return has 64 subsets. When later replacement-Active choices are included, Virizion-GX expands to 113 mechanical continuations. Spidops has one deterministic target set yet up to 25 ordered replacement pairs with full Benches.


## 20. Energy movement preserves physical identity until an attachment relation fails

[energy_movement_conservation/](energy_movement_conservation/) treats an ordinary Energy move between two in-play Pokémon as a topology change of one existing physical card. The same materialized instance changes holders without changing card-class totals.

[special_energy_move_conservation/](special_energy_move_conservation/) adds the restricted-Special-Energy boundary. Using Expanded-legal Double Dragon Energy as the concrete regression, a legal destination preserves the same physical instance and its two-unit representation. When the chosen destination cannot legally have that Special Energy attached, the source still loses the card, the destination does not gain it, and the same copy enters the exchangeable discard count.

**Working synthesis:** selecting a destination and successfully forming an attachment relation are distinct transition stages. Physical identity should persist through a legal topology move and dematerialize only when the card leaves board topology.


**Retreat source and information composition:** [retreat_environment_modifiers/](retreat_environment_modifiers/) adds exact-board Galar Mine, Big Net Ariados, and Benched Hisuian Sneasler modifiers to the conserved Retreat transaction. With one attached Double Colorless Energy, adding a friendly Benched Sneasler changes a modeled cost-4 failed payment into a cost-2 legal payment. [retreat_prize_provider_uncertainty/](retreat_prize_provider_uncertainty/) prevents an unknown Prize-dependent Counter/Reversal Energy unit snapshot from authorizing conditional payments while admitting guaranteed payments through lower/upper unit bounds. Both regressions execute through the existing board-derived Retreat adapter. Their limits are explicit: an externally identified effective Stadium, already-resolved Ability suppression, and an exact six-family provider surface. These are source- and information-composition results, not deck-level win-rate estimates.

**Continuous Retreat denial:** [retreat_ability_denial/](retreat_ability_denial/) extends the board-derived Retreat transaction to exact-print opponent Abilities whose source position or target Special Condition forbids normal Retreat. Five print sources require opposing Active residency; Cradily and two Dragalge prints have conditional passive coverage. In a reproducible Float Stone witness, an effective cost of zero still cannot bypass an applicable continuous prohibition, although a separate effect-based switch remains available. Eight prints and source-suppression cases are validated in CI; coverage is deliberately narrower than the full legality corpus.

**Causal Ability-lock composition:** [retreat_causal_ability_overlay/](retreat_causal_ability_overlay/) projects the repository's verified Ability-lock dependency state into immutable Retreat source boards. A Benched Alolan Muk suppresses Active Snorlax's Block, turning an otherwise forbidden Float Stone Retreat into a legal one; Garbotoxin suppresses Cradily's Special Condition-dependent restriction; opposing Neutralizing Gas disables friendly Sneasler's cost reduction, making a physical Double Colorless Energy payment necessary. A reciprocal Wobbuffet/Weezing cycle without verified precedence stops the transaction. The integration preserves unmodified physical board objects and reports unresolved lock status explicitly.

**Stadium-to-Tool projection:** [retreat_stadium_tool_overlay/](retreat_stadium_tool_overlay/) demonstrates that an effective exact-print Jamming Tower must blank attached Tool effects before deriving Retreat cost, opponent Ability protection, and the destinations of physically paid Energy. In the same immutable Retreat adapter, Float Stone loses its zero-cost effect, Dashing Pouch routes Double Colorless Energy to discard instead of hand, opposing Gravity Gemstone loses its extra cost, and Stealthy Hood no longer shields its holder against Snorlax Block. The physical Tools remain attached. Source predicates and all three cataloged Jamming Tower prints are covered by reproducible regression; full Stadium-zone state remains an external input.

**Executable Retreat action frontiers:** [retreat_action_enumeration/](retreat_action_enumeration/) composes physical payment subsets with every Bench destination, checks each against the established Retreat transaction, and returns exact committed action branches. One Double Colorless Energy plus two single-unit Energy and two Bench targets yields eight legal payment-and-promotion actions at cost 2; Galar Mine raises cost to 4 and leaves two. An independent 1,800-state finite oracle compares generated actions against brute-force subsets. The related Rescue Board correction admits an unknown low-HP condition when unconditional reductions already make Retreat free, while preserving unresolved status for genuinely HP-dependent payments. These are complete enumerations for the represented exact-card semantics; the full Expanded source compiler is still partial.

**Resource outcomes from Retreat payment choice:** [retreat_resource_allocation_frontier/](retreat_resource_allocation_frontier/) demonstrates two legal Retreat Cost-2 Dashing Pouch payments from the same Active carrying Double Colorless Energy and a Basic Energy. Paying only DCE returns DCE to hand while keeping Basic Energy attached to the outgoing Pokémon; paying both cards returns both to hand, leaving that Pokémon without attached Energy. Opposing damaged-holder Scoop-Up Block and Jamming Tower instead route paid Energy to discard. The two resource futures are non-dominated absent continuation objectives, cautioning against minimal-card-only Retreat enumeration. The verified witness is a mechanics result, not a deck-level performance estimate.

## 21. Simultaneous Knock Outs require a pre-discard batch state

[simultaneous_knockout_conservation/](simultaneous_knockout_conservation/) adds an explicit pending Knock Out batch before physical disposal.

The pending state keeps every Knocked Out Pokémon, evolution card, and attachment present for the rulebook's Knock Out-trigger window. Disposal then removes the complete batch atomically and permits promotion only from Pokémon that survive the whole batch.

The regression shows a concrete sequential-processing failure: when the Active and one Benched Pokémon are Knocked Out simultaneously, promoting that doomed Benched Pokémon after removing the Active would create an impossible intermediate state. Batch resolution rejects that promotion and conserves every stack card and attachment into discard.

**Working synthesis:** simultaneous state changes need phase boundaries. A transition engine should distinguish "known to be Knocked Out but still present for triggers" from "physically discarded and ready for promotion."


## 22. Knock Out disposal needs per-card destination routing

[knockout_zone_routing/](knockout_zone_routing/) extends the pending Knock Out batch with resolved per-instance destination zones.

Expanded-legal Huntail `sv10-55` provides the concrete counterexample to unconditional KO-to-discard semantics: Diver's Catch can return all Basic Water Energy attached to a qualifying Knocked Out Water Pokémon to hand instead. The regression keeps two Basic Water Energy and a Double Colorless Energy visible during the trigger window, routes only the Basic Water copies to hand, and lets the DCE and Pokémon follow normal discard disposal.

**Working synthesis:** conservation and destination choice are separate concerns. The identity ledger should preserve copy totals while card/effect semantics select the zone each removed physical instance enters.


## 23. Cross-player simultaneous Knock Outs contain ordered promotion decisions

[cross_player_knockout_resolution/](cross_player_knockout_resolution/) composes two pending KO batches with the rule that, when both Active Pokémon are Knocked Out simultaneously, the player whose turn would be next promotes first.

The regression gives each player one surviving Bench Pokémon, marks both Active Pokémon Knocked Out, and sets Player B as the next player. The legal decision protocol is `B -> A`: an attempted A-first promotion is rejected, B commits a surviving promotion, then A chooses after that visible decision. Only after both required choices are recorded are both KO batches physically disposed.

**Working synthesis:** simultaneity of the physical event does not imply simultaneity of downstream choices. Promotion order is an information boundary that a policy model should expose explicitly.

## 24. Post-Knock-Out resolution now joins Prize counts to material and belief state

[post_knockout_game_resolution/](post_knockout_game_resolution/) evaluates the complete Prize/no-Pokémon terminal snapshot produced by one Knock Out event before replacement-Active policy is requested. Its rulebook-table regression covers all 11 simultaneous loss-condition rows and represents them compactly by comparing the number of fulfilled loss conditions on each side.

[prize_take_conservation/](prize_take_conservation/) extends that count-level phase with the missing hidden-zone transition. Exact underlying card classes move from `prize` to `hand` under the physical identity ledger while the taking player's grouped `PrizeBelief` conditions on each observed Prize identity and shrinks its Prize set. A labeled five-card exhaustive check reproduces `P(next Prize=A)=1/5` and `P(B remains Prized | A was taken)=1/4`, while physical card totals remain invariant.

**Working synthesis:** Prize taking changes material truth and player information at the same boundary. A simulator that updates only Prize counts loses card identity, while one that moves physical cards without updating the taker's belief preserves uncertainty the player has already resolved.

## 25. Knock Out redirection is an ordered per-instance destination program

[knockout_redirection_routes/](knockout_redirection_routes/) translates the four currently catalogued KO-zone-routing signatures into explicit destinations for physical evolution-stack cards and attachments. The regression conserves one three-card evolution stack plus Energy and Tool attachments through Aegislash-like hand return, Tyranitar-GX-like full Lost Zone routing, Lost City routing, and Huntail-like selected-Energy recovery.

[knockout_redirection_conflicts/](knockout_redirection_conflicts/) shows that an explicit discard instruction must remain distinct from an unassigned destination. Lost City and a return-to-hand effect conflict on every physical Pokémon card in the stack, while Lost City and Lost Out agree on the stack but conflict on attachments. Huntail-like recovery conflicts only on selected Energy instances.

[knockout_redirection_ordering/](knockout_redirection_ordering/) then resolves an already-legally-ordered set of destination programs by taking the earliest explicit assignment for each physical instance. An official Pokémon Asia Lost City + Reuniclus ruling validates the order sensitivity: Reuniclus's owner chooses which effect resolves first, and that choice determines hand versus Lost Zone. The model deliberately leaves ordering authority upstream because this card-specific ruling is narrower than the rulebook's separate current-turn-player ordering rule for effects activated when several Pokémon are Knocked Out simultaneously.

[ko_effect_topology_witnesses/](ko_effect_topology_witnesses/) separates destination routing from other KO-trigger work using four official ruling witnesses. Team Plasma Weezing's Aftermath resolves before Lost City or Rescue Scarf moves Weezing, Aftermath and Reversal Trigger can be owner-ordered, and Reuniclus plus Lost City is an owner-ordered competition between two physical destinations. The evidence supports separate trigger, side-effect, destination-conflict, and physical-movement layers without asserting a universal precedence beyond the witnessed cases.

[effect_order_authority_overlap/](effect_order_authority_overlap/) makes the unresolved overlap explicit instead of guessing a precedence. It evaluates every evidence-backed authority scope that an upstream semantic layer says applies. If all claims identify the same concrete player, execution is safe; if complete claims identify different players, the result is an authority conflict and neither player is silently granted control. In the current Lost City/Reuniclus versus multi-Pokémon-KO overlap example, the outcome depends on whether the Reuniclus owner is also the current-turn player.

[order_authority_rule_change/](order_authority_rule_change/) records the 2025-08-01 chooser-rule migration for E-04, E-07, and E-08. Rulebook v3.0 used ownership-based chooser roles for those scopes; v3.4 assigns the current-turn player, current-turn player, and next-turn player respectively. A still-searchable Manaphy plus Team Plasma Weezing FAQ preserves the old E-04 owner-choice answer, so historical FAQ evidence needs version and effective-date metadata.

[pre_ko_attachment_removal/](pre_ko_attachment_removal/) maps damaging attacks that can remove Energy or Pokémon Tools from the opposing Active before the Knock Out check. The current legal Expanded snapshot contains 216 distinct signatures across 334 print instances: 27 resolve removal before damage and 189 resolve it in the later effects-outside-damage step. Both timing classes occur before Knock Out evaluation.

[pre_ko_attachment_snapshot/](pre_ko_attachment_snapshot/) proves the corresponding physical boundary. When an attack effect discards one Basic Water Energy before a lethal Knock Out, the later Huntail-like recovery can select only the Basic Water Energy still attached at the KO-trigger boundary. The earlier discarded copy remains in discard and cannot re-enter the recovery route.

**Working synthesis:** KO routing needs three semantic states per physical instance: unassigned, explicitly assigned to the ordinary discard sink, and explicitly assigned elsewhere. Trigger eligibility must use the board snapshot after earlier attack phases resolve. Destination conflict detection, order-selection authority, and physical execution remain separate layers.


## 26. Per-turn action budgets are shared mechanical state

[turn_action_budget/](turn_action_budget/) extracts Supporter, Stadium-play, manual Energy attachment, and Retreat bandwidth plus the attack / voluntary-end boundary into one immutable quota budget. Basic-rule limits default to one, while usage and current limits remain separate.

The integration review found a concrete split-state failure in the unified kernel: `BenchState.turn_ended` already blocked Bench additions and Supporter play, while several ordinary Item, Tool, manual-Energy, and Stadium actions could still be called after that boundary. Those transitions are now explicitly gated, and the unified-state regression passes in CI.

[turn_budget_integration/](turn_budget_integration/) adds a non-breaking bridge from the current split flags in `BenchState`, `UnifiedState`, and `BoardState` into one `TurnActionBudget`. The bridge round-trips ordinary one-use states back into the legacy fields and rejects modified quotas that those booleans cannot encode, providing a staged path toward canonical ownership.

**Working synthesis:** action bandwidth should have one canonical owner in composed planners. Specialized kernels can retain local compatibility fields during migration, while policy search should query and consume one shared budget.

The canonical budget now feeds the exact `supporter_outs_timing` probability model and the exact `energy_action_budget` route solver. Both integrations apply play permission separately from remaining quota, and both have passing CI regressions.



## 27. Prize information is observer-relative and visibility-sensitive

[prize_take_information_asymmetry/](prize_take_information_asymmetry/) distinguishes the taking player's observed Prize identity from an opponent who sees only the Prize count decrease. In the five-card, two-Prize toy state, after the taker observes A, the taker assigns zero probability that A remains Prized and 1/4 that B remains; the uninformed observer still assigns 1/5 to either singleton remaining. Hidden random removal also preserves the hypergeometric family: a uniform P-card Prize subset followed by unseen random removals is distributed as a smaller uniform subset of the same pool.

[observer_prize_beliefs/](observer_prize_beliefs/) makes that asymmetry explicit by storing a separate `PrizeBelief` per observer for the same physical Prize zone and updating each posterior according to what that observer actually saw.

[prize_visibility_partition/](prize_visibility_partition/) adds a second necessary axis after face-up Prize effects. Two states can have identical exact total composition while one has singleton A face up and the other has A face down; a face-down-only effect therefore has A-target probability 0 in one state and 1 in the other. The partition keeps exact face-up counts and a belief over the remaining face-down cards.

**Working synthesis:** hidden-state knowledge belongs to observers, and Prize targetability depends on visibility as well as composition. One global composition belief can alias strategically different states.

## 28. Prize card text already supports a reusable transition vocabulary

[prize_effect_catalog/](prize_effect_catalog/) conservatively compiles 139 legal Expanded effect rows into 19 Prize transition atoms, including inspection, face-up revelation, Prize/hand/deck/discard movement, top-deck and hand swaps, direct and extra Prize taking, Prize destination overrides, shuffling, and before-hand Prize triggers.

Named regressions cover Gladion, Hisuian Heavy Ball, Peonia, Rotom Dex, Redeemable Ticket, Burst-GX, Arc Phone, Team Rocket's Bother-Bot, Lost Block, Billowing Smoke, Town Map, and several before-hand trigger cards. Arc Phone produced a useful parser correction because its wording names the top-deck referent before the switch operation.

**Working synthesis:** Prize mechanics are better represented as ordered multi-axis transition programs than card-level labels. The atom catalog is a conservative semantic island and still leaves typed selection, optionality, counts, ordering, stochastic gates, and full referent resolution for later compiler layers.


## 29. Typed search execution must preserve the exact target witness

[typed_search_zone_transition/](typed_search_zone_transition/) closes one part of the compiler-to-state boundary by moving the exact targets chosen by a `TypedTargetAction` from exchangeable deck counts into exchangeable hand counts.

A generic one-Energy demand provides a concrete aliasing counterexample: one Basic Fire Energy and one Double Colorless Energy both produce the same demand profile `(1,)`, while the allocator retains two distinct exact actions, `target_cost=(1,0)` and `target_cost=(0,1)`. Executing those actions produces different hand states even though the strategic output vector is identical.

The bridge validates current source-zone availability and per-card-class conservation, and rejects stale exact actions after their selected target leaves the source zone. It deliberately keeps searched deck/hand copies exchangeable rather than inventing stable instance IDs.

**Working synthesis:** demand satisfaction is an evaluation projection, not a sufficient execution record. Policy search should carry the exact target-allocation witness until the chosen action has mutated canonical zone state.



## 30. Turn-action limits can change with live board effects

[action_quota_effects/](action_quota_effects/) uses Expanded-legal Magnezone `bw8-46` as a counterexample to boolean action usage. Dual Brains permits two Supporter cards during its controller's turn, so after one Supporter the state simultaneously has `used > 0` and remaining Supporter quota.

The quota model therefore separates usage count from current limit. Active quota grants recompute limits from the basic-rule baseline, so suppressing the granting Ability after one Supporter can reduce the limit from two to one without erasing the earlier play. Restoring the Ability reopens the second use. If two Supporters were already played before suppression, the coherent historical state is `used = 2, limit = 1`, with no further use available.

**Working synthesis:** action limits belong to live board state. Play permission, quota, and usage history are separate variables, and Ability suppression can change quota without changing history.



## 31. Extra turns reset action bandwidth for the same player

[turn_sequence_kernel/](turn_sequence_kernel/) models the boundary created by Expanded-legal extra-turn attacks such as Timeless-GX and Star Chronos. The current attack still closes the turn budget, the checked card text skips the intervening between-turn / Pokémon Checkup step, and the scheduled turn begins with reset ordinary action usage for the same player.

The sequence state retains separate budgets for both players. This prevents a player-specific quota such as Dual Brains from leaking to the opponent on an ordinary handoff, while preserving that quota when the same player receives the extra turn or later regains turn ownership.

**Working synthesis:** action history is turn-scoped and player-owned. Extra-turn effects multiply Supporter, Stadium, manual-attachment, Retreat, and attack windows because they create a new turn for the same player rather than extending the already-spent current turn.



## 32. Discard feasibility needs an exact execution witness

[discard_cost_witness/](discard_cost_witness/) shows that scalar discard capacity can prove a cost payable while several exact card-class selections still produce different hand states. A four-class hand can satisfy one three-card cost in four distinct ways. Per-class discard maxima can preserve a strategically protected card. Exact selections move hand counts to discard, reject stale choices, and conserve card totals.

**Working synthesis:** discard capacity is a useful feasibility projection; canonical execution should retain the exact card-class selection.

## 33. Compiled Item and Supporter search can execute as one conserved transaction

[trainer_search_transaction/](trainer_search_transaction/) composes exact search targets, exact discard selection, lock channels, exchangeable zone counts, and the quota-based turn budget.

Green regressions cover Secret Box, Arven, Guzma & Hala, and Larry's Skill. The played Trainer temporarily occupies a resolving zone, so another same-name copy remains a legal "other card" discard. Whole-hand discard uses the remaining hand snapshot before searched targets enter hand. Ordinary Supporter limit 1 rejects a second Arven, while limit 2 permits two uses.

**Working synthesis:** a committed connector action needs explicit resolution state and exact target/cost witnesses rather than only its low-dimensional optimization projection.



## 34. Hidden-zone correlation now spans observer belief, material truth, and Prize-taking timing

[observer_top_prize_beliefs/](observer_top_prize_beliefs/) extends the Arc Phone-style top/Prize joint belief to multiple observers. In its toy policy, the actor privately sees X and swaps; an opponent who knows that X swaps with probability 1 and Y with probability 1/4 updates to 80% X and 20% Y for the inserted face-down Prize. Both observers preserve the exact anti-correlation between the outgoing top card and the untouched Prize.

[top_prize_physical_bridge/](top_prize_physical_bridge/) binds those observer posteriors to one exact material state. The top card and ordered Prize slots are materialized `CardInstance` objects, the swap conserves those same instances, and every observer posterior must keep positive support on the exact physical world. The actor's private top observation is derived from that physical world.

[prize_joint_position_removal/](prize_joint_position_removal/) shows that taking one correlated Prize can reveal information about another hidden zone. In the A/B toy branch, privately observing B leave the untouched Prize slot makes the actor certain that the hidden deck top is A, while an opponent who sees only the Prize count change remains at 50/50.

[prize_pending_take/](prize_pending_take/) adds an explicit `prize_pending` timing state before hand entry. Selected physical Prize instances leave the Prize topology, the taking player receives the appropriate private identity observation, and pending cards resolve one at a time to hand or another legal destination. This preserves before-hand effects that can route a taken Prize directly into play without an artificial hand intermediate.

**Working synthesis:** hidden-zone state needs an exact material world plus observer-relative joint beliefs. Prize taking also needs a timing boundary between learning a previously face-down identity and its final destination.


## 35. Prize-taking precedes replacement-Active policy in conserved physical state

[promotion_pending_prize_information/](promotion_pending_prize_information/) fills the missing physical interval after Knock Out disposal and before replacement Active selection.

The new `PromotionPendingState` permits surviving former Bench Pokémon to remain in play with no chosen Active while preserving the same physical `IdentityLedger`. It composes that state with the existing `prize_pending` queue and observer-relative Prize beliefs, then opens promotion only after the Prize window closes and an external game-resolution decision says play continues.

The regression disposes both Knocked Out Active Pokémon first, moves a face-down Prize through `prize_pending`, privately reveals that Prize to the taker, resolves the same physical instance to hand, and only then permits the next-turn player to choose a replacement Active. The second player chooses after observing the first promotion. Per-class card totals remain conserved throughout.

A toy decision witness makes the sequencing consequence explicit: when two equally likely Prize observations favor different replacement choices, a fixed pre-observation choice reaches 50% utility while an observation-conditioned choice reaches 100%. Those values describe the toy policy objective, not match win rate.

**Working synthesis:** replacement-Active selection is an information-sensitive phase boundary. A stable-board representation that requires an Active at every intermediate instant can either retain a Knocked Out Active too long or commit a replacement before rules-visible Prize information exists.

## 36. Selected E-31 Prize effects now execute as physical Bench-entry transitions

[prize_before_hand_bench_entry/](prize_before_hand_bench_entry/) turns two cataloged `before_hand_prize_trigger` cards into executable transitions over the canonical Prize-pending and promotion-pending state.

The implementation covers Chansey's Lucky Bonus (`sv3pt5-113`) and Jirachi Prism Star's Wish Upon a Star (`sm7-97`). The pending face-down Prize instance itself moves into `in_play`, receives a board-object binding, and becomes a real `BoardPokemon` without passing through hand. Extra Prizes are staged at the front of the existing pending queue, so Jirachi can take a Chansey that immediately becomes the next E-31 event.

The regression also mirrors an official Japanese Q&A boundary: after a self-KO with five surviving Benched Pokémon, the Bench remains full during the Prize window, so a Chansey Prize cannot use Lucky Bonus even though the later replacement-Active promotion would open a slot.

A second witness begins with no surviving Pokémon after Active disposal and shows that a pending Chansey can physically create a new future promotion candidate. The result intentionally leaves the separate terminal-precedence question to the game-resolution layer.

**Working synthesis:** before-hand Prize text is an executable hidden-zone phase, and some effects can change board geometry or recursively create more Prize work before promotion becomes legal.

## 37. Recursive additional Prize-taking preserves observer asymmetry

[prize_pending_observer_extra/](prize_pending_observer_extra/) extends the pending-Prize queue across effects that take another face-down Prize before the current pending window has finished.

The adapter moves the selected exact Prize instance to the front of `prize_pending` and updates every observer's joint top/Prize belief at the same transition. The taker privately learns the additional Prize identity; an uninformed opponent observes only the public Prize-position removal.

In the regression's two-world correlation witness, Player B taking an exact Switch as the additional Prize makes B certain the hidden deck top is Other, while Player A remains at 50% because the Prize identity was private. The same material truth remains inside every observer's posterior support and card-class totals stay conserved.

**Working synthesis:** recursive Prize effects need one coupled material-and-information transition. Extending only the physical pending queue would preserve card conservation while silently losing observer-relative Bayesian state.

## 38. Dream Ball carries exact typed search identity directly into Bench topology

[dream_ball_typed_bench_execution/](dream_ball_typed_bench_execution/) composes the Prize-origin Dream Ball resolving state with the typed target allocator and the physical board ledger.

Two legal Pokémon targets can collapse to the same strategic one-Pokémon demand profile while retaining different exact target-cost witnesses. The executor carries that exact witness through deck depletion, instance materialization, and a new `BoardPokemon` binding. A Stage 2 Pidgeot ex witness enters play as a one-card stack with no invented prior stages and no hand intermediate.

The regression rejects a full Bench, a stale target witness whose selected Pokémon already left the deck, and a dimensionally valid non-Pokémon witness. Dream Ball itself remains in `resolving_trainer` until the secondary search has finished, then the same physical Item enters discard. Card-class totals remain conserved.

**Working synthesis:** search-demand output is a planning projection. When a searched card immediately acquires board topology, the exact target witness is the correct bridge from exchangeable deck multiplicity to materialized physical identity.

## 39. Terminal game resolution occurs after board-changing E-31 Prize effects

[post_prize_window_game_resolution/](post_prize_window_game_resolution/) resolves a timing ambiguity with an official Jirachi Prism Star ruling.

The cited Q&A starts with both players on one Prize, no Benched Pokémon, and both Active Pokémon being Knocked Out simultaneously. The attacking player takes Jirachi Prism Star as the final face-down Prize. The official ruling allows Wish Upon a Star to put Jirachi onto the Bench and declares Jirachi's owner the winner.

A terminal check taken immediately after KO disposal and final-Prize counts would see both players at zero Pokémon and zero Prizes, producing a tie under the existing loss-condition table. The correct sequence resolves the E-31 pending Prize first. Jirachi then exists in play, and the same table gives Jirachi's owner a win.

The new `resolve_after_prize_window()` adapter refuses terminal evaluation while any `prize_pending` card remains. Once the queue closes, it evaluates Prize/no-Pokémon conditions from the current physical board and advances to `TERMINAL` or `PROMOTION`.

**Working synthesis:** before-hand Prize effects belong inside the game-resolution phase. They can change the final no-Pokémon condition, so Prize counts alone are insufficient until the E-31 window has closed.

## 40. Simultaneous E-31 Prize effects expose an owner-selected order after reveal

[before_hand_prize_ordering/](before_hand_prize_ordering/) separates the physical selection of several Prize cards from the later resolution order of their before-hand effects.

The official Japanese Q&A gives a mixed Chansey plus Dream Ball two-Prize example and says the Chansey owner chooses which effect to process first. The new `PendingPrizeBatchOrder` therefore opens an explicit same-award sibling choice after the Prize cards have been staged. It does not treat physical Prize position or pre-reveal selection order as the effect order.

Nested additional Prize work remains a barrier. If the chosen sibling takes another Prize, that new pending card stays ahead of unresolved siblings from the original award. The regression rejects an attempt to move Dream Ball past such a nested Prize, then permits Dream Ball once the nested card has finished.

**Working synthesis:** simultaneous hidden-zone selection and effect ordering can have different information sets. E-31 policy should reveal the awarded cards first, expose owner-controlled ordering among same-award effects, and preserve stack-like priority for nested Prize work.

## 41. Dream Ball exposes a large Evolution-Ability topology-bypass surface

[dream_ball_evolution_ability_catalog/](dream_ball_evolution_ability_catalog/) audits effectively legal Evolution-Pokémon Ability text for explicit source and board-position constraints.

Across 1,539 exact Evolution-Pokémon Ability rows, 1,175 have geometry compatible with direct Dream Ball Bench entry: 1,152 general in-play rows and 23 Bench-required rows. The compatible set contains 570 turn-action Abilities, 563 passive/continuous rows, and 42 triggered rows. These are candidate counts rather than claims that every remaining Ability condition is satisfied.

Pidgeot ex Quick Search is a compatible turn-action witness; Vileplume Irritating Pollen is a compatible passive witness. Team Rocket's Crobat ex Biting Spree is the counterexample because it explicitly requires play from hand to evolve.

**Working synthesis:** Dream Ball is more than a one-Pokémon search edge. For Evolution Pokémon it can bypass prerequisite stages and ordinary evolution timing, so downstream evaluation needs the selected target's Ability geometry rather than only search reachability.

## 42. A Prize-origin Dream Ball can establish Vileplume lock without locking the next Prize-origin Dream Ball

[dream_ball_vileplume_lock_line/](dream_ball_vileplume_lock_line/) composes two pending Dream Balls with Vileplume `xy7-3` and Pidgeot ex `sv3-164`.

The first Dream Ball puts Stage 2 Vileplume directly into play. Irritating Pollen then blocks Item play from hand. The second Dream Ball remains legal because its source is `prize_pending`, which is outside that explicit hand scope, so it can still put Pidgeot ex directly onto the Bench. Both searched Pokémon skip hand and card-class totals remain conserved.

**Working synthesis:** lock channels need source-zone predicates. A scalar `item_play=False` would erase a legal E-31 line and misrepresent a lock that is explicitly scoped to Items played from hand.

## 43. Final-Prize Dream Ball can change the terminal result before promotion

[dream_ball_terminal_rescue/](dream_ball_terminal_rescue/) applies the official Jirachi-established E-31 phase boundary to Dream Ball.

With both players at zero remaining Prizes and zero Pokémon after the KO batch, declining the pending Dream Ball and letting it enter hand closes the Prize window as a tie. Using Dream Ball to put Pidgeot ex onto the empty board changes the post-E-31 terminal snapshot to one Pokémon versus zero, producing a win for the Dream Ball player. Promotion is never reached because terminal resolution happens first.

**Working synthesis:** E-31 cards can have discrete terminal value. Terminal evaluation must consume the board produced by the finished Prize window rather than an earlier zero-Pokémon snapshot.

## 44. Dream Ball lock access splits into direct, prerequisite-gated, and position-gated cases

[dream_ball_lock_bypass_catalog/](dream_ball_lock_bypass_catalog/) cross-references exact Evolution-Pokémon lock Abilities with Dream Ball entry geometry.

There are 50 exact Evolution lock rows in the audited pool, of which 22 are compatible with direct Dream Ball Bench placement. Eleven have no extra activation prerequisite recognized by the lock taxonomy, ten still require a Pokémon Tool, and one requires a Stadium. Vileplume Irritating Pollen and Alolan Muk Power of Alchemy are direct passive witnesses; Garbodor Garbotoxin still needs a Tool; Galarian Weezing Neutralizing Gas remains Active-gated and is excluded from the Dream Ball-compatible set.

**Working synthesis:** lock reachability is not lock establishment. An AMR-aware connector model should preserve target position and activation prerequisites after the search edge is found.

## 45. Dream Ball into Alolan Muk creates a large symmetric Basic-Ability deadline

[alolan_muk_basic_ability_surface/](alolan_muk_basic_ability_surface/) audits the effectively legal Basic-Pokémon Ability surface removed by Power of Alchemy.

The current pool contains 1,103 exact legal Basic-Pokémon Ability rows across 420 unique card names. Of those, 123 exact rows across 48 names use hand-to-Bench trigger wording. Named examples include Tapu Lele-GX Wonder Tag, Dedenne-GX Dedechange, and Crobat V Dark Asset.

Because Power of Alchemy removes Abilities from Basic Pokémon in play, hand, and discard on both sides, Dream Ball into Alolan Muk creates a sequencing boundary for the opponent and for the Dream Ball player. Support that has not been consumed before Muk can lose its Ability line immediately.

**Working synthesis:** direct lock establishment can carry large self-denial costs. Lock value should be evaluated against the controller's remaining Ability-dependent support, not only the opponent's engine.

## 46. Owner-selected E-31 ordering can allocate the final Bench slot

[e31_bench_slot_ordering/](e31_bench_slot_ordering/) composes the official Chansey + Dream Ball sibling-order choice with one remaining Bench slot.

Choosing Chansey first puts Chansey into play, fills the Bench, and leaves Dream Ball to enter hand with its Vileplume target still in deck. Choosing Dream Ball first puts Vileplume directly into the final slot, discards Dream Ball after resolution, and forces Chansey to enter hand because Lucky Bonus is no longer usable. Both branches conserve the same physical cards.

**Working synthesis:** simultaneous Prize-effect order is an information-aware resource-allocation decision. Arbitrary queue order can produce the wrong legal board when sibling effects compete for Bench capacity or another constrained channel.


## 47. Full deck search preserves Prize/top correlation after shuffle

[deck_search_shuffle_belief/](deck_search_shuffle_belief/) closes the belief-layer gap left by the physical deck-search/shuffle topology. For each possible Prize state, the new top card is sampled from the remaining deck counts conditional on that state. The searching player first conditions on the exact Prize composition learned from full deck inspection; other observers retain their prior unless a separate public observation gives them information.

A five-card labeled regression exhaustively checks all 60 ordered Prize/Prize/top branches. With one A, two B, and two filler cards, a searcher who learns that A is Prized updates the post-shuffle top to A=0, B=2/3, filler=1/3, while an uninformed observer remains at A=1/5, B=2/5, filler=2/5. The uninformed joint state also keeps the singleton exclusion exactly: A cannot simultaneously occupy a Prize slot and the new deck top.

**Working synthesis:** K1 changes future draw distributions as well as line choice. Hidden-zone planners should carry the joint Prize/top distribution through a shuffle rather than resampling a top marginal independently of Prize composition.



## 48. Physical deck-search/shuffle state now derives K1 and preserves observer truth support

[deck_search_shuffle_physical_belief/](deck_search_shuffle_physical_belief/) composes the search/shuffle belief transition with the exact identity ledger. The bridge derives the searching player's exact grouped Prize composition from materialized Prize instances, derives the current deck-plus-Prize pool from physical zones, materializes one exact sampled post-shuffle top, and requires every observer posterior to retain positive support on that exact world.

In the five-card regression, the material world has A plus filler Prized and both B copies plus filler in deck. The bridge derives A=1 and B=0 as the actor's K1 Prize composition, derives pool counts A=1 and B=2, and materializes B as the exact shuffled top. The actor assigns B top probability 2/3 while the uninformed observer assigns 2/5. Both remain consistent with top=B and Prizes=(A, filler), and per-class card totals are conserved. An attempted A top is rejected independently by the physical ledger because the singleton A is Prized.

**Working synthesis:** exact physical truth can serve as the conditioning source for K1 while observer-relative beliefs remain separate. Hidden-state transitions should validate both material conservation and posterior support for the material world.



## 49. Revealed deck-search targets can leak K1 Prize information

[deck_search_target_signal/](deck_search_target_signal/) treats a publicly revealed target chosen after full deck inspection as Bayesian evidence about the searcher's private Prize information. The target-selection policy is conditioned on grouped Prize composition, other observers update on the observed target, the searched copy leaves the deck-plus-Prize pool, and the shuffled-top distribution is then derived from each observer's posterior.

A six-card labeled regression uses singleton A, singleton targets X and Y, and three fillers. Under a deterministic policy that prefers X when A is Prized and prefers Y when A is unprized, observing X leaves 42 exact ordered Prize/Prize/top branches. The opponent updates to P(A Prized)=4/7 and gets post-shuffle top probabilities A=1/7, Y=1/7, filler=5/7. In an exact actor world with A Prized, the actor's K1 top distribution is A=0, Y=1/3, filler=2/3. An incoherent policy that reveals singleton X from states where X is Prized is rejected by pool conservation.

**Working synthesis:** public actions selected after private deck inspection can leak hidden-zone information through policy. K1 should therefore update the searcher's belief state and may also change an opponent's posterior when the search outcome is observable.



## 50. Same-line reacquisition creates transient payload discardability

[reacquisition_discardability/](reacquisition_discardability/) refines temporal discard replenishment at exact card-class resolution.

In the concrete Secret Box into Guzma & Hala branch, a TM: Evolution or Artazon retrieved by Secret Box can pay Guzma & Hala's later two-card discard when another copy remains searchable. Guzma & Hala then restores that same required payload while also finding Jet Energy. For the core TM + Artazon + Jet endpoint, one reacquisition channel lowers minimum pre-Box filler stock from four cards to three. When Tag Call is also an independent downstream requirement, both TM and Artazon must be replaceable to keep the three-card floor.

A 200,000-state seeded Aichi probe found that 23,665 of 27,552 raw Secret Box-access states, 85.8921%, still had both deck copies of at least one of TM: Evolution or Artazon before Secret Box searched. This is a sufficient structural condition for the exact discard-and-reacquire witness.

**Working synthesis:** discardability can be copy-local and transient. An endpoint-required card class can supply discard material when a later legal search restores the requirement before its deadline. Temporal planners therefore need exact generated identities, retention requirements, and reacquisition availability in addition to scalar resource production.


## 51. Exact physical target movement preserves revealed-search signaling

[deck_search_target_signal_physical/](deck_search_target_signal_physical/) binds the public target-signal posterior to exact card movement. In the six-card witness, A plus filler are materially Prized, X is the revealed searched target, and Y is materialized as one exact shuffled-top branch. X becomes a stable hand instance, Y becomes `deck_top`, the actor retains P(top=Y)=1/3, and the opponent's target-conditioned posterior gives P(top=Y)=1/7. Both observers keep positive support on top=Y and Prizes=(A, filler), and all card-class totals are conserved.

The bridge independently derives K1 composition and pre-search pool counts from the exact ledger, then verifies that the physical target movement removes exactly the same group/count assumed by the belief update. A search attempt for a materially Prized singleton is rejected by the physical deck state.

**Working synthesis:** a public target label and a physical searched copy are distinct pieces of state that must agree. The signal changes observer knowledge, while exact zone movement determines material truth.

## 52. A one-target Trainer search can execute mechanics and hidden information atomically

[trainer_search_hidden_state_bridge/](trainer_search_hidden_state_bridge/) composes the existing atomic Trainer transaction with exact Prize truth and observer-relative search signaling. A Quick Ball regression enforces Item play permission, one exact discard, typed Basic-Pokémon target selection, the resolving-Trainer boundary, K1 Prize conditioning, public target-X signaling, exact searched-copy materialization, shuffle, and exact top materialization in one immutable transition.

In the exact world, Quick Ball and one fodder card enter discard, searched X becomes a materialized hand instance, and Y becomes the sampled shuffled top. The actor assigns P(top=Y)=1/3 while the opponent assigns 1/7 after observing target X. Item lock rejects the same transaction, the Supporter budget remains unspent, every observer retains positive support on exact truth, and card-class totals remain conserved.

**Working synthesis:** connector execution should join action legality, payment, exact target identity, information acquisition, information leakage, and shuffle consequences. A reachability edge such as "Quick Ball reaches X" omits several mechanically and strategically relevant state transitions.



## 53. Common one-target revealed searches now compile from card text

[single_output_search_profile_compiler/](single_output_search_profile_compiler/) adds a separate conservative compiler for deterministic one-card reveal-to-hand Trainer searches whose selectors are already supported by the typed target lattice. It leaves the established multi-output compiler unchanged.

The current snapshot yields **28 legal print profiles across 8 names**: Ultra Ball (13), Energy Search (4), Quick Ball (3), Team Rocket's Petrel (3), Poké Kid (2), Evolution Incense (1), Master Ball (1), and Skyla (1). Quick Ball compiles to one Basic-Pokémon output plus an exact one-card discard cost; Ultra Ball compiles across older and newer wording to one Pokémon output plus an exact two-card discard cost.

The compiler deliberately excludes coin-gated Poké Ball, disjunctive Fighting Gong, multi-output Arven, and multi-unit searches such as Earthen Vessel and Boxed Order. The Quick Ball hidden-state transaction now obtains `swsh1-179` directly from this compiler, and the integrated CI remains green.

**Working synthesis:** card-text compilation should expand through small validated semantic islands. This family now provides a traceable path from bundled text to typed target execution, exact discard payment, K1, public signaling, and shuffle state without hand-authored Quick Ball metadata.



## 54. Physical deck depletion gates transient payload reacquisition

[reacquisition_physical_bridge/](reacquisition_physical_bridge/) executes the concrete Secret Box into Guzma & Hala reacquisition witness as two canonical typed Trainer transactions over one conserved zone state.

Secret Box moves the first TM: Evolution from deck to hand. Guzma & Hala then discards that TM plus Tag Call and physically retrieves the second TM together with Jet Energy, leaving TM + Artazon + Jet in hand. Supporter quota is consumed and per-card-class totals remain conserved.

A one-copy counterfactual exposes the key gate. After Secret Box takes the only TM, the same abstract Guzma & Hala retrieval vector still asks for one Tool, but execution rejects the line because no TM remains in deck. A separate regression confirms that replacement availability also does not supply the second physical card required for Guzma & Hala's two-card discard.

**Working synthesis:** transient discardability requires both a live replacement route and enough physical payment material. Connector reachability alone can preserve a stale search edge after its final target copy has left the deck; canonical zone execution must gate the continuation.

## 55. Trigger-order authority currently depends on the rules source

[ko_trigger_order_authority/](ko_trigger_order_authority/) records a current rules-source divergence that affects Knock Out trigger scheduling. TPCi Professor guidance published in February 2026 says that during a turn the current player chooses the order of multiple triggered effects when a Pokémon is Knocked Out, while the Pokémon Asia Trainers Website still serves a Lost City + Reuniclus Q&A assigning that exact ordering choice to Reuniclus's owner.

The repository therefore should not treat either controller as source-independent. The new authority layer returns all applicable claims from the selected rules profile and reports the exact Lost City + Reuniclus state as unresolved when both source families are admitted. The existing physical ordered-destination resolver remains useful once a legal order has been supplied.

**Working synthesis:** rules provenance is part of simulator state when currently served authorities disagree. Timing authority, chosen effect order, and physical execution should remain separate layers.


## 56. The full transient-reacquisition matrix survives conserved Trainer execution

[reacquisition_transaction_matrix/](reacquisition_transaction_matrix/) cross-validates the provenance-aware temporal ledger against canonical Trainer transactions across all eight combinations of two endpoint profiles and four Guzma & Hala reacquisition modes.

For the TM + Artazon + Jet endpoint, the exact minimum initial filler counts are 4 with no reacquisition and 3 when TM, Artazon, or both can be restored. When Tag Call is also independently required, the minima become 5, 4, 4, and 3 respectively. Every cell exactly matches the abstract temporal ledger while enforcing physical deck counts, exact discard selections, resolving-Trainer movement, one Supporter use, and card-class conservation.

This extends the single-witness physical bridge into a complete small-family falsification test. It confirms the positive replacement cases and the negative boundaries where one live replacement channel is still insufficient because another payload must remain in hand.

**Working synthesis:** transient discardability should be derived from live replacement channels plus endpoint obligations. A current copy may be discardable even while its class remains required, but only when a conserved continuation restores that class before the deadline.


## 56. Knock Out membership can grow during the KO trigger window

[knockout_cascade_growth/](knockout_cascade_growth/) shows that the final disposal batch cannot always be known at the first KO check. A conservative legal-card audit finds 14 print rows across 11 names whose KO-trigger Ability can directly Knock Out the Attacking Pokémon or place damage counters on it after the original KO. Current Gengar ex Fainting Spell is a direct witness.

The new growable cross-player context begins with either side's pending set empty, adds later KO members idempotently while the trigger window is open, and only then materializes the existing fixed `PendingKnockOutBatch` objects for promotion and conserved disposal. A regression starts with one defending Active pending, adds the Attacking Active on a Fainting Spell-like heads branch, then disposes both while conserving both players' physical-card totals.

**Working synthesis:** atomic KO disposal does not imply fixed KO membership. Trigger execution must be allowed to enlarge the pending set before the batch is frozen.


## 57. Discard legality can be derived from future replacement continuations

[continuation_aware_discard_policy/](continuation_aware_discard_policy/) turns transient payload discardability into an executable policy seam. It enumerates exact current discard witnesses, runs caller-supplied legal continuations, retains only branches that satisfy the endpoint, and applies DCI-style scoring only after that future-feasibility filter.

In the three-filler Secret Box state, the policy is given every legal Guzma & Hala retrieval rather than a chosen reacquisition mode. With replacement TM and Artazon both still in deck, Tag Call + TM, Tag Call + Artazon, and TM + Artazon are all future-feasible for the TM + Artazon + Jet endpoint. With only TM replaceable, only Tag Call + TM survives. With only Artazon replaceable, only Tag Call + Artazon survives. With neither replacement available, no two-card discard can preserve the endpoint. If Tag Call is also required, both replacement channels are needed and only TM + Artazon is safe.

An illustrative DCI ranking then prefers Tag Call + TM among the already-safe witnesses. Removing the replacement TM removes that witness before scoring.

**Working synthesis:** discardability is a continuation property. Current-hand value, endpoint obligations, live replacement copies, deadlines, and connector availability jointly determine whether a copy can be spent. Scalar DCI is safest as a ranking objective over continuation-valid exact witnesses.



## 58. Canonical Trainer execution can carry causal provenance without expanding the physical state

[trainer_transaction_provenance/](trainer_transaction_provenance/) synchronizes the canonical Trainer-search transaction state with an origin-labeled resource ledger. Each searched card receives hand-arrival provenance such as `0:Secret Box`, exact discard witnesses preserve that provenance, and forgetting origins must reproduce the canonical post-transaction zone counts exactly.

In the concrete Secret Box into Guzma & Hala line, the TM retrieved by Secret Box later appears in discard with origin `0:Secret Box`, while the replacement TM in hand has origin `1:Guzma & Hala`. A second regression puts an initial TM and a Secret-Box-retrieved TM in the same hand. The physical transaction “discard one TM” has two valid provenance witnesses, yet both project to the same physical post-state.

**Working synthesis:** provenance is valuable for causal resource-flow auditing, while exchangeable same-class provenance histories can usually be quotiented for mechanical continuation. Keeping a compact canonical state plus an optional synchronized provenance layer avoids forcing historical identity into ordinary game-state execution.


## 58. A live replacement edge can still fail under Supporter contention

[replacement_connector_contention/](replacement_connector_contention/) adds a bounded breadth-first planner over validated immutable transitions and uses it to test replacement-aware discard safety under shared Supporter bandwidth.

After discarding a current TM: Evolution, Arven can individually restore TM and Colress's Tenacity can individually find Jet Energy. Under the ordinary one-Supporter limit, the joint TM + Jet endpoint is unreachable because either Supporter consumes the only action window. The continuation-aware policy therefore rejects the TM discard even though both missing resources have true individual access paths.

Raising the Supporter limit to two makes the TM discard safe. Keeping the ordinary limit while adding Guzma & Hala also makes it safe because one paid multi-axis Supporter retrieves both TM and Jet in the same action.

**Working synthesis:** replacement reachability must be joint, deadline-aware, and resource-constrained. Independent access edges can falsely certify a discard when the restoration routes compete for the same Supporter window; multi-axis connectors can be valuable specifically because they compress several obligations into one scarce action.


## 59. UnifiedState can own the per-turn action budget canonically

[canonical_turn_budget_owner/](canonical_turn_budget_owner/) advances the staged turn-budget migration by giving `UnifiedState` an optional authoritative `TurnActionBudget`. Legacy-only states still project their Supporter, Stadium, manual-Energy, and turn-ended booleans as before. Once an explicit budget is present, migrated UnifiedState actions query and consume the integer budget instead of trusting those booleans.

Magnezone `bw8-46` / Dual Brains supplies the decisive counterexample. After one Supporter in a two-Supporter turn, `BenchState.supporter_used` is already true while the canonical state has `supporter_plays_used = 1`, `supporter_play_limit = 2`, and one legal Supporter use remaining. The regression deliberately keeps the stale boolean true and confirms Gladion can still consume the second use. It also verifies live suppression and restoration of Dual Brains changes the limit without erasing usage history.

The same ownership rule now gates modeled manual Energy attachment, Stadium play, Item/Tool/Bench-entry turn boundaries, and a physical Retreat adapter. A synthetic two-Retreat quota proves the composite adapter can execute two exact Retreat transitions even after the legacy `BoardState.retreat_used` bit becomes true; the ordinary base limit still permits only one.

**Working synthesis:** integer turn bandwidth now has a canonical owner for the migrated composite path. Legacy booleans are compatibility projections, not sufficient execution state once quotas can exceed one or live effects can change their limits.


## 59. Prize uncertainty turns replacement-aware discard safety into a belief-weighted quantity

[belief_weighted_replacement_safety/](belief_weighted_replacement_safety/) evaluates each exact discard witness across every grouped Prize-composition world and weights the mass of worlds where a conserved continuation restores the endpoint.

With one replacement TM: Evolution in a 53-card unknown pool and six Prize cards, discarding the current TM is safe in exactly 47/53 worlds, 88.679245283%, because Arven can restore it precisely when the replacement is unprized. Discarding ordinary fodder remains 100% safe. After K1, the TM discard collapses to safety 1 when the replacement is known unprized and 0 when it is known Prized.

With two replacement copies, the TM discard fails only when both are Prized, raising K0 safety to 98.911465893%.

**Working synthesis:** continuation-aware discardability has a world-conditional legality layer and a belief-level risk layer. K1 can change the safe-discard witness family even when the visible hand is unchanged. Redundant replacement copies reduce catastrophic Prize risk but do not eliminate it.


## 57. KO-trigger cascades are deferred until the active effect completes

[knockout_trigger_deferral/](knockout_trigger_deferral/) combines the 2025/2026 non-interruption ruling with growable KO membership. A concrete Gastly `sm10-67` and Gengar ex `me55-90` witness starts with only Gengar ex pending, resolves Fainting Spell heads to add the Attacking Gastly to the KO set, and records Gastly's Swelling Spite as newly triggered. Swelling Spite cannot start while Fainting Spell remains active; it becomes ready only after Fainting Spell's final modeled step completes.

The new `TriggerDeferralState` keeps ready effects unordered, so choosing among simultaneous triggers remains upstream in the effect-order authority layer. After the cascade completes, the grown two-player KO membership is frozen into the existing fixed-batch promotion and disposal protocol, preserving physical-card totals.

**Working synthesis:** trigger scheduling needs both dynamic readiness and a non-interruptible active effect. Newly triggered work can enlarge future state while the current effect still owns the execution window.


## Direct-to-Bench search is now compiled and physically distinct from hand search

[direct_bench_search_profile_compiler/](direct_bench_search_profile_compiler/) compiles a conservative literal family of effectively legal effects whose complete search body puts Basic Pokémon directly from the deck onto the Bench. The current snapshot contains **101 print-level profiles across 76 names**: 95 attack profiles, five Nest Ball prints, and Battle VIP Pass. The compiler preserves maximum output, explicit `up to` wording, attack cost, source action class, and Battle VIP Pass's first-turn condition while excluding nearby HP-gated, coin-gated, arbitrary-count, distinct-type, and extra-effect families.

[direct_bench_search_execution/](direct_bench_search_execution/) carries an exact selected copy into `StackBoardMaterialState`. Each selected card is removed from the physical deck count, materialized as a stable in-play instance, bound to a new Basic Pokémon board object, and checked for card-class conservation. The executor rejects stale target counts and non-Basic targets.

The capacity regression preserves the Advanced Player's Rulebook's source-sensitive C-11 boundary. A full-Bench Nest Ball cannot be used, while a full-Bench Call for Family attack resolves its search body without searching. When only one Bench slot remains, Battle VIP Pass can place one exact copy but cannot materialize two.

**Working synthesis:** `deck -> hand` and `deck -> Bench` are different connector destinations. Direct placement spends Bench capacity immediately and carries action-class-specific legality, so a card-text compiler or reachability graph should preserve destination, current board capacity, and source action class before claiming executable access.


## 60. Turn scheduling can use UnifiedState-owned budgets without duplicating them

[canonical_turn_sequence_owner/](canonical_turn_sequence_owner/) separates turn-order metadata from per-player action history. `TurnScheduleState` stores only the current player, other player, queued-extra-turn flag, and checkup-skip flag; each player's explicit `UnifiedState.turn_budget` remains the sole action-budget owner.

A regression spends Supporter, Stadium, manual Energy, and Retreat bandwidth for Player A under a two-Supporter limit, gives Player B a separate ordinary one-Supporter history, and then resolves an extra-turn boundary. A's new turn resets A's usage while retaining A's two-Supporter limit, B's untouched history remains unchanged until B actually starts a turn, and the checked extra-turn boundary skips Pokémon Checkup. Ordinary handoffs later reset only the incoming player's own budget.

The test also deliberately makes A's legacy usage booleans stale before the extra-turn attack. Scheduling still follows the canonical budget.

**Working synthesis:** turn order and turn-action bandwidth are separate state axes. A composed planner no longer needs `TurnSequenceState.budget` plus `UnifiedState.turn_budget`; schedule metadata can refer to two player states whose budgets own their own history.


## 60. K1 has measurable decision value at a continuation-aware discard deadline

[discard_information_value/](discard_information_value/) compares one fixed discard under a Prize belief with choosing the exact discard after perfect Prize composition is known.

In a stylized one-replacement TM example, the guaranteed fodder discard has utility 0.9 while a TM discard has utility 1 only when Arven can restore an unprized replacement. Under K0 the TM line is worth 47/53 = 0.886792453, so the best fixed choice is fodder at 0.9. If K1 is acquired first, the player chooses TM in the 47/53 unprized worlds and fodder in the 6/53 Prized worlds, giving value 0.988679245. Gross value of exact information at this deadline is therefore 0.088679245 in the model's utility units.

With two replacement copies, K0 already prefers the TM discard because recovery succeeds in 98.911465893% of worlds. Exact information still catches the rare double-Prized state, but its marginal value falls to about 0.009796807.

**Working synthesis:** information value is decision-specific. K1 is valuable when different Prize worlds prefer different exact continuation-aware discard witnesses; redundant recovery can both increase line reliability and reduce the marginal value of inspection.


## 61. Live Supporter quota can be derived from exact physical board state

[board_action_quota_derivation/](board_action_quota_derivation/) connects the canonical turn budget to exact in-play source identity. `BoardPokemon` now optionally records a Pokémon print ID and effective Ability activity, allowing the quota layer to recognize Dual Brains only on the legal Magnezone print `bw8-46`.

After one Supporter has been played, an active Dual Brains source yields limit 2 and leaves one use. Suppressing that physical object's Abilities reduces the live limit to 1 without erasing usage; restoring the Ability reopens the second use; removing the source from play removes the grant. A different Magnezone print does not create the quota, and two active Dual Brains sources still establish a ceiling of two.

**Working synthesis:** quota limits should be derived from physical source identity and current effect activity, while the canonical turn budget preserves usage history. Ability suppression, source removal, quota exhaustion, and Supporter lock are distinct state transitions.

## 62. Garbotoxin can suppress board-derived quota through a recomputable overlay

[garbotoxin_quota_suppression/](garbotoxin_quota_suppression/) connects one verified Ability-lock family to the physical quota derivation. The overlay recognizes the four legal Garbotoxin prints, requires the source Garbodor to have a Tool attached, and returns suppressed board-object IDs without overwriting the base board.

With one Supporter already used, opposing Garbotoxin reduces Dual Brains from limit 2 to 1. Stealthy Hood on Magnezone prevents the opposing Ability effect and restores limit 2. Jamming Tower then blanks Hood's effect while leaving the Tool physically attached, so Garbotoxin suppresses Dual Brains again. A same-side Garbotoxin suppresses the player's other Pokémon despite Hood because Hood is opponent-specific.

**Working synthesis:** suppression dependencies are best represented as derived overlays over physical attachment/effect state. This lets locks disappear and be recomputed without destroying the target's unsuppressed Ability state, while preserving the Tool-attachment versus Tool-effect distinction required by Garbotoxin and Jamming Tower.

## 63. Continuous Ability locks require source and target geometry before dependency resolution

[single_source_ability_lock_geometry/](single_source_ability_lock_geometry/) generalizes the suppression overlay to five verified source families while deliberately evaluating one live source at a time. Profiles preserve exact print families, activation geometry, owner scope, target tags, target position, exemptions, and Stealthy Hood protection.

For Dual Brains, active Wobbuffet suppresses a non-Psychic Magnezone but exempts a Psychic-tagged target; Galarian Weezing and Slaking require the opponent source to be Active; Slaking does not suppress its owner's Magnezone; Benched Gastrodon suppresses Magnezone only while the target is also a Benched Stage 2; Garbotoxin retains its Tool-attached geometry. Opponent-sourced locks are removed by live Stealthy Hood and restored by Jamming Tower.

**Working synthesis:** a global Ability-allowed flag loses source position, target position, owner scope, target traits, and protection. The predicate layer can be derived exactly for one source; mutually suppressing continuous sources still require a separate dependency-resolution rule rather than a naive union.

## 64. Continuous Ability-lock composition is a source-dependency problem

[ability_lock_dependency_graph/](ability_lock_dependency_graph/) composes the single-source suppression predicates into a graph whose nodes are physically live lock sources and whose edges mean one source would suppress another source.

Acyclic graphs can be resolved without pretending every candidate source remains active. Tool-attached Garbotoxin opposite Active Bide Barricade yields a one-way edge because Garbodor is Psychic and therefore exempt from Wobbuffet's effect; Garbotoxin remains active and suppresses Wobbuffet.

Active Neutralizing Gas opposite Active Slaking/Lazy yields a two-source cycle because each source suppresses the other's Pokémon. The resolver marks that component unresolved and produces no final suppression overlay. Stealthy Hood on Weezing removes the incoming Lazy edge and resolves the graph; Jamming Tower blanks Hood and recreates the cycle.

**Working synthesis:** continuous lock composition requires source-dependency resolution between the predicate layer and the final target overlay. Acyclic components can be solved; cyclic components should remain explicit until timing/history semantics are supported by stronger authority rather than being assigned an arbitrary fixed point.

## 65. Taken-Prize destination replacements expose a per-card chooser decision

[prize_destination_override_conflicts/](prize_destination_override_conflicts/) inserts an explicit replacement-resolution stage between the existing `prize_pending` event and final physical movement. The bundled legal card pool supplies a concrete overlap: Barbaracle `swsh11-107` / Lost Block redirects the opponent's taken Prizes to the Lost Zone, while Billowing Smoke `swsh3-158` redirects Prizes from its holder's attack Knock Out to discard.

An official Japanese Pokémon Card Q&A resolves this exact pair. The Prize-taking opponent chooses which effect to process first; Lost Block first sends the Prize to the Lost Zone, while Billowing Smoke first sends it to discard. A second official ruling for a two-Prize Pokémon V Knock Out allows that player to inspect the two Prize cards and choose Lost Zone or discard separately for each card.

The regression therefore keeps a conflicting pending Prize physically unmoved until the rules-backed choice is supplied, then executes the selected destination while preserving card-class totals. It also resolves a two-Prize award to one discard and one Lost Zone card, proving that the decision granularity is the exact pending Prize rather than one global ordering choice for the award.

**Working synthesis:** replacement effects belong between the underlying event and the final conserved move. The ordinary destination, applicable replacements, chooser authority, per-card choice, and physical destination are separate state variables. Card-specific authority should resolve a documented interaction without being generalized automatically to every replacement conflict.


## 66. Unrestricted search execution separates physical selection from useful output

[unrestricted_search_zone_execution/](unrestricted_search_zone_execution/) carries the rulebook-backed exact-count search law into conserved `ZoneCountState` transitions without weakening the repository's constrained-search invariant.

A Computer Search-style witness selects one fallback card from a nonempty deck while supplying zero useful strategic units. A Mallow-style exact-two witness selects two physical cards while only one satisfies the represented demand. Per-class totals remain conserved in both cases.

For ordered top-deck destinations, the same selected multiset can produce the same aggregate zone counts with two different `top_order` values. Desired-first and filler-first Mallow branches are therefore distinct continuation states even though ordinary card conservation cannot distinguish them.

**Working synthesis:** card-text cardinality, physical selected-card witness, useful demand output, and destination topology are separate search-state dimensions. Constrained searches can identify some of them safely; unrestricted fixed-count search can force them apart.

## 67. Mandatory unrestricted-search filler changes later draw-to-N bandwidth

[forced_search_draw_bandwidth/](forced_search_draw_bandwidth/) composes the exact-count search rule with a hand-size-sensitive draw effect.

In a seven-card Computer Search -> Crobat V witness, playing Computer Search and discarding two cards drops the hand to four, the mandatory fallback restores it to five, and playing Crobat V leaves four cards before Dark Asset. Dark Asset therefore draws two to reach six. A useful-output-only model that treats the unavailable intended target as a zero-card search leaves three cards before Dark Asset and incorrectly predicts three draws.

Across modeled initial hand sizes 4 through 9, the omission overstates Dark Asset by exactly one card; at initial size 10 both branches are already at the draw ceiling and the error disappears.

**Working synthesis:** connector payment and search resolution can push draw bandwidth in opposite directions. Costs shrink the hand while mandatory filler refills it. Continuation value for draw-to-N effects should read the physical post-action hand state rather than infer draw volume from scalar connector cost or strategically useful output alone.

## 68. Prize-destination replacement applicability crosses the Knock Out boundary

[prize_destination_applicability/](prize_destination_applicability/) distinguishes the lifetime of Lost Block from the trigger snapshot used by Billowing Smoke.

An official Japanese Pokémon Card Q&A says that when Barbaracle itself is Knocked Out, Lost Block no longer redirects the opponent's Prize because Barbaracle leaves play before Prize taking. The adapter therefore derives Lost Block from surviving post-KO board objects. Billowing Smoke is derived from the removed Pokémon's Tool snapshot, requires its Tool effect to have been live, and requires the Knock Out to come from opponent attack damage.

The regression covers a surviving Barbaracle plus Smoke conflict, Barbaracle itself being Knocked Out with Smoke, suppressed Lost Block, blanked Smoke, and a non-attack-damage Knock Out. Its CI is green.

**Working synthesis:** replacement applicability can cross an event boundary asymmetrically. Continuous effects need their source to survive to the later destination event, while triggered replacements can depend on a pre-disposal source snapshot.


## 69. Before-hand Prize effects require an actual hand-bound destination

[prize_before_hand_destination_gate/](prize_before_hand_destination_gate/) adds a planned destination to the shared Prize-origin E-31 executor before cards such as Chansey, Treasure Energy, or Dream Ball may resolve their "before you put it into your hand" text.

Official Japanese Q&A witnesses show Treasure Energy cannot attach under Lost Block or Billowing Smoke, and Chansey cannot use Lucky Bonus under Billowing Smoke. The executor now rejects those triggers when the planned destination is discard or Lost Zone. If the trigger is declined, the same exact pending card moves directly to that replacement destination.

The regression compiles the repository's real profiles for Chansey, Treasure Energy, and Dream Ball, checks redirected and ordinary hand-bound branches, and preserves exact physical card totals. The focused CI and the existing before-hand execution suite both pass.

**Working synthesis:** Prize identity observation can precede destination resolution, while E-31-style effects require the resolved destination to remain hand. The correct chain is Prize selection, private identity observation, destination replacement resolution, eligible before-hand effects, then final movement.


## 68. Private unrestricted-search targets require observer-specific deck composition

[private_search_target_belief/](private_search_target_belief/) models the information geometry of arbitrary-card search that puts a selected card into hand without revealing its identity.

A five-card exact enumeration with one Prize, one uniformly private searched card, and one shuffled top produces 60 labeled branches. The analytic belief kernel matches every collapsed top/Prize probability. Under uniform private selection, the opponent retains top marginals A=1/5, B=1/5, filler=3/5 and unchanged Prize marginals. In the exact world where the Prize is filler and the actor privately selected A, the actor instead has next-top A=0, B=1/3, filler=2/3.

A second policy that privately prefers A whenever searchable leaves the opponent's Prize marginal unchanged while shifting the next-top marginal to A=0, B=1/5, filler=4/5.

**Working synthesis:** a shared exact post-search deck composition is valid only when removed target identity is public or jointly known. Private unrestricted search needs actor-specific exact target removal and policy-marginalized target removal for other observers. Public target signaling and private target removal are separate Bayesian transitions.

## 70. Public redirected Prize cards can restore hidden correlations

[pending_prize_public_reveal_belief/](pending_prize_public_reveal_belief/) preserves a removed Prize identity as a latent variable until its destination visibility is known.

The official Pokémon glossary says discard-pile cards are face up and inspectable, and Lost Zone cards are face up; Japanese Q&A confirms an opponent's Lost Zone cards can be checked. The existing observer-removal primitive is therefore too lossy for a Prize that begins privately observed by the taker and later enters one of those public zones.

In the Arc Phone correlation witness, privately taking B leaves the opponent at P(top=A)=1/2. If that same pending B enters hidden hand, the opponent correctly stays at 1/2. If Billowing Smoke or Lost Block routes B to a public destination, conditioning on the newly public B raises the opponent to P(top=A)=1. Immediate marginalization cannot recover that update.

**Working synthesis:** a card leaving a hidden physical zone does not automatically end its information-state relevance. Latent identity should survive until the destination determines who can observe the card, especially when that identity remains correlated with top-deck or remaining-Prize state.


## 69. Exact private search target can coexist with observer-marginalized beliefs

[private_search_target_physical/](private_search_target_physical/) binds the private-target belief kernel to exact physical card movement.

In a six-card world, exact physical truth has A plus filler Prized, X privately selected into hand, and Y as the sampled shuffled top. The actor, who knows both K1 and the private target, assigns P(top=Y)=1/3. The opponent, who knows only that a uniform private selection occurred, assigns P(top=Y)=1/6. Both posteriors retain positive support on exact truth top=Y, Prizes=(A, filler), and per-class card totals are conserved.

The bridge also rejects a branch that tries to privately select singleton A while the exact ledger places A in Prize.

**Working synthesis:** exact physical identity and observer-relative knowledge can diverge safely. A simulator may materialize one shared private hand instance as truth while exposing that identity only through observer-specific belief transitions. Public revealed search, private arbitrary search, and K1 are therefore distinct composition layers.

## 70. Computer Search now executes as one private-information transaction

[computer_search_private_transaction/](computer_search_private_transaction/) composes the bundled Computer Search effect across Item permission, resolving-card state, exact two-card discard payment, private unrestricted target selection, K1, observer-specific beliefs, shuffled-top materialization, and card conservation.

In the exact regression, Computer Search plus two specified fodder cards begin in hand while A + filler are Prized and X, Y + two fillers remain searchable. The transaction pays both discards, privately selects X, samples Y as the shuffled top, then moves Computer Search to discard. The actor assigns P(top=Y)=1/3 while the observer assigns 1/6 under uniform hidden target selection. Item lock rejects the action, one-card payment is rejected, and an already-spent Supporter use is unchanged.

**Working synthesis:** unrestricted private search needs an action-level transaction distinct from selector-limited typed search. One play can jointly change action state, hand/discard material, private deck knowledge, observer beliefs, exact target identity, and shuffled-top topology while preserving one shared physical world.

## 71. Materialized hand instances must contribute to canonical hand size

[materialized_hand_size_continuation/](materialized_hand_size_continuation/) closes a projection gap between aggregate zone counts and exact physical identity.

After the atomic Computer Search transaction, Crobat V remains exchangeable in hand while the privately searched X exists as a materialized hand instance. Physical hand size is 2 although the exchangeable hand count is 1. After Crobat V is materialized from hand into play, physical hand size is 1 and exchangeable hand count is 0. A draw-to-six continuation therefore draws 5; an exchangeable-only projection incorrectly predicts 6.

The new physical_zone_count helper derives zone cardinality from exchangeable counts plus materialized instances.

**Working synthesis:** materialization changes representation while the card can remain in the same game zone. Hand size, deck size, discard size, Lost Zone size, and other physical zone metrics must project across both identity layers whenever materialized instances can occupy those zones.

## 72. Multi-Prize pending identities remain observer-relative until each card resolves

[pending_prize_batch_identity_belief/](pending_prize_batch_identity_belief/) extends latent pending-Prize identity to simultaneous multi-card awards. Exact pending instance IDs key observer-relative latent groups, and each card can be revealed or kept private independently as its destination resolves.

The Arc Phone witness shows reveal order can change intermediate posteriors: revealing B first immediately makes the opponent certain top=A; revealing X first leaves P(top=A)=1/2 until B is later exposed. If B enters hidden hand and only X becomes public, the opponent finishes at 1/2.

**Working synthesis:** a simultaneous Prize award creates a vector of latent identities rather than one anonymous removed-card event. Per-card destination visibility must condition the matching latent variable while preserving correlations among unresolved siblings and hidden state.


## 73. Physical pending Prize order and observer beliefs can share exact instance IDs

[prize_pending_batch_observer/](prize_pending_batch_observer/) couples conserved physical Prize instances, sibling-order choice, latent observer identities, and destination visibility.

The exact regression stages physical X and B together, lets B resolve to public discard before X reaches public Lost Zone, and keeps the opponent posterior synchronized with those movements. A hidden-hand counterfactual preserves the opponent's uncertainty. A nested extension then prepends an additional Prize C, rejects attempts to move an older sibling across that barrier, and conditions the opponent only when C becomes public.

[nested_prize_observer_barrier/](nested_prize_observer_barrier/) contains the nested regression. All corresponding CI workflows are green.

**Working synthesis:** physical queue order and information-state queue order should use the same stable pending-instance key. This prevents a simulator from reordering one layer without the other, and it gives nested Prize effects one shared barrier for both mechanics and information.


## 72. Materialized deck top must contribute to physical deck size

[materialized_deck_size_projection/](materialized_deck_size_projection/) establishes the deck-side counterpart to canonical physical hand counting.

After the atomic Computer Search line, exact Y is represented as deck_top while two fillers remain exchangeable in deck. The aggregate deck zone reports 2 cards; physical deck size is 3 because the materialized top remains part of the deck. Drawing exact Y moves that instance to hand and reduces physical deck size to 2 while the aggregate deck count remains unchanged at 2.

**Working synthesis:** deck_top is a relation on a deck card rather than a separate card population. Deck-out checks, remaining-deck denominators, draw counts, and deck-size-sensitive effects need a canonical projection that includes active top relations until they are consumed or collapsed.

## Reusable infrastructure

The top-level [../tools/](../tools/) directory contains deterministic analyzers, catalog builders, exact combinatorial models, and state-transition kernels supporting these results. Many result directories contain a local `reproduce.py` that checks the corresponding claims against the bundled resources.

Particularly foundational components include:

- `build_expanded_legality_baseline.py`
- `release_legality.py`
- `card_identity.py`
- `typed_access_network.py`
- `typed_energy_access.py`
- `trainer_search_materialization.py`
- `direct_bench_search_profile_compiler.py`
- `direct_bench_search_execution.py`
- `energy_action_budget.py`
- `turn_action_budget.py`
- `legacy_turn_budget_bridge.py`
- `canonical_turn_budget_owner.py`
- `action_quota_effects.py`
- `board_action_quota_derivation.py`
- `garbotoxin_suppression.py`
- `single_source_ability_lock_geometry.py`
- `ability_lock_dependency_graph.py`
- `turn_sequence_kernel.py`
- `canonical_turn_sequence_owner.py`
- `bench_capacity_model.py`
- `lock_effect_catalog.py`
- `prize_belief_decision.py`
- `observer_top_prize_beliefs.py`
- `top_prize_physical_bridge.py`
- `prize_joint_position_removal.py`
- `prize_pending_take.py`
- `pending_prize_identity_belief.py`
- `prize_pending_batch_observer.py`
- `pending_prize_batch_identity_belief.py`
- `prize_destination_applicability.py`\n- `prize_destination_overrides.py`
- `post_prize_window_game_resolution.py`
- `unified_state_kernel.py`
- `multicopy_zone_state.py`
- `board_object_kernel.py`
- `energy_board_conservation.py`
- `identity_materialization.py`
- `card_class_namespace.py`
- `temporal_resource_ledger.py`
- `continuation_discard_policy.py`
- `bounded_state_planner.py`
- `belief_weighted_discard_policy.py`
- `belief_discard_decision.py`
- connector-capacity and contention models under `tools/connector_*.py`

## Open synthesis questions

Several larger questions remain promising:

1. **General conservation across unified state layers.** The repository now has conserved materialization paths for Energy, evolution stacks, Tools, movement, simultaneous Knock Outs, zone-routing recovery, cross-player promotion ordering, post-KO terminal resolution, and physical Prize taking with the taker's belief update. The next shared-kernel problems are competing replacement effects, opponent-specific Prize knowledge, and migrating the now-explicit turn budget into canonical composite ownership.
2. **Compiler from card text to transitions.** A validated semantic island now compiles multi-output Trainer deck-search text through typed physical-target feasibility. The larger open problem is extending the same auditable approach to more wording families and then materializing successful compiled actions into canonical zone / instance state without guessing ambiguous semantics.
3. **Policy evaluation across turns.** Many exact results analyze one action window or one narrow line. A multi-turn policy model could quantify when short-term access sacrifices later connector, Bench, Prize, or Supporter value.
4. **Evidence-bearing legality composition.** Print-specific errata, historical reprint evidence, region-aware semantic sources, and the audited 30th Celebration product anchor now exist as separate layers. The next legality problem is composing exact print identity, functional-reprint evidence, regional availability, product/promo release dates, bans, and card-specific restrictions into one queryable provenance object without collapsing those evidence types.
5. **Empirical archetype validation.** ALS modeling has one strong concrete case. More published Expanded lists could test which archetypes are well described by narrow lines and which are better modeled as flexible resource policies.

## Methodological caution

Counts and probabilities in this map are summaries of their linked result directories. Consult the detailed result before reusing a number or assumption. Simulations and abstractions are evidence about the modeled state space, not automatic claims about full-match win rate or universal deck strength.


## 67. Position-changing effects need chooser and target geometry

[position_effect_profile_compiler/](position_effect_profile_compiler/) compiles a conservative literal family of effectively legal switch, forced-switch, and gust text into executable position-effect profiles. The bundled English snapshot yields **318 print-level profiles across 192 names**: 17 Trainer self-switch profiles, 2 Trainer opponent-chosen forced switches, 29 Trainer targeted gusts, 169 attack self-switches, 71 attack forced switches, and 30 attack targeted gusts. The attack self-switch family preserves mandatory versus optional movement and exact heads gates.

The profile preserves action class, attack metadata, simple Trainer play conditions, chooser authority, and the physical object receiving the effect. The executor then delegates the actual Active/Bench swap to the conserved board-object kernel.

The rulebook-backed distinction is strategically material. An attack that switches out the opponent's Active applies its switching effect to that old Active, while an attack that gusts a selected Benched Pokémon applies its effect to the selected Bench target. The regression demonstrates that an effect-immunity overlay can therefore block Bayleef's Push Down and Clefairy's Follow Me in opposite geometries even though both successful transitions are board swaps.

**Working synthesis:** position access is not just a reachability edge. Opponent-chosen force-out and actor-chosen gust expose different reachable state sets and different immunity targets; planners should preserve chooser authority and effect target before treating two movement effects as substitutable. Current card text must also be applied before compilation: three legal Black & White Pokémon Catcher records in the bundled snapshot still contain the pre-errata unconditional switch text, while the current official erratum requires a heads coin flip. The compiler now normalizes those records and refuses execution without an explicit heads result.


## 68. Two-sided pivot effects form a dependent movement program

[compound_position_effects/](compound_position_effects/) compiles **19 legal clean-text profiles across 10 names** whose move body first switches the attacking Pokémon and only afterward forces the opponent to switch. Twelve use `If you do`; seven use the older `Then` construction.

The executor preserves the E-20 dependency. If the first self-switch cannot occur, the second movement is skipped. If the first succeeds while the second is impossible or blocked, the first movement remains. This produces a directional dependency that two independent graph edges cannot represent.

Two apparent additional records are left uncompiled because the bundled English text contains obvious-looking typos (`xyp-XY122` “The,” and `me55-20` “oppoennt”). The compiler leaves those uncertain rather than silently repairing source data.

**Working synthesis:** compound card text should compile to ordered, gated transition programs. For movement, reachability depends on both printed order and whether earlier effects actually occurred.


## Position-changing Abilities require activation geometry

[position_ability_profiles/](position_ability_profiles/) compiles a conservative pure-movement Ability island with **52 legal print-level profiles across 23 card names**: 22 self-switch profiles, 17 actor-chosen targeted gusts, and 13 opponent-chosen force-outs.

The profiles preserve source position, chooser authority, and activation timing. Keldeo-EX's Rush In can promote only its own Benched source object, Solgaleo-GX's Ultra Road can choose any Benched replacement, Umbreon VMAX's Dark Signal requires the hand-evolution event, and Tornadus's Sudden Cyclone requires hand-to-Bench entry. Event-triggered profiles cannot execute unless the caller explicitly supplies a satisfied trigger, and Ability lock remains an execution gate.

The supporting Ability classifier was also corrected so a leading event clause retains control even when prefixed by "Once during your turn." Across 1,539 exact legal Evolution-Ability rows, 28 rows move from the turn-action class to the triggered class; among 1,175 Dream Ball geometry-compatible rows, 11 move to triggered. Geometry itself is unchanged.

**Working synthesis:** movement access depends on effect semantics, source geometry, event history, and lock state. A planner that exposes every in-play movement Ability as a free edge overstates realistic access and can invent illegal lines.


## Source-authorized Knock Out ordering now reaches physical execution

[ko_redirection_authorized_order/](ko_redirection_authorized_order/) composes the source-scoped authority catalog with concrete player roles and the existing order-sensitive Knock Out destination resolver.

For Lost City plus a return-to-hand KO effect, TPCi February 2026 guidance and current Japan/Asia card-specific Q&A can identify different abstract chooser roles. The bridge blocks routing when those roles instantiate to different players. When the current player is also the Knocked Out Pokémon's owner, the claims collapse to the same concrete chooser and execution is safe without deciding which abstract source rule has precedence.

The conserved evolution-stack regression confirms both authorized physical branches: Lost City first sends the complete Pokémon stack to the Lost Zone, while the return effect first sends the stack to hand. Invalid effect orders, missing role context, unauthorized submitters, and source conflicts are rejected before physical mutation. Pull-request CI run 37586706221 passed.

**Working synthesis:** rules-source selection, concrete chooser resolution, chosen effect order, and physical destination execution should remain separate layers. Source disagreement only needs to halt a simulator when it changes the concrete player's control of the decision.

## State-dependent Prize utility requires acquired-set state

[prize_terminal_utility_policy/](prize_terminal_utility_policy/) extends the finite-horizon physical Prize planner with utility evaluated from the set of targets acquired by a deadline. In an exact three-state posterior over A, B, C, and filler, a fixed additive proxy with A=5, B=5, C=6 chooses slot 2, while the acquired-set objective of 10 for completing A+B plus 6 for C chooses slot 3. The terminal values by first slot are (6, 22/3, 6, 26/3), so the additive first choice loses 8/3 utility units under the actual objective.

**Working synthesis:** positional value-of-information depends on resource history as well as the hidden-zone posterior. ALS prerequisites, fallback lines, and finite deadlines can require a non-additive terminal objective; fixed per-card values can select the wrong first information-gathering action.

## Prize-position deadlines can force immediate coverage

[prize_position_deadlines/](prize_position_deadlines/) adds per-target acquisition deadlines to the physical Prize belief-state planner. In a four-state posterior over A, B, C, and filler, relaxed deadlines give first-slot success values (3/4, 1, 1/2, 3/4), so the information-rich slot 1 guarantees all three targets. Making only A due on the current probe changes the values to (1/2, 0, 1/4, 1/4): slot 1 becomes impossible because it can never contain A, the optimum shifts to slot 0, and success falls from 100% to 50%.

**Working synthesis:** hidden-zone information value is deadline-sensitive. Physical-position beliefs and strategic target deadlines must be carried together; a raw count of remaining probes can overvalue an information-gathering action whose prerequisite expires before that information can be converted into access.

## Prized Supporter access can miss the execution window

[prize_supporter_execution/](prize_supporter_execution/) bridges physical Prize access to the canonical turn-action budget. For a known Prized Supporter among six unknown positions, Arc Phone -> Trekking Shoes has 1/6 hand-access and same-turn execution probability. Peonia -> Arc Phone -> Trekking Shoes raises hand access to 2/3, yet ordinary same-turn Supporter execution is 0 because Peonia has consumed the one-Supporter channel. Gladion reaches the known Prized target with probability 1 but likewise has ordinary same-turn execution probability 0. Dual Brains changes those execution probabilities to 2/3 and 1 respectively, while Neutralizing Gas removes the board-derived extra quota and makes the Item-only line best again. A next-turn execution deadline resets ordinary Supporter usage, making Gladion's recovered target fully executable on the following turn under the stated persistence assumptions.

**Working synthesis:** card access and executable access are distinct state variables. A connector can improve hidden-zone recovery while consuming the exact action quota required by its payload; quota-changing board effects can reverse that line evaluation without changing the Prize posterior.

## Regidrago delayed double-KO windows are state-dependent

[regidrago_timeless_phantom_state_windows/](regidrago_timeless_phantom_state_windows/) generalizes the Timeless-GX -> Phantom Dive line beyond undamaged printed HP. If the first target has prior damage D_A, resolved Timeless damage T, and later receives K damage-counter value, its delayed-KO condition is D_A + T < HP_A <= D_A + T + K. The second Active target is in range when HP_B <= D_B + P for prior damage D_B and resolved Phantom Dive damage P. Attack-effect immunity remains a separate gate because Phantom Dive's Bench counters are an effect rather than attack damage.

Concrete baseline bands show how prior chip damage opens the line against larger attackers: Iron Thorns ex at 230 HP needs 20-70 prior damage as the first target, Regidrago VSTAR at 280 needs 70-120, and Shadow Rider Calyrex VMAX at 320 needs 110-160. The full executor exhaustively matches the closed-form thresholds across multiple prior-damage and damage-modifier families.

**Working synthesis:** target-selection value depends on live damage state and on the channel by which later damage is delivered. Printed HP alone is an insufficient range classifier for multi-attack ALSes that mix ordinary damage with effect-placed counters.

## K0 discard costs can leak future Prize information into search planning

[k0_discard_reacquisition_bias/](k0_discard_reacquisition_bias/) isolates the information boundary created by discard-before-search connectors. In a first-turn 52-card unknown deck-plus-Prize pool with six Prizes, two endpoint-critical discard candidates, one replacement copy for each, and a forced choice to discard one of them, a fixed K0 policy succeeds with 88.461538% probability. A K1 or information-privileged chooser succeeds with 98.868778%, a local 10.407240 percentage-point gap.

The regression also constructs two Aichi Secret Box states with the same K0-observable hand and opposite hidden replacement Prize placements. The existing `aichi_vileplume_secret_box._core_possible` recursion succeeds in both because it receives exact post-Prize deck counts while choosing the pre-search Secret Box payment. Fixing one discard choice before exposing the hidden deck makes that choice fail in one of the two states.

This is a policy-information audit rather than a deck-level correction. Later Guzma & Hala decisions can already be K1 when an earlier Tag Call or Secret Box has inspected the full deck, while Jirachi's Stellar Wish creates partial information that needs a richer observer-belief treatment.

**Working synthesis:** exact physical hidden state and legal policy information must remain separate. A search simulator can use sampled Prize truth for transitions, while any pre-inspection action choice must be shared across hidden worlds that are observationally equivalent to the player.

## Aichi first-Secret-Box payment is robust to K0 policy restriction in the clean subset

[aichi_secret_box_k0_policy/](aichi_secret_box_k0_policy/) forces the first represented Secret Box payment to be one choice across all hidden Prize worlds sharing the same visible opening and draw. In 50,000 accepted Aichi states, 1,265 qualified as clean first-Box states. Across 333 compressed observations, the exact hidden-Prize integration found zero observation with an oracle advantage. Conditional core success was 96.734882613% under both the hidden-state oracle and the best K0-consistent payment policy.

**Working synthesis:** a transition can contain a real information leak without that privilege affecting a particular state distribution. Payment slack can make one observation-consistent discard witness work in every hidden world that the oracle can rescue.


## Aichi direct Guzma & Hala has visible payment slack

[aichi_gnh_k0_policy/](aichi_gnh_k0_policy/) audits the direct two-card Guzma & Hala payment before full deck inspection. In 1,082 clean states from 10,000 seeded accepted starts, exact six-Prize integration finds zero oracle advantage across every sampled observation for all seven established Aichi endpoints.

[discard_information_slack/](discard_information_slack/) explains the boundary. When the paid G&H branch is needed, at most four of the six remaining hand cards must be preserved for the richest endpoint, leaving two cards that can always cover the cost. The earlier Secret Box counterexample has only two safe cards for a three-card payment, forcing one of two critical candidates and creating the 10.407240 percentage-point local information gap.

**Working synthesis:** belief-sensitive discard policy becomes necessary only after visible payment slack is exhausted and a genuine choice among critical candidates remains.

## Cost-before-search discard timing is a reusable Expanded card-pool surface

[cost_before_search_catalog/](cost_before_search_catalog/) conservatively scans legal paper-Expanded Trainer text for an explicit hand discard before the first printed deck search. It finds 54 legal prints across 16 names and 23 gameplay fingerprints. Fourteen names have selective or typed-selective payments, while Peony and Larry's Skill discard the whole hand.

**Working synthesis:** K0/K1 policy constraints belong in shared search infrastructure rather than only in one Aichi simulator. Exact hidden Prize truth may be carried by the state, while selective payment policy must be restricted to information available before the search inspection.


## Replacement multiplicity suppresses the value of exact Prize information

[replacement_information_value/](replacement_information_value/) generalizes the discard/reacquisition information model to arbitrary replacement-copy counts. In a 52-card unknown pool with six Prizes and two discard candidates, the K1 advantage for choosing one critical discard falls from 10.407240 percentage points with one replacement copy per class to 1.125681 points with two copies and 0.090493 points with three copies.

**Working synthesis:** reacquirability is quantitative. Copy multiplicity, Prize uncertainty, the number of forced critical discards, and the actor's information state jointly determine discard safety.

## Effect-based evolution has separate first-turn timing

[effect_evolution_timing/](effect_evolution_timing/) separates ordinary A-05 evolution timing from C-12 effect-based evolution timing. A conservative literal scan finds **115 print-level direct-evolution profiles across 53 card names**. On the player's first-turn axis, 76 profiles rely on C-12's default permission, nine state an explicit permission, and 30 block the window. On the target-entry-turn axis, the split is 76 default, 10 explicit, and 29 blocked. Phantump's Spiteful Evolution is a concrete asymmetric case: it blocks first-turn Ability use while retaining C-12's default entry-turn permission on later turns.

The source action remains a separate gate. Eevee's Energy Evolution can have a structural first-turn window for either player, Salvatore's Supporter source ordinarily narrows the window to the player going second, Technical Machine: Evolution inherits attack timing, and Precocious Evolution explicitly opens the attack window even when going first.

**Working synthesis:** evolution transitions should preserve their origin. Ordinary evolution uses A-05 timing. Effect-based evolution uses C-12 plus card-text overrides, then composes with the source action's own timing and resource gates. A global first-turn evolution boolean loses legal lines and can also invent illegal source-action access.

## Full-state Raichu backup rescue exposes latent redundancy

[raichu_backup_rescue_full_state/](raichu_backup_rescue_full_state/) reconnects the clean post-search backup-Gladion connector race to Harto Miki's full opening, Prize, residual-hand, and one-card Dark Asset distribution. The fixed K0 policy discards a visible Gladion to Quick Ball before the Crobat V search establishes that Alolan Raichu is Prized.

Conditional on that branch, the second Gladion is physically available in hand or deck in **90.649372%** of states. Same-turn recovery reaches **16.054113%** before Dark Asset and **20.482909%** after Dark Asset, leaving **70.166462 percentage points** of topological availability stranded beyond the modeled deadline. Forest Seal Stone is stronger than Computer Search in this narrow rescue role because searched Crobat V supplies the Tool host while Computer Search still requires two conservative disposable cards.

A new continuation mechanism also appears: Dark Asset can rescue the line by drawing an ordinary disposable card that turns an already-held Computer Search from unpayable into payable.

**Working synthesis:** copy redundancy, zone survival, timed exposure, connector readiness, and connector payment are separate layers. Random draw can improve access by changing a connector's cost state even when it does not reveal the target or connector itself.

## C-12 timing now reaches conserved physical evolution stacks

[effect_evolution_execution/](effect_evolution_execution/) carries the timing compiler into the existing board-position and physical identity layers. The executor keeps the player's first-turn gate, the target's entry-turn gate, the source action's availability, and the physical evolution-chain match as separate checks.

The regression proves that ordinary evolution still fails on the player's first turn, Eevee Energy Evolution can bypass that ordinary gate through C-12, Salvatore remains blocked when its Supporter source is unavailable, Phantump can be blocked on the first-turn axis while open on the entry-turn axis, and Rare Candy remains blocked on both axes. A materialized Eevee -> Vaporeon transition preserves the persistent Pokémon object, binds both physical cards to the same evolution stack, and conserves card-class totals.

**Working synthesis:** effect-based evolution should be compiled as a timing policy and executed against canonical physical state. C-12 can relax evolution timing without granting permission to the source action, and the two ordinary timing gates cannot safely be collapsed into one boolean.



## Reachable-state witnesses can shrink the historical Trainer semantic-review pool

[trainer_semantic_divergence/](trainer_semantic_divergence/) proves four additional same-name Trainer families non-equivalent across eight historical prints. The witnesses are deliberately state-semantic rather than text-similarity based: Apricorn Maker's historical Trainer-card target domain can reach Ball Guy while the current card is Item-only; Pokémon Fan Club sends the searched Basic to Bench instead of hand; historical Super Potion heals at most 40 damage where the current print heals 60; and historical TV Reporter remains able to change state in an empty-deck window where the current print is explicitly unplayable.

The integrated reprint resolver now records **67 known non-equivalent historical prints across 21 names**, leaving **3,974** same-name historical prints in semantic review. The positive high-confidence candidate set is **219** after the rules-grounded Trainer normalizations plus eight schema-only empty-attack-field matches.

Computer Search adds a separate rule-category boundary from Agent 1's deck-construction audit: the current Expanded print is an ACE SPEC with an explicit one-ACE-SPEC deck restriction that the two historical prints lack.

Friend Ball adds a fifth target-domain case: official Restored Pokémon rules explicitly exclude Restored Pokémon from Basic and Evolution classes while permitting generic Pokémon search. Current Friend Ball can therefore reach a legal Expanded Restored Archen that the historical wording cannot.

**Working synthesis:** historical reprint analysis should search for distinguishing reachable states across target domain, zone destination, action availability, information, timing, and material transitions. Small wording differences are important only when they induce a semantic difference under current rules.

## Harto Raichu has an exact observation-consistent Quick Ball discard rule

[raichu_k0_discard_policy/](raichu_k0_discard_policy/) compares discarding a visible Gladion with discarding a conservative disposable before Quick Ball has revealed whether Alolan Raichu is in deck or Prizes. Across **1,331** modeled visible observations, a five-clause rule using only K0 information exactly matches the observation-consistent optimum.

Always discarding Gladion gives 28.050472% same-turn Raichu access in the observable branch; always discarding a disposable gives 25.868810%. The optimal K0 rule reaches **32.988189%**, while a hidden-state oracle reaches **36.909665%**, leaving a **3.921476 percentage-point** information advantage.

The rule preserves Gladion when Forest Seal Stone is already visible or when enough discard stock remains to pay two-card connectors after spending a disposable. It instead preserves discard stock in connector-rich low-slack hands. Although the best fixed action is Gladion discard, the optimal state-dependent policy chooses a disposable in 67.568228% of branch mass.

**Working synthesis:** DCI is an observation-state policy rather than a fixed card ranking. Hidden target zone, connector availability, and residual payment stock jointly determine which visible card is cheapest to spend before a search establishes K1.



## Historical Moomoo Milk is a rules-grounded exact semantic candidate

[rule_grounded_trainer_semantics/](rule_grounded_trainer_semantics/) now also normalizes historical Moomoo Milk `hgss1-94`. Its older effect removes three damage counters for each heads, while current `sm8-185` heals 30 damage for each heads. Under current rules, one damage counter represents 10 damage and healing removes damage counters, so the two phrasings induce the same damage-state transition.

The resolver therefore promotes `hgss1-94` from semantic review to `exact_fingerprint_candidate`. With the later VS Seeker, Bill's Maintenance, and Underground Expedition normalizations, plus the independent empty-attack-field canonicalization, exact current-semantic candidates reach **133**, positive high-confidence historical candidates reach **219**, and Trainer high-confidence candidates reach **106/168**.

Bill's Maintenance adds four further exact candidates: current Supporter playability rules prevent the historical no-card-in-hand branch from creating a usable no-op Supporter, so every playable state performs the same one-card shuffle followed by a three-card draw.

Lucky Egg does not join that positive set. Official print-specific errata for `pl4-88` adds a condition that the Knocked Out Pokémon reach the discard pile before the draw applies, so it remains in semantic review.

Underground Expedition contributes two more exact candidates because all three wordings inspect the same bottom-four window, move the same required count to hand, and return the remainder to the same deck region under current numbered-choice rules.

Historical VS Seeker also converges under the same evidence standard. Its old reveal step occurs in the already-public discard pile, and both texts retrieve one Supporter into hand.

Empty optional attack fields add eight separate exact Pokémon matches by canonicalizing database schema noise only. That work is documented in [attack_empty_field_normalization/](attack_empty_field_normalization/).

**Working synthesis:** terminology changes should be normalized only when current rules give an explicit semantic bridge. This is stronger evidence than edit-distance similarity and can produce positive equivalence candidates without weakening known-negative boundaries.


## Hosted Forest Seal can convert part of Harto Raichu's oracle gap into a legal K1 line

[raichu_presearch_forest_seal/](raichu_presearch_forest_seal/) re-evaluates the exact Harto Quick Ball branch when Forest Seal Stone and a visible Crobat V host are already available before the discard payment. Star Alchemy can search deck-resident Alolan Raichu directly; if Raichu is Prized, the full-deck inspection establishes K1 and the branch's already-visible Gladion can retrieve it.

This observable line appears in **244 of 1,331** visible observations and **1.822834%** of branch probability mass. The baseline K0 policy succeeds in **85.487944%** of that hosted subbranch; Forest Seal first reaches the local endpoint in **100%** of those modeled worlds. Overall branch success rises from **32.988189%** to **33.252720%**, a **+0.264531 percentage-point** gain that recovers **6.745692%** of the prior hidden-state oracle gap. CI run `37762608113` passed.

**Working synthesis:** an oracle gap should be partitioned into truly unavailable information and value recoverable through legal sequencing. Search actions can carry information value and direct endpoint value simultaneously, so a planner should test pre-decision information-acquisition lines before treating K0/K1 loss as irreducible.


## Visible connector sequencing beats Harto Raichu's Quick-Ball-first oracle

[raichu_visible_connector_sequencing/](raichu_visible_connector_sequencing/) broadens the exact Harto branch from "Quick Ball first, optimize its payment" to other connectors already visible in the same observation. Because the branch already contains Quick Ball, Gladion, and a conservative disposable, a visible Ultra Ball or Computer Search has the fixed legal payment `Quick Ball + disposable`, preserving Gladion.

If Alolan Raichu is in deck, the stronger connector searches it directly. If Raichu is Prized, the full-deck inspection establishes K1 and the preserved Gladion retrieves it. Visible Ultra Ball or Computer Search occurs in **847 of 1,331** observations and **32.562616%** of branch mass. Replacing Quick-Ball-first with this visible direct-connector line where available raises same-turn Raichu access from **32.988189%** to **48.483601%**, a **+15.495412 percentage-point** gain. Combining the prior hosted Forest Seal line reaches **48.690299%**. CI run `37763645757` passed.

The earlier hidden-state oracle reaches **36.909665%**, so the legal direct-first policy exceeds it by **11.573936 points**. This is coherent because that oracle was constrained to Quick Ball as the first connector.

**Working synthesis:** optimize the visible action family before optimizing hidden-information policy inside one preselected action. A hidden-state oracle over a dominated connector can be weaker than a legal observation-consistent policy that chooses a stronger connector first.

## Physical copied-attack reactions preserve two conserved boards through simultaneous Knock Outs

[physical_copy_damage_reaction_bridge/](physical_copy_damage_reaction_bridge/) connects copied-attack damage on the stack-bearing physical board to the existing damaged-by-attack counter-reaction families. A Haughty Order -> Timeless-GX witness deals 150 to a 130-HP defender; Strong Bash-like reflection and a Spiky Energy-like trigger put 17 counters on the 170-HP attacker. Both Pokémon then enter pending physical Knock Out batches with their Tool and Energy still attached. The existing cross-player batch resolver orders promotions and conserves every physical card class. Prevented damage and one-sided Knock Out controls prevent accidental overgeneralization.

**Working synthesis:** the post-damage reaction barrier can preserve one physical authority for both players. Reaction-source eligibility is still supplied as input; real activation conditions, non-counter reaction bodies, Prize awards, and terminal checks belong to upstream or downstream layers.

## Optional overkill can convert a final-Prize win into a tie under damage reflection

[optional_overkill_reflection/](optional_overkill_reflection/) gives a legal English Expanded card-text witness: Cetitan ex's Crushing Press deals 140 damage or can discard a Stadium for 280. Zamazenta's prior-turn Strong Bash reflects all final damage to the Attacking Pokémon, even after a Knock Out. With Cetitan already carrying 150 damage of its 300 HP, the 140 branch leaves it at 290 HP damage and takes the final Prize for a win. The 280 branch reaches 430 damage on Cetitan, so both Actives are Knocked Out and both players take their final Prizes, producing a tie. The regression checks source prints, damage calculation, reaction counters, terminal outcomes, and all 14 ten-counter-aligned pre-damage states where choosing more damage flips attacker survival.

**Working synthesis:** optional damage magnitude interacts discontinuously with retaliation and Prize value. When the unboosted branch already KOs the target, maximizing damage can be strategically dominated because mirrored damage is based on the full damage dealt, including overkill.

## Copied attacks can retain target-specific damage provenance across multiple recipients

[physical_multitarget_damage_reactions/](physical_multitarget_damage_reactions/) extends the physical copied-attack replay with an ordered record of each damaged Pokémon, including its target index and six-step damage result. The concrete card-text witness is Electivire ex's Dual Bolt copied through Haughty Order. An Active and Bench target each receive 50 damage, while both physically carry Spiky Energy. Only the damaged Active's Spiky Energy triggers its two-counter reflection; the Bench holder's Spiky Energy cannot trigger. That reflection knocks out the already damaged attacker while the opponent's 40-HP Bench Pokémon is simultaneously knocked out. Both physical ledgers conserve card classes through cross-player disposal and promotion. The regression refuses to infer reactions when the same body event has multiple indistinguishable damage records for one target.

**Working synthesis:** the provenance key for a copied attack's damaged-by-attack reaction is the actual target record inside the executed attack body. An event name alone is insufficient when one body damages multiple Pokémon; reaction-source geometry and event-target identity must both be preserved.

## Fixed optional-damage boosts have narrow, computable retaliation frontiers

[optional_attack_damage_catalog/](optional_attack_damage_catalog/) inventories 71 effectively legal print rows in the exact optional damage-boost text family, spanning 39 distinct signatures. Of those, 61 are fixed-additive branches. [optional_boost_reflection_frontier/](optional_boost_reflection_frontier/) evaluates those branches against 130-HP Zamazenta's Strong Bash reflection with printed Weakness/Resistance. Only two signatures, four print rows, have a damage-counter-aligned state where the unboosted attack already KOs Zamazenta and survives the reflection while optional extra damage knocks out the attacker: Cetitan ex, Crushing Press (14 possible starting-damage values) and M Houndoom-EX, Inferno Fang (5 values). Houndoom's Fire attack is doubled by Zamazenta's Weakness, illustrating the importance of final damage over printed arithmetic.

**Working synthesis:** the local damage-benefit frontier depends on the entire damage pipeline and remaining attacker HP. The census enumerates abstract board states without assigning matchup frequency, line feasibility, or strategic likelihood.

## Printed damage-triggered Abilities can inflict physical Special Conditions before disposal

[physical_damage_condition_reactions/](physical_damage_condition_reactions/) complements the physical counter-reflection bridge with ordinary status backlash compiled from exact legal card prints. Roselia's Poison Point can Poison the attacker even when the 150-damage copied attack knocks Roselia out at 60 HP. Heatran's Incandescent Body supplies Burned, and an established Stage 2 Hatterene's Hazard Sensor supplies Confused. The adapter checks target provenance, printed source identity/legality, final damage, Active source position, an enabled Ability, and opposing attack origin. It reuses the typed condition state's coexistence and rotation rules while conserving all physical card identities. Suppressed Abilities, prevented damage, and an attacking Pokémon that has already moved to the Bench are explicit controls.

**Working synthesis:** post-damage reactions have heterogeneous outputs and source predicates. The same pre-Knock-Out reaction barrier supports damage counters and regular Special Conditions, provided each effect is attached to a verified physical source and attacking Pokémon identity. Rich irregular condition payloads, live lock inference, and Checkup timing remain separate models.

## Backlash can discard, return, or relocate physical Energy before the defending source leaves play

[physical_energy_backlash_reactions/](physical_energy_backlash_reactions/) compiles actual Expanded-legal Ability and Tool source texts: Turtonator Shell Spikes and Klawf ex Counterattacking Pincer discard an attacker Energy; Rugged Helmet returns one to the attacker's hand; Handheld Fan moves one to an attacker's Benched Pokémon. Each effect is bound to a unique recorded damage target and the actual attached source when applicable. The reproduced Haughty Order -> Timeless-GX attack Knocks Out 120-HP Turtonator, yet the Shell Spikes source still removes a selected Energy before Knock Out disposal. Identity-ledger conservation holds across all three actions, even when the original attacking Pokémon was moved to the Bench before the reaction. Suppressed Tool/Ability sources, missing Energy, missing destination, and invalid target choices are explicit negative tests.

**Working synthesis:** zero-HP sources remain capable of changing resource topology during the damage-reaction window. Discard, hand return, and attachment transfer alter different future connectivity edges. A deck optimizer must consider conditional retaliation beyond reflected counters and the availability of an exact recipient Bench slot.

## The defender controls noncommuting damage-triggered Energy reactions

[physical_energy_reaction_orderings/](physical_energy_reaction_orderings/) demonstrates the damaged player's rulebook E-03 choice over ordering. Turtonator's Shell Spikes and its attached Handheld Fan both trigger when a copied Timeless-GX body deals a KO. The Attacking Pokémon has a single Double Colorless Energy. Ordering Shell Spikes first discards that card, leaving nothing for Handheld Fan to move. Ordering Handheld Fan first moves it to the attacking player's Bench, leaving nothing on the Attacking Pokémon for Shell Spikes to discard. The original materialized card ends in a different zone or holder under the two legal orders, with complete card-class conservation and the same defender Knock Out.

**Working synthesis:** independent post-damage reactions can consume one another's choice sets. The damaged player's ordering authority is a decision variable in the game state. Multi-reaction simulators need sequential state transitions and source eligibility on each intermediate state, rather than summing isolated effects.


## Harto Raichu reset engines add a large post-Quick-Ball continuation

[raichu_draw_engine_fallback/](raichu_draw_engine_fallback/) splits Harto Miki's real 2 Dedenne-GX and 1 Squawkabilly ex out of the earlier collapsed setup-Basic bucket and lets Quick Ball choose among Crobat V, Dedenne-GX and Squawkabilly ex after the search establishes K1. A 5,000,000-state paired simulation, with each later engine draw integrated exactly, estimates a **+12.221472 percentage-point** later-turn gain and **+12.410005 points** on the first turn over the preceding combined visible-connector policy. Anchoring the paired increment to that policy's exact 48.690299111% baseline gives local same-turn Raichu-access estimates of **60.911771%** later and **61.100304%** on turn one. Searching Dedenne-GX contributes about **11.553599 points**, roughly 93.1% of the first-turn gain; Squawk and Seize availability adds about **0.188533 points** beyond the later-turn engine set.

The model also exposes a smaller information-only continuation: Quick Ball's deck inspection can establish K1 even when Crobat V is unavailable or strategically unused, allowing an already-visible Gladion or connector to finish the local endpoint. The result is explicitly simulation-based, preserves a seeded 5-million-state raw output and CI regression, and does not value the future cost of discarding the hand to Dedechange or Squawk and Seize.

**Working synthesis:** connector identity matters through its downstream state transition. Quick Ball reaching Crobat V, Dedenne-GX and Squawkabilly ex is not one generic "draw engine" edge. The large Dedenne contribution also makes visible reset-first sequencing the next important whole-action comparison.


## Search-before-reset can be materially free when the reset will destroy the same hand

[pre_reset_search_dominance/](pre_reset_search_dominance/) formalizes a sequencing boundary exposed by the Harto Dedenne/Squawk continuation. Current constrained deck-search rules allow Quick Ball to inspect the deck and take zero Basic Pokémon. If a legal payment and Quick Ball would both be discarded by an immediately planned Dedechange or Squawk and Seize anyway, then playing Quick Ball first, taking zero targets and resolving the reset can finish with the same unordered hand, deck, discard and Bench multisets as resetting first while adding deck-composition knowledge.

The proof harness checks held Dedenne-GX and an already-in-play Squawkabilly ex with identical fresh-draw witnesses. This weak dominance is conditional on the projection: known top-deck order, discard-timing triggers, lock changes, Bench constraints, or other intermediate-state effects can break the material equivalence.

**Working synthesis:** downstream destruction can make an upstream payment incrementally free. Search costs and DCI should therefore be evaluated against the already-planned zone transition, not as isolated card losses.


## Deck-order belief determines whether a pre-reset shuffle helps or hurts

[pre_reset_shuffle_value/](pre_reset_shuffle_value/) gives the exact first boundary condition for the search-before-reset theorem. For a singleton target known to be in an N-card deck and a planned d-card reset draw, let p be the current belief that the target lies inside those next d physical positions. Resetting without a shuffle hits with probability p; a full-deck shuffle changes that to d/N. The direct shuffle value is therefore exactly `d/N - p`.

For the Harto-sized 46-card, six-draw window, the neutral threshold is 13.043478%. A target certainly inside the next six makes the shuffle cost 86.956522 percentage points of direct exposure, while a target certainly outside that window makes the shuffle gain 13.043478 points. Knowing only that the top card is a non-target gives 5/45 = 11.111111% no-shuffle exposure, so shuffling improves the singleton hit rate by 1.932367 points.

**Working synthesis:** the material cost of Quick Ball can be incrementally free before a full-hand reset while the mandatory shuffle still has a separate deck-order information cost. Composition belief and position belief must remain distinct when prior effects make the top of deck non-exchangeable.


## K1 can create option value by letting the player cancel a destructive reset

[raichu_reset_cancel_option/](raichu_reset_cancel_option/) measures a decision node that the material-equivalence proof deliberately omitted. After Quick Ball establishes K1, a player holding Dedenne-GX or a first-turn Squawkabilly ex can decline the reset when the residual hand already reaches Alolan Raichu.

In the same 5,000,000-state Harto sample, held Dedenne remains reset-capable after Quick Ball in 11.581746% of branch states. Retaining the right to stop adds **+1.118200 percentage points** across the full later-turn branch, or **+9.654847 points** conditional on reset-capable states. On the first turn, adding Squawk expands reset-capable mass to 18.410106%; the cancel option is worth **+1.788257 points** across the branch, or **+9.713452 points** conditional on reset capability.

**Working synthesis:** information can be valuable because it changes whether a later action should occur at all. A planner that commits to a draw reset before acquiring K1 misses this cancellation option.


## Full-hand reset catalog and typed transition compiler

[full_hand_reset_catalog/](full_hand_reset_catalog/) generalizes the Harto reset phenomenon across the current paper-Expanded snapshot. The shared legality classifier finds **80 legal prints across 15 canonical effect families** with literal `Discard your hand and draw N cards` text. These include five Supporter families, six Ability families and four attack families.

[reset_transition_profiles/](reset_transition_profiles/) compiles those families into a typed state-transition layer. Five families end the turn, ten leave the fresh hand actionable in the same turn, five consume the Supporter window, one consumes VSTAR Power, one consumes the GX attack, one requires a hand-to-Bench entry, and one is explicitly top/bottom-deck position-sensitive.

[pre_reset_sequencing_synthesis/](pre_reset_sequencing_synthesis/) integrates the Harto draw-engine, doomed-resource, shuffle-value and reset-cancellation results. Its core state recommendation is to keep material zones, deck/Prize composition belief, deck-position belief, action budgets and reset commitment separate rather than collapsing them into a scalar draw or connector value.


## Beheeyem self-vacating Item-lock handoff: blind-draw baseline

[beheeyem_handoff_blind_draw/](beheeyem_handoff_blind_draw/) supplies an exact, independently reproducible finite-population model for turn-two Beheeyem `Mysterious Noise` followed by a second Active-dependent lock. In an unassisted nine-card access window, with four copies of each required component, the Stage 1 Honchkrow-GX or Galarian Weezing handoff has **0.940606%** access under the specified opening/Bench constraints; Stoutland plus Rare Candy has **0.281798%**. These are raw-draw benchmarks, not competitive consistency or win-rate estimates. The result identifies search and evolution bandwidth as important AMR costs for an otherwise mechanically legal multi-lock package.


## Renewable Beheeyem lock: recycling pipeline and Prize-collapse tradeoff

[beheeyem_lock_recycling/](beheeyem_lock_recycling/) shows a constrained mechanical repeatability result: with ordinary evolution and ideal access, two Elgyem can alternate to reuse one Beheeyem and one Triple Acceleration Energy on consecutive turns while a Float Stone-equipped lock anchor returns Active after each Mysterious Noise. One Elgyem cannot produce consecutive turn-two and turn-three attacks by ordinary evolution alone. The necessary recurring access workload remains three recycled card identities per later turn, before accounting for actual search contention. With singleton Beheeyem and singleton TAE, initial Prize configurations hide at least one of them in **19.152542%** of games without Prize access; with two of each, complete-category initial Prize collapse drops to **1.691839%**. The cycle is a perfect-access feasibility witness and leaves competitive reliability open.


## Beheeyem return-trip access: discard payment and Trainer depletion

[beheeyem_recycle_access_packet/](beheeyem_recycle_access_packet/) constructs a literal later-turn return trip using Nest Ball to Bench recycled Elgyem, Evolution Incense to retrieve Beheeyem, and Guzma & Hala to retrieve Triple Acceleration Energy by discarding two other cards. A synthetic exact hand-composition study shows how the number of independently disposable deck cards changes packet AMR. With four copies each of the three connectors and seven uniformly sampled cards, whole-packet probability rises from **0.492420%** at eight disposable deck cards to **3.939161%** at 32. Conditional on already holding one of each connector, the probability of two extra disposable cards rises from **9.048379%** to **78.165110%**. This is a sensitivity illustration, not an actual turn-three hand distribution. Even with recyclable Beheeyem and Triple Acceleration Energy, the exact three-Trainer packet can be used only four times before its own copies are depleted, absent recovery or alternate lines.


## Opponent Prize race, Counter Catcher reopening and source choice

[opponent_prize_race_gust/](opponent_prize_race_gust/) extends the bounded mixed Boss/Counter gust minimax to explicit opponent Prize-taking trajectories and terminal losses. Across 23,652 independent finite-deadline cross-checks and 6,570 first-source tests, it demonstrates a Counter Catcher window reopening after an opponent Prize and proves that the **conditional Counter-first resource exchange remains valid for arbitrary future opponent Prize trajectories**, provided Boss/Counter have identical target permissions and source-neutral execution. Conditional clocks are deliberately not treated as matchup frequencies.


## Beheeyem turn-one staging: Battle VIP Pass versus Nest Ball

[beheeyem_first_turn_staging/](beheeyem_first_turn_staging/) exactly counts opening-hand, natural-draw, and Prize uncertainty for establishing two Elgyem and one lock-anchor Basic in play by the end of the first own turn, with Elgyem required in the opening seven to start Active. With four Elgyem and four partner Basics, the unaided ready-board probability is **3.034427%**. Four Battle VIP Pass raise it to **18.483546%**, compared with **11.775394%** for four Nest Ball; both Items at four copies yield **24.168324%**. VIP's two-Basic search beats Nest Ball's one-Basic search on the immediate staging deadline, while Nest Ball retains later-turn access for the Elgyem recycler. These are precise first-turn substrate probabilities and omit full attack setup and opposition.


## Two-deadline Beheeyem setup: ranking reversal for VIP versus Nest Ball

[beheeyem_joint_staging_reserve/](beheeyem_joint_staging_reserve/) extends the first-turn Basic-staging exact model to require **both** a ready board of two Elgyem plus an anchor Basic by end of turn one **and** an unused Nest Ball in hand by turn two to retrieve the Elgyem recycled after the first Mysterious Noise. With four search-Item slots, **four Battle VIP Pass** maximizes first-turn staging at **18.483546%** but has zero access to a reserved Nest Ball, while **one VIP plus three Nest Ball** maximizes the two-deadline event at **3.181558%** (13.452432% initial staging). All five four-slot allocations were evaluated exactly with six Prizes and post-search deck depletion. This is a controlled example of a card-ranking reversal when future connector availability is included, not a full deck optimization.


## Stochastic opponent Prize tempo

[stochastic_opponent_prize_tempo/](stochastic_opponent_prize_tempo/) gives an exact rational study of Counter Catcher under random and opponent-selected Prize-taking. Across 13,140 scenarios, 24 and 7 structural boards show non-monotonic success under increased opponent scoring. An independently checked example has win probability 1 - (1-p)p². These conditional simulations are not empirical matchup win rates.
