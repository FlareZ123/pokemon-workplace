# Aichi 2026 Mew VMAX / Genesect V: fourth Battle VIP Pass opening frontier

**Question.** How much does replacing the second Special Red Card with a fourth Battle VIP Pass improve first-turn access to a Mew V alongside two or three Genesect V, before resolving any other draw or search effect?

**Baseline.** Yamato Nakano's May 10, 2026 fifth-place Aichi Open League list, already transcribed and print-checked by the project in [competitive_deck_baselines](../competitive_deck_baselines/mew_genesect_reproduce.py). Tournament counts: https://www.limitlesstcg.com/tournaments/566/decklists. The experimental counterfactual differs only by **+1 Battle VIP Pass (swsh8-225), −1 Special Red Card (me4-82)**. It keeps 14 Pokémon, 42 Trainers, four Double Colorless Energy, 11 opening Basics, and one ACE SPEC.

## Exact first-turn source-access probabilities

A legal seven-card opener contains at least one Basic. Six cards then occupy the hidden Prize zone and the turn's first natural draw supplies one additional visible card. The player may put naturally held Basic Pokémon into play and may resolve one naturally held Battle VIP Pass for at most two *unprized* Basic Pokémon from the deck. The Mew V and requested number of Genesect V may occupy the Active Spot or Bench. The target fits ordinary Bench capacity, even if a different Basic must start Active.

| First-turn board endpoint | Published 3 VIP: direct only | Published 3 VIP: extra VIP lines | Published 3 VIP: union | Four-VIP candidate: union | Gain |
|---|---:|---:|---:|---:|---:|
| Mew V + at least 2 Genesect V | 3.902404359% | 27.714175847% | **31.616580206%** | **38.866894354%** | **+7.250314147 pp** |
| Mew V + at least 3 Genesect V | 0.250309888% | 8.794307451% | **9.044617339%** | **11.433180079%** | **+2.388562740 pp** |

The VIP-only contributions for the four-VIP candidate are 34.964489994% and 11.182870191%, respectively. Direct access is invariant under this swap because all Basic-Pokémon counts remain fixed.

The denominator conditions on a valid seven-card starting hand, with unconditional probability 1 − C(49,7)/C(60,7). For each eight-card visible multiset, the calculation accounts for which card could have been the one-card turn draw while preserving a valid opener. All six-Prize compositions are explicitly allocated from the unseen cards, with card identities conserved. VIP cannot rescue a Prized target.

## Reproduction and validation

- [reproduce.py](reproduce.py) returns exact rational weighted counts with integer combinatorial weights for each event.
- A separately implemented labeled-card oracle exhaustively enumerates 46,620 valid hand/Prize/turn-draw worlds from a twelve-card toy deck. The exact solver agrees for direct, VIP-only, and combined access under both one- and two-Genesect requirements.
- Fixed-seed 100,000-shuffle tests for each 60-card composition independently check the grouped calculation; each produces 77,832 accepted Basic-valid openings and agrees within 0.6 percentage points.
- The reproduction calls the project's authoritative snapshot print checker for both 60-card lists, including the counterfactual four VIP and remaining one Special Red Card. It requires construction validity and conservative paper Expanded eligibility as of October 12, 2026.
- GitHub Actions Windows regression: validate-mew-genesect-vip-frontier.yml. Run from repository root using: python -m results.mew_genesect_vip_opening.reproduce.

## Strategic interpretation and limitations

This is a **narrow first-turn source-access study**. It omits Quick Ball, Ultra Ball, Trainers' Mail, Secret Box, Dedenne-GX, Crobat V, Genesect V's Fusion Strike System, Forest Seal Stone, further natural turns, Energy attachments, VMAX evolution, and opponent interaction. It does not model match wins. Genesect's Ability draw size also depends on hand size and the number of Fusion Strike Pokémon in play, so an extra Genesect is not a fixed card-draw reward.

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

