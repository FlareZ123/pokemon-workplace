**Twinleaf counterfactual policy evaluation now uses a separate seeded RNG lane:** [Pinned Twinleaf RNG stream isolation](twinleaf_rng_stream_isolation/) demonstrates that the old one-stream headless runner consumed 662/793 Mega Absol random values while evaluating hypothetical moves, contaminating later physical chance events. The new research runner isolates game and policy streams, verifies 700 speculative draws cannot advance a live game stream, and records both draw classes. The [complete manual CI 38292013716 passed](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38292013716). This repairs replay comparability for the pinned runner, not bot strategy or competitive win-rate inference.

**Reactive Ability and Tool locks have unequal effects and a real competitive reference self-conflict:** [Scrafty/Spiritomb counterattack versus Garbotoxin, Path, Wobbuffet and Jamming Tower](reactive_counter_lock_profiles/) source-verifies the full 29-counter ceiling becomes 24 under Path to the Peak, 20 under Garbotoxin or Active Wobbuffet, 17 under Jamming Tower, and eight under Garbotoxin plus Jamming. The published 2026 Aichi eighth-place Absol/Garbodor list contains Garbotoxin and Secret Box ACE SPEC, making Ability-based counter-reaction imports self-conflicting and a second Deluxe Bomb ACE SPEC illegal. [Windows CI 38291864243 passed](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38291864243). Static source-window mechanics, not outcome probabilities.

# Competitive paper Expanded: playable decks and research

*Updated 12 October 2026. Paper Pokémon TCG Expanded, Black & White onward.*

## Best documented playable candidates

The strongest **tournament-supported starting point** in this repository is the 2026 Aichi champion Shadow Rider Calyrex list. The other decks below also placed highly in the same 926-player Open League event on 10 May 2026. A placement is evidence about that tournament field, and does not establish a universal ranking or a future win probability. No reliably validated, diverse-field head-to-head win-rate comparison is yet available. Every linked deck page provides a full 60-card list with representative English printing IDs.

| Tournament evidence | Deck and full 60-card list | Main competitive mechanism | Confidence |
| --- | --- | --- | --- |
| Aichi champion, Yasunori Kato | **[Shadow Rider Calyrex VMAX](decks/shadow-rider-calyrex/)** | Underworld Door acceleration/draw, Max Geist damage, Radiant Eternatus early VMAX launch, Copycat/Timeless-GX response | Published first place; paper Expanded English print validation |
| Aichi runner-up, Takahiro Ando | **[Vileplume / Pidgeot / Stoutland control](decks/vileplume-control/)** | Tag Call and Guzma & Hala into double TM: Evolution, Item lock and conditional Active Supporter lock | Published second place; paper Expanded English print validation |
| Aichi fifth, Yamato Nakano | **[Mew VMAX / Genesect V](decks/mew-genesect/)** | Fusion Strike draw engine and rapid attack access | Published fifth place; paper Expanded English print validation |
| Aichi eighth, Yusuke Kobayashi | **[Mega Absol ex / Garbodor](decks/mega-absol-garbodor/)** | Garbotoxin Ability lock with Mega Absol pressure and searched tools | Published eighth place; paper Expanded English print validation |
| Aichi tenth, Haruku Yoshioka | **[Regidrago VSTAR](decks/regidrago-vstar/)** | Apex Dragon toolbox with Timeless-GX, Phantom Dive, Item lock and gust options | Published tenth place; paper Expanded English print validation |

