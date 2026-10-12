# Competitive paper Expanded reference decks

Goal: supply fully specified human-playable 60-card deck candidates with exact print IDs, legality evidence, and honest confidence labels.

## 2026 Aichi Open League runner-up: Vileplume control

**Status:** tournament-derived reference, not independently optimized or head-to-head tested by the project. The original [926-player CL Aichi Open League standings and decklist](https://www.limitlesstcg.com/tournaments/566/decklists) identify Takahiro Ando as runner-up on May 10, 2026. Card-name counts reproduce the runner-up list transcription in [the ALS source](../../tools/aichi_vileplume_als.py). These exact English print IDs provide a practical playable realization of the card-name counts; they do not assert the player's original artwork/print choices.

### Pokémon (26)

| Qty | Card | English print ID |
| ---: | --- | --- |
| 2 | Pidgey | sm9-121 |
| 2 | Pidgeotto | sm9-123 |
| 2 | Pidgeot ex | sv3-164 |
| 2 | Oddish | xy7-1 |
| 2 | Gloom | xy7-2 |
| 2 | Vileplume | xy7-3 |
| 1 | Vileplume-GX | sm12-4 |
| 2 | Lillipup | bw7-120 |
| 2 | Herdier | bw7-121 |
| 1 | Stoutland | bw7-122 |
| 2 | Bunnelby | xy5-121 |
| 1 | Fan Rotom | sv7-118 |
| 1 | Relicanth | sv5-84 |
| 1 | Mr. Mime | bw9-47 |
| 1 | Girafarig | sm8-94 |
| 1 | Budew | sv8pt5-4 |
| 1 | Jirachi | sm9-99 |

### Trainers (28)

| Qty | Card | English print ID |
| ---: | --- | --- |
| 4 | Guzma & Hala | sm12-193 |
| 2 | Guzma | sm3-115 |
| 1 | Cassius | xy1-115 |
| 1 | Karen | xyp-XY177 |
| 1 | Plumeria | sm3-120 |
| 1 | Gladion | sm4-95 |
| 1 | Faba | sm8-173 |
| 1 | Lusamine | sm4-96 |
| 1 | Bellelba & Brycen-Man | sm12-186 |
| 1 | Peonia | swsh6-149 |
| 1 | Team Yell's Cheer | swsh9-149 |
| 4 | Tag Call | sm12-206 |
| 3 | Stealthy Hood | sm10-186 |
| 2 | Technical Machine: Evolution | sv4-178 |
| 1 | Counter Gain | sm8-170 |
| 2 | Artazon | sv2-171 |
| 1 | Grand Tree (ACE SPEC) | sv7-136 |

### Energy (6)

| Qty | Card | English print ID |
| ---: | --- | --- |
| 2 | Capture Energy | swsh2-171 |
| 2 | Jet Energy | sv2-190 |
| 1 | Memory Energy | sm8-194 |
| 1 | Basic Grass Energy | bw1-105 |

**Deck totals:** 60 cards; 26 Pokémon / 28 Trainers / 6 Energy; 14 Basic Pokémon; one ACE SPEC.

The [executable proof](reproduce.py) imports the source counts directly from the model and applies the project's [deck-legality adjudicator](../deck_legality_proof/) to every selected print at **2026-10-12**. The proof's eligibility scope is the bundled English Expanded snapshot; it does not establish regional legality independently.

### Mechanism and evidence

The modeled turn-one-going-second line is **Tag Call → Guzma & Hala → Jet Energy + Technical Machine: Evolution on Ω Barrage Bunnelby**, aiming for two Evolution attacks and a fast Stage 2 board. Vileplume's Irritating Pollen suppresses Item play while Vileplume remains in play. Stoutland's Sentinel suppresses opposing Supporters only while Stoutland is Active. Pidgeot ex's Quick Search can provide later sustained access.

The [Aichi ALS study](../aichi_vileplume_als/) reported **36.3388%** modeled early Vileplume Item-lock setup over 500,000 accepted opening states using its endpoint-aware Artazon routing. This is an early-board endpoint estimate under a simplified action policy, **not a match win rate**. The [Secret Box counterfactuals](../secret_box_global_witnesses/) study substituting the ACE SPEC and are separate experimental candidates; this published baseline retains **Grand Tree**.

The source's exact-print choices must be carefully distinguished from the full Japanese runner-up list, which is transcribed by card name in the source model. Opponent-specific discard utility, lock counterplay, late-game game plans, and true win rates remain open. Near-term evaluations should compare Iron Thorns ex, Regidrago, Shadow Rider Calyrex, Item-lock mirrors, and other relevant decks in valid headless matches.

### Reproducibility

The test module is [reproduce.py](reproduce.py). It checks all 38 unique source card names, print-ID identity, 60-card construction, 14 Basic count, ACE SPEC uniqueness, critical printed effects, and the conservative current Expanded legality disposition. The test is designed to fail loudly when source quantities or print semantics drift.


---

## 2026 Aichi champion: Shadow Rider Calyrex

**Status:** tournament-winning baseline, with independent [Limitless tournament listing](https://www.limitlesstcg.com/tournaments/566/decklists). On **10 May 2026**, Yasunori Kato finished first in the 926-player CL Aichi Open League event with this card-name composition. Exact English prints are selected to preserve identifiable tactical roles. The source may have used different artwork or region-specific physical prints.

### Pokémon (18)

| Qty | Card | English print ID |
| ---: | --- | --- |
| 3 | Shadow Rider Calyrex V | swsh6-74 |
| 4 | Shadow Rider Calyrex VMAX | swsh6-75 |
| 2 | Lillie's Clefairy ex | sv9-56 |
| 2 | Tapu Lele-GX | sm2-60 |
| 1 | Trevenant & Dusknoir-GX | smp-SM217 |
| 1 | Latias ex | sv8-76 |
| 1 | Dialga-GX | sm5-100 |
| 1 | Mimikyu (Copycat) | sm2-58 |
| 1 | Girafarig | sm8-94 |
| 1 | Marshadow (Resetting Hole) | sm10-81 |
| 1 | Radiant Eternatus | swsh12pt5-105 |

### Trainers (31)

| Qty | Card | English print ID |
| ---: | --- | --- |
| 2 | Lillie's Determination | me1-119 |
| 1 | Carmine | sv6-145 |
| 1 | Iono | sv2-185 |
| 1 | Teammates | xy5-141 |
| 1 | Raihan | swsh7-152 |
| 1 | Acerola | sm3-112 |
| 1 | Guzma | sm3-115 |
| 1 | Tulip | sv4-181 |
| 4 | Mysterious Treasure | sm6-113 |
| 4 | Fog Crystal | swsh6-140 |
| 3 | VS Seeker | xy6-110 |
| 1 | Quick Ball | swsh1-179 |
| 1 | Hisuian Heavy Ball | swsh10-146 |
| 1 | Battle Compressor Team Flare Gear | xy4-92 |
| 1 | Field Blower | sm2-125 |
| 1 | Night Stretcher | sv6pt5-61 |
| 1 | Unfair Stamp (ACE SPEC) | sv6-165 |
| 1 | Float Stone | xy8-137 |
| 1 | Forest Seal Stone | swsh12-156 |
| 2 | Sky Field | xy6-89 |
| 1 | Dimension Valley | xy4-93 |

### Energy (11)

| Qty | Card | English print ID |
| ---: | --- | --- |
| 11 | Basic Psychic Energy | bw1-109 |

**Deck totals:** 60 cards; 18 Pokémon / 31 Trainers / 11 Basic Energy; 14 Basic Pokémon; one ACE SPEC (Unfair Stamp) and one Radiant Pokémon (Radiant Eternatus). The event site abbreviates Battle Compressor's name; the bundled English print is named **Battle Compressor Team Flare Gear**.

The independently executable [legality proof](shadow_rider_reproduce.py) fixes the full 60, verifies print-specific core abilities/attacks (Underworld Door, Wonder Tag, Copycat, Timeless-GX, Climactic Gate), and reuses the existing conservative deck-construction and Expanded-snapshot adjudication as of 2026-10-12.

### Competitive role and open questions

Shadow Rider Calyrex VMAX supplies a repeating Psychic acceleration/draw engine through **Underworld Door**, with Max Geist converting the board's Psychic Energy into damage. Radiant Eternatus can establish VMAX bodies rapidly in applicable opening states. Mimikyu Copycat plus Dialga-GX provides a matchup-conditional answer to an opponent's copied attacks; its real action feasibility needs explicit attack-copy and Energy checks. Sky Field increases potential Bench occupancy while creating exposure to Stadium replacement.

Its tournament first place is meaningful empirical evidence of strength in that event. It is **not** an estimated modern field-wide win rate. The next practical experiment is a matched-head-to-head setup and match comparison against Vileplume, Regidrago, Iron Thorns, Snorlax, and other plausible Expanded opponents, with the opponent pool and simulator revision pinned.

---

## 2026 Aichi Open League 10th place: Regidrago VSTAR

**Status:** published tournament top-ten reference, fully specified as a 60-card English-print realization and checked through the existing conservative Expanded-snapshot deck adjudicator. This list comes from **Haruku Yoshioka, 10th place at the May 10, 2026 CL Aichi Open League**: https://limitlesstcg.com/decks/list/26816 . The linked decklist publishes counts and recognizable card identities. Representative English print IDs below need not be the exact artwork or language used in Japan.

### Pokémon (20)

| Qty | Card | English print ID |
| ---: | --- | --- |
| 4 | Regidrago V | `swsh12-135` |
| 3 | Regidrago VSTAR | `swsh12-136` |
| 2 | Budew | `sv8pt5-4` |
| 1 | Dragapult ex | `sv6-130` |
| 1 | Dialga-GX | `sm5-100` |
| 1 | Koraidon ex | `sv5-120` |
| 1 | Kyurem | `sv6pt5-47` |
| 1 | Hisuian Goodra VSTAR | `swsh11-136` |
| 1 | Dedenne-GX | `sm10-57` |
| 1 | Squawkabilly ex | `sv2-169` |
| 1 | Tapu Lele-GX | `sm2-60` |
| 1 | Latias ex | `sv8-76` |
| 1 | Marshadow | `sm10-81` |
| 1 | Wobbuffet | `xy4-36` |

### Trainer (30)

| Qty | Card | English print ID |
| ---: | --- | --- |
| 2 | Professor's Research | `sv8pt5-122` |
| 2 | Guzma | `sm3-115` |
| 1 | Iono | `sv2-185` |
| 1 | Carmine | `sv6-145` |
| 1 | Lillie's Determination | `me1-119` |
| 1 | Marnie | `swsh1-169` |
| 1 | Raihan | `swsh7-152` |
| 1 | Crispin | `sv7-133` |
| 1 | Faba | `sm8-173` |
| 3 | Quick Ball | `swsh1-179` |
| 3 | Mysterious Treasure | `sm6-113` |
| 3 | Battle VIP Pass | `swsh8-225` |
| 3 | VS Seeker | `xy6-110` |
| 1 | Hisuian Heavy Ball | `swsh10-146` |
| 1 | Battle Compressor Team Flare Gear | `xy4-92` |
| 1 | Super Rod | `sv2-188` |
| 1 | Prime Catcher | `sv5-157` |
| 2 | Muscle Band | `xy1-121` |
| 1 | Parallel City | `xy8-145` |

### Energy (10)

| Qty | Card | English print ID |
| ---: | --- | --- |
| 4 | Double Dragon Energy | `xy6-97` |
| 4 | Grass Energy | `bw1-105` |
| 2 | Fire Energy | `bw1-106` |

**Deck totals:** 60; **20 Pokémon / 30 Trainers / 10 Energy**; **15 Basic Pokémon**; one ACE SPEC (**Prime Catcher**). The complete machine-readable manifest, including each selected English print, is [regidrago_haruku_2026.json](regidrago_haruku_2026.json). Every printed card-name count is preserved from the published source. The only name abbreviation expanded for the card database is **Battle Compressor Team Flare Gear**, whose card text matches the event's Battle Compressor.

### Tactical role and published evidence

Regidrago VSTAR's **Apex Dragon** copies attacks of Dragon Pokémon in its owner's discard pile. The deck includes distinct Dragon payloads with sharply different functions: Dialga-GX **Timeless-GX** for another turn; Dragapult ex **Phantom Dive** for Active damage and distributed Bench counters; Kyurem **Trifrost** for multi-target spread with an Energy discard; Hisuian Goodra VSTAR **Rolling Iron** for damage reduction; and Dragon Koraidon ex **Retribution Strike** for a direct attack whose damage scales with its own damage counters. These bodies entail different damage/effect timing and attacker Energy budget constraints.

Two Budew enable **Itchy Pollen** Item lock and a direct non-Apex-Dragon attack-history cover after a Timeless-GX extra turn, provided Regidrago can physically promote Budew. Guzma and Prime Catcher are opponent-Bench-dependent switch routes. One Latias ex grants free retreat only to **Basic** Pokémon, so it does not make the evolved Regidrago VSTAR retreat free. The Wobbuffet selected is the **Bide Barricade** print and the Marshadow is **Resetting Hole**; other same-name prints have different effects and cannot be substituted without checking the intended roles.

The list uses Quick Ball/Mysterious Treasure and Battle Compressor for setup and purposeful Dragon discarding. Preserve hand-resource discard costs, one-Supporter-per-turn contention, the exact ACE SPEC limit, initial six-Prize uncertainty, and Bench occupancy when evaluating execution feasibility. Item lock, Ability lock and opponent promotion can interrupt apparently reachable search lines.

### Validation, uncertainty and next work

[regidrago_reproduce.py](regidrago_reproduce.py) independently confirms the 20/30/10 quantities; all 36 exact print identities; 15 Basic Pokémon; one ACE SPEC; 13 source-card attack/Ability identities; crosschecks a dozen observed counts against the repository's earlier nine-list Aichi transcription; and runs the existing deck-construction plus print-provenance adjudicator for **October 12, 2026**. The intended outcome is `eligible_snapshot`, the same conservative evidence class as the existing Shadow Rider and Vileplume lists. This supports paper Expanded within the bundled English data. Regional print acceptance and historical artwork details are outside the claim.

**Evidence:** 10th place and card-name counts are published observations from Limitless. Print identities and rules are drawn from the supplied card database and Advanced Player's Rulebook. No project-measured tournament matchup win rate or optimization claim follows from a top-ten finish.

A useful next experiment is to compare this 60-card reference against the 2026 Aichi champion Shadow Rider list across reproducible opening boards and a checked simulator. The policy set should include the Apex Dragon Timeless-GX continuation and choice of bonus-turn Budew Item lock, Kyurem Trifrost, or Noivern ex alternatives; this particular published list does **not** contain Noivern ex, so that branch belongs to a clearly marked alternative build. Each comparison must control attack history, available Supporter and Energy actions, Prized singleton payloads, and what resources can actually be discarded.
