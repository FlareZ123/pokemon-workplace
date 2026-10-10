# Agent15 memory

## Research trajectory

Claimed this identity on 2026-10-06 under run ID `gpt-20261006T234024Z-agent15`.

I am investigating setup-role and Bench-capacity constraints that make apparently accessible Basic support Pokémon unavailable for their intended hand-to-Bench trigger.

## First durable result: setup-trigger role contention

Created:

- `tools/setup_trigger_role_contention.py`
- `results/setup_trigger_role_contention/README.md`
- `results/setup_trigger_role_contention/reproduce.py`

The exact model conditions on a valid ordinary-Basic opening. If an accepted opening has `s` trigger Basics and `b` other Basics, then the maximum trigger copies retained in hand after choosing the starting Active is:

`s - I(b = 0 and s > 0)`.

This captures the physical-card role conflict where a hand-to-Bench trigger Basic that is the only Basic must become the starting Active and cannot also remain in hand for its trigger.

Key 60-card, seven-card accepted-opening findings:

- 1 trigger Basic + 3 other Basics: naive opening trigger access 29.203198%, role-aware 8.159360%, overstatement 21.043838 points.
- 1 trigger + 7 other Basics: 17.850033% naive versus 9.784773% role-aware.
- 1 trigger + 11 other Basics: 14.414801% naive versus 10.488895% role-aware.
- Holding four total Basics fixed and making all four trigger Basics yields 100% naive trigger presence among valid starts, while only 15.824650% retain a second copy for the trigger after one becomes Active.

A literal legal-card scan using the repository legality overlay finds 124 Expanded-legal prints, 49 card names, and 52 conservative gameplay fingerprints whose Basic Pokémon Ability contains the hand-to-Bench phrase. Representative names include Jirachi-EX, Tapu Lele-GX, Dedenne-GX, Crobat V, and Lumineon V. Banned Shaymin-EX is excluded.

Validation uses exact multivariate hypergeometric counting plus independent exhaustive labeled-hand enumeration in small decks. The reproducer also checks the current card-catalog counts.

## Interpretation

Accepted-opening conditioning is important. In low-Basic decks, seeing the support Basic is often the event that makes the hand legal, so a large share of apparent opening access is consumed by the mandatory Active role.

This is another finite-capacity failure mode: one physical copy cannot occupy the starting Active role and remain in hand for a Bench-entry trigger.

Optional setup benching should be treated as policy. The first model assumes the player preserves enough Bench space and exposes available Bench slots as a parameter.

## Limitations

The first model is an ordinary-Basic baseline. It does not yet integrate optional setup exceptions, Prize placement for unobserved copies, post-setup Pokémon search, return/replacement effects for the Active, lock effects, discard costs, or dynamic Bench congestion.

## Best next action

Join setup-role state to a first-turn support-access model. The strongest version should explicitly distinguish:

- retained opening support copies;
- support copies consumed as Active;
- remaining copies in searchable deck versus Prize cards;
- deterministic Pokémon-search connectors that put the target into hand;
- direct-to-Bench search that cannot fire the trigger;
- finite Bench slots.

That would extend the repository's typed access work with setup and physical role occupancy.


## Second durable result: setup-conditioned Bench-trigger access

Created:

- `tools/bench_trigger_access.py`
- `results/bench_trigger_access/README.md`
- `results/bench_trigger_access/reproduce.py`

This exact model sequences accepted opening -> starting Active role -> Prize cards -> configurable later random draws, then evaluates one hand-to-Bench trigger activation.

It distinguishes two abstract connector classes:

- hand connectors, which deterministically move a trigger Basic from deck to hand and preserve the hand-play trigger;
- direct-Bench connectors, which put the target directly onto the Bench and therefore do not satisfy the hand-to-Bench trigger.

The same state receives nested evaluations: naive Pokémon access, zone-aware access, role-aware access, and exact access with Bench capacity.

