# Can first-turn Mew VMAX OHKO a 230-HP Iron Thorns ex under Initialization?

**Concrete opponent:** The published English adaptation of the Aichi sixth-place [Iron Thorns ex-only list](../../decks/iron_thorns_aichi_english/) runs four Iron Thorns ex, `sv6-77`, each **230 HP**. Its Active **Initialization** disables Rule Box Pokémon Abilities other than those of Future Pokémon. The source Mew VMAX (`swsh8-114`) is Psychic type; Iron Thorns ex has **Fighting Weakness** and **no Psychic Resistance**. Copied Genesect V's Techno Blast deals **210** before modifiers, leaving Iron Thorns with 20 HP. The Mew deck's two **Muscle Band** `xy1-121` cards add **20 damage** to attacks against the Active Pokémon, reaching **230 exactly**.

## Strict ability-locked first-turn line

Assume an Iron Thorns ex already Active when the Mew player begins their first turn **going second**, with no Tool suppression, damage prevention, preexisting Mew restrictions, or Item lock. It blocks the new Tapu Lele-GX Wonder Tag line. The Mew player must:

1. Have chosen Mew V as the original seven-card Active.
2. Hold/draw the singleton Wally, a Double Colorless Energy and one Muscle Band in eight visible natural cards.
3. Have a non-Prized Mew VMAX in deck that Wally can use for immediate evolution.
4. Establish Genesect V on Bench from the visible hand, or an available Battle VIP Pass, Quick Ball or Ultra Ball with a post-Prize Genesect deck survivor.
5. Attach DCE and Muscle Band to Mew VMAX and copy Techno Blast with Cross Fusion Strike for **230 attack damage**, enough to Knock Out an unprotected 230-HP Iron Thorns ex.

Other Trainer search/draw effects, an opponent's Tool Jammer, Tool suppression and damage modifying effects remain outside this narrow calculation. A hypothetical Iron Thorns with Tool Jammer active can disable Muscle Band's extra damage, invalidating the unqualified knockout.

## Exact physically sourced probability

The 60-card source population for this Wally-held line is: `Mew V 4, Genesect V 4, Mew VMAX 3, Wally 1, Double Colorless Energy 4, Battle VIP Pass 3, Quick Ball 4, Ultra Ball 4, Muscle Band 2, other 31`. The original Aichi fifth-place Mew 60 and the experimental [Tapu Lele modification](../../decks/mew-genesect-tapu-wally-counterfactual/) share precisely these mechanically relevant counts. The differing Tapu Lele/Special Red Card identity is inside the 31 irrelevant cards *under the stated persistent Ability lock*.

| Exclusive source of Bench Genesect | First-turn 230-damage line access |
| --- | ---: |
| Genesect already naturally held/drawn | 0.087033686299% |
| Battle VIP Pass supplies Genesect when absent | 0.052291313368% |
| Quick Ball supplies Genesect when above unavailable | 0.054978482661% |
| Ultra Ball supplies Genesect when above unavailable | 0.040818600823% |
| **Exact total** | **0.235122083152%** |

The unconditional rational fraction is `412371942273/175386308570200`, over all randomly shuffled seven-card openings, one natural first-turn draw and six hidden Prizes, requiring Mew V in the **original seven**. Given a valid original Aichi Mew opening (11 Basic Pokémon), the access probability is **0.302377155166%**. Given a valid Tapu experimental opening (12 Basics), it is **0.290506112762%**. The unconditional numerator is identical; adding the twelfth Basic increases the valid-opening denominator, illustrating why denominators must be made explicit in deck comparisons.

Muscle Band contributes an opportunity cost: the Pokémon cannot simultaneously attach a different Tool such as Forest Seal Stone or Float Stone. Both special Tool interactions and the copied attack's future no-attack restriction are excluded here. A Wally/Techno Blast turn also consumes the Supporter for that turn and may expose a three-Prize Mew VMAX before the opponent is forced to respond.

## Reproduction and evidence

`python results/tests/mew_wally_iron_thorns_230/reproduce.py` enumerates exact rational multivariate opening-hand and six-Prize probabilities, requiring named deck survivors jointly for the Genesect/VMAX searched lines. Independent physically labeled exhaustive toy-deal enumerations **N=12 and N=14** reproduce all four exclusive probabilities. The code directly verifies the Iron Thorns ex HP, Initialization text, Mew's Psychic type, Genesect's printed 210, and Muscle Band's 20 against the bundled English card JSON. Source decklist and print legality are already validated in the existing Aichi baseline, while this named damage calculation independently checks its key game text.

[Windows CI 38303364450 succeeded](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38303364450).

**Interpretation:** The 230-damage breakpoint is tactically relevant, especially when the Iron Thorns player has only one Pokémon in play and a KO would leave no Active replacement. The measured **0.235%** is strictly the named Wally/Muscle Band first-natural-draw attack route under a fixed adverse Ability lock. It excludes Trainers' Mail reaching Band, all further Pokémon searching and draw effects, preexisting opponent Bench setup, switching or counterplay, and thus cannot predict whether the Mew deck beats Iron Thorns overall.
