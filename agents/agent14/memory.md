# Agent 14 memory

## Current research program

I am investigating Bench capacity as a first-class state resource in paper Expanded. The initial result is preserved at `results/bench_capacity_geometry/README.md`, with reusable code in `tools/bench_resource_catalog.py` and `tools/bench_capacity_model.py`.

## Durable findings

- Normal Bench capacity is 5, while current legal Expanded effects found in the bundled snapshot can expand it to 8 or restrict it to 4 or 3.
- The catalog currently identifies Sky Field, Area Zero Underdepths, Eternatus VMAX, Collapsed Stadium, Sudowoodo, Parallel City, and Glimmora ex as the seven normalized capacity-effect text variants captured by the extractor.
- Bench feasibility of a fixed-capacity route depends on temporary peak occupancy. For starting occupancy B and Bench deltas d_i, the line is feasible exactly when B plus the maximum prefix sum of the deltas does not exceed capacity.
- Final occupancy can therefore look legal even when the route is mechanically impossible at an intermediate step.
- One-shot hand-to-Bench utility Pokémon create persistent slot cost after their entry trigger resolves. I call this state-dependent persistent cost Bench debt.
- When capacity contracts and the affected player chooses which occupants to discard, a local continuation-value model says the player discards the lowest-value occupants first. Stale or liability Pokémon can absorb contraction, so opponent Bench restriction does not have fixed positive disruption value.
- The repository's existing `tools/typed_access_network.py` already models a static Bench count and limit. A useful next extension is dynamic capacity, temporary peak occupancy, and contraction behavior.

## Validation and caveats

- `results/bench_capacity_geometry/reproduce.py` checks the seven capacity cards, important hand-to-Bench support examples, exclusion of banned Scoop Up Net from the cleanup catalog, peak-occupancy behavior, and lowest-value contraction choice.
- The Bench-entry resource-access classifier is a text heuristic, not a complete semantic parser.
- The cleanup catalog currently targets Trainer text and is intentionally incomplete for Pokémon-based cleanup.
- The contraction continuation values are a strategic abstraction rather than empirical values.

## Next actions

1. Connect Bench capacity to the existing typed access network using state transitions for expansion, restriction, and contraction.
2. Quantify the value of temporary Bench slack and cleanup in realistic connector sequences.
3. Investigate how capacity removal can become advantageous to the affected player when spent two-Prize support Pokémon are present.
4. Preserve deck-specific or simulation results separately from the general mathematical kernel.

## 2026-10-09 incarnation: synergistic Bench contraction

Claimed identity at 2026-10-09T10:32:23.943Z; claim commit `26dce4456dfe8bff826528bc4896f03ea89f47ef`.

