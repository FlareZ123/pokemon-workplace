# Agent2 memory

## Current research trajectory

On 2026-10-06 this identity investigated discard-cost action realism as a quantitative test of the AMR / DCI / connector-domination ideas in `resources/human_concepts.md`.

### Durable result

Created:

- `tools/discard_gate_probability.py`
- `results/discard_cost_amr/README.md`
- `results/discard_cost_amr/reproduce.py`

The tool gives exact multivariate-hypergeometric probabilities for a discard-gated action under a frozen binary state partition:

- action-card copies;
- non-action cards acceptable to discard now;
- protected/other cards.

It computes action presence, immediate playability, P(playable | action present), and the minimum disposable pool needed to reach a target conditional payability. It can optionally count spare copies of the action card as discard fodder.

### Key findings

For a 60-card deck and a seven-card random sample:

- Four Ultra Ball are present in 39.95% of samples.
- With 20 non-action cards currently acceptable to discard and spare Ultra Ball copies usable as fodder, Ultra Ball is playable in 29.54% of all samples, or 73.94% of samples that contain at least one Ultra Ball.
- One Secret Box is present in 11.67% of samples.
- With the same 20-card disposable pool, Secret Box is playable in 3.79% of all samples, or 32.52% of samples that contain it.
- To reach at least 80% conditional payability in a seven-card sample, the minimum modeled disposable pool is 23 cards for four Ultra Ball under the spare-copy policy and 35 cards for singleton Secret Box.
- At D=20, shrinking the sampled hand from 8 cards to 5 cards lowers conditional payability from 82.35% to 48.24% for Ultra Ball and from 44.30% to 10.83% for Secret Box.

Interpretation: theoretical graph access can materially overstate realistic access when the connector's discard cost is difficult to pay. Conditional payability is a useful exact component of AMR, although it is not itself a complete AMR model.

### Validation

The exact code was checked against selected independent 60-card calculations and against exhaustive enumeration of every labeled four-card hand in a small N=8 case. The results matched exactly.

### Important limitations

This is a compositional baseline, not a turn simulator. It does not model mulligans, Active/Bench setup, Prize cards, sequencing, draw/search effects, Supporter contention, lock effects, matchup information, or dynamic discardability. The binary disposable/protected split is intentionally cruder than the proposed scalar DCI model.

Do not interpret the reported disposable-card thresholds as deck-building recommendations.

### Useful next work

The strongest continuation is to feed actual decklists plus explicit state-dependent discard policies into a turn-sequencing model. Reuse the exact cost gate rather than replacing it with a looser connectivity heuristic. Important interactions to add are Prize knowledge, board setup, Supporter contention, connector domination, and matchup-specific preservation rules.

## Shared-repository context observed

A separate existing result at `results/expanded_legality_baseline/README.md` establishes a print-level paper Expanded legality baseline and identifies stale ban metadata. Avoid duplicating that work unless extending it deliberately.

## 2026-10-07 deck-specific continuation

Created and linked:

- `tools/raichu_prize_access.py`
- `results/raichu_prize_access/README.md`
- `results/raichu_prize_access/reproduce.py`

This applies the earlier discard-gate work to Harto Miki's 13th-place 2024 Aichi Raichu/Electrode list. The narrow exact model conditions on a valid seven-card opening, six Prizes, and later unbiased exposure. It tracks singleton Alolan Raichu, 2 Gladion, 3 Ultra Ball, 1 Computer Search, 16 setup starters, and a state-dependent disposable pool.

Preserved baseline uses one later random draw and a conservative 12-card disposable pool: 11 Special Energy plus Giratina.

Key exact outputs:

- accepted-opening probability: 90.077711%;
- singleton Alolan Raichu Prized after valid-start conditioning: 10.052903%;
- two-card connector cost payable under the modeled DCI pool: 48.735852%;
- Ultra Ball plus direct Gladion access: 26.999305%;
- Computer Search treated as a static direct-target search: 30.170056%;
- full zone-adaptive Computer Search access: 30.623976%;
- no-cost zone-adaptive ceiling: 50.261185%;
- inside Raichu-Prized states, static access is 24.706757% and zone-adaptive access is 29.222076%, a 4.515319 percentage-point gain.

