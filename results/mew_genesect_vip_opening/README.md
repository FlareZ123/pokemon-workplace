# Aichi 2026 Mew VMAX / Genesect V: fourth Battle VIP Pass opening frontier

**Question.** How much does replacing the second Special Red Card with a fourth Battle VIP Pass improve first-turn access to a Mew V alongside two or three Genesect V, before resolving any other draw or search effect?

**Baseline.** Yamato Nakano's May 10, 2026 fifth-place Aichi Open League list, already transcribed and print-checked by the project in [competitive_deck_baselines](../competitive_deck_baselines/mew_genesect_reproduce.py). Tournament counts: https://www.limitlesstcg.com/tournaments/566/decklists. The experimental counterfactual differs only by **+1 Battle VIP Pass (swsh8-225), −1 Special Red Card (me4-82)**. It keeps 14 Pokémon, 42 Trainers, four Double Colorless Energy, 11 opening Basics, and one ACE SPEC.

## Exact first-turn source-access probabilities

A legal seven-card opener contains at least one Basic. Six cards occupy the hidden Prize zone and the first turn's natural draw supplies one additional visible card. The player may put naturally held Basics into play. Every naturally held Battle VIP Pass can be played on this first turn, retrieving up to two *unprized* Basic Pokémon directly onto the Bench per use. The requested Pokémon may occupy the Active Spot or Bench. Unneeded naturally held Basics need not be Benched, and both objectives fit ordinary Bench capacity even when another Basic starts Active.

### All held VIP Passes may resolve (rules-faithful source-only model)

| Required first-turn board | Published 3 VIP: direct | Published 3 VIP: VIP extra | Published 3 VIP: combined | Four VIP: combined | Fourth VIP gain |
| --- | ---: | ---: | ---: | ---: | ---: |
| Mew V + 2 Genesect V | 3.902404359% | 28.354476423% | **32.256880782%** | **40.058393597%** | **+7.801512815 pp** |
| Mew V + 3 Genesect V | 0.250309888% | 11.663533105% | **11.913842993%** | **16.791066902%** | **+4.877223909 pp** |

The four-VIP version's VIP-only additions are **36.155989238%** and **16.540757014%**. These rows permit two or more naturally held Battle VIP Passes to be played sequentially, subject to unprized search targets and Bench capacity.

### One VIP Pass maximum (controlled ablation)

| Required first-turn board | Published 3 VIP: union | Four VIP: union | Fourth VIP gain |
| --- | ---: | ---: | ---: |
| Mew V + 2 Genesect V | 31.616580206% | 38.866894354% | +7.250314147 pp |
| Mew V + 3 Genesect V | 9.044617339% | 11.433180079% | +2.388562740 pp |

The one-Pass cap is an experimental restriction, and its smaller result illustrates the importance of jointly modeling multiple Item activations. Direct naturally held Mew and Genesect access remains invariant under the swap because all Basic-Pokémon counts are unchanged.

The denominator conditions on a valid seven-card opening hand, with unconditional probability 1 − C(49,7)/C(60,7). For every eight-card visible multiset, the exact calculation accounts for which one card could be the natural turn draw while leaving a Basic-valid opener. Each Prize composition is enumerated from the remaining deck; no Prized target can be retrieved.

## Reproduction and validation

- [reproduce.py](reproduce.py) returns exact rational weighted counts with integer combinatorial weights for each event.
- A separately implemented labeled-card oracle exhaustively enumerates 46,620 valid hand/Prize/turn-draw worlds for each of two twelve-card toy decks containing one or two VIP Passes. The exact solver agrees for direct, VIP-only, and combined access with both one- and two-Genesect demands, and with either one or every held VIP allowed.
- Fixed-seed 100,000-shuffle tests for both 60-card compositions and both VIP-play limits independently check the grouped calculation; each produces 77,832 accepted Basic-valid openings and agrees within 0.6 percentage points.
- The reproduction calls the project's authoritative snapshot print checker for both 60-card lists, including the counterfactual four VIP and remaining one Special Red Card. It requires construction validity and conservative paper Expanded eligibility as of October 12, 2026.
- GitHub Actions Windows regression: validate-mew-genesect-vip-frontier.yml. Run from repository root using: python -m results.mew_genesect_vip_opening.reproduce.

## Naturally held Trainers' Mail finding VIP Pass

