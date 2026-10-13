# Aichi champion Shadow Rider: Dialga discard and competing Pokémon searches

**Status:** exact physical-opening calculation, source-print checked and exhaustive toy-validated. **Scope:** published 2026 Aichi champion's unchanged 60, going second. This measures available first-turn actions; it does not measure the likelihood of winning.

## Strategic question

Against Regidrago VSTAR, the champion's singleton **Dialga-GX** is a Dragon-type Basic with Timeless-GX. Placing it in discard can eventually provide the attack copied through the Mimikyu Copycat -> opposing Apex Dragon interaction, if the opponent first used a suitable attack and the copying sequence's requirements are satisfied.

The same card can pay **Mysterious Treasure** to retrieve a Psychic or Dragon Pokémon. When both **Radiant Eternatus** and **Mimikyu** remain in deck, one Treasure provides two competing choices:

* Fetch Radiant Eternatus and potentially end the turn with its Climactic Gate double-VMAX launch.
* Fetch Mimikyu to set up the later Regidrago-specific counter line.

The champion also has four **Fog Crystal**. Fog Crystal can independently obtain Mimikyu, a Basic Psychic Pokémon. With a Fog Crystal plus a Treasure accessible, the two searches can be sequenced before activating Climactic Gate, if other actions and Bench space permit. This avoids consuming one Treasure for two different targets.

## Physical sample and action constraints

The [published, print-verified champion deck](../../decks/shadow-rider-calyrex/) partitions into the following **60 physical copies**:

| Category | Count |
| --- | ---: |
| Dialga-GX (Basic Dragon, singleton) | 1 |
| Mimikyu (Basic Psychic, singleton) | 1 |
| Radiant Eternatus (Basic Dragon, singleton) | 1 |
| Other opening-eligible non-Radiant Basics | 11 |
| Shadow Rider Calyrex VMAX | 4 |
| Mysterious Treasure | 4 |
| Fog Crystal | 4 |
| All remaining cards, including 11 Psychic Energy | 34 |

Draw an unordered starting seven, set six face-down Prizes, then receive one natural first-turn draw. Condition on an initial seven with at least one non-Radiant Basic, consistent with the champion's first-turn Radiant setup concept. The event requires:

1. Dialga in the initial hand or first draw and **still in hand** to discard.
2. At least one of the **other 11 Basics already in the initial seven**, so Dialga need not be the forced Active. A Basic first drawn later does not repair a forced Dialga start.
3. At least one Mysterious Treasure in the initial hand or first draw.
4. Both Mimikyu and Radiant Eternatus among the 46 physical cards in deck after the opening, Prizes and first draw.
5. At least two VMAX among those 46 cards, allowing the nominal Climactic Gate two-VMAX selection.

The model does **not** give any other Items, Pokémon Abilities or Supporters a role. It assumes no Item/Ability lock, ignores the opponent's actual board and future responses, and models no continuation damage or Prize-taking. It also excludes direct-Radiant and direct-Mimikyu hand routes by construction. Remaining Bench capacity can be reserved through voluntary initial benching choices, but actual turn execution is outside the enumeration.

## Exact results

Probabilities are **conditional on an opening seven containing at least one of the 13 non-Radiant Basics**, whose exact probability is 9797437/11703240 = 83.715594998% before conditioning.

| Mutually distinguishable milestone or subset | Probability of Basic-valid deal |
| --- | ---: |
| **Shared Treasure fork**: Dialga payable, both search targets in deck, at least two VMAX in deck | **2.772251473%** |
| Fork with Dialga already in the opening seven | 2.400676194% |
| Fork with Dialga appearing as the first draw | 0.371575279% |
| Fork with **any Fog Crystal** held/drawn, enabling the independent Mimikyu search | **0.984274407%** |
| Fork with no Fog Crystal held/drawn | 1.787977066% |
| Fork with exactly one accessible Treasure and no Fog Crystal | **1.490683850%** |
| Fork with exactly one Treasure and at least one Fog Crystal | 0.857672137% |
| Fork with at least two Treasures accessible | 0.423895486% |

The one-Treasure/no-Fog event isolates a particularly clear local conflict between the two Pokémon searches. Quick Ball, a previously benched Pokémon, a later turn, or another effect could still offer an alternative, so this event does **not** assert that the whole match has a permanently forced choice. Two Treasures alone do not imply both are playable: another discard payment may be strategically unacceptable. Fog availability also does not guarantee favorable game continuation.

For reproducibility, the unconditioned **fork** probability is exactly **58613434588753/2525562843410880**. The unconditioned **Fog-accessible fork** probability is **6503254679603/789238388565900**. Conditioning divides each by **9797437/11703240**.

## Exact method and validation

[Kernel](../../../tools/shadow_rider_dialga_connector_fork.py), [source-grounded reproducer](reproduce.py).

Each outcome counts distinct unordered opening hands, the exact individual first natural draw, and unordered six-card Prize subsets with integer combinatorial multiplicity. Normalization is

\[
\binom{60}{7}\,53\,\binom{52}{6}.
\]

This is equal to dealing the starting hand, then six Prizes, then the first draw because the disjoint zones are exchangeable under a uniform shuffle. A singleton's identity and starting-Active opportunity are preserved explicitly. Prize VMAX allocation is summed exactly rather than treating two accessible VMAX as an independent event.

An **independent full physical-label oracle** enumerates every hand/draw/Prize deal in three smaller decks, including copies distinguished by physical label. Grouped and labeled output counters must match exactly for all categories. The three tests cover **12,600 + 27,720 + 360,360 = 400,680** complete toy deals. They test the first-turn Basic safeguard, both Treasure/Fog availability subsets, and VMAX Prize survival. No randomized Monte Carlo estimation is used.

The reproducer also checks the actual champion source counts and the exact English print identities and effects of sm5-100 Dialga-GX, sm2-58 Mimikyu, sm6-113 Mysterious Treasure, swsh6-140 Fog Crystal, and swsh12pt5-105 Radiant Eternatus in the repository card resource files.

## Competitive interpretation

These restricted forks occur in a small minority of Basic-valid opening deals. They expose real **connector opportunity cost** and the difference between a paid single-output search and combining independent search channels. They should **not** motivate card slots on frequency alone. The effect of preserving a future Mimikyu/Timeless-GX counter, as well as whether the opponent even plays Regidrago, must be evaluated in full game states.

Promising continuation: score choices using subsequent Regidrago Apex Dragon timing, surviving Mimikyu access, Dialga actually reaching discard, paid search resources, and the opponent's likely attack response. Cross-reference [Dialga discard payoff sensitivity](../../shadow_rider_dialga_payload_discard/) and [direct-Radiant-to-Max-Geist continuation](../shadow_rider_direct_launch_attack/).
