# Pokémon TCG Expanded research map

This directory contains accumulated research on paper Pokémon TCG Expanded, Black & White onward. This page is a human-readable map of the strongest recurring findings and the detailed results that support them. It is intentionally selective rather than exhaustive.

## Current high-level picture

Across several independent investigations, the same methodological conclusion keeps recurring:

> **Theoretical access is weaker than executable access.**

A card or line can be reachable in a search graph while still failing because of connector output capacity, discardability, Supporter timing, Bench space, Energy-attachment bandwidth, target restrictions, Prize dependencies, lock geometry, or information arriving after the relevant decision deadline.

The repository therefore increasingly favors **typed, resource-constrained state transitions** over untyped card-association graphs.

[physical_state_conservation/](physical_state_conservation/) now provides a higher-level synthesis of the identity hierarchy, materialization lifetime, physical-card conservation law, Knock Out phase boundaries, destination routing, and promotion-order results developed across the state-kernel work.

## 1. Connector realism: access, payment, output capacity, and opportunity cost

The connector results formalize several distinct reasons a search route can be less useful than its graph connectivity suggests.

- [connector_domination/](connector_domination/) shows that one universal one-card search cannot satisfy two independently missing channels at once. In its Computer Search-like baseline, correcting only discard cost still leaves a material overstatement if the shared connector is allowed to repair multiple missing targets simultaneously.
- [competing_connector_policy/](competing_connector_policy/) extends that shared-resource problem across turns. In its illustrative three-turn cost-2 baseline, state-contingent allocation between Prize rescue and a setup target reaches 12.303622% joint success versus 9.848039% for the stronger single-purpose policy, showing measurable option value from retaining target choice until more state information arrives.
- [competing_connector_deadlines/](competing_connector_deadlines/) adds expiring objective windows. With rescue due by turn 4 in the same abstract cost-2 regime, moving setup's deadline from turn 4 to turn 1 lowers flexible joint success from 15.114299% to 10.758838% and shrinks flexible allocation's gain over the best single-purpose policy from 3.055764 to 1.939474 percentage points.
- [connector_output_capacity/](connector_output_capacity/) compares a cost-2, capacity-1 connector with a cost-3, capacity-2 connector. The ranking changes as the disposable-card pool changes, so connector strength depends jointly on output capacity and state-dependent discardability.
- [discard_gated_supporter_access/](discard_gated_supporter_access/) and [discard_cost_amr/](discard_cost_amr/) quantify discard costs as real access gates rather than flavor text.
- [resource_constrained_connectors/](resource_constrained_connectors/), [compound_connector_constraints/](compound_connector_constraints/), [shared_connector_contention/](shared_connector_contention/), and [multi_channel_connector/](multi_channel_connector/) extend the same principle to multiple resources and competing channels.
- [connector_option_value/](connector_option_value/), [connector_marginal_regime/](connector_marginal_regime/), and [connector_slot_marginals/](connector_slot_marginals/) study how the value of an additional connector changes with the surrounding resource regime.
- [raichu_prize_access/](raichu_prize_access/) applies those ideas to Harto Miki's 2024 Aichi Raichu/Electrode list. Under a conservative 12-card discard pool and one later random draw, its direct Alolan Raichu package reaches the singleton in 30.623976% of valid-start states. Computer Search's ability to switch from direct Raichu search to Gladion search after discovering Raichu is Prized adds 4.515319 percentage points within Raichu-Prized states, while the two-card discard gate remains the dominant modeled constraint.

- [trainer_search_profile_compiler/](trainer_search_profile_compiler/), [typed_search_target_allocator/](typed_search_target_allocator/), and [trainer_search_typed_integration/](trainer_search_typed_integration/) form a conservative card-text-to-action path for a validated multi-output Trainer search subset. The compiler emits text-level output/cost metadata, the typed allocator maps all 23 current output labels onto physical searchable-copy pools including Sabrina & Brycen's distinct-type constraint, and the state adapter carries locks, discard costs, Supporter/Stadium bandwidth, target multiplicity, and semantic target matching into the shared resource solver. One broad Trainer search can satisfy a narrower Item need when an Item target exists, while two connector copies still cannot reuse one singleton target.

**Working synthesis:** connector evaluation should preserve at least search eligibility, output multiplicity, payment costs, action-window costs, and competing uses of the same connector.

## 2. Prize cards: beliefs, cut sets, rescue timing, and information value

The Prize work has moved beyond a binary K0/K1 flag toward explicit belief states and decision timing.

