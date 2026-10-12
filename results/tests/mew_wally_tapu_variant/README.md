# Tapu Lele-GX / Wally search bridge in Aichi 2026 Mew VMAX

**Counterfactual, not tournament result:** replace **one Special Red Card** (`me4-82`) with **one Tapu Lele-GX** (`sm2-60`) in Yamato Nakano's published fifth-place Aichi 2026 Mew/Genesect 60. No other slot changes. See [the complete experimental 60](../../decks/mew-genesect-tapu-wally-counterfactual/). Exact reproducible model: [reproduce.py](reproduce.py). The standalone 60-card print proof and two independent small-deck physical oracles passed [CI run 38301605855](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38301605855).

## Executable first-turn route, going second

Start Mew V Active from the opening seven, and hold/draw Double Colorless Energy. Wally can immediately evolve this Mew V into Mew VMAX even during the first turn. Cross Fusion Strike copies a Benched Genesect V's Techno Blast for **210 damage before modifiers and defenses**. The original deck has one Wally but **zero Tapu Lele-GX**.

The experimental Tapu Lele-GX introduces **Wonder Tag**, searching Wally from the deck when Lele is played **from hand** to Bench. Quick Ball or Ultra Ball can search Lele into hand, then Lele can be played to trigger Wonder Tag. **Battle VIP Pass puts Basics straight onto Bench and cannot trigger Wonder Tag**, but can supply Genesect V. Wally cannot be used on the starting player's first turn under today's going-first Supporter restriction; the modeled first attack is for the player going **second**. Relevant source print texts: `sm2-60`, `xy6-94`, `swsh1-179`, `swsh9-150`, `swsh8-225`, `swsh8-114`, `swsh8-185`, `sm1-136`. Official Tapu card: https://www.pokemon.com/uk/pokemon-tcg/pokemon-cards/series/sm2/60/ .

## Exact physical first-turn access

The shuffle contains seven initial cards, six hidden Prize cards, and one natural draw going second. Starting Mew V must be in the original seven. Require one DCE held/drawn; Genesect available to Bench from held card or legal VIP/Ball search; Wally held/drawn or obtainable via hand-to-Bench Lele; and all required search targets surviving the six random Prize cards. No Ability-draw engine, further topdeck, or opponent interference is modeled.

| Disjoint launch route | Published 60 | Counterfactual 60 |
| --- | ---: | ---: |
| Wally held; Genesect obtained directly, VIP, Quick or Ultra | 1.444045204289% | 1.444045204289% |
| Wally obtained via Tapu Lele-GX already held/drawn | 0% | 1.169715991446% |
| Wally obtained via Quick/Ultra → Tapu Lele-GX → Wonder Tag | 0% | 4.712520633398% |
| **Union** | **1.444045204289%** | **7.326281829134%** |

**Absolute lift:** **5.882236624844 percentage points** on this restricted mechanical-access endpoint. Original union exact fraction `167155400140607/11575496365633200`; experimental union `636040115150563/8681622274224900`. The original deck has eleven opening Basics (**77.757885850414%** initial-valid seven), while the candidate has twelve (**80.935330728926%**). Conditional on a valid initial seven, the respective restricted access probabilities are **1.857104509075%** and **9.052019387764%**.

Ten disjoint card classes for the experimental 60: Mew V 4, Genesect V 4, Mew VMAX 3, Wally 1, DCE 4, VIP 3, Quick Ball 4, Ultra Ball 4, Tapu Lele-GX 1, other 32. For each physically possible opener/first draw, exact hypergeometric weights are multiplied by one **joint** six-Prize availability probability for VMAX, Wally, Lele and/or Genesect. Inclusion-exclusion prevents independent-out calculations from ignoring correlated Prize losses. A separate physically labeled exhaustive deal enumerator with N=11 and N=13 verifies all three disjoint categories; source-deck quantity and English Expanded print legality are checked by `adjudicate_deck` using the October 12, 2026 legality snapshot.

Quick Ball and Ultra Ball must pay one or two discards. Even a line needing two distinct Ultra Balls has at least four hand cards available beyond Active Mew, the two Ultra Balls and DCE among its eight observed cards, so the search costs are **mechanically payable**. Whether those discarded cards are strategically expendable remains unmodeled. The model chooses VIP to find Genesect where held, retaining Balls for the Lele line.

## Why this is still experimental

Adding Lele removes one Special Red Card disruption option. Tapu Lele-GX uses Bench space, awards two Prizes if Knocked Out, and is **not** a Fusion Strike Pokémon, so it does not increase Genesect's Fusion Strike System draw ceiling. Wonder Tag is unavailable under Path to the Peak and relevant opposing Ability locks, including some Iron Thorns states. Those locks and opponent first-turn board states are not simulated; the deck's own two Path copies require careful sequencing. Genesect/Dedenne/Crobat draws, Trainers' Mail and other search combinations are also excluded, so 7.326% is a precisely delimited **subset of legal first-turn launch pathways**, not a complete opening rate and certainly not a match win rate.

The published deck's fifth-place tournament performance belongs only to the original 60. This new list is a **hypothesis to playtest**. Next: simulate source-aware Genesect draw windows, realistic discard choices, Path/Ability lock matchups, the missing Special Red Card utility, and complete matches against multiple validated decks.
