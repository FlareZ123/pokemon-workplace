# Mew VMAX / Tapu Lele-GX / Wally: exact conditional opening lock matrix

**Question:** How do active Item lock, Rule Box Ability suppression, an opposing Path to the Peak, and an Active-position Supporter lock change the [first-turn-going-second Techno Blast route](../mew_wally_tapu_variant/) in the experimentally altered Mew deck?

**Deck and scope:** same fully legal [Aichi Mew experimental +1 Tapu Lele-GX / −1 Special Red Card 60](../../decks/mew-genesect-tapu-wally-counterfactual/). This is a set of **explicitly conditioned board states**, with an opponent's lock effects assumed to be already active before Mew's first own turn. The likelihood, earliest setup turn, stability, and mutual compatibility of these effects on a real opposing board are unmodeled. **No match win rates are measured.**

## Mechanic sources

- **Vileplume `xy7-3` Irritating Pollen:** each player cannot play Items from hand. This removes Quick Ball, Ultra Ball, Battle VIP Pass, Field Blower and Lost Vacuum searches/remedies.
- **Stoutland `bw7-122` Sentinel:** while this Stoutland is Active, the opponent cannot play Supporters from hand. The specific Wally evolution route is unavailable under this ongoing restriction.
- **Path to the Peak `swsh6-148`:** Rule Box Pokémon in play have no Abilities. Tapu Lele-GX's Wonder Tag is suppressed until Path is replaced by the naturally held Sky Field, removed by an Item, or otherwise disabled.
- **Persistent independent Ability suppression:** a hypothetical active lock (e.g., suitable Active Iron Thorns ex) that continues to suppress Wonder Tag even if Path is removed. This is a **separate toggle**, never equated with Path itself.
- **Sky Field `xy6-89`:** Stadium replacement, usable under ordinary Item lock (unless a separate Stadium restriction exists). No played-Vileplume weakness or changing lock resolution is implicitly assumed.

All names, identifiers and relevant printed abilities/rules are asserted directly against `resources/cards/en/` in [reproduce.py](reproduce.py). Wally and the required Mew/Genesect/DCE/VIP/Ball counts inherit the verified source [decklist](../../decks/mew-genesect-tapu-wally-counterfactual/).

## Exact probabilities

Each row requires Mew V to start Active in the original seven, one Double Colorless Energy available after the first natural draw, deck-available Mew VMAX for Wally, and Benched Genesect V for Cross Fusion Strike to copy its **210-damage Techno Blast**. The six hidden Prize cards are jointly enumerated, as are the original seven and the first natural draw. Wally can be found through Wonder Tag only if Wonder Tag remains active and Tapu enters Bench **from hand**. Search Items are usable only without Item lock. Path removal uses the naturally held two Sky Field, one Field Blower or one payable Lost Vacuum when applicable.

| Opponent first-turn condition | Restricted going-second attack access |
| --- | ---: |
| Neither Path nor Item nor additional Ability lock | **7.326281829134%** |
| Opposing Path, Items accessible, no other Ability lock | **3.217190331194%** |
| Item lock active, no Path or additional Ability lock | **1.055943416886%** |
| Both Item lock and Path active | **0.653777573117%** |
| Persistent external Wonder Tag Ability suppression, Items accessible | **1.444045204289%** |
| Item lock and persistent Wonder Tag suppression | **0.581386703842%** |
| Active Supporter lock preventing Wally | **0%** for the specified Wally route |

Within the Item-locked baseline **1.055943416886%**, the Wally-naturally-held plus Genesect-naturally-held component is **0.581386703842%**. The remaining **0.474556713043%** requires **both Tapu Lele-GX and Genesect V naturally held/drawn**, with Wally retrieved from the non-Prized deck through Wonder Tag. Under Item lock plus Path, that extra route must also have a naturally held Sky Field and is only **0.072390869275%**. Distinct physical cards and deck survivors are enforced throughout.

This is a **line-specific counterfactual scenario table**. For example, Garbotoxin suppresses other Pokémon's Abilities, potentially shutting down an opposing Vileplume's Ability; the conditional row with both persistent Ability lock and Vileplume Item lock must not be read as asserting Garbotoxin and Irritating Pollen are necessarily active together. Likewise, actual Stoutland Supporter-lock board timing and potential gust escape are outside the model. Under Supporter lock, some other route to attacking might exist, but it is **not the modeled Wally-based turn-one attack**.

## Evidence and reproduction

`python results/tests/mew_wally_lock_matrix/reproduce.py` checks the actual printed Vileplume/Stoutland/Path/Sky/Tapu rules and enumerates exact rational opening/Prize/draw probabilities. Two entirely physical small-deck enumerators for **N=12** and **N=14** each verify **all 16 Path × Item × Ability × Supporter toggle states** against the grouped mathematical solver. The fully expanded 60-card rational checks also pin the prior no-lock and Path results and the Wally-only/Item-plus-Ability route. [Windows CI 38302764960 passed](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38302764960).

Important omissions include ordinary mulligan redraws beyond the explicit conditioning, broader Trainers' Mail routes, Genesect/Crobat/Dedenne Ability draws, opponent's actual turn-one setup, opponent's remaining board, damage prevention, DCI and discard continuation, switching out of lock, future attacks, and match winning. The attack copied from Genesect also carries **Techno Blast's next-turn cannot-attack restriction** on the attacking Mew VMAX; this future cost is excluded from this one-turn endpoint. Retreating or switching Mew to the Bench removes an attack effect under the Advanced Player's Rulebook; regaining the Active Spot for a next turn's attack can consume additional resources.

## Strategic conclusion

The 5.882236624844 percentage-point unrestricted Tapu-driven lift drops to 0.474556713043 points under an already-active Item lock and 0.072390869275 under Item lock plus Path, in these first-turn conditions. A persistent Wonder Tag Ability lock eliminates it, leaving the original Wally-held physical routes. For matchups involving early locks, preserving one Special Red Card may be more valuable than the lost first-turn Tapu search opportunities; that comparative value remains to be demonstrated in actual games. See also [the Path-only payment study](../mew_wally_path_joint/) and the [earlier Mew Path-counter access study](../mew_genesect_path_escape/).
