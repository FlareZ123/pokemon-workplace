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