Tournament source: [CL Aichi Open League decklists](https://limitlesstcg.com/tournaments/566/decklists). The [competitive deck baseline audit](competitive_deck_baselines/) includes the card-name and English-print provenance, 60-card checks, core effect audits, and limitations of those legality checks.

**Promising experimental candidate:** [Mew/Genesect with a fourth Battle VIP Pass](decks/mew-genesect-vip4-aichi-counterfactual/) swaps one Special Red Card for an additional first-turn setup Item. The [exact restricted setup model](mew_genesect_vip_opening/) quantifies improvement in a defined Mew-plus-Genesect early-access endpoint; its lost Red Card disruption value and actual match results remain untested. This is an experiment, not a replacement for the fifth-place published list.

## How to interpret strength

The research contains exact mathematical probabilities, constrained first-turn launch simulations, card-rule regressions, physical conservation tests, and tournament observations. These answer different questions. **A first-turn access probability is not a match win rate.** Candidate swaps that improve an access endpoint can still worsen tactical value under lock effects, Supporter contention, occupied Bench slots, Prize configurations, resource discard requirements, or other metagames.

Current priority is reproducible full-game headless match evaluation between the five tournament baselines, including realistic opposing policies and verified card-engine coverage. Until that evidence exists, prioritize decks by credible tournament results, tactical matchup considerations, and the rules-validity of their key lines. The repository [Twinleaf simulation integration](../simulation/twinleaf/) uses a pinned upstream submodule at [`vendor/twinleafgg`](../vendor/twinleafgg/); automated engine support must be checked card by card before interpreting match results.

## Technical research and replication

- **[Competitive deck baselines](competitive_deck_baselines/):** primary tournament transcription, full 60-card print lists, reproducible legality and key-text checks.
- **[Aichi Vileplume ALS](aichi_vileplume_als/):** constrained turn-one setup and timing analysis. The model's Item-lock endpoint is not a game outcome.
- **[Mew/Genesect VIP4 opening analysis](mew_genesect_vip_opening/):** exact early Pokémon-access comparisons for source-aware paid search.
- **[Regidrago K0 launch](regidrago_k0_joint_launch/):** information-constrained opening sequence with explicit discard costs.
- **[Mega Absol lock-state lattice](absol_garbodor_lock_lattice/):** source-access changes under Item and Ability locks.
- **[Prize-to-Bench E-31 execution](prize_before_hand_bench_entry/):** official-ruling-backed KO Bench geometry, recursive Jirachi/Chansey Prize chain and Billowing Smoke hand-destination gate; verified by [CI run 38291234939](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38291234939).
- **[First-action information value](first_action_information_value/):** exact information value under hidden-Prize decisions, with restricted Regidrago cases.
- **[Two-player identity conservation](match_scoped_identity_liveness/):** reusable exact physical-card invariant for joint match modeling.
- **[Partial Prize observability](gnh_partial_prize_information/):** narrow decision-dependent value of Prized card knowledge.

The many independent atomic investigations remain temporarily in their original `results/<study>/` directories so reproducibility scripts, CI workflows, Python imports and cross-references still work. The owner has requested migration into `results/tests/`. Implement that migration incrementally, with an inventory of internal references and green CI after each move; avoid mechanically moving hundreds of directories in a way that invalidates existing experiments. `results/decks/` now holds playable deck pages. Duplicate folders produced by concurrent agents should be reconciled only after comparing their complete print inventories and inbound links.

## Research decisions still open

1. Measure realistic matches and matchup spreads across several independently validated strategies, with complete decklists, fixed bot policy and simulator revision.
2. Audit key attack-copying, lock interaction, Prize replacement and Trainer payment mechanics before trusting automated-game conclusions.
3. Retest individual card substitutions with opponent-dependent utility, unknown-Prize information, and multi-turn continuation costs.
4. Curate or retire superseded tests as evidence accumulates, retaining enough detail to reproduce each substantive finding.

---

*Repository maintainer directive, 12 October 2026:* The owner removed the oversized results index and requested a concise, continuously curated deck-focused README (target at most approximately 10,000 words, with a 3,000-word tolerance), a separate `results/decks/` directory for complete variants, migration of scattered test archives to `results/tests/`, and avoidance of another sprawling uncurated index. This directive is preserved here as requested. The legacy test paths are being kept until their dependencies can be migrated safely.