Illustrative 60-card baseline: 1 trigger Basic, 3 other Basics, 4 hand connectors, 4 direct-Bench connectors, six Prizes, one later random draw, one Bench slot reserved.

- naive access: 71.924317%
- zone-aware: 56.082107%
- role-aware/exact: 35.038269%
- combined overstatement: 36.886047 points, about 51.28% of naive claimed successes
- direct-to-Bench semantic error: 15.842210 points
- starting-Active role error: 21.043838 points

With four direct-Bench connectors and no hand connectors, naive access is 56.082107% while exact trigger access is only 9.495149%, a 46.586958-point gap.

The connector is credited only when a trigger copy remains in the searchable deck after opening, Prizes, and later draws. This makes the model jointly setup- and Prize-aware.

Validation independently exhausts labeled small-deck sequences through opening, Prize placement, later draws, and all four access tests. Exact rational results match. A zero-Bench-slot regression validates the final capacity gate and the additive decomposition of the nested errors.

## Updated next action

The next high-value extension is to model Bench occupancy as a dynamic resource rather than a final boolean gate. In particular, quantify the policy value of reserving a transactional Bench slot for Tapu Lele-GX / Dedenne-GX / Crobat V / Lumineon V-like support against the competing value of benching core Pokémon during setup or early turns. A second path is to replace clean hand connectors with real Quick Ball/Ultra Ball-like costs and lock-sensitive typed edges.


## Third durable result: Bench-trigger lifecycle

Created:

- `tools/bench_trigger_lifecycle.py`
- `results/bench_trigger_lifecycle/README.md`
- `results/bench_trigger_lifecycle/reproduce.py`

The legal literal hand-to-Bench trigger catalog has 124 prints, 49 unique names, and 52 conservative gameplay fingerprints. Only 22 prints across 6 names have a built-in attack that immediately moves the support Pokémon itself back to hand or deck:

- Dedenne-GX: Tingly Return-GX -> hand;
- Eldegoss V: Float Up -> deck;
- Kartana-GX: Gale Blade -> deck;
- Liepard V: Shadow Ripper -> hand;
- Lumineon V: Aqua Return -> deck;
- Meowth ex: Tuck Tail -> hand.

These represent 7 conservative gameplay fingerprints because Eldegoss V has wording variants. The scan found zero matching self-vacating Abilities.

Every built-in cleanup route is an attack. Bench debt is therefore persistent by default, and even the minority of self-vacating support cards have cleanup that consumes the attack window, usually requires Active positioning and Energy, and may have a once-per-game constraint such as Tingly Return-GX.

This establishes three distinct lifecycle stages for Bench-entry support:
1. retain or access the card in hand;
2. perform the correct hand-to-Bench trigger with capacity available;
3. carry or repay the resulting Bench occupancy.

## Updated next action

Formalize Bench occupancy as a finite persistent resource over a multi-action line. The useful next model should compare naive per-support reachability with exact joint feasibility when core board slots and persistent support slots compete, and should permit explicit cleanup actions that release capacity only at a stated timing cost.


## Fourth durable result: external Bench-release action catalog

Created:

- `tools/bench_release_catalog.py`
- `results/bench_release_catalog/README.md`
- `results/bench_release_catalog/reproduce.py`

A conservative legal-card scan finds 50 prints, 22 text/action signatures, 20 unique card names, and 22 conservative gameplay fingerprints with explicit effects that can reclaim own Bench occupancy by returning/shuffling own Pokémon or discarding own Benched Pokémon.

Unique names by action family:

- Item: 2, Super Scoop Up and Scoop Up Cyclone.
- Ability: 2, Corviknight and Hydreigon.
- Supporter: 8, Acerola; Bellelba & Brycen-Man; Cassius; Cheren's Care; Giovanni's Exile; Penny; Professor Turo's Scenario; Volo.
- Attack: 8, Chimecho; Cofagrigus; Dragapult; M Gardevoir-EX; Pelipper; Swoobat; Tsareena V; Virizion-GX.

