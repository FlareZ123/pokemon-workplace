# Two independent own-pivot recovery channels and the Garbotoxin / Jamming Tower conjunction

**Status:** Exact conditional same-turn KO reachability model. Tested against an independent physical-action graph. This is a rules-dependent matchup hypothesis, not evidence of real tournament win rates.

## Published decks and source evidence

The [Aichi 2026 champion Shadow Rider Calyrex](../../decks/shadow-rider-calyrex/) list has one **Latias ex** (sv8-76), one **Float Stone** (xy8-137), and one **Guzma** (sm3-115). The [eighth-place Mega Absol / Garbodor](../../decks/mega-absol-garbodor/) list has **two Garbodor** (bw11-68) and **four Float Stone**, which can activate its Garbotoxin Ability while attached. **Neither of these published 60-card lists contains Jamming Tower**; its addition here is a distinct hypothetical opponent-counterplay state.

Exact English card print facts:

- Latias ex's *Skyliner* makes your Basic Pokémon have **no Retreat Cost** when its Ability is active.
- Float Stone makes the Pokémon it is attached to have **no Retreat Cost** while that Tool's effect is active.
- Garbodor's *Garbotoxin* removes other Pokémon Abilities while a Pokémon Tool **card is attached to Garbodor**, even if that Tool's own effect is nullified.
- Jamming Tower (sv6-153) makes attached Pokémon Tools have **no effect**. It does not remove or discard those cards.
- Path to the Peak (swsh6-148) removes Rule Box Pokémon Abilities, disabling Latias ex but leaving an attached Float Stone's effect alone.

A Stadium has a single shared play zone. In these states Path to the Peak and Jamming Tower are **mutually exclusive**. A tool-attached Garbodor can exist concurrently with either Stadium; its Garbotoxin condition still sees an attached Tool under Jamming Tower. Other lock-source suppression, Stealthy Hood, Tool removal, stadium replacement and precedence cycles are outside this model.

## Attack setup and tactical objective

Use the previous [champion Max Geist / Latias-Guzma board](../shadow_rider_latias_lock/): own Active VMAX has five Basic Psychic, two Benched VMAX have two and one, and three unpowered Basic support Pokémon include Latias ex. Our Bench is full. The target is the healthy opposing 210-HP two-Prize Shadow Rider V on the Bench. Max Geist does 250 while eight Psychic remain in play, but falls to 190 after spending two Psychic on ordinary VMAX Retreat. A held Guzma must switch our own Active after switching the opposing target in.

An existing or freely playable Float Stone can rescue the powered original VMAX through a free Retreat. Latias ex can also rescue it by allowing the newly promoted Basic Pokémon to free Retreat back after Guzma. Each rescue needs one functioning effect. The player gets exactly one normal Retreat, one Guzma and one attack. No additional attachments from hand, Underworld Door, Stadium replacement or opposing actions are allowed.

## Exact outcome matrix

Here both Latias ex is on the Bench and Float Stone is already attached to the originally Active VMAX. No Tool removal or Bench reconfiguration occurs.

| Stadium | Tool-attached opposing Garbodor's Garbotoxin active? | Latias *Skyliner* | Float Stone effect | Two-Prize Max Geist reachable? |
| --- | --- | --- | --- | --- |
| None | No | Active | Active | **Yes** |
| Path to the Peak | No | Suppressed | Active | **Yes** |
| Jamming Tower | No | Active | Suppressed | **Yes** |
| None | Yes | Suppressed | Active | **Yes** |
| Path to the Peak | Yes | Suppressed | Active | **Yes** |
| Jamming Tower | Yes | Suppressed | Suppressed | **No** |

The lone-Stadium cases expose a **two-channel hedge**. Path disables Latias, yet Float Stone still enables free Retreat. Jamming disables Float Stone, yet Latias still enables free Retreat through an unpowered Basic. The combination of *Garbotoxin with an attached Tool* plus *Jamming Tower* removes both channels: the attached Tool still triggers Garbotoxin's condition while its own effect is suppressed. With the fixed eight-Psychic board, the necessary paid retreat then loses the two-Prize KO.

That is a conditional vulnerability to *combined persistent locks*, and there is no claim that the published eighth-place Mega Absol/Garbodor 60 actually contains the Jamming Tower needed for this combined line.

## Validation and limits

`tools/shadow_rider_dual_rescue.py` carries the actual Basic/Evolution distinction, Latias ex's printed two-Energy own Retreat Cost when its Ability is suppressed, whole attached Psychic Energy counts, Float Stone attachment timing and two independent continuous effect predicates. It explores every permitted order of a single normal Retreat, one optional Tool attachment, one Guzma and one final Max Geist. The independent `reproduce.py` enumerates the equivalent action state graph with breadth-first search, validates actual card print text, and checks **5,184** configurations of attached Energy, Latias presence, Garbotoxin on/off, Stadium name, Float Stone in hand/on board, and Tool play permission.

Reproduce from the repository root: `python -m results.tests.shadow_rider_dual_rescue.reproduce`.

All statements are conditional single-turn rules evaluations with a constructed opposing board. The correct decklist response to this interaction requires a representative opposing metagame, knowledge of Tool/Stadium availability, Bench saturation, multiple Supporters and next-turn utility. The champion decklist and eighth-place Garbodor decklist have been preserved without alteration.
