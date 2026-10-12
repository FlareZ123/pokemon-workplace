# Float Stone's timing under Item lock changes the Shadow Rider Guzma outcome

**Status:** Card-text and manual grounded conditional attacking-turn model, tested with an independent physical-action search. This extends [the champion Shadow Rider mirror witness](../shadow_rider_guzma_damage/) by separating Item play permission, Pokémon Tool attachment, and the ongoing effects of attached Tools.

## Source rules and why these are different permissions

The supplied Advanced Player's Rulebook defines **Items** (B-01) and **Pokémon Tools** (B-02) as different Trainer categories. This explicitly includes older Tools whose historic printed text says “Item.” A Pokémon Tool can normally be attached from hand to a Pokémon with no already-attached Tool during your turn, subject to any particular restrictions.

The checked-in English source prints are:

- **Vileplume (xy7-3)**: Irritating Pollen says neither player may play Item cards from hand while the Ability remains active. This is an **Item lock** and, under the applicable current Tool rules, does not itself prevent attaching Float Stone.
- **Float Stone (xy8-137)**: a Pokémon Tool, causing its attached Pokémon to have **no Retreat Cost** while the effect functions.
- **Jamming Tower (sv6-153)**: Stadium that causes all attached Pokémon Tools to have **no effect**, including the effect of a Float Stone already attached.
- **Guzma (sm3-115)**: Supporter that switches the opponent's Active with a selected Benched Pokémon, then switches your own Active after that succeeds.

The distinction matters specifically because a freely playable independent Switch **Item** cannot resolve through Vileplume's Item lock, but a newly attached Float Stone may still remove the Retreat cost needed to undo Guzma's own switch.

## Controlled attack geometry

Retain the source-checked Shadow Rider champion board from [the preceding experiment](../shadow_rider_guzma_damage/): our Active Shadow Rider VMAX with five Basic Psychic, two Benched VMAX with two and one Psychic, and three unpowered support Basics. Eight Psychic in play give Max Geist 250 damage; the opposing Bench target is an undamaged, two-Prize, 210-HP Shadow Rider V. Without a self-switch remedy, the mandatory own Guzma pivot must be repaired by paying Retreat 2, reducing Psychic count from eight to six and Max Geist to 190. A full rules-complete opponent turn is outside this model.

For the purpose of isolating card semantics, **Vileplume's Item-lock restriction and Jamming Tower's Tool-effect restriction are independent experimental overlays** on the same fixed attacking board. They are not claimed to be simultaneously present in the published opposing Shadow Rider mirror deck.

| Conditional resource and effect state | Item play permitted? | Tool attachment/effect | Successful Guzma + two-Prize Max Geist? |
| --- | --- | --- | --- |
| No Float Stone, one Switch Item held | No (Vileplume Item lock) | none | **No** |
| One Float Stone in hand, Tool slot empty | No (Vileplume Item lock) | can attach and functions | **Yes** |
| Float Stone already attached to original VMAX | No (Vileplume Item lock) | functions | **Yes** |
| Float Stone in hand, explicit Pokémon Tool play prohibition | No | attachment prohibited | **No** |
| Float Stone in hand, Jamming Tower effect | No | attachment possible but effect suppressed | **No** |
| Float Stone already attached, Jamming Tower effect | No | effect suppressed | **No** |

With the second row, the best line can attach the Tool to the original Active, retreat it for zero into an unready Bench Pokémon, then Guzma the opponent's 210-HP V and promote the originally powered attacker back. All eight Psychic remain, making Max Geist do 250. Item lock does not obstruct the Tool attachment. In the Jamming Tower case, the Tool can be attached yet cannot lower the Retreat Cost. Thus it does not restore the knockout.

These conclusions assume Vileplume's Ability is actually active rather than suppressed by a separate Ability lock, and Jamming Tower remains the active Stadium where relevant.

## Implementation and verification

The exact bounded turn executor `tools/shadow_rider_tool_lock.py` expands `tools/shadow_rider_guzma_damage.py` with a physical owner for the one Float Stone, attachment from hand, a separately gated Switch Item, and independently configurable Item permission, Tool permission, and Tool-effect activation. The Tool is attached at most once, to an unoccupied Tool slot. Once attached, it remains with that Pokémon after a switch.

The independent breadth-first oracle `reproduce.py` enumerates all reachable turn states without importing the production recursive implementation. It checks Vileplume, Float Stone and Jamming Tower against their exact source print texts; asserts the six key cases above; and compares **6,912** independent combinations of Energy distribution, Supporter, Item permission, Tool play permission, Tool effectiveness, Float Stone attachment state and Switch Item possession. All cases condition on a single 210-HP two-Prize gust target.

Reproduce from the repository root with `python -m results.tests.shadow_rider_tool_lock.reproduce`.

**Deck-building scope:** The actual tournament champion list includes one Float Stone and one Guzma. This witness strengthens the rationale for retaining and protecting a Tool's distinct tactical role, but does not establish the correct copy count or superiority of an alternative 60. A full analysis would additionally model Float Stone being Prized, card access, attached Tools already occupying slots, Tools being discarded or moved, Ability/Tool lock precedence, and the opponent's strategic responses.
