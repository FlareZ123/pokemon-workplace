# Forest Seal Stone Tool occupancy can block the Float Stone recovery line

## Question

The 2026 CL Aichi Open League winning Shadow Rider Calyrex deck includes one each of **Forest Seal Stone**, **Float Stone**, and **Field Blower**; it also has **Dimension Valley** and **Sky Field** as Stadium options (source: https://limitlesstcg.com/decks/list/26807).

A previously validated response after Regidrago's Apex Dragon -> Trifrost bonus-turn knockout was:

`Tulip -> Mimikyu + two Psychic Energy into hand -> Bench Mimikyu -> Underworld Door + manual attachment -> Float Stone on Active Shadow Rider VMAX -> retreat Mimikyu Active -> Copycat`.

What happens if **Forest Seal Stone is already attached to the incumbent Active Shadow Rider VMAX**?

The normal Pokémon Tool attachment rule allows only one Tool on each Pokémon at a time, and a player cannot simply replace it with a different Tool. Forest Seal Stone therefore occupies the same slot needed by Float Stone. Drawing Float Stone alone does not solve the promotion step.

## Physical repair

**Field Blower** (`sm2-125`) is an Item that may discard up to two in combination of Pokémon Tools and Stadiums in play, including the user's own. In an Item-unlocked state:

1. Play Field Blower, choosing your own Active VMAX's Forest Seal Stone.
2. Attach Float Stone to the now-empty Tool slot.
3. Recover, energize and promote Mimikyu through the prior Tulip route.

An attached **Forest Seal Stone** (`swsh12-156`) can itself provide its VSTAR Power, **Star Alchemy**, if its effect works and the player has not spent a VSTAR Power. If Field Blower is in deck and Star Alchemy can be used, the nested action chain is:

`Star Alchemy -> search Field Blower -> discard the Forest Seal Stone providing the search -> attach Float Stone`.

This has a striking connector property: a reusable-looking search Tool must be voluntarily removed to open the position required by the line it searched for.

The VSTAR Power slot is then consumed. Forest Seal Stone does not automatically detach after using Star Alchemy, so discarding it is a separate, necessary action.

## Interacting Item and Tool locks

The Advanced Player's Rulebook B-02 distinguishes Pokémon Tools from Items, including older Sword & Shield/XY Tools whose printed header may also say Item. Consequently:

- **Item lock alone** prevents Field Blower, although Float Stone can still be attached to an empty Tool slot and Tulip remains playable.
- If Forest Seal Stone already occupies the Active Tool slot, Item lock prevents the Field Blower release line.
- **Jamming Tower** (`sv6-153`) makes attached Pokémon Tools have no effect. This prevents Forest Seal Stone's Star Alchemy while Jamming Tower remains in play and makes Float Stone's free Retreat Cost effect ineffective.
- If Item play is available and Field Blower is already accessible, **one Field Blower** can discard both the incumbent Forest Seal Stone and the Jamming Tower Stadium. The Item's two-target text makes both repairs simultaneous.
- If a different Stadium such as Dimension Valley is available, it can replace Jamming Tower without playing an Item. With Forest Seal Stone still attached, the sequence may be `play Dimension Valley -> activate Star Alchemy -> search Field Blower -> discard own Tool -> attach Float Stone`.
- With no incumbent Tool, playing Dimension Valley or Sky Field to replace Jamming Tower can restore Float Stone's effect **even while Item-locked**, assuming Stadium play is available and there is no other applicable Tool lock.

The bounded search treats Forest Seal Stone on Active VMAX, Field Blower presence in hand/deck, one-use VSTAR Power, Jamming Tower, replacement Stadium availability and the Item lock independently.

It also preserves the option to avoid Float Stone: when Night Stretcher can recover Mimikyu, enough Psychic Energy is already in hand, and Guzma is usable against an opponent with a Bench, Tool occupancy alone does not block every route.

## Conditional state matrix

| Starting condition | Can the modeled Tulip/Float Stone line be repaired? |
| --- | --- |
| Active FSS, Field Blower in hand, Items unlocked | Yes |
| Active FSS, Field Blower in hand, Items locked | No |
| Active FSS, Field Blower in deck, Star Alchemy unused and active, Items unlocked | Yes |
| Same, Star Alchemy already used | No |
| Active FSS, Jamming Tower, Field Blower in hand, Items unlocked | Yes; one Field Blower removes both |
| Active FSS, Jamming Tower, Field Blower only in deck, no replacement Stadium | No; Star Alchemy's Tool effect is suppressed |
| Same, Dimension Valley in hand and Items unlocked | Yes; Stadium unlocks Star Alchemy, then Field Blower |
| Active Tool slot empty, Jamming Tower, Dimension Valley in hand, Item lock | Yes; Stadium and Float Stone remain playable |
| Active FSS, Jamming Tower, Dimension Valley in hand, Item lock | No, within the named Tool-removal package |

Every case assumes the underlying Mimikyu recovery, Energy, Supporter, Bench and GX-history conditions from the earlier model.

## Reproduction

`tools/shadow_rider_tool_slot_repair.py` enumerates the pre-recovery Tool/Stadium repair actions, then calls the independently validated `tools/shadow_rider_post_trifrost_recovery.py` from each resulting state.

`results/shadow_rider_tool_slot_repair/reproduce.py` checks source texts for Forest Seal Stone, Float Stone, Field Blower, Jamming Tower, Dimension Valley and Sky Field and verifies positive and negative cases.

Run `python results/shadow_rider_tool_slot_repair/reproduce.py`.

The research establishes conditional rules and bounded routes. It does not assert that Forest Seal Stone was attached to the Active VMAX during the tournament game, that Jamming Tower was actually used in the event, or that these resource chains were likely to be assembled. Other retreat, gust, recovery, and lock-removal effects lie outside the named action package.

## Broader significance

This demonstrates a **three-way connector bottleneck**: Forest Seal Stone can obtain a needed card, yet its physical attachment obstructs the Float Stone needed to promote Mimikyu; Field Blower repairs the slot but is an Item vulnerable to Budew lock; and a Tool-locking Stadium can suppress the very Star Alchemy ability that would have searched Field Blower.

A graph can show `Forest Seal Stone -> Field Blower -> Float Stone`, but actual execution requires verifying attached-Tool occupancy, VSTAR-Power use, Item restriction, Stadium state and card-access sequencing.
