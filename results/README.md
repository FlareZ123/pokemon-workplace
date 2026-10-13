**Two additional fully specified Aichi top-eight paper Expanded decks:** [Quad Iron Thorns, sixth-place Japanese source and two validated English-print adaptations](iron_thorns_international_adaptation/) preserve the original 57 internationally available card slots and transparently replace three JP-only cards (Palace Book, Palace Belt, Player's Ceremony). Both English 60s (4 Pokémon/48 Trainer/8 Energy) pass October 12, 2026 print and deck legality, single ACE SPEC and Prism Star constraints in [Windows CI 38293543104](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38293543104). Four Basic-only Iron Thorns yield a 39.9499625745% valid opening-seven probability and 1.503 expected own mulligans. Exact physical hand/Prize access for a named Tag Call/Guzma & Hala + DCE + Thunder Mountain line is 29.0751478452% conditional on Basic-valid; legal action execution and actual match rates remain untested. Aichi sixth-place empirical performance belongs to the original Japanese list, not the altered English builds.

# Competitive paper Expanded: playable decks and research

*Updated 12 October 2026. Paper Pokémon TCG Expanded, Black & White onward.*

## Best documented playable candidates

The strongest **tournament-supported starting point** in this repository is the 2026 Aichi champion Shadow Rider Calyrex list. The other decks below also placed highly in the same 926-player Open League event on 10 May 2026. A placement is evidence about that tournament field, and does not establish a universal ranking or a future win probability. No reliably validated, diverse-field head-to-head win-rate comparison is yet available. Every linked deck page provides a full 60-card list with representative English printing IDs.

| Tournament evidence | Deck and full 60-card list | Main competitive mechanism | Confidence |
| --- | --- | --- | --- |
| Aichi champion, Yasunori Kato | **[Shadow Rider Calyrex VMAX](decks/shadow-rider-calyrex/)** | Underworld Door acceleration/draw, Max Geist damage, Radiant Eternatus early VMAX launch, Copycat/Timeless-GX response | Published first place; paper Expanded English print validation |
| Aichi runner-up, Takahiro Ando | **[Vileplume / Pidgeot / Stoutland control](decks/vileplume-control/)** | Tag Call and Guzma & Hala into double TM: Evolution, Item lock and conditional Active Supporter lock | Published second place; paper Expanded English print validation |
| Aichi fourth, Shu Hosoda | **[Raichu / Electrode Combo](decks/raichu-electrode-aichi-2026/)** | Extra Energy Bomb self-KO changes Prize differential and powers Electro Rain with conditional triple/double Energy | Published fourth place; exact English 60 validated by [Windows CI 38293458838](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38293458838) |
| Aichi fifth, Yamato Nakano | **[Mew VMAX / Genesect V](decks/mew-genesect/)** | Fusion Strike draw engine and rapid attack access | Published fifth place; paper Expanded English print validation |
| Aichi sixth in Japan, Kazuma Kashi, **adapted internationally** | **[Iron Thorns ex quad-lock](decks/iron_thorns_aichi_english/)** | Active Initialization suppresses Rule Box Abilities, control Supporters/Items, first-attack Energy line | Experimental English-legal 57/60-copy adaptation, [Windows print proof passed](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38292730598); **not the published 60** |
| Aichi eighth, Yusuke Kobayashi | **[Mega Absol ex / Garbodor](decks/mega-absol-garbodor/)** | Garbotoxin Ability lock with Mega Absol pressure and searched tools | Published eighth place; paper Expanded English print validation |
| Aichi tenth, Haruku Yoshioka | **[Regidrago VSTAR](decks/regidrago-vstar/)** | Apex Dragon toolbox with Timeless-GX, Phantom Dive, Item lock and gust options | Published tenth place; paper Expanded English print validation |

Tournament source: [CL Aichi Open League decklists](https://limitlesstcg.com/tournaments/566/decklists). The [competitive deck baseline audit](competitive_deck_baselines/) includes the card-name and English-print provenance, 60-card checks, core effect audits, and limitations of those legality checks.

**Promising experimental candidate:** [Mew/Genesect with a fourth Battle VIP Pass](decks/mew-genesect-vip4-aichi-counterfactual/) swaps one Special Red Card for an additional first-turn setup Item. The [exact restricted setup model](mew_genesect_vip_opening/) quantifies improvement in a defined Mew-plus-Genesect early-access endpoint; its lost Red Card disruption value and actual match results remain untested. This is an experiment, not a replacement for the fifth-place published list.

**Experimental Mew Wally/Tapu frontier:** [A fully specified 2 Wally / 1 Tapu Lele-GX 60](decks/mew-genesect-wally2-tapu1/) and its [six-allocation exact opening-access comparison](tests/mew_wally_slot_frontier/) test replacing both Special Red Cards in the Aichi fifth-place source. A restricted going-second 210-damage Wally route reaches 8.762569342969% with Wonder Tag available, 2.766576228949% with Wonder Tag fully suppressed. These are untested, simplified access hypotheses, with late-game disruption lost and no match outcomes.

**Experimental Regidrago:** [Two-Dragapult 60-card variant](decks/regidrago_dragapult_2/) substitutes one Battle VIP Pass for a second Dragapult ex. [Exact first-Item study](regidrago_joint_launch/) improves the restricted joint access endpoint; legality is checked by its [variant proof](decks/regidrago_dragapult_2/reproduce.py). Match win rates remain unknown.

**Pinned simulator correctness:** [Mega Absol ex Terminal Period direct-KO effect correction](mega_absol_direct_ko/) demonstrates and repairs an artificial-damage engine divergence relevant to the Aichi eighth-place list. Its exact-six threshold and Big Parasol protection regressions pass pinned-engine CI. Headless matchup conclusions remain subject to policy and other engine limitations.

## How to interpret strength

The research contains exact mathematical probabilities, constrained first-turn launch simulations, card-rule regressions, physical conservation tests, and tournament observations. These answer different questions. **A first-turn access probability is not a match win rate.** Candidate swaps that improve an access endpoint can still worsen tactical value under lock effects, Supporter contention, occupied Bench slots, Prize configurations, resource discard requirements, or other metagames.

Current priority is reproducible full-game headless match evaluation between the tournament baselines, including realistic opposing policies and verified card-engine coverage. Until that evidence exists, prioritize decks by credible tournament results, tactical matchup considerations, and the rules-validity of their key lines. The repository [Twinleaf simulation integration](../simulation/twinleaf/) uses a pinned upstream submodule at [`vendor/twinleafgg`](../vendor/twinleafgg/); automated engine support must be checked card by card before interpreting match results.

## Technical research and replication

- **[Competitive deck baselines](competitive_deck_baselines/):** primary tournament transcription, full 60-card print lists, reproducible legality and key-text checks.
- **[Aichi Vileplume ALS](aichi_vileplume_als/):** constrained turn-one setup and timing analysis. The model's Item-lock endpoint is not a game outcome.
- **[Mew/Genesect VIP4 opening analysis](mew_genesect_vip_opening/):** exact early Pokémon-access comparisons for source-aware paid search.
- **[Regidrago K0 launch](regidrago_k0_joint_launch/):** information-constrained opening sequence with explicit discard costs.
- **[Mega Absol lock-state lattice](absol_garbodor_lock_lattice/):** source-access changes under Item and Ability locks.
- **[Prize-to-Bench E-31 execution](prize_before_hand_bench_entry/):** official-ruling-backed KO Bench geometry, recursive Jirachi/Chansey Prize chain and Billowing Smoke hand-destination gate; verified by [CI run 38291234939](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38291234939).
- **[Raichu physical Item payment](tests/raichu_target_payment_frontier/):** exact one-turn Alolan Raichu search through Ultra Ball/Computer Search with six hidden Prizes, Gladion fallback and mutually competing two-card discard costs; restricted access **30.578700%** under strict payment and **33.390969%** under an Ultra-for-Computer-sacrifice policy. [Migrated Windows CI 38292324506 passed](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38292324506); this is card access, not wins.
- **[Shadow Rider Treasure payment sensitivity](tests/shadow_rider_treasure_payment/):** exact Path + Iron Thorns counter-launch access falls from 2.622360% to 2.027751% with an Energy-only Mysterious Treasure discard policy. The source-tested endpoints are conditional first-turn access, not match outcomes.
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
