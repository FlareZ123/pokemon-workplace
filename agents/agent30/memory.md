# agent30 memory

## Current identity
- Claimed at `2026-10-07T02:56:00Z` under run `chatgpt-20261007T025600Z-agent30`.
- Primary thread: exact Prize-origin E-31 timing, ordering authority, recursive Prize work, and strategic resource contention.

## 2026-10-07 checkpoint: simultaneous E-31 ordering
- Added `tools/prize_pending_batch_order.py`.
- Added `results/before_hand_prize_ordering/` with a reproducible regression.
- Added `.github/workflows/validate-before-hand-prize-ordering.yml`.
- CI run `37566415906` passed.
- Indexed the result in `results/README.md` as section 40 and repaired a concurrent duplicate section number by moving terminal Prize-window timing to section 39.
- Broadcast the result and sent agent6 a targeted note because their effect-order-authority work is the natural integration point.

### Finding
Official Japanese Pokémon Card Game Q&A for a two-Prize award containing Chansey (Lucky Bonus) and Dream Ball says the Chansey owner chooses which effect to process first. Therefore physical Prize position or pre-reveal selection order cannot safely stand in for E-31 effect order.

The new `PendingPrizeBatchOrder` keeps one simultaneous award as an unresolved sibling set. After staging/reveal, the owner may move any unresolved sibling to the queue head. If that chosen effect takes another Prize, the recursively taken card is a barrier: an older same-award sibling cannot be moved ahead of it until the nested Prize work resolves.

### Concurrent correction
The earlier zero-Pokémon terminal-precedence ambiguity was resolved concurrently by `results/post_prize_window_game_resolution/`. An official Jirachi Prism Star ruling establishes that applicable E-31 Prize effects resolve before the final Prize/no-Pokémon terminal snapshot. Do not preserve the older uncertainty as current research state.

### Next research
- Execute the strategic consequence of owner-selected E-31 order when the Bench has exactly one open slot.
- Chansey/Jirachi self-entry and Dream Ball search-to-Bench compete for that slot, so resolution order can decide which effect remains executable and whether an extra-Prize branch survives.
- Prefer an end-to-end conserved physical regression using the existing Prize batch-order wrapper, Lucky Bonus executor, and Dream Ball typed Bench executor.

## 2026-10-09 incarnation: E-31 stochastic precedence and Prize positional information

Claimed agent30 at `2026-10-09T18:35:15.378Z` as `gpt6-chat-20261009T183515378Z-agent30` (verified main-branch lease commit `6cdaaa1f`). Prior Chansey+Dream Ball one-slot contention had already been developed by another identity in `results/before_hand_bench_contention/`, so I pivoted.

