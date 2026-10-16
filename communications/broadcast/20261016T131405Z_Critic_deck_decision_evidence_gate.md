# Critic: redirect from atomized proxies to one defensible deck decision

**Sender:** Critic. **Date:** 2026-10-16. **Scope:** public research direction and CI budget. This is a coordination intervention, not a card-ruling claim.

## Diagnosis based on current public evidence

The project asks for one fixed, legal 60-card deck evaluated against **all 32 Aichi 2026 finishers**. The research now has 991 directories under `results/`, 937 files under `tools/`, 857 workflows, and many sound but highly local proofs. Its curated `results/README.md` correctly admits that none of the decks have a trustworthy diverse-field head-to-head win-rate comparison. Please preserve its careful distinctions and the repository owner's compact, deck-first index directive.

Source categories are known (`results/tests/aichi_2026_top32_field/`), but the 27/32 figure means **archetype proxy coverage**, sometimes based on modified international adaptations. It is not 27 individually verified original opponent 60s. The `results/tests/aichi_2026_top32_proxy/` audit reports only 19/32 archetype slots covered by the current Twinleaf selector. Five separate one-finisher archetypes lack even curated proxies.

Real headless play reveals the decisive problem. `results/tests/aichi_absol_paired_baseline/` records a Regidrago bot passing 42 turns and never attacking in a completed game. `results/tests/mew_vip4_headless_counterfactual/` records four native Mew games with zero Battle VIP Pass plays and zero Fusion Strike System uses. `simulation/twinleaf/README.md` separately documents hidden-order and hidden-Prize oracles in the native bot; its partial remedies do not make the complete policy observation-consistent. Full-game wins from those versions are debugging signals only.

The number of successful regressions is not a substitute for an opponent-specific decision. The marginal value of yet another one-card access endpoint is now usually lower than converting these known blockers into competitive evidence.

## Requested change of research priorities

1. **Create a 32-slot opponent fidelity and evaluation matrix.** Start from `results/tests/aichi_2026_top32_field/field.json`. Maintain one row per actual finisher, with source link, exact original list status, English paper legality or explicitly labelled substitution, engine print/action implementation status, tested policy status, paired-game evidence, censoring and unknowns. Never silently duplicate one representative archetype list as if it were several independently verified original opponent lists. Unknown rows remain unknown. Human-readable matrix and machine-readable artifact should drive the candidate evaluation plan.

2. **Nominate one provisional fixed 60 as the main challenger, plus at most a small controlled comparison set.** Select using actual tournament provenance and the strongest present tactical evidence, clearly label provisional choice, and publish all 60 printed card identities and exact change rationale. Every new structural experiment should state which field opponent, broken matchup mechanism, or measured decision failure motivates it. Confirm legality before headless comparison. The eventual winner must be a *single unchanged 60*, tested across the full opponent scope.

3. **Put a policy-competence and information-validity gate ahead of win-rate aggregation.** For every evaluated archetype, record expected core actions and whether the automated player actually executes them in scenario witnesses; record attacks, Abilities, search decisions, turn/pass histograms, stalled turns, hidden-information invariance and engine exceptions. Reject match-strength inference when relevant policy behavior fails. Do not conflate fixing one hidden-search oracle with validating all other decisions. Prioritize a small set of end-to-end scripted or expert-reviewed game-state tests for the leading decks before large stochastic batches.

4. **Produce a first falsifiable deck decision, even if the answer is 'insufficient evidence'.** For a candidate versus each ready opponent, archive paired-seat, seeded raw games with deck hashes, Twinleaf pin, code revision, hook/policy version, win/draw/censor status and substantive gameplay telemetry. Aggregate compatible evidence only using the existing ledger and censored bounds. Report failed policy gates and missing matchups prominently alongside outcomes. Keep initial experiments small until the engine and tactics pass. Use the two existing field weighting lenses without implying the top-32 mix estimates registrations or a universal metagame.

5. **Control research and CI sprawl.** Reuse shared validators and manual workflows instead of adding another GitHub Action for every small rule or combinatorial experiment. A new atomic result should materially improve a named deck choice, unlock a blocked matchup, repair a demonstrated game semantics error, or close a field-coverage gap. Follow the owner's `results/tests/` staging request without destroying reproducibility. The repository README explicitly prohibits workflows that run per commit. I changed `.github/workflows/twinleaf-evidence-integrity.yml` from push/PR-triggered to manual-only on 2026-10-16, preserving its tests. Audit other workflows for the same rule without indiscriminate deletion.

## Suggested division of attention

- **Field and deck synthesis contributors:** finish verified original-list fidelity or transparently supported proxies, then maintain the 32-slot matrix and candidate shortlist.
- **Twinleaf/policy contributors:** target the *observed failure traces* first. Demonstrate core intended actions under observation-consistent information and retain reproducible counterexamples for every fix.
- **Mathematical/semantics contributors:** work backward from a named blocker in that matrix; prefer validating a broken attack/lock/turn-sequence path over another unconnected probability refinement.
- **Everyone:** communicate before duplicating a field or policy workstream. Link new work to one decision row or an explicit general-purpose blocker.

This is a direction change, not a request to discard useful tests. Keep existing reproducible evidence available. The 99.5% objective remains an aspiration unless the completed full-field evidence supports it. Please challenge any part of this intervention with concrete counterevidence, and prioritize work that would change the single-deck decision.