[trainers_mail_vip_bridge.py](trainers_mail_vip_bridge.py) adds the published list's **three Trainers' Mail** (xy6-92). Each playable Mail inspects the top four cards of the remaining deck. It takes one Battle VIP Pass when seen and shuffles the other cards back into the deck; Mail cannot retrieve another Mail under its printed card text. Several naturally held Mail copies may each perform this search sequentially, and several retrieved or held VIP Passes may each Bench up to two unprized Basics.

| Required first-turn board | Published VIP3 with Mail | Experimental VIP4 with Mail | +Fourth VIP |
| --- | ---: | ---: | ---: |
| Mew V + 2 Genesect V | **37.120816259%** | **45.728999471%** | **+8.608183212 pp** |
| Mew V + 3 Genesect V | **14.602422392%** | **20.566011923%** | **+5.963589530 pp** |

The bridge includes the same Basic-valid initial seven-card condition, six hidden Prizes, and first natural draw. Every Mail inspection is integrated analytically over the *unprized* remaining deck. A Mail hit physically removes one VIP from the deck; a miss leaves the deck size unchanged. Subsequent inspections are sampled after the mandated shuffle. Top-four draws are random under the shuffled-deck assumption, and the policy always selects VIP when available.

The independent oracle exhausts **10,500 labeled valid starting-hand / Prize / natural-draw deals** of a ten-card two-Mail toy deck, then enumerates all top-two inspection choices after each Mail branch. Its exact probabilities match the grouped calculation for two separate target requirements. Disabling Mail reproduces the earlier all-held-VIP exact model identically.

This study intentionally excludes Mail's alternative Trainer choices and does not combine the Mail route with payable Quick Ball/Ultra Ball or with Genesect draws. Thus the three source-only, paid-Ball, and Mail tables quantify different restricted windows; their percentages must not be added together. Neither the improved setup access nor its hypothetical card swap is a demonstrated match-win advantage.

## Paid Quick Ball and Ultra Ball extension

The published deck and variant each retain **four Quick Ball and four Ultra Ball**, in addition to the Battle VIP Pass copies. [paid_ball_frontier.py](paid_ball_frontier.py) adds these sources with their actual printed costs: Quick Ball consumes one other hand card for one Basic Pokémon; Ultra Ball consumes two other hand cards for one Pokémon. Both may acquire a missing Mew V or Genesect V from the unprized deck. All naturally exposed Pass, Quick Ball, and Ultra Ball copies are shared physical resources and each copy is usable at most once. Quick Ball is allocated before Ultra Ball when maximizing only the number of Basic searches from the same approved discard pool.

Because the real discardability of other cards depends on state and matchup, this model designates exactly **D other, non-Basic deck cards as safe discard payment** and protects every other non-Basic card. The D categories are hypothetical sensitivity policies on the otherwise unchanged sixty-card decks, with D held cards as the only allowed Ball discards. Draw Abilities, Trainer Mail, Secret Box, and cards newly drawn or searched by those effects remain excluded.

| Board target | D safe cards | Published 3 VIP with paid Balls | Four VIP with paid Balls | Fourth VIP gain |
| --- | ---: | ---: | ---: | ---: |
| Mew V + 2 Genesect V | 0 | 32.256880782% | 40.058393597% | +7.801512815 pp |
| Mew V + 2 Genesect V | 6 | 38.246260181% | 45.874230398% | +7.627970217 pp |
| Mew V + 2 Genesect V | 12 | 44.049425752% | 51.407525025% | +7.358099273 pp |
| Mew V + 2 Genesect V | 24 | 53.386342601% | 60.019573174% | +6.633230574 pp |
| Mew V + 3 Genesect V | 0 | 11.913842993% | 16.791066902% | +4.877223909 pp |
| Mew V + 3 Genesect V | 6 | 16.521479564% | 22.223912880% | +5.702433316 pp |
| Mew V + 3 Genesect V | 12 | 20.523005698% | 26.834820308% | +6.311814610 pp |
| Mew V + 3 Genesect V | 24 | 26.256085577% | 33.100660270% | +6.844574694 pp |

**Sensitivity inversion.** As safe payment density grows, the incremental fourth-VIP advantage *decreases* for the two-Genesect goal, while it *increases* for the three-Genesect goal over the examined D values. Extra searchable capacity has different marginal returns at different simultaneous target demands.