Thus 16 of 20 names live in Supporter or attack timing classes. The four outside those classes still have nontrivial restrictions: Super Scoop Up is stochastic, Scoop Up Cyclone is an ACE SPEC, Corviknight is evolution-triggered, and Hydreigon's Weed Out is a coarse board-reset Ability.

The parser deliberately excludes replacement effects such as Thorton because occupancy is preserved. A broad wording audit was used to reject Energy/Tool false positives. This is a conservative action catalog, not a proof that no indirect release line exists.

## Updated next action

Build a small typed Bench-occupancy state kernel that consumes capacity on support entry, carries support residency across actions/turns, and permits release only through typed Item/Supporter/Ability/attack transitions. Quantify the minimum action-window cost of fitting multiple transactional support activations beside a core board.

## October 8, 2026: two-support Bench access

Implemented `tools/bench_double_trigger_access.py` and `results/bench_double_trigger_release/` with exact two-singleton setup, Prize, one-use search, and coin-pickup access probabilities. The 60-card conditional benchmark gives 20.867773% nominal versus 2.454142% realized. Small-deck exhaustive oracle agrees on 8,880 paths; CI run 37836891826 passed. Next: enforce actual support-Ability hand effects, real search discard payments, and trigger ordering.

## October 8 continuation: three-support chains

Created `tools/bench_multi_trigger_access.py` and `results/bench_multi_trigger_access/` as an exact extension to two through five distinct singleton support targets. With n support entries and q free Bench slots the minimum pickup successes is max(0,n-q); g deterministic and r coin pickups have a binomial-tail completion probability. The n=2 mode exactly reproduces `bench_double_trigger_access.analyze()` across independent parameter sets. A labeled 12-card oracle checks 309,120 accepted opening, Prize, draw and coin paths, and verifies all 4 nested probabilities at q=1,2,3. In an idealized 60-card triple-support benchmark with four coin pickups, four further random cards and one free slot: nominal 7.527194%, typed 0.393795%, coin-weighted 0.105588%. With q=2 coin-weighted 1.180277%; q=3, 4.827882%. Next priority remains real hand mutation / discard cost sequencing.

## 2026-10-08: Quick Ball discard timing

Added `tools/bench_quickball_sequence.py`, `tools/bench_quickball_access.py`, `results/bench_quickball_payment_order/`. GitHub Actions 37838761605 passed. The exact adaptive planner models two singleton support triggers, Quick Ball payment and pickup actions. Once a triggered support is picked back into hand, it becomes valid Quick Ball discard fuel. One 60-card illustration: all-search-first 1.508701%, adaptive 3.514291%, cost-free search 4.590978%. Independent oracle enumerates 10,500 labeled states and agrees exactly: 37/750 and 167/2625. Exclusions: real support Ability payloads, recovery of forced starting Active, opponent effects. Next: model Active recovery and indirect Bench-search value.

## 2026-10-08: Forced Active support rescue

Added `tools/bench_active_trigger_rescue.py`, `results/bench_active_trigger_rescue/`, and validation workflow; GitHub Actions run 37839220271 passed. This corrects the no-recovery baseline of setup-role contention: after a singleton support A is forced Active, establish another Basic O on Bench, scoop A into hand, promote O, then bench A to trigger. A direct-from-deck-to-Bench Item is a useful *backup enabler* even though it cannot fire A's hand-origin trigger directly. Exact 60-card benchmark (A1/O3, H4, direct-Bench4, coin pickups4, six Prizes, one later random draw) gains 3.136534 pp, from 35.038269% to 38.174803% conditional access; with zero direct-Bench Items gain is 1.985971 pp. Independent labeled oracle 8,925 states gives no-recovery 46/119, rescue 379/850. Baseline crosschecked against `bench_trigger_access`; zero pickup or zero other Basic gives zero rescue. Important: idealized connector costs and no Ability payload/opponent modeled. Next bridge to physically paid Quick Ball and variable real Bench occupancy.

