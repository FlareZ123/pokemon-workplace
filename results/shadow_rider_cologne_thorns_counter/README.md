# Shadow Rider vs Iron Thorns: the Canceling Cologne and Forest Seal Stone counterline

The [2026 Aichi Open League champion Shadow Rider Calyrex list](../competitive_deck_baselines/) contains one Radiant Eternatus, four Shadow Rider Calyrex VMAX, four Mysterious Treasure, three Shadow Rider Calyrex V and one Forest Seal Stone. Against the [Iron Thorns ex-only opponent](../iron_thorns_shadow_rider_suppression/), active **Initialization** suppresses Radiant Eternatus's Climactic Gate under the initial state, making that Ability-mediated launch impossible until the suppression changes.

## Concrete paper Expanded answer to Initialization

**Canceling Cologne** (Astral Radiance, swsh10-136) is an Item that makes the opposing Active Pokémon have no Abilities for the rest of the player's turn. Playing it against Active Iron Thorns ex negates Initialization for that turn. Shadow Rider can then play Radiant Eternatus from hand to the Bench and use Climactic Gate, placing two VMAX from the deck onto its Bench if the pieces remain there.

**Forest Seal Stone** (Silver Tempest, swsh12-156) is already in the champion list. Attached to Shadow Rider Calyrex V, it grants use of the Star Alchemy VSTAR Power and can search for exactly one missing Cologne or Radiant. A distinction between an Ability **on a Tool** and a Pokémon **having an Ability** permits this Tool-granted search under active Thorns Initialization. See [Pokémon's published Tool explanation](https://www.pokemon.com/uk/features/pokemon-tcg-sword-shield-silver-tempest-top-competitive-cards) and [official community quoting the Pokémon Rules Compendium](https://community.pokemon.com/en-us/discussion/comment/8557); an [Iron Thorns-specific discussion](https://www.reddit.com/r/PTCGL/comments/1fhnvka/) independently recognizes the exception.

Conditions: going second, before your first attack; opposing Iron Thorns remains Active throughout the action; no additional Ability suppression, Item lock, Tool lock or other restriction is present; Forest Seal Stone has an eligible untolled Pokémon V and the once-per-game VSTAR Power is unused. The owner must play Cologne **before** benching Radiant. Opponent Stadiums such as Path to the Peak can invalidate the simple line unless removed or countered.

## Fully specified legal 60-card variants

The [source baseline's complete 60-card exact-print list](../competitive_deck_baselines/shadow_rider_reproduce.py) is retained apart from these explicit swaps. All print IDs remain unchanged, with added Cologne using swsh10-136. [The reproducer](reproduce.py) builds and validates each entire variant against the repository's conservative paper Expanded legality overlay dated 2026-10-12.

| Cologne copies | Exact cuts to the original 60 |
| ---: | --- |
| 0 | None |
| 1 | 1 Sky Field |
| 2 | 2 Sky Field |
| 3 | 2 Sky Field, 1 Dimension Valley |
| 4 | 2 Sky Field, 1 Dimension Valley, 1 Night Stretcher |

The cuts are controlled **research counterfactuals**, not strategic endorsements. Sky Field, Dimension Valley and Night Stretcher have competing tactical value against the opponent field.

## First-turn exact Prize-integrated access results

The model draws an accepted Basic opening seven, reserves a non-Radiant Basic as Active from that opening, deals six face-down Prizes, and draws one card at the beginning of the first going-second turn. It partitions all 60 physical cards into eight categories: Radiant (1), Shadow VMAX (4), Mysterious Treasure (4), Cologne (k), Stone (1), Shadow Rider V (3), other Basics (10), and residual (37-k).

Success requires two Shadow VMAX remaining **inside the searchable deck**, a legal counteraction obtaining Cologne, and Radiant obtained from hand or one available Mysterious Treasure/Stone search. A Stone needs an available V from the opening or first draw and can fetch just **one** missing piece. Treasure's one-card discard cost is mechanically payable, but no DCI opportunity cost is charged. Search effects beyond the stated ones are excluded.

All mass comes from exact combinatorial allocations of opening hand, Prizes and first draw (not simulated samples). Probabilities are **conditional on a valid Basic opening**:

| Cologne | Already held Cologne | Held or Forest Seal Stone access | Stone improvement |
| ---: | ---: | ---: | ---: |
| 0 | 0.000000% | 0.000000% | 0.000000 pp |
| 1 | 5.057565% | **6.820639%** | +1.763074 pp |
| 2 | 9.615842% | **11.643271%** | +2.027429 pp |
| 3 | 13.715222% | **15.830381%** | +2.115158 pp |
| 4 | 17.393585% | **19.570259%** | +2.176674 pp |

For Cologne 1 the five disjoint subroutes are: held Cologne + direct Radiant **1.346379%**, held Cologne + Treasure **3.711186%**, Stone seeks Cologne + held Radiant **0.394944%**, Stone seeks Cologne + Treasure seeks Radiant **1.100775%**, and held Cologne + Stone seeks Radiant **0.267355%**.

The published [unlocked first-turn launch probability](../shadow_rider_radiant_launch/) is **43.699162430%** with a different assumption about the opponent's suppression; the present result does not imply 43.7% wins against Iron Thorns. A zero with Cologne=0 means only that this specified Cologne counterline is missing.

## Reproduction and limitations

[reproduce.py](reproduce.py) verifies source card texts, five complete exact-print deck constructions and conservative legality, 60-card mass conservation, all five fixed **rational** success fractions, and an independent **8,925-world labeled physical-card toy oracle** against the weighted hypergeometric solver. Windows CI runs the same self-contained checks.

Excluded: all other search and draw connectors, opponent mulligan cards, Prize recovery, opponent responses and turn sequencing beyond this action window, competing VSTAR uses, Bench congestion, realistic DCI/AMR discard pricing, Tool-attached contest, retained Stadium value, opponent Stadiums and Items, future turns and real KO/Prize win rates. The objective is **narrow line access**. It is useful for counter-card research but insufficient to establish the competitive superiority of any tested swap.
