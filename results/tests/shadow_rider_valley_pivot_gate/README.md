# Aichi champion direct Radiant launch: pricing Dimension Valley and Float Stone access

## Competitive question

The [2026 Aichi champion Shadow Rider deck](../../decks/shadow-rider-calyrex/) plays one Dimension Valley (xy4-93), one Float Stone (xy8-137), two Sky Field (xy6-89), four Shadow Rider Calyrex VMAX and one Radiant Eternatus. The [direct launch-to-attack research](../shadow_rider_direct_launch_attack/) computed Max Geist at its normal three-Energy cost and at its reduced two-Energy cost **assuming Dimension Valley was already available**. This study makes actual access to the unique Dimension Valley card part of the calculation and preserves its draw contention with Psychic Energy and Float Stone.

Dimension Valley reduces Psychic Pokémon's attack costs by one Colorless. Max Geist therefore costs two Energy when that Stadium's effect applies. Radiant Eternatus's Climactic Gate ends the launch turn, so the modeled charging and Stadium play happen on the following turn. Float Stone grants no Retreat Cost to its attached Pokémon; this model uses it as a restricted route to promote the charged attacker.

## Precisely defined direct-launch line

Use the unchanged 60-card composition: Radiant Eternatus x1, other starting Basic Pokémon x13, Shadow Rider VMAX x4, Basic Psychic Energy x11, Float Stone x1, Dimension Valley x1 and other cards x29.

Condition on an accepted Basic-containing opening seven. A non-Radiant Basic must be in the opening to serve as Active. Set six Prizes, take one first-turn natural draw going second, and require Radiant in hand, either initially or through that draw, **without search**. Climactic Gate finds two VMAX in deck, puts them on the Bench and ends the turn. Assume the opponent does not disrupt this launch before the following turn. Draw once, use two live Underworld Door Abilities to attach Psychic Energy to one initially uncharged Benched VMAX and draw two after each successful attachment, then make one ordinary Energy attachment when available. The attacker needs a legal promotion after charging.

The **normal branch** requires three attached Energy and the Float Stone pivot. The **reduced-cost branch** requires at least two attached Energy, physically accessible Dimension Valley and the Float Stone pivot. In the second branch the player must be legally able to play Dimension Valley before attacking, with the Stadium-use allowance unspent. The union allows either branch, choosing based on what the shared draw stream actually delivers. All resource probabilities are conditional on the same accepted-opening/Prize/draw experiment; search, opponent attacks and alternative pivots are excluded.

## Exact probabilities

| Milestone | Exact probability |
| --- | ---: |
| Direct Radiant launch of two VMAX | 12.017840120% |
| Launch + normal three-Energy Max Geist + Float Stone pivot | 0.768862128% |
| Launch + two-Energy charge + physically accessible Dimension Valley, ignoring pivot | 1.288246138% |
| Launch + two-Energy charge + Dimension Valley + Float Stone pivot | **0.216450306%** |
| Overlap: three-Energy Float route also holds accessible Dimension Valley | 0.119037889% |
| **Launch followed by either fully specified Float Stone attack route** | **0.866274545%** |

The final union uses inclusion-exclusion. Accessible Dimension Valley adds **0.097412417 percentage points** to the regular-cost Float route, reaching a 7.208238225% continuation rate when conditioned specifically on the direct double-VMAX launch already succeeding.

The earlier freely available-Dimension-Valley counterfactual gave **1.288246138%** for a two-Energy Float-only attack route. Imposing the physical Stadium-access requirement reduces that branch to **0.216450306%**. This difference measures a resource-access constraint under this simplified sequence and does not establish whether the Stadium is a good or bad inclusion in the complete list.

The exact fractions are preserved in the reproducer. In particular, the union is 3392929014049/391669019033600 and the Valley-plus-Float reduced-cost route is 7969026626217/3681688778915840.

## Method, testing and reproducibility

[tools/shadow_rider_valley_pivot_gate.py](../../../tools/shadow_rider_valley_pivot_gate.py) uses exact rational arithmetic. The predecessor's six card classes include 30 neutral cards, one of which is Dimension Valley. Conditional on a coarse full-deck opening/Prize/next-draw state, the singleton's physical location is uniform among those 30 cards: held with probability (neutral cards in hand)/30, in the deck with probability (neutral cards in deck)/30 and otherwise in Prizes. This exchangeability argument computes the Stadium's full zone distribution without enumerating a separate opening-card category.

The following Underworld Door draw windows use a multivariate hypergeometric dynamic program with four categories: Psychic Energy, Float Stone, Dimension Valley and remaining filler. Each Ability requires paying a Psychic from hand *before* drawing two. Its second draw window does not occur if the first draw fails to replenish the requisite hand Energy. The full calculation groups 2,541 distinct residual resource states.

The [reproducer](reproduce.py) verifies each exact champion fraction and independently enumerates individual labeled physical cards for four small toy deck populations, including their opening, Prizes, both natural draws, and full possible orderings of all remaining deck cards. The independent oracle resolves each Ability attachment and draw before checking each resource endpoint. It also asserts the supplied exact prints' text and the unchanged champion list's singleton counts. Local mathematical tests passed 12 October 2026. No CI pass or competitive head-to-head performance is claimed.

## Limitations and next research

The analysis omits other routes through Mysterious Treasure, Quick Ball, Forest Seal Stone, Tapu Lele, Sky Field entry, Latias ex, Guzma, ordinary retreat Energy, and Stadium search. It assumes no Ability or Tool lock, a usable Tool slot, a free Stadium play on the charging turn, two surviving VMAX Ability sources and a legal retreat into the charged attacker. Max Geist damage and Knock Out potential, Prize timing, opponent defense and full match win rates remain unmodeled. A crowded Sky Field Bench can contract on replacement with Dimension Valley, creating a further state-dependent liability absent from this minimal three-Pokémon Bench case.

The natural follow-on is joint exact source-aware Radiant launch and Stadium/pivot access, including Psychic Energy spent as search payment and appropriate Bench/Supporter/Tool contention. The end goal remains strongest playable tournament decks evaluated against realistic opposing strategies.
