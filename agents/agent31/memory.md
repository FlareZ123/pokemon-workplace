# agent31 memory

## 2026-10-07: Knock Out -> Prize -> promotion timing

Claimed agent31 at 2026-10-07T02:56:19.194Z.

### Promotion-pending physical state

Created:
- `tools/promotion_pending_conservation.py`
- `results/promotion_pending_prize_information/`
- `.github/workflows/validate-promotion-pending-prize-information.yml`

Durable finding: the stable `BoardState` invariant requiring an Active cannot represent the rules-visible interval after a Knocked Out Active is physically discarded and before a replacement Active is chosen. `PromotionPendingState` permits `active_id=None`, preserves surviving physical board objects and the canonical `IdentityLedger`, and validates stacks/attachments.

`PostKnockOutPromotionContext` gates PRIZES -> PROMOTION or PRIZES -> TERMINAL. Replacement-Active policy cannot run while any card remains in `prize_pending`. When both players need promotion, the next-turn player chooses first, then the second player can react to that visible choice.

Regression composes exact KO disposal, private face-down Prize observation, Prize hand entry, then promotion. Toy decision witness: with two equiprobable observations favoring opposite promotion choices, fixed pre-observation utility is 50% and observation-conditioned utility is 100%. These are toy objective values, not match win rates.

CI:
- 37565196267 passed initial implementation.
- 37565457771 passed after official full-Bench geometry regression.

### Official full-Bench validation

Official Japanese Pokemon Card Game Q&A asks about five Benched Pokemon plus a 50-HP Great Tusk ex using Gigant Tusk, KOing the opponent Active and itself, then taking Chansey as a Prize. Ruling: Lucky Bonus cannot be used.

This is a strong sequencing witness: after Active disposal and during the Prize window, all five survivors still occupy the Bench. A later promotion would open a slot, but that happens too late for Lucky Bonus.

Source URL preserved in `results/promotion_pending_prize_information/README.md`.

A second Great Tusk official Q&A confirms that when both Active Pokemon are KO simultaneously, the player whose turn would be next promotes first. Another confirms final-Prize + self-KO resolution depends on whether players can supply replacements.

### Executable E-31 Bench-entry effects

Created:
- `tools/prize_before_hand_bench_entry.py`
- `results/prize_before_hand_bench_entry/`
- `.github/workflows/validate-prize-before-hand-bench-entry.yml`

Implemented exact card classes:
- `sv3pt5-113` Chansey / Lucky Bonus
- `sm7-97` Jirachi Prism Star / Wish Upon a Star

The same pending Prize instance moves from `prize_pending` to `in_play`, gains a board-object binding, and becomes a real `BoardPokemon` without a hand intermediate. Bench capacity is checked in the promotion-pending geometry.

Jirachi can stage an additional Prize at the front of the pending queue. Regression chains Jirachi -> extra Chansey -> Lucky Bonus, conserving exact physical identities.

A zero-survivor physical witness shows Chansey can create a future promotion candidate at the material level. The separate win/loss precedence question is intentionally unresolved.

CI 37565825259 passed.

### Observer-aware recursive additional Prize staging

Created:
- `tools/prize_pending_observer_extra.py`
- `results/prize_pending_observer_extra/`
- `.github/workflows/validate-prize-pending-observer-extra.yml`

`stage_additional_prize_front_with_observers` couples the existing physical extra-Prize transition to observer-relative joint top/Prize beliefs. The taker privately learns the selected face-down Prize identity; other observers update only on public slot removal. Every posterior must retain positive support on exact physical truth.

Regression uses a two-world top/Prize anti-correlation. B takes exact Switch as the additional Prize and becomes certain top=Other; A remains 50/50. The physical Switch is prepended to `prize_pending`; conservation holds.

CI 37566106587 passed.

### Synthesis and coordination

`results/README.md` now contains sections 35, 36, and 37 for these results.

Sent:
- broadcast `communications/broadcast/20261007T0308Z_agent31_prize-before-promotion.md`
- direct message to agent49 `communications/agent49/20261007T0315Z_agent31_e31-execution-overlap.md`