The calculation conditions on Basic-valid seven-card starts, considers the first natural draw, and integrates all six Prizes. It marginalizes non-target Prize categories only after demonstrating that this endpoint depends on Prize placement solely through the remaining Mew and Genesect counts. Four independent twelve-card exhaustive physical deal tests, each comprising 46,620 valid labeled worlds, reproduce the grouped direct, VIP-only and paid-Ball counts. A separate brute-force paid-Item allocation oracle checks every Quick/Ultra payment combination across 250 small hand-resource configurations. The D=0 case provably reduces to the all-VIP source-only result.

## Exact joint Ball-first → Trainers' Mail → VIP Pass sequence

The separate paid-Ball and Mail results are strongly overlapping. [combined_mail_ball_frontier.py](combined_mail_ball_frontier.py) constructs the **joint first-turn sequence** under one physical approved-discard pool: perform paid Quick Ball/Ultra Ball searches for missing Mew/Genesect targets, shuffle the smaller remaining deck, inspect its top four with each naturally held Trainers' Mail, take VIP Pass if present, and play the held/fetched VIP Passes for any remaining Basic targets. Each source can act once per physically held copy. Quick Ball costs one approved hand card and Ultra Ball costs two; only the exogenous D designated otherwise-unused other cards may fund these searches.

| Board target | D protected-policy safe cards | Published VIP3 + paid Ball + Mail | VIP4 candidate + paid Ball + Mail | Fourth VIP gain |
| --- | ---: | ---: | ---: | ---: |
| Mew V + 2 Genesect V | 0 | 37.120816259% | 45.728999471% | +8.608183212 pp |
| Mew V + 2 Genesect V | 6 | **43.036318802%** | **51.414233600%** | **+8.377914798 pp** |
| Mew V + 2 Genesect V | 12 | 48.695370189% | 56.737992550% | +8.042622360 pp |
| Mew V + 2 Genesect V | 24 | 57.596988300% | 64.784901514% | +7.187913214 pp |
| Mew V + 3 Genesect V | 0 | 14.602422392% | 20.566011923% | +5.963589530 pp |
| Mew V + 3 Genesect V | 6 | 19.816099967% | 26.602450225% | +6.786350258 pp |
| Mew V + 3 Genesect V | 12 | 24.274709384% | 31.649058552% | +7.374349168 pp |
| Mew V + 3 Genesect V | 24 | 30.439123780% | 38.268255407% | +7.829131627 pp |

**Why Ball-first?** When a Ball can physically pay using only designated safe cards and retrieve a needed unprized Basic, removing that Basic from the deck shrinks Mail's search population while retaining every remaining VIP Pass. This weakly improves the chance of Mail seeing a VIP compared with resolving Mail first, for this narrow all-or-nothing setup objective. No discard opportunity cost is assigned inside the permitted D pool, and the model does not reward preserving unused Balls for later turns.

The solver conditions on a Basic-valid opening, exactly six Prizes, the first natural draw, the actual card counts, and deck-card conservation after each search. Three ten-card toy populations, with Mew/Genesect goals of one or two, each undergo an exhaustive independent 10,500-deal physical hand/Prize/draw oracle plus every random Mail-inspection branch, six independently verified cases. Algebraic reductions prove that D=0 equals the Mail-only model, disabling Mail equals the paid-Ball-only model, and the union result weakly dominates both for each tested state.

The D marker is a **policy hypothesis**, not a factual designation of which actual tournament-list cards are discardable. Real hands contain protected Supporters, search pieces, and tactical singletons; opponent lock effects and draw Ability sequencing may reverse a specific card-choice policy. These probabilities still measure a sharply restricted setup event rather than games won.

## The lost second Special Red Card: a late-game access counterweight

The tournament baseline contains **two Special Red Card**, whereas the experimental fourth-VIP list retains only one. The exact printed `me4-82` Item is playable only when the opponent has **three or fewer Prize cards remaining**. It puts the opponent's hand at the bottom of their deck and, if cards were put there, makes them draw three cards. The discarded copy therefore has a conditional disruption role that a first-turn setup metric cannot score.

[special_red_access_frontier.py](special_red_access_frontier.py) gives an exact, independent natural-exposure proxy: *conditional on a Basic-valid seven-card opening*, the probability of seeing at least one Special Red Card in the opening hand plus `r` subsequently drawn unprized cards. It integrates random six-card Prizes. No Red is presumed discarded, and the card's opponent-Prize threshold must be met independently.

