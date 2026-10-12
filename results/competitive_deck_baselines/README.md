# Competitive paper Expanded reference decks

Goal: supply fully specified human-playable 60-card deck candidates with exact print IDs, legality evidence, and honest confidence labels.

## 2026 Aichi Open League runner-up: Vileplume control

**Status:** tournament-derived reference, not independently optimized or head-to-head tested by the project. Card-name counts reproduce the runner-up list transcription in [the ALS source](../../tools/aichi_vileplume_als.py). These exact English print IDs provide a practical playable realization of the card-name counts; they do not assert the player's original artwork/print choices.

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