Agent49 is actively developing the broader before-hand Prize trigger/compiler family. Proposed split: agent49 owns broader trigger semantics/compiler; agent31 owns post-KO phase composition and observer-aware recursive Prize transitions.

### Open questions / next work

1. Authoritative terminal precedence remains unresolved: if a player has zero Pokemon immediately after KO disposal but takes a face-down Chansey/Jirachi Prize that could enter play in E-31 timing, does game resolution preclude that effect? Do not encode an assumed answer without official evidence.
2. Observer-aware extra-Prize staging is currently a downstream adapter; an atomic card-effect composition with the executable Chansey/Jirachi layer can be added after coordination with agent49.
3. Strong next validation work: collect official KO/E-31 Q&A witnesses into reusable regression invariants rather than relying only on abstract rule interpretation.

## 2026-10-12: KO geometry and Prize-destination gate

Claimed new lease 2026-10-12T18:22:51.890Z. Previous terminal-resolution uncertainty was already solved by agent32's `dream_ball_terminal_rescue`, per their direct message; the physical code remains useful.

### Verified full-Bench Jirachi/Chansey chain

Extended `results/prize_before_hand_bench_entry/reproduce.py` and its README with four physical simultaneous-KO patterns beginning from five own Benched Pokemon and three face-down Prize cards in order: Jirachi Prism Star, Chansey, Other. The opposing Active KO that awards the initial Prize is an upstream assumption.

- Own Active KO only: no opening, Jirachi refuses.
- Own Benched KO only: Jirachi enters the single opening and occupies the fifth Bench slot; extra Prize Chansey cannot enter.
- Own Active plus one Benched KO: same single-slot contention before promotion.
- Own Active plus two Benched KOs: Jirachi and Chansey both enter; heads on Lucky Bonus stages a third Prize which enters hand.

Both official Jirachi rulings (own Active versus own Benched KO with initially full Bench) directly support the first two geometries. Remaining cases are physical derivations. Exact ledger conservation holds. CI: https://github.com/FlareZ123/pokemon-workplace/actions/runs/38290942440 passed.

### Billowing Smoke compatibility

Official Japanese Jirachi ruling confirms that a Prize awarded against a KO holder with Billowing Smoke cannot use Wish Upon a Star. Card `swsh3-158` redirects Prizes from hand to discard. The repository already has `prize_destination_applicability.py` and `prize_destination_overrides.py`, plus the generic `before_hand_prize_executor.py` `pre_hand_destination` parameter.

Added matching `pre_hand_destination` parameter to `tools/prize_before_hand_bench_entry.py` and gated both Jirachi and Chansey self-to-Bench actions when destination differs from hand. A fixture uses an explicit Billowing Smoke destination decision; both before-hand triggers refuse, and Chansey physically resolves to discard. Jirachi's Prism Star Lost-Zone replacement is **not implemented here**; the regression intentionally does not perform its final discard transition. CI run https://github.com/FlareZ123/pokemon-workplace/actions/runs/38291234939 passed.

### Follow-ups

1. Integrate `derive_knockout_prize_overrides` with specialized E-31 Bench-entry from a real pre-KO object and verify one physical Jirachi end-to-end where Prism Star Lost-Zone replacement applies.
2. Add authoritative source check for the exact Prism Star discard->Lost Zone replacement; keep it separate from destination override to avoid inadvertently sending other Prize cards to Lost Zone.
3. Test whether a full game-state policy values Jirachi/Chansey chains after multi-KOs; no present match-win evidence exists.
4. Coordinate with agent49/agent32 on Prize-destination and before-hand executor overlap.

### Replaced Prize Prism Star zone and game-state result

Official Jirachi Prism Star printed rule and Pokémon TCG Prism Star appendix: any attempted discard goes to Lost Zone. Added `resolve_replaced_jirachi_prize` in `tools/prize_before_hand_bench_entry.py` which consumes the chosen `PrizeDestinationDecision` from the existing override mechanism. On Billowing Smoke attempted discard or a chosen Lost Block Lost-Zone replacement, exact `sm7-97` is moved directly from `prize_pending` into `lost_zone`; no in-play object is created, and shared post-KO board/Prize ledger remains conserved. Other cards such as Chansey remain subject to ordinary discard. Regression `results/prize_before_hand_bench_entry/reproduce.py` green GitHub Actions 38292550834; see corresponding README for official links and scope limitations. The specialized function intentionally does not claim global Prism Star card class coverage.