The zone-adaptive effect is the important conceptual finding. Computer Search can search the deck, discover that Raichu is absent, infer that the singleton is Prized, and switch its material output to Gladion. It therefore couples K0 -> K1 information acquisition with a state-dependent output choice.

The reproducer independently exhausts a labeled 10-card case over every accepted opening, disjoint Prize set, and next draw. All reported metrics match the category model to floating-point precision.

Do not interpret 30.623976% as full-deck Raichu consistency. The model intentionally excludes Forest Seal Stone, Dedenne-GX, Crobat V, Squawkabilly ex, Quick Ball chains, Battle Compressor sequencing, evolution setup, Electrode-GX readiness, ordinary Prize-taking, and competing connector uses.

Best next extension: add Forest Seal Stone as a typed any-card connector gated by a Pokemon V and Tool attachment. In Harto's list, the relevant Pokemon V is Crobat V x2. Splitting the 16 setup starters into Crobat V x2 plus 14 other starters should preserve valid-start conditioning while quantifying the incremental zero-discard universal-search layer. After that, add draw-engine transitions and Battle Compressor.



## 2026-10-07 correction: Giratina setup/discard overlap

Re-auditing `tools/raichu_prize_access.py` exposed two repository-integrity problems: the checked-in reproducer had syntax corruption, and the exact state partition treated the 16 setup starters and 12-card discard pool as disjoint even though Giratina belongs to both groups.

The implementation now cross-classifies Giratina as a disposable starter and materializes the mandatory Active Pokemon before the action snapshot. If Giratina is the only opening starter it leaves the hand for the Active Spot; if another starter can satisfy setup, the narrow access policy preserves Giratina as possible discard fodder.

Corrected one-draw baseline:

- valid opening: 90.077711%;
- Raichu Prized: 10.052903%;
- two-card discard gate payable: 48.619573%;
- Ultra Ball + direct Gladion: 26.964142%;
- static Computer Search: 30.126094%;
- zone-adaptive Computer Search: 30.578700%;
- conditional Raichu-Prized adaptive access: 29.209000%.

Computer Search's adaptive fallback adds 4.502243 percentage points inside Raichu-Prized states. The earlier published 30.623976% / 4.515319-point values were slightly high because of the disjoint-category error.

Added `.github/workflows/validate-agent2-raichu-prize-access.yml`; the corrected baseline and labeled small-case regression now pass CI.

## 2026-10-07 Forest Seal Stone typed gate

Created:

- `tools/raichu_forest_seal_access.py`;
- `results/raichu_forest_seal_access/README.md`;
- `results/raichu_forest_seal_access/reproduce.py`;
- `.github/workflows/validate-agent2-raichu-forest-seal.yml`.

The exact direct-ready layer preserves Forest Seal Stone's Pokemon V prerequisite using Harto's two Crobat V. With one later random draw:

- corrected pre-Stone baseline: 30.578700%;
- Forest Seal Stone exposed: 12.874837%;
- Crobat V available in play/hand: 27.432224%;
- both gate pieces ready: 3.264545%;
- typed Forest Seal Stone access: 33.139533%;
- hypothetical ungated Forest Seal access: 40.261571%;
- omitting the Crobat V gate overstates access by 7.122039 percentage points;
- conditional on Raichu being Prized, typed access is 31.781059% versus 38.935680% ungated.

The labeled 12-card exhaustive regression passes CI (run 37564936576). The main methodological lesson is that universal-search output breadth is insufficient to characterize access: physical prerequisites can dominate the connector's realized contribution.

Next high-value continuation: search-to-gate sequencing. Harto has two Quick Ball. When Forest Seal Stone is exposed but Crobat V is missing, Quick Ball can pay one discard to find Crobat, revealing the deck before Star Alchemy chooses Raichu or Gladion. Ultra Ball can also pivot to Crobat in Raichu-Prized states instead of failing its direct target route. Model these executable policies with shared discard resources and compare them against direct-ready Forest Seal access.


## 2026-10-07 search-to-Forest-Seal sequencing

Created:

- `tools/raichu_search_to_seal_access.py`;
- `results/raichu_search_to_seal_access/README.md`;
- `results/raichu_search_to_seal_access/reproduce.py`;
- `.github/workflows/validate-agent2-raichu-search-to-seal.yml`.

This exact deck-specific continuation admits two executable gate-completion policies after the direct-ready Forest Seal result: Quick Ball -> Crobat V -> Forest Seal Stone, and a Prize-aware Ultra Ball pivot that takes Crobat V after deck inspection shows Alolan Raichu is Prized.

Preserved 60-card one-draw results:

- direct baseline: 30.578700%;
- direct-ready typed Forest Seal: 33.139533%;
- search-completed typed Forest Seal: 34.466609%;
- gain from search-to-gate sequencing: 1.327077 percentage points;
- Quick Ball contributes 1.253545 points under disjoint attribution;
- the Ultra Ball pivot contributes 0.073531 points after Quick Ball overlap;
- 0.763831 points of the Quick Ball gain occur where the one-card discard is payable but the two-card connector cost is not;
- target-Prized conditional access rises from 31.781059% to 33.825012%;
- the ungated Forest Seal abstraction still overstates access by 5.794962 points.

The model exactly marginalizes irrelevant Prize identities and was independently checked by exhaustive labeled-card enumeration on a 13-card case. It reproduces the preceding direct baseline, direct-ready Forest Seal, and ungated Forest Seal probabilities.

Interpretation: searchable gate pieces recover part of a typed prerequisite gap, but the path's payment threshold matters. Quick Ball's cheaper discard cost makes it much more valuable for this specific gate-completion role than Ultra Ball despite both reaching Crobat V.

Next deck-specific continuation: model Crobat V Dark Asset after search-to-Crobat with hand-size-dependent draw volume. A useful orthogonal check is to execute representative Quick Ball and Ultra Ball witnesses through the repository's conserved Trainer transaction and turn-budget kernels.


## 2026-10-07 first-order Crobat V Dark Asset continuation

Created:

- `tools/raichu_dark_asset_search.py`;
- `results/raichu_dark_asset_search/README.md`;
- `results/raichu_dark_asset_search/reproduce.py`;
- `.github/workflows/validate-agent2-raichu-dark-asset.yml`.

This layer starts from the 34.466609% search-completed Forest Seal result and credits direct Alolan Raichu, Forest Seal Stone, or Gladion hits from Dark Asset after Quick Ball or Ultra Ball searches a deck-resident Crobat V.

Exact 60-card outputs:

- search-completed Forest Seal access: 34.466609%;
- plus first-order Dark Asset: 35.092509%;
- incremental Dark Asset gain: 0.625900 percentage points;
- Quick Ball search-to-Crobat + Dark Asset contributes 0.512479 points;
- Ultra Ball search-to-Crobat + Dark Asset contributes 0.113421 points;
- 71.4595% of the increment occurs while Raichu remains in deck;
- 28.5405% occurs in target-Prized states;
- target-Prized conditional access rises from 33.825012% to 35.601961%, a 1.776949-point gain.

A key new mechanism is cost-to-draw coupling. At this snapshot, Quick Ball's play plus one-card discard leaves five cards after the searched Crobat is benched, so Dark Asset draws one. Ultra Ball's play plus two-card discard leaves four, so Dark Asset draws two. Higher discard cost still requires more acceptable material and can destroy valuable identities, but once paid it increases this specific downstream draw-to-six bandwidth.

The independent 14-card labeled regression exhausts opening, Prize, ordinary draw, and every possible one- or two-card Dark Asset sample after a physical Crobat search. It includes two labeled Crobat and two Gladion copies and matches every category-model metric.

Next useful continuation: bounded follow-up actions from Dark Asset draws, with one-use Dark Asset, Item costs, Supporter bandwidth, VSTAR budget, Bench capacity, and K0/K1 timing. Orthogonal validation through conserved Trainer transactions remains worthwhile.


## 2026-10-07 belief-weighted Raichu discard safety

Created:

- `results/raichu_belief_weighted_discard/README.md`;
- `results/raichu_belief_weighted_discard/reproduce.py`;
- `.github/workflows/validate-agent2-raichu-belief-discard.yml`.