New research: `results/e31_greedy_order_option/README.md`, `tools/e31_greedy_order_option.py`, `tools/e31_greedy_order_physical.py`, `results/e31_greedy_order_option/reproduce.py`, and validation workflow `.github/workflows/validate-e31-greedy-order-option.yml`. Local exact tests passed. CI green: [run 37975518702](https://github.com/FlareZ123/pokemon-workplace/actions/runs/37975518702) after correcting an exact printed Jirachi name in the physically materialized ledger.

Controlled four remaining-Prize fragment: Greedy Dice and Dream Ball are the simultaneous first two awarded Prizes; the other two are one Jirachi Prism Star and inert filler, face down. One Bench space and one legal Dream Ball target exist. The Greedy coin is fair. Greedy-first on heads can take Jirachi, which can use the last Bench slot for Wish Upon a Star and take the final Prize; Dream-first uses the slot and blocks Jirachi's secondary effect.

Conditional exact results: Dream-first expected prizes 5/2 and zero fourth-Prize probability; Greedy-first with known unordered composition but unknown positions has 11/4 expected and fourth-Prize probability 1/4; Greedy-first with exact private positional knowledge has 3 expected and fourth-Prize probability 1/2. With utility `U=Prizes + v*I(Dream target enters Bench)`, optional Jirachi decline makes early Greedy weakly dominate late Greedy: values `B + max(0,1-v)/4` composition-only and `B+max(0,1-v)/2` position-known, where `B=5/2+v`.

**Critical correction:** ordinary deck search K1 conveys Prize composition, not exact face-down positions! The stronger position-known state requires a separate source of positional information, potentially a known face-down placement through Peonia. Public face-up methods such as Town Map disqualify Prize-origin face-down effects. Never label position-known as K1.

Physical regression checks 32 branches against `PendingPrizeBatchOrder`, Greedy Dice resolving_trainer, typed Dream Ball Bench allocation, exact Jirachi bench entry and nested extra Prize, and `IdentityLedger` conservation. The first CI run failed because I had called the materialized Jirachi card `Jirachi Prism Star` whereas its board object uses `Jirachi ◇`; fixed and green.

**Rules limitation:** official Japanese Q&A explicitly establishes owner choice of order for simultaneous Chansey+Dream Ball, not the Greedy Dice+Dream Ball pair. The model assumes the same mixed-E-31 rule extends; do not silently upgrade to directly verified. Sent focused question to agent6 via `communications/agent6/20261009T1845Z_agent30_prize_order_question.md`.

Next work: add observer-belief updates to the physical Greedy/Jirachi nested Prize trace. Validate that composition-only and exact position-known input beliefs yield these policy choices. Test Peonia placement rules as a concrete source for exact privately known face-down positions; verify it does not invalidate E-31 conditions. Possibly integrate post-E-31 terminal game resolution directly.

## 2026-10-09 Peonia placement confirmation

Official Japanese Peonia Q&A directly says its hand-to-Prize replacements need no shuffle and may be put in a chosen order; same page says Chansey taken into hand via Peonia cannot use Lucky Bonus. Source: https://www.pokemon-card.com/rules/faq/search.php?freeword=%E3%82%B7%E3%83%A3%E3%82%AF%E3%83%A4&regulation_faq_main_item1=all.

Added `tools/e31_peonia_seed_execution.py` and `results/e31_peonia_seed_execution/README.md`. Four remaining Prize cards; Peonia takes three selected Prizes including Chansey directly to hand without triggering it and places Greedy Dice, Dream Ball, Jirachi face down in known positions 0,1,2 with an inert fourth original Prize. A later independently supplied two-Prize KO selects first two; Greedy-first on heads takes Jirachi then Jirachi's Wish Upon a Star takes fourth Prize; on tails Dream Ball benches Tapu Lele-GX. Expected Prizes exactly 3 given the supplied packet, physical identities and conservation checked. Passing CI run https://github.com/FlareZ123/pokemon-workplace/actions/runs/37976094692.

This upgrades the position-known information state from hypothetical to demonstrated Peonia-enabled source. It does not establish frequency of such a hand and setup, and the exact Greedy/Dream sibling effect-order extrapolation remains under review by agent6. Next valuable work: integrate observer-specific hidden positional beliefs through Peonia and the extra Prize into existing observer Prize kernels; test if an opponent who sees which positions were replaced but not their identities remains uncertain and if the actor posterior is exact.

## 2026-10-12 incarnation: Peonia hidden placement meets observer choice signaling

Lease claimed successfully at `2026-10-12T11:09:12.207Z` under run `gpt6-chat-agent30-20261012-deck-research-20261012T110912207Z`. Physical repo submodule remains at `vendor/twinleafgg` pinned `3348ebdc898f175a2ed8f999133cd13d1afd01f5`.

Added:
- `tools/e31_peonia_packet_observer.py`
- `results/e31_peonia_packet_observer/README.md` and `reproduce.py`
- `.github/workflows/validate-e31-peonia-packet-observer.yml`
- top of `results/README.md` indexed result.

The exact observer model assumes **uniform random permutation** of the known three-card Peonia packet (Greedy Dice, Dream Ball, Jirachi ◇) in positions 0/1/2 with unchanged filler in slot 3. The actor privately sees mapping; opponent knows packet composition and randomized policy but not actual permutation. Physical realization is G,D,J. The actor later chooses exactly the Greedy and Dream positions for a two-Prize award. Seeing the public unordered selected pair {0,1} updates opponent P(Jirachi at 2) from 1/3 to 1 and leaves G/D order probability 1/2 each. An independent random pair choice does not update beliefs. This is conditional action-policy inference, **not** a typical opponent's necessarily available information and not match strength.

Converted actor/opponent `PrizePositionTopBelief`s to `ObserverTopPrizeBeliefs`, then staged *actual* physical Peonia packet using `stage_prize_batch_with_latent_observers`. Verified exact pending IDs, hidden two-world posterior, physical truth support, and Greedy-heads additional Jirachi pending position. Nested Jirachi correctly blocks resolving original Dream Ball sibling. Independent `run_seeded` existing physical executor checks tails=2 and heads=4 Prizes, conditional expected 3. [CI run 38241472671 PASSED](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38241472671).

**Important limitation:** this new bridge stops at staged nested Jirachi pending work. The old physical executor independently resolves Jirachi Bench entry and Dream Ball, but they are not yet a single atomic observer-updated continuation. Existing official sibling-order authority concerns Chansey+Dream Ball; Greedy+Dream remains an extrapolation.

**Next high-value work:** integrate full Greedy-heads -> nested Jirachi -> Wish Upon a Star -> filler Prize -> original Dream Ball resolution with observer-relative evidence and actual board/ledger changes. Alternatively prioritize direct match-testing for complete 2026 Aichi finalist decklists; the existing simulations measure early endpoint access, not tournament win rates.

### Second 2026-10-12 contribution: exact Shadow Rider discard payment sensitivity

Created `tools/shadow_rider_treasure_discard_sensitivity.py`, `results/shadow_rider_treasure_discard_sensitivity/README.md`, `reproduce.py`, and workflow `validate-shadow-rider-treasure-discard-sensitivity.yml`. Linked at top of `results/README.md`. [CI 38242160754 passed](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38242160754). Sent agent7 a targeted message at `communications/agent7/20261012T1125Z_agent30_shadow_rider_discard_sensitivity.md`.

Uses agent7's complete exact-print 60-card Shadow Rider 2026 Aichi winning list, count partition (Radiant=1, VMAX=4, Mysterious Treasure=4, other Basics=13, Psychic Energy=11, other=27), valid opening 7 + 6 Prizes + first draw going second. One eligible non-Radiant Basic must be in initial seven to start Active; require 2 VMAX still in deck for Climactic Gate. Exact Fraction grouped hypergeometric enumeration and independent 18,312-world labeled toy oracle. Matches original unrestricted exact direct=12.017840120% and Treasure=31.681322310%.

**Critical policy sensitivity:** hypothetical Treasure discard guards (they are strategic conservation choices, not legal restrictions): (1) at least one Psychic Energy or spare Treasure in hand => Treasure route 26.390181773%, total 38.408021894%; (2) at least two Energy or spare Treasure => Treasure 16.072588787%, total 28.090428907%; (3) allow in-hand VMAX in addition => total 34.933859492%. This gives a 15.608733523pp free-payment/guarded envelope difference. All exact fractions pinned and CI passed. Crucial qualification: cannot infer match win rate or true DCI from these gates; real decisions depend on next-turn Underworld Door, future evolution and matchup.

**Promising next question:** split actual Dialga-GX singleton out from other Basic group. Against Regidrago it is often a desired discard payload for Mimikyu -> Copycat -> Apex Dragon -> Timeless-GX, so its DCI can be high. Real start-Active constraints make it an eligible discard only if another Basic started Active, even if it is in hand by the first draw. Card pool source confirms `sm5-100` Dialga-GX is **Dragon-type Basic** (searchable by Mysterious Treasure), `sm2-58` Mimikyu is Psychic Basic, and `swsh10-146` Hisuian Heavy Ball can swap one face-down Prized Basic into hand. Avoid treating Dialga as Metal type on intuition.

### Third 2026-10-12 contribution: Dialga-GX active-aware discard payload

Added `tools/shadow_rider_dialga_payload_discard.py`, `results/shadow_rider_dialga_payload_discard/{README.md,reproduce.py}` and workflow, indexed result in `results/README.md`. [CI 38242957811 passed](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38242957811).

In champion Shadow Rider, 1 Dialga-GX (`sm5-100`) is a Dragon-type Basic that can serve as an Apex Dragon/Timeless-GX payload in discard when Mimikyu copies opposing Regidrago's non-GX Apex Dragon. Prior strict hypothetical Treasure payment policy permits spare Treasure or a Psychic Energy if at least two held; extend it with held Dialga when Dialga can be discarded instead of forced as the starting Active. Compute exact incremental probability **2.0745519012150795 percentage points** (fraction `84865653/4090794400`), raising two-VMAX Radiant conditional launch from **28.090428907%** to **30.164980808%**.

Key combinatorial theorem: conditioned on the 6-class opening/prizes/draw with `b` other Basics among the opening 7 and first draw indicator `d` for a Basic, exactly one of the 13 interchangeable Basic labels is Dialga. It is held/discardable with conditional probability `((b if b>=2 else 0) + d)/13` in relevant launch states. A first wrong guess using `b-1` was detected and falsified by an independent physically labeled toy enumerator; corrected and checked in 3 toy pools with B=1/2/3 covering 6,720+18,312+41,328=66,360 accepted deals. This test is a useful example of choosing an initial Active non-anticipatively: a Basic drawn on the first turn cannot correct a forced Dialga start. Code checks Dialga's actual Basic Dragon type and Timeless-GX against bundled `sm5.json`.

The result is a Regidrago-specific discardability sensitivity, **not** a prediction of win-rate improvement. Mysterious Treasure connector choice conflicts with searching Mimikyu, and the later attack must meet Energy/opponent/matchup requirements. Follow up with agent7 to coordinate broader Shadow Rider launch decision research.


## 2026-10-13 incarnation: Aichi champion Dialga/Mimikyu/Radiant search contention

Lease successfully claimed at 2026-10-13T01:07:32.076Z (commit af04dc835274864bc7465d70fad629994d75066b). Existing Agent 30 memory and Agent 6 coverage messages inspected. Current pinned Twinleaf revision from prior identity memory: 3348ebdc898f175a2ed8f999133cd13d1afd01f5.

New compact study:
- tools/shadow_rider_dialga_connector_fork.py
- results/tests/shadow_rider_dialga_connector_fork/{README.md,reproduce.py}
- .github/workflows/validate-shadow-rider-dialga-connector-fork.yml
- Windows CI https://github.com/FlareZ123/pokemon-workplace/actions/runs/38331103493 succeeded.

Exact physical categories for champion 60: singleton Dialga/Mimikyu/Radiant, 11 other Basics, 4 VMAX, 4 Mysterious Treasure, 4 Fog Crystal, 34 others. First 7, 6 Prizes, first natural draw; no additional search channels. Require Dialga held and discardable without forcing it Active, Mimikyu and Radiant still in deck, >=2 VMAX in deck, at least one Treasure held/drawn, and another eligible Basic initially in opening. Of Basic-valid hands (probability 9797437/11703240), this fork occurs 2.772251473%; 0.984274407% include a held/drawn Fog Crystal that can retrieve Mimikyu independently, and 1.490683850% have exactly one Treasure and no Fog. These probabilities are reachability constraints, not win rates or an optimal discard policy.

Independent physically labeled oracle matches grouped exact counts across 12,600+27,720+360,360=400,680 toy deals, and the source reproducer asserts all five exact print card effects. Do not double-count the second Mysterious Treasure as playable without additional discard assessment; Climactic Gate ends turn, so execute other searches before it.

Next: collaborate with agents 7/14/35 over stronger joint turn1 to turn2 line probabilities, and compare the tactical payoff of counter-ready Mimikyu/Dialga against an immediate Radiant VMAX line with late Regidrago pressure and real opposing action rights. Preserve distinction between reachability and executable legal lines. Avoid editing results/README.md to append atomic tests, as the owner wants that index compact.


## 2026-10-13 continuation: paid Quick Ball relief and Twinleaf Night Watch live fairness

1. Extended initial one-Treasure/no-Fog Dialga search fork with Quick Ball as a second source. The original residual 34 contains exactly 1 Quick Ball, 11 Basic Psychic Energy, 22 others. Exact Basic-valid probabilities: parent **1.490683850%**, Quick held/drawn **0.168974085%**, Quick plus two held/drawn Psychic Energy as conservative second-payment safeguard **0.045096166%**. Added tools/shadow_rider_dialga_quick_ball_rescue.py and extended source reproducer, result and CI; independent physically labeled cards tested 1,078,935 small deals. Windows CI [38331470417](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38331470417) passed after detecting/correcting a grouped VMAX Prize survival-bound bug (initial failures preserved by CI history). These are restricted access endpoints, no win rate inference.

2. Followed Agent6's Night Watch semantic-audit request. Found already-existing research-only Night Watch random-pair reducer hook, but tournament-bounded-match.cjs never installed it. Pinned Twinleaf SMP217 Night Watch wrongly issues attacker-owned ChooseCardsPrompt despite '2 random cards' source text. Installed installNightWatchRandomHook via ensureResearchEngineHooks, passing random:()=>Math.random() (important: install occurs before runOne's Math.random seeded ledger swap, so capturing Math.random directly would be wrong). Live trace and aggregated report now label night_watch_uniform_discard_v1 alongside the three existing source-correctness hooks. Created physically labeled real reducer SFT simulation/twinleaf/test-night-watch-live-hook.cjs with six RNG bins, all 3 unordered pairs exactly twice, normal card movement/reveal/shuffle, one/zero-card boundaries, no attacker-prompt exposure, idempotence. Extended test-tournament-engine-hooks.cjs to assert actual runOne hook install; added push-based limited CI workflow .github/workflows/validate-twinleaf-night-watch-live.yml and integrated SFT into manual paired matchup workflow. [CI 38331907995 PASSED](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38331907995), source pinned 3348ebdc898f175a2ed8f999133cd13d1afd01f5. Detailed result: results/tests/twinleaf_night_watch_live_hook/README.md.

**Next:** validate manual real Aichi match trace under all four installed source guards; amend any incompatibility. Coordinate with Agent6. Full-match competitive win estimates remain unsafe while the native SimpleTacticsAi policy leaks hidden deck order and makes weak decisions.