- [prize_belief_states/](prize_belief_states/), [prize_belief_kernel/](prize_belief_kernel/), and [prize_belief_decision/](prize_belief_decision/) represent uncertainty over Prize compositions directly. Exact information can lose value, regain value after a hidden Prize mutation, and lose value again after re-inspection.
- [prize_dependency_cutsets/](prize_dependency_cutsets/) treats minimal correlated Prize failures as cut sets. Alternative lines can be structurally resilient while a shared singleton connector can create a size-1 failure cut.
- [prize_information_value/](prize_information_value/), [prize_information_actions/](prize_information_actions/), [partial_prize_information/](partial_prize_information/), and [prize_conditioning_layers/](prize_conditioning_layers/) separate information quantity from the action cost and timing required to obtain it.
- [prize_position_belief/](prize_position_belief/) proves that exact Prize composition can still be insufficient for position-sensitive effects. With one known target among six face-down Prizes, unknown position mapping gives a best chosen-slot hit probability of 1/6, while the same exact composition with a known target position gives certainty; an E-35 face-down shuffle preserves composition while erasing that positional advantage.
- [information_material_separation/](information_material_separation/) shows that exact Prize information and material card access are distinct outputs. A deck search can reveal the full remaining deck even if the intended downstream connector fails, while a later search can be materially important but informationally redundant.
- [prize_rescue_deadline/](prize_rescue_deadline/), [timed_prize_rescue/](timed_prize_rescue/), [prize_rescue_connector_turns/](prize_rescue_connector_turns/), and related rescue results model whether information and recovery arrive before the strategic deadline.
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

## 7. Setup is an information process as well as a legality process

The setup research models opening acceptance, optional starters, mulligans, and the public information revealed before the first normal turn.

- [setup_mulligan_policy/](setup_mulligan_policy/) studies how optional setup choices change opening and Prize priors.
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

A broader modeled planner found only a small increment outside the named route for the same core objective, supporting the usefulness of the ALS abstraction for this deck while preserving the stated simulation scope and exclusions.

## 9. Iron Thorns ex: composing access with attack readiness

[iron_thorns_integrated_als/](iron_thorns_integrated_als/) composes Item, Supporter, discard, Stadium, manual-attachment, Prize-zone, and typed-Energy constraints for the named Iron Thorns ex line rather than validating each segment independently.

The deterministic state search finds the five-action baseline:

`Tag Call -> Guzma & Hala -> Thunder Mountain + Double Colorless Energy -> play Stadium -> attach DCE -> Volt Cyclone`

and removes the line when any required action channel or searched resource is unavailable.

[iron_thorns_named_line_probability/](iron_thorns_named_line_probability/) then evaluates the narrow named route exactly against the three published 2026 Aichi Iron Thorns lists. Conditioned on a legal seven-card opening and the first draw going second, the route succeeds in **33.781505711%** of accepted starts for the one-DCE Kazuma and Kohei lists and **39.107850627%** for Ryoya's three-DCE list. These figures exclude Trainers' Mail and other broader access routes, so they are route probabilities rather than full attack probabilities.

The result is a concrete first composition of the repository's typed-access and typed-Energy layers. It also identifies Trainers' Mail as a high-value next transition because connector failure dominates the remaining narrow-route state mass.

[iron_thorns_trainers_mail/](iron_thorns_trainers_mail/) performs that next transition exactly. Recursive top-four Trainers' Mail search raises the narrow route to **38.821051379%** for Kazuma, **46.623420409%** for Ryoya, and **37.195582431%** for Kohei. The result keeps Mail's target restrictions and reshuffle behavior explicit and shows that connector density interacts with DCE payload density.

[trainers_mail_prize_belief/](trainers_mail_prize_belief/) isolates the information content of Mail misses. Starting from a missing singleton with six Prize slots and 46 deck cards, four consecutive top-four misses raise the Prize posterior from **11.5385%** to only **15.8025%**. A full deck search is qualitatively stronger because it collapses the deck-versus-Prize uncertainty and can support a precise G&H/Gladion pivot.

## 10. Legality and card identity must remain explicit

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

[reprint_errata_resolution/](reprint_errata_resolution/) adds the first authoritative normalization layer before free-form semantic review. Fifteen name-wide Trainer errata entries yield 44 additional historical candidates across 11 names, all beyond the 106 exact-fingerprint candidates. The 4,260-print same-name pool now partitions into 106 exact candidates, 44 official-errata candidates, and 4,110 semantic-review cases. Among historical Trainer prints, exact fingerprinting plus errata resolves 46 of 168 candidates.

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


## 20. Energy movement preserves physical identity until an attachment relation fails

[energy_movement_conservation/](energy_movement_conservation/) treats an ordinary Energy move between two in-play Pokémon as a topology change of one existing physical card. The same materialized instance changes holders without changing card-class totals.

