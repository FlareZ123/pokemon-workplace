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
- [temporal_resource_replenishment/](temporal_resource_replenishment/) generalizes shared-resource allocation to ordered actions that can replenish resources. A Box-like cost-3 action that produces two later discard units can feed a cost-2 downstream connector from only three units of starting stock, so feasibility depends on action order and intermediate state updates.
- [temporal_discard_replenishment/](temporal_discard_replenishment/) anchors that effect in the Aichi Vileplume Secret Box line. In its seeded 100,000-state regression, all 4,175 Secret-Box-only successes had a continuation where later Guzma & Hala discards were paid entirely by cards generated after Secret Box, separating five-card discard throughput from three-card initial discard stock in those witnessed lines.
- [prize_rescue_xtransceiver/](prize_rescue_xtransceiver/) keeps Xtransceiver's coin flip inside the exact turn-by-turn rescue transition. Four copies raise first-window conditional rescue from 20.988290% to 36.853866%, while treating those same copies as certain-hit connectors would claim 49.984029%; same-turn retry bandwidth is most valuable when the rescue deadline expires immediately.
- [literal_gladion_projection/](literal_gladion_projection/) preserves Gladion's literal self-shuffle into the Prize zone and proves a narrow projection theorem: for the isolated objective of recovering all initially critical Prizes, the literal value is exactly equal to the earlier consumed-rescuer abstraction. A labeled physical-card enumerator validates the equivalence, while the result documents the richer interactions that can break it.
- [gladion_vs_seeker_destination/](gladion_vs_seeker_destination/) quantifies why physical Gladion destination matters once VS Seeker is available; an incorrect discard transition can create extra rescue uses.
- [compressor_vs_seeker_gladion/](compressor_vs_seeker_gladion/) adds provenance-aware Battle Compressor -> VS Seeker -> Gladion access and validates the two-Item complementarity with a labeled physical-card enumerator.
- [resource_constrained_connectors/](resource_constrained_connectors/), [compound_connector_constraints/](compound_connector_constraints/), [shared_connector_contention/](shared_connector_contention/), and [multi_channel_connector/](multi_channel_connector/) extend the same principle to multiple resources and competing channels.
- [connector_option_value/](connector_option_value/), [connector_marginal_regime/](connector_marginal_regime/), and [connector_slot_marginals/](connector_slot_marginals/) study how the value of an additional connector changes with the surrounding resource regime.
- [multi_output_slot_marginals/](multi_output_slot_marginals/) shows that the capacity-one slot ordering does not generalize to Secret Box-like multi-output search. With four distinct required channels, two outs per channel, and 20 currently disposable cards, +1 disposable gains 0.341283 percentage points of exact joint access versus 0.058064 points for +1 direct out, because crossing the discard gate can activate several outputs at once.
- [raichu_prize_access/](raichu_prize_access/) applies those ideas to Harto Miki's 2024 Aichi Raichu/Electrode list. After cross-classifying Giratina as both a setup starter and a discard candidate, and materializing the mandatory Active Pokemon, its direct Alolan Raichu package reaches the singleton in 30.578700% of valid-start states after one later random draw. Computer Search's zone-adaptive Gladion fallback adds 4.502243 percentage points within Raichu-Prized states.
- [raichu_forest_seal_access/](raichu_forest_seal_access/) adds the list's Forest Seal Stone layer while preserving its Pokemon V gate. Direct-ready typed access rises to 33.139533%, while an ungated universal-search abstraction claims 40.261571%. Omitting the Crobat V prerequisite therefore overstates this narrow access objective by 7.122039 percentage points.

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

The current broader modeled planner reaches the same core in 70.7090% of a deterministic 100,000-state regression after the Active-Bunnelby correction. That remains a modest increment over the named route and preserves the usefulness of the ALS abstraction within its stated scope.

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

## Reusable infrastructure

The top-level [../tools/](../tools/) directory contains deterministic analyzers, catalog builders, exact combinatorial models, and state-transition kernels supporting these results. Many result directories contain a local `reproduce.py` that checks the corresponding claims against the bundled resources.

Particularly foundational components include:

- `build_expanded_legality_baseline.py`
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
- `prize_pending_take.py`\n- `prize_destination_overrides.py`
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
4. **Errata-aware reprint equivalence.** Name-wide Trainer errata now provides an authoritative layer above exact fingerprints while Copycat and Rainbow Energy remain positive and negative semantic boundary cases. The next layer should cover print-specific errata and a small auditable semantic grammar without turning same-name cards into automatic matches.
5. **Empirical archetype validation.** ALS modeling has one strong concrete case. More published Expanded lists could test which archetypes are well described by narrow lines and which are better modeled as flexible resource policies.

## Methodological caution

Counts and probabilities in this map are summaries of their linked result directories. Consult the detailed result before reusing a number or assumption. Simulations and abstractions are evidence about the modeled state space, not automatic claims about full-match win rate or universal deck strength.