### Maintainer-requested results curation

Repo owner deleted oversized 433KB `results/README.md` on 2026-10-12 18:30 UTC and requested deck-first concise index, `results/decks/` and eventually `results/tests/`, with directive retained as footnote. Rewrote `results/README.md` to a readable 5 published tournament-deck shortlist, experimental Mew VIP4, tactical evidence, clear no-win-rate qualifications, and migration caveat (commit 60c34e44989e907a856ed4ff561c94bd628962b0). Other agents meanwhile created and deduplicated actual 60-card deck pages, so canonical links are currently `shadow-rider-calyrex`, `vileplume-control`, `mew-genesect`, `mega-absol-garbodor`, `regidrago-vstar`. Agent2 created `results/tests/` and began staged moves; coordinate future reindexing.

Added `tools/curated_deck_catalog_audit.py` with CI `validate-curated-deck-catalog.yml`: checks canonical six deck pages' physically printed quantities against five published Aichi 60s and the Mew +1 VIP/-1 Red legal counterfactual. Validated green CI https://github.com/FlareZ123/pokemon-workplace/actions/runs/38292342388 after excluding concurrently deleted redundant page names. It checks written card identities/counts and does not replace the original project legality proof or demonstrate match performance. Broadcast `communications/broadcast/20261012T183539Z_agent31_results-curation-coordination.md`.

### Near-term next actions
- Canonical deck list index should withstand competing atomic-result prepends; owner requested no more index spam.
- Verify Prism Star destination under simultaneous Lost Block and Billowing Smoke with chooser authority, using official Q&A which explicitly allows distinct routing of multi-Prize cards.
- Add end-to-end knockout object -> Billowing Smoke applicability -> Prize override -> Jirachi Prism Star terminal resolved state, rather than passing artificially constructed override tuples.
- Evaluate actual deck-level effect only after full-game simulator has verified coverage; these rule tests are not win rates.

### Exact per-Prize replacement selection and terminal impact

A new regression in `results/prize_before_hand_bench_entry/reproduce.py` derives Billowing Smoke and Lost Block directly from the KO victim's `swsh3-158` Tool and a surviving Barbaracle `swsh11-107` via `tools/prize_destination_applicability.py`. Under an assumed two-Prize award, both choices can be made independently per Prize (official Japanese Q&A explicitly allows it). In either choice order, Jirachi Prism Star ends Lost Zone, Chansey ends either Lost Zone or discard per the chosen effect; both before-hand Bench-entry triggers refuse. Exact physical card conservation holds. CI https://github.com/FlareZ123/pokemon-workplace/actions/runs/38292844142 passed.

A further final-Prize simultaneous double-Active-KO fixture composes `resolve_after_prize_window` and `Outcome`. With Jirachi's hand-bound Wish Upon a Star, it appears on otherwise empty Bench and the Jirachi player wins. With Billowing Smoke, Jirachi fails trigger, is sent to Lost Zone via Prism Star rule, and both players tie. Early terminal resolution is refused while either Prize remains `prize_pending`. CI https://github.com/FlareZ123/pokemon-workplace/actions/runs/38293359832 passed. The exact source-grounded event is conditional on a mutually lethal attack and both players taking their final Prize; no prevalence or match-win estimate inferred. Documentation updated in `results/prize_before_hand_bench_entry/README.md`.

Updated `tools/curated_deck_catalog_audit.py` for the experimental +Dragapult/-Battle VIP Regidrago candidate, now seven canonical complete published or experimental 60s checked; CI https://github.com/FlareZ123/pokemon-workplace/actions/runs/38293047599 passed. `results/README.md` also links the Regidrago candidate. Sent agent8 a request for Twinleaf feasibility tests of the paired Regidrago baseline/candidate. 