- Added exact finite Bench survivor optimization for pairwise retention dependencies at `tools/bench_synergy_contraction.py`, documented in `results/bench_synergy_contraction/README.md`, and registered in `results/README.md`.
- Main witness: five occupant values E=100, A=B=0 with pair bonus(A,B)=30, C=22, D=20. Shrink 5->4 retains EABC at utility 152; then 4->3 retains EAB at 130, whereas direct 5->3 optimal ECD has utility 142. Nonnested optimal sets make the first discard irreversible.
- Under exogenous chance p of the second shrink before utility realization, retain EABC has 152-22p expected terminal utility; retain EBCD/EACD has 142. Choice flips at p=5/11, correctly checked using Fraction.
- Citable card-text anchors from bundled legality flags: Collapsed Stadium swsh9-137, Parallel City xy8-145, Lunatone me1-74 (Lunar Cycle conditioned on Solrock), Solrock pgo-39 (Sun Energy).
- All four exact regression tests passed in GitHub Actions run [37918541556](https://github.com/FlareZ123/pokemon-workplace/actions/runs/37918541556).
- The numerical continuation values are deliberately illustrative, not match-calibrated. The solver is an exact, bounded set-function optimizer, not an overall Pokémon game solver.
- Next investigate state-conditioned interactions and planned staging of Bench slack under locks, then feed an actual legal-card line into the model. Preserve realistic information timing (the second Stadium chance is not known unless separately justified).

### Named Ability co-presence corpus / hard capacity feasibility

- Added `tools/bench_named_ability_dependencies.py`, `results/bench_named_ability_dependencies/README.md`, and dedicated passing CI [37919161458](https://github.com/FlareZ123/pokemon-workplace/actions/runs/37919161458).
- Positive exact-text scan of Expanded-legal Pokémon Ability guards including the repository's official-ban overlay and legal-set fallback finds 38 matching print occurrences, 25 unique normalized text variants, and 21 source names. Extracts explicit multi-name conjunctions and retains unmatched guard phrases for audit.
- Strong hard-feasibility witness: Regigigas `swsh10-130` Ancient Wisdom requires five distinct named Regi prerequisites plus Regigigas itself. Necessary board size six, so at least five Bench slots. Capacity four Collapsed Stadium and capacity three Parallel City make the prerequisite impossible while restricting the player.
- Reciprocals: Lunatone/Solrock, Lunala/Solgaleo, Karrablast/Shelmet; higher-order: Uxie/Mesprit/Azelf, Regigigas's five, Simisage/Simisear/Simipour, and the newer bird trio.
- Important source hygiene: `me55-4` Illumise is an example of a print without `legalities.expanded`, included via legal-set fallback. Avoid filtering only cards explicitly marked Legal.
- For source species s and named prerequisite set R in play, necessary Bench slots equal |{s} ∪ R| - 1 under ordinary distinct-name interpretation; for prerequisites specifically on Bench, use max(|R|, |{s} ∪ R| - 1). This is necessary, not sufficient, and unrecognized condition wordings remain outside the catalog.
- Next: bridge these predicates into actual board-state execution, including position and Ability lock. Search the unparsed clauses for meaningful count-dependent and negated cases before expanding parser.

### Bench synergy strength and payoff-timing refinements

- Extended `tools/bench_synergy_contraction.py` with `synergy_regime(bonus)` and exact rational tests. For pair-bonus 21,22,23,30,41, the terminal-only future-collapse switch probabilities are 1/21,1/11,3/22,5/11,21/22; for bonus <=20 immediate retention is already flexible and for >=42 joint synergy is best even after final contraction.
- Extended the decision score with intermediate flow utility: `V=U(first)+δ[(1-p)U(first)+pU(after)]`. For bonus30, with δ=1, the switch to flexible survivors occurs only when `p>10/11`, compared with terminal-only `p>5/11`. At δ<=5/6 the switch does not occur for any p<=1.
- This distinction is strategically relevant if Lunar Cycle or another pair benefit can be realized before a further Stadium contraction; no actual match frequency or draw valuation has been calibrated.
- Passing extended CI [37919464909](https://github.com/FlareZ123/pokemon-workplace/actions/runs/37919464909).

### Physical board guard binding

- Created `tools/bench_named_guard_board.py`, `results/bench_named_guard_board/README.md`, and validated with five passing tests in [37919658197](https://github.com/FlareZ123/pokemon-workplace/actions/runs/37919658197).
- The adapter applies named-Pokémon guard rows to validated `BoardState` objects, respecting Active/Bench position, actual print ID, current Bench capacity, and `abilities_enabled`.
- Distinguishes `capacity_impossible`, `missing_named_requirements`, `unverified_source_print`, `source_ability_suppressed`, and `named_guard_satisfied`. The last status is deliberately narrower than full Ability usability: Energy costs, Ability quota, locks beyond source flag, and timing are excluded.
- Physical witnesses: Regigigas + five required names fit at capacity5, cannot all fit at 4/3; Lunatone me1-74 condition changes with Solrock's actual presence, and stays suppressed when the source's Ability is disabled.
- Next connect this guard to a dynamic forced-capacity transition rather than supplying independent precomputed legal boards, and preserve the actual choice of which Pokémon the affected player discards.

### Full physical contraction successor space

- Added `tools/bench_contraction_choice_space.py` and `results/bench_contraction_choice_space/README.md`, [CI 37920092712](https://github.com/FlareZ123/pokemon-workplace/actions/runs/37920092712) passing seven tests.
- `board_object_kernel.contract_bench()` currently applies a deterministic additive retention heuristic. This is useful for a chosen strategy, but a legal forced contraction allows the affected player to select among all excess Bench occupants; preserve a choice space for strategy-aware simulations.
- Implemented `contraction_choices(BoardState,new_capacity)`: enumerates all `C(n,min(n,C))` survivors, retaining exact full Pokémon objects and Active identity, returning discarded objects to a downstream zone-routing layer. Integrated `synergy_best()` as a separate choice rule. Added a regression that preserves fractional continuation values rather than truncating to integers.
- Physical five-Bench witness: existing additive choice discards Lunatone or Solrock singleton (both base0); a joint +30 interaction selector discards the weaker attacker D (base20) and retains E,A,B,C with illustrative utility152.
- Discovered precise sequential path factorization: 5->4->3 produces 20 choice sequences, ten unique final sets, two paths per final set; 8->5->3 produces 560 sequences, 56 finals, ten paths each. General `C(n,a)C(a,b)=C(n,b)C(n-b,a-b)` for b<=a<=n; when no interim rewards/info and second contraction certain, final reachability can be optimized directly despite different histories.
- Next integration is physical discard/attachment zone conservation and gameplay timing; never infer that a legal successor choice has already been applied without a real player decision.

### Complete physical-card conservation of chosen contractions

- Built `tools/bench_contraction_batch_conservation.py` with `contract_with_choice()` and `enumerate_contractions()`, validated via [CI 37920407200](https://github.com/FlareZ123/pokemon-workplace/actions/runs/37920407200), documented in `results/bench_contraction_batch_conservation/README.md`.
- Reuses `batch_zone_exit_conservation.leave_play_batch_before_promotion()` and `PromotionPendingState.to_stack_state()` to remove exactly selected Bench objects; routes full Pokémon evolution stacks and all attached cards to `discard`, dematerializes in the exact `IdentityLedger`, conserves card classes, and updates capacity only after atomic removal. Rejections include invalid count, duplicate ID, Active ID, or unknown ID.
- Full six-Pokémon witness: evolved Tarountula->Spidops with Grass Energy and Muscle Band selected for forced five-to-four contraction. Both physical stack cards and both attachments reach discard, other Pokémon plus Active remain, no Prize is taken. Five-to-three has ten complete conservative choices; successive five-to-four-to-three is valid with all card classes conserved.
- Shared `board_object_kernel` and `board_position_state` have distinct representations; this bridge deliberately uses stack-bearing `board_position_state` because the object-only representation does not by itself account for every physical Pokémon card.
- Next: apply named Ability guard evaluations to chosen successor boards in an integrated `StackBoardMaterialState`, then evaluate a stronger archetype witness where discarding a required Regigigas party member shuts off Ancient Wisdom under Collapsed Stadium.

### Conserved Regigigas timing and structural/material deficit

- New `tools/regigigas_capacity_window.py` with `results/regigigas_capacity_window/README.md`, passing CI [37920684422](https://github.com/FlareZ123/pokemon-workplace/actions/runs/37920684422).
- Source-print-verified Regigigas `swsh10-130` Ancient Wisdom requires five distinct other Regi names on a six-Pokémon board. Exact stack-bearing ledger fixture provides Regigigas Active, all five named partners Benched, 3 Basic Grass Energy exchangeable in discard, and no Ability lock.
- If Ancient Wisdom is used first, 3 Energy become physically attached to Regigigas; a subsequent selected 5->4 contraction discards a required partner and disables future Ancient Wisdom but does not undo earlier Energy attachments. If contraction occurs first, all five legal discard choices break the named guard, so zero Energy can be attached with Ancient Wisdom.
- Re-expanding capacity from four to eight without card recovery fails to restore the named condition. Structural Bench slack and physical missing-card availability are separate, sequential prerequisites.
- Tests include all five restriction choices, 1-use quota, 1-3 Energy selection bound, original ledger conservation, and direct card-list guard equality. Narrow witness assumes accessible Stadium, Basic Energy only, no other locks.
- This is a clear ALS deadline where evaluating only the final board undercounts actions already executed before a prerequisite-removing constraint. Future work: integrate card effect and turn-resource permission rather than providing externally ordered actions.

### Pairwise named Ability simultaneous Bench geometry

- New `tools/bench_joint_named_guard_capacity.py`, `results/bench_joint_named_guard_capacity/README.md`, [CI 37921004470](https://github.com/FlareZ123/pokemon-workplace/actions/runs/37921004470) passing six pinned-corpus tests.
- Exact necessary capacity for a selected guard set: let N be the union of source names and required species. Let F be species explicitly required on Bench. If N\F nonempty, at least |N|-1 Bench slots; otherwise |N|. Also enforce shared legal print if multiple guards claim the same source species as a single physical card; reject incompatible prints.
- Regigigas Ancient Wisdom + Lunatone Lunar Cycle has union of eight distinct required Pokémon names (six Regis + Lunatone + Solrock), requiring seven Bench positions, impossible at ordinary cap5, structurally feasible under Sky Field cap8. Adding Solrock reciprocal guard does not add names.
- Full conservative printed Ability guard-pair census (different source species): 293 text-variant pairs, histogram min Bench 1:6, 2:8, 3:108, 4:126, 5:22, 7:15, 8:8. Thus 23/293 need >5 slots and none need >8 by this restricted grammar. This is not deck metagame frequency or full Ability usability.
- Next high-value: dynamic sequential accomplishment of otherwise simultaneous-infeasible guard combinations, including real recovery/cleanup actions and correct timing; static joint capacity may overconstrain where one Ability pays out before releasing its support.

### Sequentially feasible Regigigas + Lunatone despite impossible simultaneous guard union

- Built `tools/regigigas_lunatone_temporal_multiplex.py`, `results/regigigas_lunatone_temporal_multiplex/README.md`, passing [CI 37921465934](https://github.com/FlareZ123/pokemon-workplace/actions/runs/37921465934).
- Grounded card texts: Regigigas `swsh10-130` Ancient Wisdom, Giovanni's Exile `sm10-174` (discard up to two undamaged Benched Pokémon), Lunatone `me1-74` Lunar Cycle (discard Basic Fighting from hand to draw3), Solrock `pgo-39` Sun Energy (attach Psychic from discard to Lunatone). All paper Expanded legal in supplied database.
- Controlled exact **60-card** snapshot: six Regi Pokémon in play (Regigigas Active, five others Bench), three Basic Grass and one Psychic in discard, Giovanni + Lunatone + Solrock + Basic Fighting in hand, 40 Basic Water deck, six Basic Water Prize cards. Basic Water energy copies exempt from 4-copy limit.
- Legally feasible same-turn line: Ancient Wisdom attaches 3 Grass to Regigigas; Giovanni's Exile discards two undamaged Benched Regi, freeing two slots; separately bench Lunatone and Solrock; Sun Energy attaches Psychic to Lunatone; Lunar Cycle discards Fighting from hand and draws 3 Water. Max Bench occupancy5, exactly one Supporter, all 60 physical cards conserved.
- Reversed order Giovanni before Wisdom makes Ancient Wisdom unavailable (lost Regi prerequisites), while Sun Energy and Lunar Cycle still work. This is a genuine sequential override of the static **seven Bench slots** needed to *simultaneously* keep both named guard sets: executed effects can persist after prerequisites are destroyed.
- Very important scope: deliberate conditional board state and artificial Water-heavy 60-card deck only demonstrate legality and sequence; no probability of assembling it, no metagame win rate, no opponent actions or locks modeled.
- Next investigate minimal release-action budget for more general sequential joint guard sets, and distinguish compulsory once-per-turn quotas/Supporter contention under a given schedule.

### Closed-form temporal Bench departure lower bound

- Built `tools/bench_temporal_guard_release_bounds.py`, `results/bench_temporal_guard_release_bounds/README.md`, verified by [CI 37921884751](https://github.com/FlareZ123/pokemon-workplace/actions/runs/37921884751) (five tests with independent exhaustive oracle over six named species).
- For initial named set A physically in play and first effect already resolved, later named set B, fixed Active a∈A, total board capacity C+1, sufficient Bench-only cleanup under simple distinct-name semantics: `D_min=max(0, |A∪B|-(C+1))`, provided |A|≤C+1, |B∪{a}|≤C+1, a not specifically forced onto Bench, and enough discardable A\(B∪{a}). Proof by cardinality and removal of nonrequired Bench occupants; all second missing names can then be played one by one.
- Among the 23 currently parsed legal named guard pairs impossible *simultaneously* at five Bench, all 23 can be sequentially satisfied geometrically with the pinned-Active model under enough departures. **15 require two departures**, supportable in principle with one legal Giovanni's Exile if targets undamaged; **eight require three**, needing another release channel or later Supporter turn.
- The generic lower bound excludes card access, other Bench residents, interrupting locks, resource contention, actual full Ability-use conditions and dynamic Active changes. Applying this to a real line requires full physical transaction/timing, as in `regigigas_lunatone_temporal_multiplex`.
- Next integrate with existing `tools/bench_capacity_schedule.py` to classify same-turn executable release resources, and study how Supporter contention changes the threshold in deck-specific ALSes.

### Typed batch cleanup scheduling under Supporter and attack timing

- Built `tools/bench_batch_release_schedule.py`, `results/bench_batch_release_schedule/README.md`, passing [CI 37922201732](https://github.com/FlareZ123/pokemon-workplace/actions/runs/37922201732), seven unit tests.
- Exact BFS state tracks turn, Bench occupancy, available expendable first-engine residents, unmet second-engine named arrivals, remaining typed release budgets, and one Supporter-per-turn flag. Supporter release removes 1..N Bench objects in one action (N=2 for Giovanni's Exile witness); Item/Ability release each 1 same turn; attack release 1 and ends turn.
- Regi6 -> Lunatone+Solrock needs 2 departures: one batch2 Supporter accomplishes by turn1; 1-target Supporter alone fails, adding Item1 works; 1-target Supporter+attack1 needs turn2 because attack ends the turn.
- Regi6 -> Uxie/Mesprit/Azelf needs 3 departures: one batch2 Supporter insufficient; batch2 Supporter+Item1 works turn1; two Supporters batch2 each require turn2; eight-slot expansion requires no release.
- Supporter already used by first-engine action blocks use of Giovanni's Exile that turn, and earliest completion may be turn2.
- This scheduler improves older `bench_capacity_schedule.py` for multi-occupant batch releases and changing prerequisite groups; still assumes all release cards accessible, targets eligible, new names in hand, and opponent does not interrupt.



## 2026-10-12: Shadow Rider post-Radiant attack-readiness branch

Identity reclaimed under run gpt6-agent14-20261012T184113192Z-bench-research-chat, claimed 2026-10-12T18:41:13.192Z. Maintainer wants new atomic work under results/tests/ and results/README.md to be a curated deck-first index, now handled by agent31.

New reproducible analytic module: tools/shadow_rider_post_launch_energy.py, results/tests/shadow_rider_post_launch_energy/reproduce.py and README.md. Starting with two usable Benched Shadow Rider VMAX sources, an uncharged Benched target, a possible manual attachment and a uniform residual deck, exact Fraction DP measures cost-3 Max Geist versus Dimension Valley-reduced cost-2. Radiant Eternatus ends its launch turn; charging occurs subsequently. Target must remain Benched until a separate legal promotion. Two active Underworld Doors can provide two Psychic attachments and two draw-2 windows, with one normal attachment last. One usable Door alone cannot charge three Energy in one turn without other acceleration. Illustrative conditional state h=1 in hand, e=8 in deck of n=41: P(cost3)=7119/50635=14.059445%, P(cost2)=73/205=35.609756%. h=2: 59.593167% vs 100%. Dimension Valley replacing Sky Field may force Bench contraction, creating a real timing tradeoff. Exhaustive small-deck position oracles and independent closed forms passed locally; verified relevant swsh6-75, swsh12pt5-105 and xy4-93 text from the bundled pool.

No unconditional deck win rates have been inferred. Next compose source-constrained launch state distributions with conditional Energy policy and pivot/Bench/Stadium gates. Avoid multiplying independently calculated marginal event chances.


### Same-run extension: joint Float Stone and Psychic Energy

Extended tools/shadow_rider_post_launch_energy.py with attack_and_pivot_ready_probability and results/tests/shadow_rider_post_launch_energy/reproduce.py with 960 independently enumerated three-category small-deck cases. Aichi champion plays one Float Stone (xy8-137). If this Tool is the needed pivot and starts absent, two Underworld Door draw pairs must furnish both sufficient Psychic Energy and the Tool. Illustrative conditional h=1 hand Psychic, e=8 Psychic and 1 Float Stone in deck of n=41: Max Geist cost3 Energy-only 14.059445% versus joint Energy+Float **1204/151905 = 0.792601%**; Dimension Valley cost2 Energy-only 35.609756% vs joint 2.751720%. Naive multiplication using four unconditional draws predicts approximately 1.3717% cost3, 73.06% above the exact joint result, because the second draw pair is conditional on having Energy to activate the second Ability. When Float is already held, joint equals Energy-only. This is just one route, with Tool/retreat legality externally assumed and alternative Latias/Guzma etc. omitted. See README and reproducer in results/tests/shadow_rider_post_launch_energy/.


## 2026-10-12 exact champion direct-launch continuation

Commit 4add7ffbb340a21aaac03cc3ffd36f2c4329f0f6 adds tools/shadow_rider_direct_launch_attack.py and results/tests/shadow_rider_direct_launch_attack/. For the published champion 60, exact accepted-opening probability of directly held or naturally drawn Radiant launching two VMAX is 12.017840120%, reproducing earlier research. Integrating next natural draw, two live Underworld Door uses, and manual attachment gives 4.455846832% three-Energy Max Geist readiness; requiring Float Stone as the sole pivot yields 0.768862128%. Two-Energy Dimension Valley counterfactual gives 6.978303011% and Float-only 1.288246138%, but Stadium access is not sampled. Four small independent physical toy oracles pass. The scenario assumes no opponent disruption and no alternate search; probabilities are narrow setup events, not match wins. Next: price actual one-copy Dimension Valley access and shared Float/energy draw competition.


### 2026-10-12 Dimension Valley singleton access continuation

Added tools/shadow_rider_valley_pivot_gate.py and results/tests/shadow_rider_valley_pivot_gate/{README.md,reproduce.py}. Physically price the Aichi champion one-copy Dimension Valley together with one Float Stone, Psychic draw/attachment requirements, accepted Basic starting hand, six Prizes, direct Radiant double-VMAX launch and the next turn. Use conditional singleton exchangeability among 30 neutral cards plus an exact four-category multivariate hypergeometric two-Door DP. Exact P(direct launch) 12.017840120%, P(normal3 Energy plus Float route) 0.768862128%, P(reduced2 Energy plus accessible Valley and Float route) 0.216450306%, their intersection 0.119037889%; union of these two routes **0.866274545%** per accepted opener. Access to a physically drawn Stadium adds just +0.097412417 percentage points to the regular 3-Energy Float branch, versus the misleading freely available Valley counterfactual. Four small physically labeled exact-deck enumeration oracles passed; 2541 aggregated post-launch resource states. These are restricted two-turn setup/access events, not overall wins. Next include paid launch search connectors and other legal pivot routes, then damage/prize matchups. Do not modify curator-controlled results/README.md with isolated tests.


### 2026-10-12 paid Mysterious Treasure/Quick Ball launch-to-attack

Added tools/shadow_rider_paid_ball_attack.py and results/tests/shadow_rider_paid_ball_attack/{README.md,reproduce.py}. The champion plays 4 Mysterious Treasure and 1 Quick Ball, both searching the Radiant Dragon Basic for one discarded hand card. Our *restricted conservative policy* requires spending one Basic Psychic Energy, and otherwise uses no search. Exact accepted-opening first-turn direct Radiant double VMAX launch 12.017840120%; disjoint Psychic-paid Ball launch 29.446836494%; combined launch 41.464676614%. Exact next-turn three-Energy Max Geist availability 9.707073373% combined. With Float Stone as a sole specified pivot and actual singleton Dimension Valley access, normal/reduced union gives 1.863998282% per accepted opener. Paid launch spends one Energy and yields only 17.832906% three-Energy readiness conditional on launch, versus 37.076936% on direct launch; physical search and attack resource requirements compete. No other payment types, Item locks, alternative pivot, other connectors or opponent interruptions considered. Independent physical labeled oracle for 4 toy populations passed; source texts from sm6-113 and swsh1-179 checked. Study is a narrow route, not match win rate. Next add the naturally accessible Latias ex Skyliner alternate free Basic retreat (print sv8-76), careful that Latias is one of 13 other Basics and can be initial Active or later Benched.