| Cards drawn beyond starting seven | Original 2 Red naturally seen | Candidate 1 Red naturally seen | Natural access lost |
| ---: | ---: | ---: | ---: |
| 1 | 23.807914225% | 12.598307692% | −11.209606533 pp |
| 3 | 29.611383805% | 15.959911242% | −13.651472563 pp |
| 6 | 37.885637464% | 21.002316567% | −16.883320897 pp |
| 10 | 48.113534348% | 27.725523668% | −20.388010680 pp |
| 14 | 57.422069714% | 34.448730769% | −22.973338945 pp |
| 20 | 69.661069918% | 44.533541420% | −25.127528498 pp |

This is a **different endpoint** from the first-turn Mew/Genesect source-access percentages. More natural Red exposure does not by itself mean the opponent reaches the qualifying three-Prize threshold, the player retains the Item, an Item play is legal under a lock, or that a three-card hand reset has tactical value in that matchup. Actual Genesect draws can increase exposure; Trainers' Mail and other search connectors are excluded. Six Prize identities are averaged out before random future draws, and an independent labeled-opening/Prize/draw oracle tests exact small populations with zero, one and two Red copies.

The early VIP improvement and late Special Red availability loss have no common win-probability conversion established. The fourth VIP may be promising, but the exact card cut is an unresolved optimization choice. Other non-Basic cuts can preserve both Special Red copies while sacrificing different tactical effects, which requires matchup-aware comparison.

## Sixth-variant slot-cut sensitivity (legal 60-card candidate frontier)

The precise fourth-VIP cut matters. [vip_slot_cut_frontier.py](vip_slot_cut_frontier.py) tests six complete exact-print and conservatively paper Expanded-eligible 60-card alternatives: published three-VIP list; fourth VIP at the expense of one Special Red Card, Trainers' Mail, Quick Ball, Ultra Ball, or Karen. All preserve the original 11 opening Basic Pokémon and one Secret Box ACE SPEC.

The shared, exact paid-Ball → Mail → VIP first-turn **Mew V + 2 Genesect V** benchmark distinguishes cuts of cards that directly contribute to the modeled setup:

| Full 60-card candidate | D=6 joint setup | D=12 joint setup |
| --- | ---: | ---: |
| Published 3 VIP | 43.036318802% | 48.695370189% |
| +1 VIP, −1 Special Red Card | **51.414233600%** | **56.737992550%** |
| +1 VIP, −1 Trainers' Mail | 49.624790597% | 55.019725095% |
| +1 VIP, −1 Quick Ball | 50.346499309% | 54.889753885% |
| +1 VIP, −1 Ultra Ball | 51.228134805% | 56.061337026% |
| +1 VIP, −1 Karen | **51.414233600%** | **56.737992550%** |

The Mew V + 3 Genesect V endpoint at D=6 is 19.816099967% for the published list, 26.602450225% for −Red or −Karen, 25.148701796% for −Mail, 25.522444430% for −Quick, and 26.412245932% for −Ultra.

Cutting Ultra Ball rather than Special Red Card sacrifices only **0.186098795 percentage points** of the narrowly modeled D6 two-Genesect opening access. However, Ultra Ball also retrieves **Mew VMAX**, a non-Basic Evolution target that Battle VIP Pass and Quick Ball cannot find. This model does not score Stage-1 access, evolution timing, late-game Special Red disruption, Karen's discard-control value, or matchups. Similarly, the −Red and −Karen access tie reflects their identical retained source counts, and says nothing about whether those tactical effects are equivalent.

Four newly varied physical ten-card source distributions, each evaluated with two target requirements, agree with an independent labeled-card setup/Prize/Mail-inspection oracle. Printed card identities and all 60-card candidate constructions are validated by the shared paper Expanded checker.

## Countervailing Ultra Ball function: acquiring Mew VMAX

The narrow two-Genesect Basic access difference between cutting Ultra Ball and cutting Special Red Card cannot capture the lost **Evolution search**. [mew_vmax_ultra_frontier.py](mew_vmax_ultra_frontier.py) separately models access to at least one Mew VMAX (three copies in the tournament list) in the naturally visible eight cards or through **one** physically payable Ultra Ball, with an unprized Mew VMAX still in the deck. All six Prizes and the Basic-valid seven-card opener are integrated exactly; this event means acquiring an Evolution card for possible later use, since normal first-turn evolution is prohibited.

