# Shadow Rider mirror: Guzma can reduce Max Geist below a two-Prize knockout

**Status:** Tested source-grounded board-state counterfactual, independently checked against a full reachable-action search. This is a conditional one-turn tactical result. It is not a head-to-head win-rate claim.

## Why test this deck?

The repository's [Aichi 2026 champion Shadow Rider Calyrex VMAX](../../decks/shadow-rider-calyrex/) is a full, print-validated tournament deck and includes **one Guzma**. Shadow Rider VMAX (swsh6-75) has Retreat Cost 2 and the Max Geist attack, which costs three Colorless Energy and does **10 + 30 for every Psychic Energy attached to all your Pokemon**. Shadow Rider V (swsh6-74) has 210 HP and is worth two Prizes. These exact effects, and the supporting cards' printed Retreat Costs, are asserted against the repository's English card files.

Guzma (sm3-115) has an often consequential second effect: once its opposing gust succeeds, it switches your own Active with a Benched Pokemon when an eligible one exists. A pure opponent-gust equivalent such as Boss's Orders (swsh2-154) leaves your own Active undisturbed. The Advanced Player's Rulebook A-03, B-03 and C-03/C-05 governs ordinary Retreat, once-per-turn payment and switching.

## Conditional mirror snapshot

Own board: six already-established Pokemon, the maximum normal Active-plus-five-Bench geometry:
- Active Shadow Rider VMAX with **five Basic Psychic Energy**.
- Benched Shadow Rider VMAX with **two** Basic Psychic Energy.
- Benched Shadow Rider VMAX with **one** Basic Psychic Energy.
- Benched Tapu Lele-GX, Lillie's Clefairy ex, and Mimikyu (Copycat), with no attached Energy.

The exact species/copies and the **eleven Psychic Energy** total card budget exist in the Aichi champion list. The modeled board has eight Psychic Energy in play; three Psychic remain elsewhere. Opponent has an Active 320-HP Shadow Rider VMAX and a Benched 210-HP Shadow Rider V. Both sides' evolved VMAX have been in play sufficiently long for legal attack/evolution timing. The opposing VMAX's 320 HP keeps this study focused on the gusted Shadow Rider V target. No Weakness, damage, prevention or other modifiers affect the chosen target.

**Assume** it is our attacking turn, we already hold the relevant one Supporter, and do not attach Energy from hand or use Underworld Door, draw/search, Abilities, Stadiums, extra retreat modifiers or switching effects unless explicitly added to the variant. Ordinary Retreat is available once, but costs are paid by discarding whole Basic Psychic Energy. Exactly one Max Geist can close the turn. These are intentionally narrow assumptions that make a card-text faithful local test possible.

## Checked immediate outcome

| Source/available action | Psychic remaining at attack | Max Geist damage | Immediate two-Prize KO? |
| --- | ---: | ---: | --- |
| Hypothetical Boss's Orders, keep current VMAX Active | 8 | 250 | **Yes** |
| Deck's Guzma, no other own switch; best recoverable VMAX route pays Retreat 2 | 6 | 190 | **No** |
| Deck's Guzma with one extra Basic Psychic attached to Clefairy in initial board | 7 after Retreat | 220 | **Yes** |
| Deck's Guzma with usable Float Stone on original Active or two-Energy Benched VMAX | 8 | 250 | **Yes** |
| Deck's Guzma and a held usable Switch Item, without Item lock | 8 | 250 | **Yes** |
| Deck's Guzma with held Switch but Item lock forbids playing the Item | at most 6 on a recoverable attacker | at most 190 | **No** |

The 8-Psychic result has two routes to consider: Retreat the original VMAX before playing Guzma, then Guzma promotes it back, or Guzma into a two-Energy Benched VMAX, then Retreat back to the original. In either case ordinary Retreat discards two Psychic Energy, moving the total 8 to 6, and Max Geist does 190 against the 210-HP target.

The additional-Psychic variant uses a Clefairy ex with one Energy, which cannot yet use its listed two-Energy attack. This ninth Energy raises Max Geist to 220 after the same necessary Retreat payment. A Float Stone (xy8-137, actually included in the champion list) can turn a relevant Retreat Cost to zero. A hypothetical Switch Item bypasses Retreat payment but is sensitive to Item lock. The exact attach/distribution and possession of Float Stone or Switch remain conditional; no opening-access rates are assumed.

## Implementation and independent verification

The bounded turn action engine is tools/shadow_rider_guzma_damage.py. It tracks the six Pokemon, exact attached Basic Psychic counts, single Retreat payment, optionally one already-attached Float Stone, one optional playable Switch Item, and one opposing-gust Supporter followed by one Max Geist. An independent **breadth-first search** in [reproduce.py](reproduce.py) enumerates the legal action order and all own switch choices, without using the production recursive implementation. The reproducer verifies relevant source texts and **5,832 state/source/HP/Tool/Item variants** against that independent graph, including the eight/nine-Energy witness, Item-lock and Float Stone toggles, and damage boundary at target HP 190 versus 200.

Reproduce from repository root: `python -m results.tests.shadow_rider_guzma_damage.reproduce`.

## Deck implications and uncertainty

The real champion list uses Guzma and Float Stone for tactical flexibility, and this experiment demonstrates that energy-discarding own-switch recovery can change both **attack executability and damage output**. It does **not** show a Boss-for-Guzma slot substitution improves matchup win rate. Actual late-turn states involve Underworld Door, hand Energy, other card effects, future turn priorities, Tool accessibility and opponent pressure. Those must be modeled together to rank the two Supporters across games.