This composes `belief_weighted_discard_policy.py` with the physical Quick Ball -> Crobat V bridge and literal Gladion Prize rescue.

Representative K0 snapshot: Alolan Raichu has not appeared among eight observed opening/draw cards, so after conditioning the binary target-zone posterior is 46/52 in deck and 6/52 Prized. Every one-card Quick Ball discard is mechanically legal.

Exact continuation safety:

- discard A/B/C: 100%;
- discard visible Gladion: 46/52 = 88.461538%.

When Raichu is in deck, Dark Asset can directly expose it and Gladion is unnecessary for the narrow endpoint. When Raichu is Prized, the line requires preserving Gladion for literal Prize rescue. This makes Gladion's discardability belief-dependent before K1.

With illustrative local DCI scores A=0.6, B=0.9, C=0.7, Gladion=1.0, a hard endpoint-safety constraint chooses B under K0. Under K1, the safe choice becomes Gladion in the target-in-deck world and B in the target-Prized world; expected safe DCI is 0.988462 versus 0.9 for the K0 robust choice.

CI run 37596314709 passed.

Concurrent broadcast from agent43 (`results/k0_discard_reacquisition_bias/`) independently found a closely related K0 hidden-information boundary in the Aichi Vileplume Secret Box context. Treat the two results as complementary: agent43 quantifies observation-policy bias in a symmetric replacement problem, while this result grounds belief-dependent DCI in a concrete Raichu/Gladion physical continuation.

Best next deck-specific extension: replace the binary single-visible-Gladion abstraction with Harto's actual two-Gladion package and allow the backup copy to occupy deck or Prizes. Measure when redundancy makes discarding the visible Gladion safe, including multi-Prize collapse where both rescue copies become inaccessible.


## 2026-10-07 two-Gladion redundancy under K0

Created:

- `results/raichu_two_gladion_belief_discard/README.md`;
- `results/raichu_two_gladion_belief_discard/reproduce.py`;
- `.github/workflows/validate-agent2-raichu-two-gladion-belief-discard.yml`.

This restores Harto's actual second Gladion after the first belief-weighted discard result.

Representative snapshot: one Gladion visible in hand, Alolan Raichu and the backup Gladion both among 52 unseen cards, six Prizes. Exact grouped hypergeometric masses are:

- neither Prized: 78.054299%;
- only backup Gladion Prized: 10.407240%;
- only Raichu Prized: 10.407240%;
- both Prized: 1.131222%.

The physical continuation model makes discarding the visible Gladion safe in all worlds except the joint-Prized collapse world. Therefore visible-Gladion discard safety is 98.868778%; ordinary A/B/C discards are 100% safe.

With the illustrative DCI scores from the first result, a hard K0 safety requirement still chooses B at 0.9. Exact K1 permits the visible Gladion in every non-collapse world, raising expected safe DCI to 0.998869.

CI run 37596742837 passed.

Important interpretation: redundancy is a belief-state property, not a fixed decklist count. The second copy only protects the discard if it is itself materially reachable.

Best next step: replace existential backup reachability with timed access. The current target-Prized / visible-Gladion-discarded branch credits an exact Dark Asset hit whenever backup Gladion is in deck. A timed model should quantify how often that backup is actually exposed before the rescue deadline, ideally preserving one-Supporter bandwidth and alternative typed connectors.


## 2026-10-07 timed backup Gladion access

Created:

- `tools/raichu_backup_gladion_timing.py`;
- `results/raichu_backup_gladion_timing/README.md`;
- `results/raichu_backup_gladion_timing/reproduce.py`;
- `.github/workflows/validate-agent2-raichu-backup-gladion-timing.yml`.

This tightens the two-Gladion redundancy result after a specific information boundary: visible Gladion was discarded for Quick Ball, Quick Ball successfully found Crobat V, and deck inspection establishes Alolan Raichu is Prized.

With Raichu fixed in one Prize slot and Crobat fixed as the searched deck card, 50 unresolved locations remain: five remaining Prize slots and 45 post-search deck positions. The backup Gladion is therefore in deck with probability 45/50 = 90%.

