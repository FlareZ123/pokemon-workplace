# Sixth-place Aichi Quad Thorns, two complete international paper Expanded adaptations

## Provenance and legality boundary

On **May 10, 2026**, Kazuma Kashi finished sixth among **926** competitors at Japan's CL Aichi Open League with a **4 Pokémon / 48 Trainer / 8 Energy** Iron Thorns deck. The primary [published 60-card list](https://limitlesstcg.com/tournaments/566/decklists) includes **Palace Book**, **Palace Belt** and **Player's Ceremony**. Limitless identifies each as unavailable internationally; their Japanese-only card pages are [Palace Book](https://limitlesstcg.com/cards/jp/SMP/NAN25?translate=en), [Palace Belt](https://limitlesstcg.com/cards/jp/BWP/153?translate=en), and [Player's Ceremony](https://limitlesstcg.com/cards/jp/SMP/398?translate=en).

The source counts are frozen, with the three unavailable English print IDs explicitly null, in [jp_original_names.json](jp_original_names.json). This original list reflects **Japanese Expanded legality** and must not be represented as a fully English-print legal list. The two alternatives below preserve the other 57 printed-card quantities and substitute exactly three English-available cards each. Each resulting 60 passes the repository's conservative **October 12, 2026 English Expanded snapshot** deck construction, direct print-eligibility, singleton ACE SPEC, Prism Star and four-copy adjudication. This establishes suitability under the provided paper Expanded card pool; region-specific event acceptance beyond this snapshot has not been evaluated.

## Complete 60-card playable manifests

- [Search/draw adaptation: `mail_helmet.json`](mail_helmet.json)
- [Setup/bulk adaptation: `camping_charm.json`](camping_charm.json)

These JSON manifests include a card name, quantity, English print ID and source context for every single card. The printed counts appear here to make the decks human-usable without scripts.

| Card | Print ID | Search/draw | Setup/bulk |
| --- | --- | ---: | ---: |
| **Pokémon** | | **4** | **4** |
| Iron Thorns ex | `sv6-77` | 4 | 4 |
| **Trainers** | | **48** | **48** |
| Plumeria | `sm3-120` | 4 | 4 |
| Guzma | `sm3-115` | 3 | 3 |
| Guzma & Hala | `sm12-193` | 2 | 2 |
| Team Flare Grunt | `xy1-129` | 2 | 2 |
| Lusamine | `sm4-96` | 2 | 2 |
| Cynthia & Caitlin | `sm12-189` | 1 | 1 |
| Team Skull Grunt | `sm1-133` | 1 | 1 |
| Faba | `sm8-173` | 1 | 1 |
| Eri | `sv5-146` | 1 | 1 |
| Sidney | `swsh8-241` | 1 | 1 |
| Gladion | `sm4-95` | 1 | 1 |
| Lillie's Determination | `me1-119` | 1 | 1 |
| Team Rocket's Handiwork | `xy10-112` | 1 | 1 |
| Crushing Hammer | `swsh1-159` | 4 | 4 |
| Trainers' Mail | `xy6-92` | **4** | 3 |
| VS Seeker | `xy6-110` | 3 | 3 |
| Tag Call | `sm12-206` | 2 | 2 |
| Enhanced Hammer | `sv6-148` | 2 | 2 |
| Camping Gear | `swsh5-122` | 2 | **3** |
| Captivating Poké Puff | `xy11-99` | 1 | 1 |
| Echoing Horn | `swsh6-136` | 1 | 1 |
| Megaton Blower (ACE SPEC) | `sv8-182` | 1 | 1 |
| Handheld Fan | `sv6-150` | 1 | 1 |
| Tool Jammer | `swsh5-136` | 1 | 1 |
| Lucky Helmet | `sv6-158` | **1** | 0 |
| Bravery Charm | `sv2-173` | 0 | **1** |
| Tropical Beach | `bwp-BW28` | **2** | **2** |
| Thunder Mountain ◇ | `sm8-191` | 1 | 1 |
| Wondrous Labyrinth ◇ | `sm9-158` | 1 | 1 |
| **Energy** | | **8** | **8** |
| Speed Lightning Energy | `swsh2-173` | 4 | 4 |
| Capture Energy | `swsh2-171` | 2 | 2 |
| Spiky Energy | `sv9-159` | 1 | 1 |
| Double Colorless Energy | `sm1-136` | 1 | 1 |
| **Total** | | **60** | **60** |

### Why those substitutions?

| Japanese-only original | Source effect (unofficial translation) | Search/draw replacement | Setup/bulk replacement |
| --- | --- | --- | --- |
| Palace Book (Item) | Draw 3, turn ends | Fourth Trainers' Mail, free top-four Trainer access | Third Camping Gear, any-card search, turn ends |
| Palace Belt (Tool) | Active draws 2 instead of 1 at turn start | Lucky Helmet, draw 2 after receiving attack damage | Bravery Charm, +50 HP on Basic Iron Thorns |
| Player's Ceremony (Stadium) | Each player may draw 2 and end turn | Second Tropical Beach | Second Tropical Beach |

Tropical Beach lets a player draw until seven and ends their turn; its hand-size dependence and symmetrical benefit differ from Player's Ceremony. Lucky Helmet draws on receiving damage and Bravery Charm adds bulk instead of Palace Belt's automatic turn-start draw. Thus neither alternative reproduces the Japanese tournament deck's exact functionality. The already-present single **Spiky Energy** supplies an additional passive retaliation option. These are transparent redesigns, not simulated tournament improvements. Tropical Beach may also be costly to obtain as a physical print.

## Source-verified first-turn tactical line

The published deck has precisely four Basics, all Iron Thorns ex. Its Active **Initialization** suppresses Rule Box Abilities except on Future Pokémon. It can establish immediate lock when starting with Iron Thorns. A going-second attack route is:

`Tag Call → Guzma & Hala → Thunder Mountain ◇ + Double Colorless Energy → Volt Cyclone`

Guzma & Hala can search for the Stadium and the Special Energy if it can pay its **two-card discard** requirement. Thunder Mountain removes the printed Lightning requirement from Iron Thorns ex's Lightning/Colorless/Colorless attack cost; a manually attached Double Colorless Energy supplies the two remaining Colorless. The deck has one copy each of Thunder Mountain and Double Colorless, plus two Tag Call and two Guzma & Hala. Whether the line is strategically realistic depends on hand discardability, exact Prize configuration, Supporter timing, Stadium availability and opponent disruption.

If Volt Cyclone is used while the player has another Benched Pokémon, its instruction moves an Energy away from Iron Thorns, potentially spending the Double Colorless attachment. The Advanced Player's Rulebook allows an attack to apply its other parts even when a movement effect has no eligible destination; protecting energy by maintaining no Bench is a tactical tradeoff with the risk of having no replacement Pokémon. This line needs complete game-state testing before being treated as assured first-turn pressure.

## Exact opening and Prize modeling

Two independent exact methods agree: a grouped multivariate-hypergeometric computation and an exhaustive labeled-state enumeration of the ten named physical cards (four Iron Thorns, two Tag Call, two Guzma & Hala, one Thunder Mountain, one Double Colorless), with 50 anonymous others.

| Physical opening event | Exact probability |
| --- | ---: |
| First seven cards have at least one Iron Thorns Basic | **39.9499625745%** |
| Initial seven have both DCE and Thunder Mountain, conditional on Basic-valid | **0.9200923044%** |
| A Tag Call or Guzma & Hala is held, Thunder Mountain/DCE are not Prized, and a Guzma & Hala remains available in hand/deck, conditional on Basic-valid | **29.0751478452%** |

At four Basics, the chance of a seven-card hand with no Basic is **60.0500374255%**. Independent reshuffles imply **1.5031312561 expected own mulligans** before an accepted opener. This is a meaningful cost of a four-Basic lock shell; how many bonus cards the opponent actually chooses to draw depends on their own mulligans and decisions.

The 29.075% number is **a necessary-card inventory endpoint for the named Guzma & Hala line**, with the six Prize cards modeled jointly. It does *not* check available discardable cards, a sufficient hand after paying Tag Call, the first-turn natural draw, searches other than that named connector, held Tool constraints, opponent extra draws, locks, or attack choice. It is therefore an access proxy, not an actual success rate. The two adaptations have identical counts in the ten modeled categories; their differentiated Trainers and Tools can change real performance considerably.

## Testing, evidence and next work

Run `python results/iron_thorns_international_adaptation/reproduce.py` from the repository root. It independently checks every Japanese source name count, verifies both international delta sets, all 60 precise English IDs, four Basic Pokémon, one ACE SPEC, each Prism Star, category totals, core printed attack/Ability mechanics and conservative Expanded eligibility. It checks the exact opening fractions against a separately implemented labeled physical-card oracle.

[Windows CI run 38293543104](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38293543104) passed. The original Japanese list's sixth-place finish is tournament evidence for the Japanese formulation; the English adaptations have **no measured head-to-head win rates**. Priority follow-up is realistic headless turn-one line materialization and a matchup matrix against the Aichi champion Shadow Rider, finalist Vileplume, fifth-place Mew and tenth-place Regidrago, with careful treatment of opponent starting cards drawn after Quad Thorns mulligans.