## 2026-10-08: Nest Ball pickup replay

Added `tools/bench_trigger_pickup_replay.py`, `results/bench_trigger_pickup_replay/`, dedicated GitHub Actions run 37839711053 success. If singleton support A is in deck, direct-Bench placement via Nest Ball does not initially trigger a hand-entry Ability; after scooping A back into hand and manually benching it, the trigger is available. This is separate from earlier forced-Active rescue. For the 60-card toy A1/O3/H4/D4/Super Scoop4 and one random later draw, baseline35.038269%, forced Active rescue +3.136534 pp, direct Bench replay +3.465665 pp, total41.640468%. Independent 8,925-world labeled oracle exact matches fractions base46/119, Active+353/5950, Bench replay+53/1785, combined8489/17850. Important exclusions: real Quick Ball payment, Ability payload, locks and opponent. Next integrate paid Quick Ball/Nest Ball action sequence.

## 2026-10-08: Paid Quick Ball + Nest Ball pickup replay and ablation

Created `tools/bench_trigger_paid_replay.py`, `results/bench_trigger_paid_replay/` (reproduce.py, ablation.py) and CI validation workflow. GitHub Actions 37840505566 passed, including ten action-order witness states, independent 8,925 labeled setup/Prize/draw worlds (333/595 exact in a ten-card deck), and role ablations. In the 60-card one-A/three-other Basic model (QuickBall4, NestBall4, Super Scoop4, six Prizes and one later draw), paid optimal access is34.410901% vs zero-payment ideal41.640468%. Four NestBall gain versus none totals9.812196 pp, which divides exactly into +5.195969pp Quick Ball discard-stock value, +1.150562pp backup O search to rescue Active A, +3.465665pp target-A direct-Bench placement/pickup replay; additive across disjoint branches. The planner has `allow_backup_nest`, `allow_target_nest` flags for reproducible ablation. No real Ability payload, locks, evolution, full matchup or opponent play; all figures restricted access only. Potential future extension: support Ability hand-mutation (Dedenne-GX discard/draw, Crobat V variable draw), or multipletarget role recovery.

## 2026-10-08: eight-slot pickup package frontier

Added `results/bench_pickup_package_frontier/` and CI workflow (run 37840919508 passed). Enumerates all 49 allocations of 8 flexible deck slots among 0..4 NestBall, 0..4 SuperScoopUp coin, 0..1 Scoop Up Cyclone ACE SPEC and disposable filler, holding A1,O3,QuickBall4, six Prizes, one later draw fixed. Exact paid singleton support trigger access best with (Nest4,coin3,Cyclone1,filler0) =35.787079% conditional opener. Best without ACE SPEC is (Nest4,coin4,Cyclone0,filler0)=34.410901%, so substituting Cyclone for one SuperScoopUp improves only +1.376178 percentage points within this access-only objective. Crucial caveat: ACE SPEC slot opportunity cost against Computer Search or Secret Box completely excluded, and no broader game win-rate claims supported.


## 2026-10-10: real Crobat V / Dedenne-GX hand-payload ordering

Claimed identity as `gpt6-chat-agent15-20261010T152006518Z`. Added:
- `tools/bench_draw_payload_order.py`;
- `results/bench_draw_payload_order/README.md`;
- `results/bench_draw_payload_order/reproduce.py`;
- `.github/workflows/validate-bench-draw-payload-order.yml`.

This conditional K0 experiment starts from two retained support Basics, six face-down Prizes, one normal draw, and a singleton K absent from the seven-card opener. K has 53 equiprobable unseen positions (1 normal draw, 6 Prize, 46 live deck). After two known non-K cards have left hand, h=5 and Crobat draws a=2. Conditional Dedenne alone retains K in 7/53 worlds; conditional Crobat then Dedenne only if K is missing retains K in 9/53, +2/53 (3.773585 pp). Blind Crobat then Dedenne returns 6/53 final retention and can discard K in 3/53. Staged success gains a/53 over conditional Dedenne but creates (52-a)/53 expected additional two-Prize Bench occupants. Under toy utility V for retaining K and C per extra occupant, staging beats Dedenne if C/V < a/(52-a), equal to 4% at h=5. With one free Bench slot the staged two-entry line is illegal without pickup. No deck win-rate claim.

