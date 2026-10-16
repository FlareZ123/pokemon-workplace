# Verified Aichi Open League 2026 Top 32 field manifest

**Event:** 10 May 2026, 926 players, paper Expanded tournament in Japan. [Tournament standings](https://limitlesstcg.com/tournaments/566) and [published decklists](https://limitlesstcg.com/tournaments/566/decklists).

**Snapshot:** HTML SHA-256 `ee7b17a40f851cebd986d3da8e6d4f8b922505b5222cabfdfa884678a84a55d6`, captured by manual Windows [CI run 38908257338](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38908257338), which passed six parser tests and all declared 60-card totals. [JSON card-name source artifact](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38908257338/artifacts/12048699813).

**Coverage:** 29 of 32 ranked opponents have published card-name/count lists; 23rd, 25th and 28th have standings and externally corroborated archetypes, with exact 60s unpublished at the cited decklist source.

| Rank | Player | Source archetype | Published 60? | P/T/E |
|---:|---|---|:---:|---:|
| 1 | Yasunori Kato | Shadow Rider Calyrex | Yes | 18/31/11 |
| 2 | Takahiro Ando | Vileplume Control | Yes | 26/28/6 |
| 3 | Haruto Miki | Snorlax Stall | Yes | 11/44/5 |
| 4 | Shu Hosoda | Raichu Electrode Combo | Yes | 18/30/12 |
| 5 | Yamato Nakano | Mew Genesect | Yes | 14/42/4 |
| 6 | Kazuma Kashi | Iron Thorns | Yes | 4/48/8 |
| 7 | Hiroto Fuji | Snorlax Stall | Yes | 12/44/4 |
| 8 | Yusuke Kobayashi | Absol Garbodor | Yes | 12/41/7 |
| 9 | Shun Ito | Absol Electrode | Yes | 15/38/7 |
| 10 | Haruku Yoshioka | Regidrago | Yes | 20/30/10 |
| 11 | Wataru Yano | Absol Garbodor | Yes | 13/39/8 |
| 12 | Risa Sato | Regidrago | Yes | 20/30/10 |
| 13 | Hiromu Sasaki | Regidrago | Yes | 17/33/10 |
| 14 | Manaya Asano | Regidrago | Yes | 21/29/10 |
| 15 | Ryotaro Nozawa | Lopunny Vileplume | Yes | 25/28/7 |
| 16 | Takumi Matsumoto | Absol Garbodor | Yes | 14/39/7 |
| 17 | Yuya Yamano | Raichu Electrode Combo | Yes | 18/30/12 |
| 18 | Hayato Omuro | Regidrago | Yes | 21/31/8 |
| 19 | Mark Takahashi | Raging Bolt | Yes | 16/31/13 |
| 20 | Satoru Imamura | Regidrago | Yes | 20/30/10 |
| 21 | Shun Nakajima | Regidrago | Yes | 20/30/10 |
| 22 | Haruya Mori | Absol Garbodor | Yes | 14/38/8 |
| 23 | Yuki Ueno | Regidrago | **No** | ? |
| 24 | Ryoya Fujii | Iron Thorns | Yes | 4/48/8 |
| 25 | Kazuki Kumegawa | Raichu Electrode Combo | **No** | ? |
| 26 | Hibiki Yamada | Meloetta Donk | Yes | 12/45/3 |
| 27 | Yuya Nagatsuma | Regidrago | Yes | 20/30/10 |
| 28 | Jo Kato | Regidrago | **No** | ? |
| 29 | Kohei Hamamichi | Iron Thorns | Yes | 4/48/8 |
| 30 | Koki Takeda | Lillie's Clefairy | Yes | 16/37/7 |
| 31 | Yuhi Yokoyama | Dusknoir Chimecho | Yes | 22/33/5 |
| 32 | Kaito Higuchi | Regidrago | Yes | 20/30/10 |

Archetype attribution for the missing full lists: [Regidrago tournament history](https://limitlesstcg.com/decks/260/results) identifies Ueno 23rd and Kato 28th; [Raichu Electrode tournament history](https://limitlesstcg.com/decks/282/results) identifies Kumegawa 25th. These pages identify archetypes only. The question marks above must remain unresolved until the players' 60s are independently sourced.

## Field proportions (one equal-weight row per ranked opponent)

| Archetype | Top 32 | Share |
|---|---:|---:|
| Regidrago | 11 | 34.375% |
| Absol Garbodor | 4 | 12.500% |
| Raichu Electrode Combo | 3 | 9.375% |
| Iron Thorns | 3 | 9.375% |
| Snorlax Stall | 2 | 6.250% |
| Shadow Rider Calyrex, Vileplume Control, Mew Genesect, Absol Electrode, Lopunny Vileplume, Raging Bolt, Meloetta Donk, Lillie's Clefairy, Dusknoir Chimecho | 1 each | 28.125% combined |
| **Total** | **32** | **100%** |

In an equally weighted Top 32 objective, Regidrago is the largest single matchup family. Different exact lists inside one family can vary materially in policy, counterplay, and card legality; treating them as one interchangeable opponent would discard strategically important information.

## Source preservation and access limitations

The 29 published lists contain **989 distinct displayed card-name rows** representing **1,740 physical card copies**. The live importer independently matches all source-declared per-deck card-category totals. Five repeated-name *row groups* appear in four lists: rank 15 Vileplume and Pidgeotto, rank 16 Garbodor, rank 22 Trubbish, and rank 31 Dusknoir. Their repeated display names cannot automatically be collapsed into one print variant.

Three Japanese-source card names needing regional/print handling occur at nine distinct source rows, totaling 14 physical slots across ranks 3, 6, 7, 24 and 29: Palace Book, Palace Belt, Player's Ceremony. See [English Iron Thorns adaptation work](../iron_thorns_international_adaptation/) for an existing example of explicit substitution. A published original list and an English-legal adaptation are distinct opponents for experimental attribution.

The [source importer](../../tools/aichi_top32_source.py) reproduces the live capture, and [manual workflow](../../.github/workflows/aichi-top32-source.yml) uploads JSON without automatically modifying the benchmark. This roster and source artifact are a reproducible completeness ledger. They **do not establish legal exact-print realizations for all 29 known lists or fair full-game match outcomes**, and cannot certify any 99.5% win-rate claim.

## Implications for evidence

The 99.5% target, interpreted as a uniform mean game win probability over 32 ranked opponents, permits total matchup-loss probability of only **0.16** across all 32 opponents. Missing three true decklists leaves three matchup probabilities unidentified. Even if all 29 fully published opponents were hypothetically beaten with probability 1, the three unknown opponents would collectively need a mean win probability of at least **94.6666667%** to attain 99.5%. Actual results remain unmeasured. Report assumptions for every surrogate, keep exact deck and policy identity, and quantify uncertainty rather than substituting a published same-archetype 60 under an absent player's name.