[special_energy_move_conservation/](special_energy_move_conservation/) adds the restricted-Special-Energy boundary. Using Expanded-legal Double Dragon Energy as the concrete regression, a legal destination preserves the same physical instance and its two-unit representation. When the chosen destination cannot legally have that Special Energy attached, the source still loses the card, the destination does not gain it, and the same copy enters the exchangeable discard count.

**Working synthesis:** selecting a destination and successfully forming an attachment relation are distinct transition stages. Physical identity should persist through a legal topology move and dematerialize only when the card leaves board topology.


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

**Working synthesis:** KO routing needs three semantic states per physical instance: unassigned, explicitly assigned to the ordinary discard sink, and explicitly assigned elsewhere. Destination conflict detection, order-selection authority, and physical execution should remain separate layers.


## 26. Per-turn action budgets are shared mechanical state

[turn_action_budget/](turn_action_budget/) extracts Supporter, Stadium-play, manual Energy attachment, and Retreat bandwidth plus the attack / voluntary-end boundary into one immutable quota budget. Basic-rule limits default to one, while usage and current limits remain separate.

The integration review found a concrete split-state failure in the unified kernel: `BenchState.turn_ended` already blocked Bench additions and Supporter play, while several ordinary Item, Tool, manual-Energy, and Stadium actions could still be called after that boundary. Those transitions are now explicitly gated, and the unified-state regression passes in CI.

[turn_budget_integration/](turn_budget_integration/) adds a non-breaking bridge from the current split flags in `BenchState`, `UnifiedState`, and `BoardState` into one `TurnActionBudget`. The bridge round-trips ordinary one-use states back into the legacy fields and rejects modified quotas that those booleans cannot encode, providing a staged path toward canonical ownership.

**Working synthesis:** action bandwidth should have one canonical owner in composed planners. Specialized kernels can retain local compatibility fields during migration, while policy search should query and consume one shared budget.



## 27. Prize information is observer-relative and visibility-sensitive

[prize_take_information_asymmetry/](prize_take_information_asymmetry/) distinguishes the taking player's observed Prize identity from an opponent who sees only the Prize count decrease. In the five-card, two-Prize toy state, after the taker observes A, the taker assigns zero probability that A remains Prized and 1/4 that B remains; the uninformed observer still assigns 1/5 to either singleton remaining. Hidden random removal also preserves the hypergeometric family: a uniform P-card Prize subset followed by unseen random removals is distributed as a smaller uniform subset of the same pool.

[observer_prize_beliefs/](observer_prize_beliefs/) makes that asymmetry explicit by storing a separate `PrizeBelief` per observer for the same physical Prize zone and updating each posterior according to what that observer actually saw.

[prize_visibility_partition/](prize_visibility_partition/) adds a second necessary axis after face-up Prize effects. Two states can have identical exact total composition while one has singleton A face up and the other has A face down; a face-down-only effect therefore has A-target probability 0 in one state and 1 in the other. The partition keeps exact face-up counts and a belief over the remaining face-down cards.

**Working synthesis:** hidden-state knowledge belongs to observers, and Prize targetability depends on visibility as well as composition. One global composition belief can alias strategically different states.

## 28. Prize card text already supports a reusable transition vocabulary

[prize_effect_catalog/](prize_effect_catalog/) conservatively compiles 139 legal Expanded effect rows into 19 Prize transition atoms, including inspection, face-up revelation, Prize/hand/deck/discard movement, top-deck and hand swaps, direct and extra Prize taking, Prize destination overrides, shuffling, and before-hand Prize triggers.

Named regressions cover Gladion, Hisuian Heavy Ball, Peonia, Rotom Dex, Redeemable Ticket, Burst-GX, Arc Phone, Team Rocket's Bother-Bot, Lost Block, Billowing Smoke, Town Map, and several before-hand trigger cards. Arc Phone produced a useful parser correction because its wording names the top-deck referent before the switch operation.

**Working synthesis:** Prize mechanics are better represented as ordered multi-axis transition programs than card-level labels. The atom catalog is a conservative semantic island and still leaves typed selection, optionality, counts, ordering, stochastic gates, and full referent resolution for later compiler layers.


## 30. Turn-action limits can change with live board effects

[action_quota_effects/](action_quota_effects/) uses Expanded-legal Magnezone `bw8-46` as a counterexample to boolean action usage. Dual Brains permits two Supporter cards during its controller's turn, so after one Supporter the state simultaneously has `used > 0` and remaining Supporter quota.

The quota model therefore separates usage count from current limit. Active quota grants recompute limits from the basic-rule baseline, so suppressing the granting Ability after one Supporter can reduce the limit from two to one without erasing the earlier play. Restoring the Ability reopens the second use. If two Supporters were already played before suppression, the coherent historical state is `used = 2, limit = 1`, with no further use available.