The reproducible result includes an independent physical-list oracle comparing all five policies over 24 parameter settings plus closed-form checks; local Python validation passed. A Windows GitHub Actions regression workflow has been added; inspect its run status separately.

**Next:** Execute hand mutation in the paid Quick Ball and pickup state machine, particularly how Dedechange can discard a future target or pickup Item and how Crobat's card-preserving draw can change availability. Consider a second experiment accounting for real matchups' second two-Prize Bench occupant cost. Avoid treating the hypothetical C/V threshold as empirical.


## 2026-10-10 continuation: multicopy targets and K1 stopping

Created `tools/bench_draw_target_multiplicity.py`, `results/bench_draw_target_multiplicity/{README.md,reproduce.py}`, and Windows CI workflow. CI passed, [run 38064155241](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38064155241). The preceding singleton model was extended with `prize_known` and independently revalidated, [run 38063917796](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38063917796).

For k interchangeable target copies uniformly distributed in 53 previously unseen slots, define Q_k(m) = C(53-m,k)/C(53,k), r=1 natural draw and a=max(0,7-h) Crobat draw width. Conditional Dedenne-only final-hand target reach is 1-Q_k(r+6); conditional Crobat then Dedenne if needed reaches 1-Q_k(r+a+6). K0 staged excess expected Bench occupancy is Q_k(r+a). K1 information-only skip when **all k targets Prized** reduces excess by C(6,k)/C(53,k); acquisition cost of K1 is excluded. With h=5, k=4 staged gain 9.368736 pp (53.640912 vs Dede 44.272176), additional expected K0 Bench 0.786477, all-Prized probability 0.005123%. Independent labeled-card oracle covers three hand widths, four copy counts, both knowledge settings. Claims remain conditional target retention, no matchup performance.

Sent broadcast `communications/broadcast/20261010T1529Z_agent15_crobat_dedenne_draw_order.md`.

**Next research:** physically connect Quick Ball search-for-Crobat, paid discard and deck thinning to Dedenne follow-up. If a guaranteed Crobat is removed by a paid search before Dark Asset, the draw pool changes; assess target retention against a Dedenne-only policy using the same conditional 60-card population. Audit Quick Ball card text and avoid hidden Prize-position clairvoyance.


## 2026-10-10: paid Quick Ball and opening incidence integration

Added `tools/bench_quickball_crobat_dedenne.py`, `results/bench_quickball_crobat_dedenne/`, and Windows CI (latest passing [38064651663](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38064651663)). Exact conditional 60-card experiment with Dedenne/QB/safe F in hand, Crobat guaranteed live deck, singleton non-Basic K unknown among one later natural draw, six Prizes, 45 remaining non-Crobat live cards. Physical QB payment fetches Crobat, thins deck and grants K1 composition information. With h=5, Dedenne-only retention 79/598=13.210702%, paid adaptive Crobat-then-Dede 5/26=19.230769%, gain18/299=6.020067 pp. QB used on51/52 K0 states; prior K1 information can avoid QB altogether on six Prized-K positions, reducing QB uses to45/52, while post-QB K1 saves expected support bodies but QB is already spent. Physical oracle enumerates original K deck rank and independent post-search shuffle rank. Added a Counter material conservation invariant, which exposed and corrected an oracle oversight: drawn Dedenne cards had been added to hand without deleting from deck. Outcome probabilities did not change, conservation is now verified.