| Designated safely discardable copies | Natural held Mew VMAX | Four Ultra Ball: direct or payable search | Three Ultra Ball: direct or payable search | Search access lost |
| ---: | ---: | ---: | ---: | ---: |
| 0 | 33.759100285% | 33.759100285% | 33.759100285% | 0 pp |
| 4 | 33.759100285% | 35.684429083% | 35.265837540% | 0.418591543 pp |
| 6 | 33.759100285% | **38.040233151%** | **37.113331304%** | **0.926901847 pp** |
| 12 | 33.759100285% | 46.882391219% | 44.078132488% | 2.804258731 pp |
| 20 | 33.759100285% | 56.730142863% | 51.908345690% | 4.821797173 pp |

At D=6, the 0.9269-point Ultra Ball loss for acquiring Mew VMAX is almost five times the 0.1861-point loss in the *separate* Mew+two-Genesect first-turn board metric. The increased relative effect at D=12 reflects that discard payment is no longer as much of the limiting factor.

This Stage-1 acquisition event does not simultaneously require the Mew V + Genesect setup and does not reserve a Ball or two discard cards for competing Basic searches. It therefore overstates realizable *joint* setup readiness. An independent physical labeled-card oracle exactly matches 34,272 valid toy hand/Prize/draw configurations for each of three Ultra counts, and printed English Ultra Ball/Mew VMAX identity is checked from the bundled database.

## Strategic interpretation and limitations

This is a **narrow first-turn source-access study**. The all-VIP table omits the Ball routes; the paid-Ball extension adds Quick Ball and Ultra Ball with explicit hypothetical discharge policies. Both models omit Trainers' Mail, Secret Box, Dedenne-GX, Crobat V, Genesect V's Fusion Strike System, Forest Seal Stone, further natural turns, Energy attachments, VMAX evolution, and opponent interaction. It does not model match wins. Genesect's Ability draw size also depends on hand size and the number of Fusion Strike Pokémon in play, so an extra Genesect is not a fixed card-draw reward.

The fourth VIP has a substantial measurable access benefit under this restriction. The removed Special Red Card has disruption value that this model does not score. This candidate is a **legal experimental deck**, pending richer line modeling and diverse matchup evaluation.

## Complete 60-card exact-print candidate

Machine-readable complete list: [variant.json](variant.json).

### Pokémon (14)

| Qty | Card | Exact English print |
|---:|---|---|
| 4 | Mew V | swsh8-113 |
| 3 | Mew VMAX | swsh8-114 |
| 4 | Genesect V | swsh8-185 |
| 1 | Dedenne-GX | sm10-57 |
| 1 | Crobat V | swsh3-104 |
| 1 | Lillie's Clefairy ex | sv9-56 |

### Trainers (42)

| Qty | Card | Exact English print |
|---:|---|---|
| 2 | Guzma | sm3-115 |
| 2 | Karen | xyp-XY177 |
| 1 | Wally | xy6-94 |
| 1 | Marnie | swsh1-169 |
| 1 | Pokémon Ranger | xy11-104 |
| 4 | Quick Ball | swsh1-179 |
| 4 | Ultra Ball | swsh9-150 |
| 3 | Trainers' Mail | xy6-92 |
| 4 | Battle VIP Pass | swsh8-225 |
| 2 | Special Charge | xy11-105 |
| 2 | VS Seeker | xy6-110 |
| 1 | Special Red Card | me4-82 |
| 1 | Enhanced Hammer | sv6-148 |
| 1 | Field Blower | sm2-125 |
| 1 | Lost Vacuum | swsh11-162 |
| 1 | Escape Rope | swsh5-125 |
| 1 | Hisuian Heavy Ball | swsh10-146 |
| 1 | Secret Box | sv6-163 |
| 2 | Muscle Band | xy1-121 |
| 2 | Float Stone | xy8-137 |
| 1 | Forest Seal Stone | swsh12-156 |
| 2 | Sky Field | xy6-89 |
| 2 | Path to the Peak | swsh6-148 |

### Energy (4)

| Qty | Card | Exact English print |
|---:|---|---|
| 4 | Double Colorless Energy | sm1-136 |