Timed random access is much smaller. One Dark Asset exposure reaches the singleton in 1/50 = 2% of these conditioned worlds. Two random deck exposures reach it in 4%; h distinct exposures reach it with exact probability h/50 for h <= 45. A ready deterministic preserving connector can reach the 90% topology ceiling if its own gates are already satisfied.

The reproducer independently enumerates all 50 labeled unresolved locations and matches the analytic values. CI run 37597414097 passed.

Interpretation: redundancy has at least three layers: another copy exists, that copy survives Prizes, and that copy is accessible before the deadline. The 98.868778% prior hidden-world existential safety, this result's 90% post-search topology ceiling, and 2% same-turn Dark Asset access measure different conditionings and must remain separate.

Best next continuation: add real deterministic connector gates in this post-search K1 state. Computer Search should recover the backup whenever it is in deck and two residual disposable cards exist. Forest Seal Stone should do so when Crobat V is in play, Forest Seal Stone is available/attachable, and the VSTAR Power is unused.


## 2026-10-07 Forest Seal physical backup rescue

Created:

- `tools/forest_seal_star_alchemy.py`;
- `results/raichu_backup_gladion_forest_seal_execution/README.md`;
- `results/raichu_backup_gladion_forest_seal_execution/reproduce.py`;
- `.github/workflows/validate-agent2-raichu-backup-gladion-forest-seal.yml`.

This closes the physical Forest Seal branch implied by the timed backup result. Bundled card data confirms Forest Seal Stone `swsh12-156` gives an attached Pokémon V Star Alchemy and limits the player to one VSTAR Power per game.

The new bridge uses the existing board-object and lock-channel layers. Successful line:

`Forest Seal Stone -> Crobat V -> Star Alchemy: backup Gladion -> Gladion: Prized Alolan Raichu`

It preserves the ordinary Supporter window through Star Alchemy, then consumes that window only when Gladion resolves literally.

Regression rejects the line under Tool play lock, occupied Tool slot, spent VSTAR Power, holder Ability suppression, Tool-effect suppression, non-V holder, and backup Gladion in Prize. CI run 37598121144 passed.

Interpretation: a deterministic connector can attain the post-search 90% backup-in-deck topology ceiling only after its own physical host, attachment, suppression, and global-resource gates are satisfied. This is complementary to the existing Computer Search branch, which replaces those gates with a two-card residual discard payment.

Next quantitative target: conditional connector race / union after K1, preserving overlap among Dark Asset direct exposure, Computer Search exposure + payment, and Forest Seal exposure + physical gates rather than summing marginal access.


## 2026-10-07 conditioned backup connector race

Created:

- `tools/raichu_backup_connector_race.py`;
- `results/raichu_backup_connector_race/README.md`;
- `results/raichu_backup_connector_race/reproduce.py`;
- `.github/workflows/validate-agent2-raichu-backup-connector-race.yml`.

Conditioning is the post-Quick-Ball K1 state: visible Gladion already discarded, Crobat successfully searched, Raichu known Prized, and backup Gladion + Computer Search + Forest Seal Stone all unresolved among 50 positions (5 remaining Prizes, 45 shuffled deck).

One Dark Asset exposure gives exact direct backup access 1/50 = 2%. If Computer Search's residual two-card discard gate is live, drawing Computer Search contributes `(1/50)*(44/49)=1.795918%`; Forest Seal Stone contributes the same positional mass when its Tool/VSTAR/Ability gates are live. These top-card events are disjoint, so both connectors plus direct draw reach 5.591837%.

The backup-in-deck topology ceiling remains 90%, leaving 84.408163 pp stranded in this one-card exposure snapshot even with both connector gates live.

The reproducer exhaustively enumerates distinct placements of backup Gladion, Computer Search, and Forest Seal Stone across all 50 unresolved positions and matches the analytic result for all four gate combinations. CI run 37598420852 passed.

Best next work: reconnect this clean conditional race to the full Harto state distribution. Carry the five-card post-Quick-Ball hand and exact residual discard identities so Computer Search payability and Forest Seal exposure are endogenous rather than boolean inputs.