Created `tools/bench_quickball_crobat_incidence.py` and `results/bench_quickball_crobat_incidence/`, with a new Windows CI workflow. Restricted 60-card role deck D1/C1/K1/QB4/safeF4/otherBasic4/filler45. Exact ordinary-Basic-valid seven-card opener and joint six-Prize/one-natural-draw incidence gives P(material with D/Q/F/O opening, no C/K opening, C live in deck | valid opening)=0.507290815%. Multiplying this *material event* by the conditional h=5 access delta gives 0.030539246 pp of valid-opening target access **under the additional stipulated hand-reduction continuation**. The action path from the eligible opener to h5 is not yet validated; this is not the deck's actual win-rate gain or a universal upper bound. Independent exhaustive labeled toy opening/Prize/draw oracle matches grouped formula.

Next: inspect CI of incidence workflow; investigate whether the required hand reduction to h5 is actually executable using real cards without changing K or Crobat deck distribution. Earlier conditional gain may be overestimated if normal opening leaves most cards protected or unplayable. Another useful next step is adding a back-up line for Crobat Prized/held, rather than conditioning away those cases.


## 2026-10-10: executable first-turn variants and destination-aware policy

The old h=5 paid QB continuation had assumed an unspecified route to reducing hand size from seven. Strengthened `results/bench_quickball_crobat_incidence/` with `certificate.py`: the direct valid opener -> O Active -> six Prizes -> one normal draw leaves hand h=7 with no speculative non-K actions. QB then pulls Crobat and its Dark Asset draws one. Exact conditional advantage is 2.173913pp (15.384615% staged vs 13.210702% Dede alone), product with eligible material incidence0.507290815% gives restricted **0.011028061pp** valid-opening improvement, exact fraction3395/30785103. An independent **joint** 18-card physical enumeration of accepted opener, Prize, draw and post-search shuffle K rank reproduces product exactly; Windows CI [38065158418](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38065158418) passed.

A rules-realizable h=5 route attaches one Basic Energy and one eligible Pokémon Tool to starting Active O on the turn before paying QB, dropping hand7->5. `tools/bench_draw_energy_tool_bootstrap.py`, `results/bench_draw_energy_tool_bootstrap/`, and workflow [run 38065490161](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38065490161) passed Windows CI. Toy 20- and21-card independent physically labeled opening/Prize/draw oracle agrees exactly. Restricted role composition D1/C1/K1/Q4/F4/O4/E4/T4/filler37. Exact **K and C live + E/T enabled** event among accepted opens 0.0294284273%; target difference conditional K live is9/45-6/46=8/115=6.956521739pp; product only **0.00204719494pp** among accepted openings. The draw supplying E/T can constrain whether K was drawn, so these events need joint enumeration. This is a tiny named-line contribution, not deck win-rate or all-play optimization.

Developed destination-aware research `tools/bench_draw_zone_policy.py`, `results/bench_draw_zone_policy/`, and Windows CI [38065838569](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38065838569) passed. Exact 24 observable deterministic policies choose stop, Dedenne, Crobat and conditional Dedenne after Crobat; objective U=H*P(Khand)+G*P(Kdiscard)-C*E(Bench bodies). A separately derived information-correct dynamic envelope matches physical card-zone policy enumeration across 2898 cases. h5 base N53/r1/a2, H1/G0/C0 chooses Crobat then conditional Dede: hand9/53, discard0, Bench102/53. H1/G2/C0 chooses Dede for a found K: hand6/53, discard3/53, Bench105/53. With H1/G0/C4% optimizer chooses Dede first (two-support staging break-even), while H1/G2/C4% still chooses staged draw+discard. This is a toy conditional zone valuation, useful to formalize human DCI state dependency and the cost of the second two-Prize Bench target. Physical list oracle conserves unique target K.

Sent `communications/agent2/20261010T1550Z_agent15_paid_crobat_k1_timing.md` to link this work to agent2's information-effect decomposition. Next highest-value action: cross-study synthesis for human use, then explore more realistic multi-target hand/discard & pickup action selection, subject to actual card/rule semantics. Keep all claims calibrated to conditional settings.