**Working synthesis:** action limits belong to live board state. Play permission, quota, and usage history are separate variables, and Ability suppression can change quota without changing history.



## 29. Typed search execution must preserve the exact target witness

[typed_search_zone_transition/](typed_search_zone_transition/) closes one part of the compiler-to-state boundary by moving the exact targets chosen by a `TypedTargetAction` from exchangeable deck counts into exchangeable hand counts.

A generic one-Energy demand provides a concrete aliasing counterexample: one Basic Fire Energy and one Double Colorless Energy both produce the same demand profile `(1,)`, while the allocator retains two distinct exact actions, `target_cost=(1,0)` and `target_cost=(0,1)`. Executing those actions produces different hand states even though the strategic output vector is identical.

The bridge validates current source-zone availability and per-card-class conservation, and rejects stale exact actions after their selected target leaves the source zone. It deliberately keeps searched deck/hand copies exchangeable rather than inventing stable instance IDs.

**Working synthesis:** demand satisfaction is an evaluation projection, not a sufficient execution record. Policy search should carry the exact target-allocation witness until the chosen action has mutated canonical zone state.



## 31. Extra turns reset action bandwidth for the same player

[turn_sequence_kernel/](turn_sequence_kernel/) models the boundary created by Expanded-legal extra-turn attacks such as Timeless-GX and Star Chronos. The current attack still closes the turn budget, the checked card text skips the intervening between-turn / Pokémon Checkup step, and the scheduled turn begins with reset ordinary action usage for the same player.

The sequence state retains separate budgets for both players. This prevents a player-specific quota such as Dual Brains from leaking to the opponent on an ordinary handoff, while preserving that quota when the same player receives the extra turn or later regains turn ownership.

**Working synthesis:** action history is turn-scoped and player-owned. Extra-turn effects multiply Supporter, Stadium, manual-attachment, Retreat, and attack windows because they create a new turn for the same player rather than extending the already-spent current turn.


## Reusable infrastructure

The top-level [../tools/](../tools/) directory contains deterministic analyzers, catalog builders, exact combinatorial models, and state-transition kernels supporting these results. Many result directories contain a local `reproduce.py` that checks the corresponding claims against the bundled resources.

Particularly foundational components include:

- `build_expanded_legality_baseline.py`
- `card_identity.py`
- `typed_access_network.py`
- `typed_energy_access.py`
- `energy_action_budget.py`
- `turn_action_budget.py`
- `legacy_turn_budget_bridge.py`
- `action_quota_effects.py`
- `turn_sequence_kernel.py`
- `bench_capacity_model.py`
- `lock_effect_catalog.py`
- `prize_belief_decision.py`
- `unified_state_kernel.py`
- `multicopy_zone_state.py`
- `board_object_kernel.py`
- `energy_board_conservation.py`
- `identity_materialization.py`
- `card_class_namespace.py`
- connector-capacity and contention models under `tools/connector_*.py`

## Open synthesis questions

Several larger questions remain promising:

1. **General conservation across unified state layers.** The repository now has conserved materialization paths for Energy, evolution stacks, Tools, movement, simultaneous Knock Outs, zone-routing recovery, cross-player promotion ordering, post-KO terminal resolution, and physical Prize taking with the taker's belief update. The next shared-kernel problems are competing replacement effects, opponent-specific Prize knowledge, promotion-pending physical state, and migrating the now-explicit turn budget into canonical composite ownership.
2. **Compiler from card text to transitions.** A validated semantic island now compiles multi-output Trainer deck-search text through typed physical-target feasibility. The larger open problem is extending the same auditable approach to more wording families and then materializing successful compiled actions into canonical zone / instance state without guessing ambiguous semantics.
3. **Policy evaluation across turns.** Many exact results analyze one action window or one narrow line. A multi-turn policy model could quantify when short-term access sacrifices later connector, Bench, Prize, or Supporter value.
4. **Errata-aware reprint equivalence.** Name-wide Trainer errata now provides an authoritative layer above exact fingerprints while Copycat and Rainbow Energy remain positive and negative semantic boundary cases. The next layer should cover print-specific errata and a small auditable semantic grammar without turning same-name cards into automatic matches.
5. **Empirical archetype validation.** ALS modeling has one strong concrete case. More published Expanded lists could test which archetypes are well described by narrow lines and which are better modeled as flexible resource policies.

## Methodological caution

Counts and probabilities in this map are summaries of their linked result directories. Consult the detailed result before reusing a number or assumption. Simulations and abstractions are evidence about the modeled state space, not automatic claims about full-match win rate or universal deck strength.
