# Aichi Shadow Rider: exact Radiant Eternatus + Tapu Lele-GX dual-entry frontier

## Finding

The published 2026 Aichi Open League champion deck has one **Radiant Eternatus**, two **Tapu Lele-GX**, four **Shadow Rider Calyrex VMAX**, four **Mysterious Treasure**, one **Quick Ball**, one **Hisuian Heavy Ball**, and eleven **Psychic Energy** cards. These cards create competing acquisition routes for two distinct hand-to-Bench entry Abilities: Lele's *Wonder Tag* and Radiant's *Climactic Gate*.

The initial Active choice consumes a real physical Basic. A Lele forced to start Active cannot later trigger Wonder Tag merely by being in play; a Radiant forced Active cannot later use Climactic Gate without a card returning it to hand. The exact search frontier below accounts for this setup-role contention.

Under a **Basic-valid seven-card opener, six Prizes, and one natural draw going second**, the fraction of starts with source-constrained access to a **Wonder Tag Bench entry followed by Radiant Eternatus's two-VMAX launch** is:

| Hypothetical one-card Item discard policy | Role-blind estimate | Actual setup-role-aware access | Role-blind overstatement |
| --- | ---: | ---: | ---: |
| Use only held Psychic Energy to pay each search | 19.022546418% | **15.085879759%** | 3.936666659 percentage points |
| Mechanically discard any other unreserved hand card | 27.400239403% | **23.314279776%** | 4.085959627 percentage points |

**These are constrained access endpoints, not measured turn-one full-board outcomes or match win rates.** No extra opponent bonus cards are included in the quoted Aichi figures. Both models enforce the same search cost and physical Prize restrictions; the role-blind column deliberately overcredits setup-consumed trigger cards.

## Exact-print and source-deck inputs

The source is the complete, independently legality-checked [Aichi 2026 champion 60-card baseline](../competitive_deck_baselines/README.md). The [reproducer](reproduce.py) imports its quantities directly and verifies these English-print witnesses in the bundled card database:

| Pokémon or search Item | Copies | Selected English print |
| --- | ---: | --- |
| Radiant Eternatus / Climactic Gate | 1 | swsh12pt5-105 |
| Tapu Lele-GX / Wonder Tag | 2 | sm2-60 |
| Shadow Rider Calyrex VMAX | 4 | swsh6-75 |
| Mysterious Treasure | 4 | sm6-113 |
| Quick Ball | 1 | swsh1-179 |
| Hisuian Heavy Ball | 1 | swsh10-146 |

The remaining Basic starter copies number eleven, eleven cards are Basic Psychic Energy, and all other cards form a neutral class. Mysterious Treasure searches a Psychic or Dragon Pokémon while discarding one card. Quick Ball searches one Basic Pokémon and also discards one card. Hisuian Heavy Ball can return a Basic Pokémon from a face-down Prize card by replacing that Prize with itself, provided the search conditions are met.

## Mechanically bounded acquisition sequence

One natural turn-one draw occurs after setup and the six Prize cards. A successful line chooses the starting Active *from the opening seven*, then obtains a Lele copy to hand, plays that Lele onto the Bench to trigger Wonder Tag, obtains Radiant to hand, and finally plays Radiant onto the Bench to use Climactic Gate. Two of the four VMAX must still be **in the deck**, because Climactic Gate puts its targets from the deck directly into play. Resolving Climactic Gate ends the turn, so the Lele trigger must precede it.

The abstraction assumes the searched Supporter and any subsequent actions are strategically compatible, but does not require or value any chosen Supporter. It reserves enough Bench slots for the two Ability entrants and both VMAX.

Potential normal searchers are the four Treasures and one Quick Ball. Each actual Item can retrieve **one** missing Pokémon. The Heavy Ball provides one physically separate route for one Prized missing Basic. Both search Items can be used in a sequence where physically present and mechanically payable; no single search Item is counted twice. A normal search route requires the missing Pokémon to be in the deck, whereas a Heavy Ball route requires a Prized copy.

In the Energy-only scenario, each normal search consumes an observed Psychic Energy card from hand as its sole authorized discard type. The mechanical scenario may pay with any hand card beyond one Active Basic, the retained trigger copies and the Items used for those searches. This mechanical criterion ignores strategic discard opportunity costs and assumes the remaining generic cards are disposable.

## Exact conditional computation

Classify the original 60 into disjoint card classes for other Basics, Radiant, Lele, VMAX, Treasure, Quick Ball, Heavy Ball, Psychic Energy, and other filler. Use exact multivariate-hypergeometric weights for the observed opening+draw composition. If m opponent bonus cards are also drawn, the combined seen size is s = 7 + 1 + m.

The opening Basic acceptance denominator includes every Basic: eleven unrelated Basics, one Radiant and two Lele.

Given a seen union of s cards containing x unrelated Basics and l Lele copies, the opening-subset multiplicities for role-aware Active policy are:

- **Unrelated-Basic Active:** C(s,7) - C(s-x,7), with all l Lele copies available from the seen union.
- **One Lele forced Active:** C(s-x,7) - C(s-x-l,7), with only l-1 Lele copies available from the union.
- **Only Radiant satisfies setup:** the remaining Basic-valid opener assignments, which cannot realize the Radiant hand-entry endpoint with this route inventory.

The role-blind comparator credits every Basic-valid opener assignment, including the setup-consumed Lele or Radiant. Search eligibility, distinct Item capacity, payment and VMAX deck survival are then evaluated against explicitly enumerated Prized Radiant, Lele, and VMAX counts. Exact rational weights are summed. Neither model uses Monte Carlo sampling.

## Reproductions and sensitivity

Removing the Wonder Tag requirement gives the independently published [Radiant + two-VMAX Quick Ball frontier](../shadow_rider_quick_ball_frontier/) to full floating-point agreement:

| Reference endpoint with no Wonder Tag requirement | Exact resulting access |
| --- | ---: |
| Unrestricted mechanical search payment | 50.659437625% |
| Psychic Energy-only payment | 42.703458196% |

This recovers the correct single-Quick-Ball contribution from the full published list, and avoids comparing to older incomplete radiating-launch envelopes.

An exploratory counterfactual holds the **total fourteen ordinary Basics** constant and swaps unrelated starting Basics for Lele copies. All other counts and print families stay fixed for the mathematical exercise:

| Lele copies | Other starting Basics | Energy-only joint access | Mechanically paid joint access |
| ---: | ---: | ---: | ---: |
| 1 | 12 | 10.488501420% | 17.629263055% |
| 2, published list | 11 | **15.085879759%** | **23.314279776%** |
| 3 | 10 | 18.364894837% | 26.861746585% |
| 4 | 9 | 21.052709634% | 29.676848718% |

These counterfactuals optimize one narrow two-entry availability event only. Two-Prize Pokémon liabilities, lost alternate starters, hand disruption, future Supporter use, the high opportunity cost of the Wonder Tag body, and actual match performance are outside the comparison. The increase is no evidence that any swapped deck is competitively superior.

[Reproducer](reproduce.py) uses two **independent labeled physical-card reduced-deck oracles**. Each enumerates ordinary Basic-valid opening hands, Prizes, bonus draws, the natural draw, and the real starting Active role. The physical oracles exhaustively compare two payment policies, both with and without Wonder Tag, and role-aware versus role-blind evaluation to the exact class-count implementation. The normal published Aichi card identities and printed search text are checked in the same test. Run from repository root:

\`python results/shadow_rider_dual_entry_launch/reproduce.py\`

[Exact kernel](../../tools/shadow_rider_dual_entry_launch.py) and [CI validator](../../.github/workflows/validate-shadow-rider-dual-entry-launch.yml) preserve the computation.

## Limits and next steps

The champion list has additional potential access via Forest Seal Stone, Fog Crystal indirectly through other Basic or Psychic-Pokémon actions, Supporters, Draw Abilities, and further search lines, all omitted. Lock effects and opponent interaction are omitted. The setup role is optimized for **this specific endpoint** rather than the complete game. One Lele and Radiant must enter legally into sufficient Bench slots before Radiant ends the turn; some actual board positions cannot do so. The model also abstracts away the fact Wonder Tag's useful Supporter may need a separate action or may be obstructed by a Supporter lock.

A higher-fidelity continuation should integrate Forest Seal Stone with actual V Tool-host prerequisites, the real Supporter quota, two-Pokémon Bench entry reservation, and downstream Shadow Rider VMAX energy acceleration and turn-two attacks. A full headless engine with verified card behavior and capable decision policies will eventually be required to convert these probabilities into strength estimates.
