> **Further research:** [Preloading a third Elgyem](../beheeyem_three_elgyem_frontload/) provides an alternate turn-four continuation without reserving a turn-three Basic tutor, changing the optimum for high-HP anchors. This report's reserve-only optimum applies only to its specifically defined event.

# Buddy-Buddy Poffin changes the Beheeyem staging/reserve optimum

## Question

The [joint Beheeyem staging/reserve experiment](../beheeyem_joint_staging_reserve/) optimized four Battle VIP Pass / Nest Ball slots and selected **1 VIP + 3 Nest** for the joint first-turn setup plus turn-two reserve event. That restricted choice set omitted **Buddy-Buddy Poffin**, a legal paper-Expanded Item in the bundled card snapshot.

Poffin searches the deck for up to two Basic Pokémon of **70 HP or less**, then puts them directly onto the Bench. The actual `sm11-90` Elgyem is **60 HP**, and the `bw7-120` Lillipup that evolves toward Sentinel Stoutland is **60 HP**. Both are eligible. A counter-regime models a partner Basic above 70 HP, such as the 80-HP `me55-93` Murkrow. This is a **print-dependent** comparison.

Local primary sources: `resources/cards/en/sv5.json` (`sv5-144` Poffin), `resources/cards/en/sm11.json` (`sm11-90` Elgyem), `resources/cards/en/bw7.json` (`bw7-120` Lillipup), `resources/cards/en/me55.json` (`me55-93` Murkrow), `resources/cards/en/swsh8.json` (`swsh8-225` VIP), and `resources/cards/en/sv1.json` (`sv1-181` Nest). Official [Buddy-Buddy Poffin card text](https://asia.pokemon-card.com/sg/card-search/detail/21759/) independently confirms the effect. The English-language bundled card pool remains a regional-scope limitation.

## Experimental definition

The 60-card synthetic deck has four Elgyem, four partner Basics, and **exactly four Item slots** split across VIP (`V`), Nest (`N`), and Poffin (`P`). Remaining cards are inert. Of the randomized opening seven, **one Elgyem must already be present and chosen Active**. After setting six random Prize cards and drawing one card on the first turn, stage a second Elgyem and one partner Basic on the Bench by first-turn end. For every search, the necessary target must actually remain in the post-Prize deck.

The stricter joint event additionally requires an **unspent Nest or Poffin in hand by the start of own turn two**, including that turn's one natural draw, which can be retained to fetch the returning Elgyem on own turn three. VIP expires after first turn.

The policy uses VIP for first-turn capacity first and then spends as few live tutors as necessary. A Poffin fetches up to two missing eligible Basics; a Nest fetches one. If the partner Basic exceeds 70 HP, Poffin may fetch Elgyem only, while VIP and Nest retain access to either type. This policy is optimal for retaining at least one post-T1 live Item **within the defined event**, where no other Item-specific opportunity cost or ancillary search target is modeled.

No mulligan-conditioning, opponent action, extra draw, Supporter, recycle search, turn-two Beheeyem, Triple Acceleration Energy, anchor evolution, retreat, or Item lock is simulated. The joint event measures a **necessary continuation resource**, not actual renewable lock execution or match success.

## Exact method

`reproduce.py` enumerates all opening-seven category count vectors, one first-turn natural draw, and six random Prizes. Each state is weighted by products of exact binomial coefficients. Search targets are removed from the deck before the turn-two draw; its size is `46 - missing Basics`. The program uses rational arithmetic and a common integer continuation denominator `lcm(44,45,46)`. All evaluated sample weights conserve

`C(60,7) * 53 * C(52,6)`.

There are 15 possible four-slot compositions. Both partner eligibility regimes are evaluated exactly. The no-Poffin rows reproduce the previous five published results byte-for-byte at six decimal places.

An **independent physical-shuffle Monte Carlo**, `monte_carlo.py`, shuffles whole synthetic decks, physically sets six Prizes before the first-turn draw, searches actual residual deck cards, and samples the turn-two draw. It validates six representative cases at 200,000 seeded trials each.

## Main results

| Four Item slots | Partner at most 70 HP: staged | Partner at most 70 HP: joint | Partner over 70 HP: joint |
| --- | ---: | ---: | ---: |
| 4 VIP | 18.483546% | 0.000000% | 0.000000% |
| 4 Nest | 11.775394% | 2.757941% | 2.757941% |
| 1 VIP + 3 Nest | 13.452432% | 3.181558% | **3.181558%** |
| 3 Poffin + 1 Nest | 16.806508% | 4.408952% | 2.477227% |
| 4 Poffin | **18.483546%** | **4.510096%** | 2.183252% |

With both Basics eligible, **4 Poffin is the unique joint-event maximizer** among the fifteen compositions. It increases the event from **3.181558%** to **4.510096%**, an absolute gain of **1.328538 percentage points** and **41.76% relative** to the previously restricted best. All-VIP and all-Poffin tie for first-turn board setup, but only Poffin remains live.

When the partner is Poffin-ineligible, **1 VIP + 3 Nest remains the unique joint-event maximizer**. All-Poffin drops to 2.183252% joint. An eligibility predicate, determined by the exact Basic Pokémon print, changes the preferred allocation.

The full 15-row values for both regimes are printed by `reproduce.py`.

## Structural reason and limitations

Under the 70-HP restriction, Poffin can perform every required early and late search action of VIP and Nest in the model. It matches VIP's first-turn two-Basic capacity and stays usable after turn one. It can emulate one Nest search without discarding cards. Replacing any VIP or Nest with Poffin therefore **weakly dominates on both modeled events** when both target Basics have at most 70 HP. The exact experiment quantifies the strict gain across the four-slot candidates.

This coupling argument does **not** apply with ineligible targets or with additional goals, competing search demand, card-name interactions, Stadium/Ability suppression, Item lock, hand resource costs, or Bench oversubscription. In the high-HP partner regime, Poffin can reach only the missing Elgyem, and the need to find a distinct high-HP partner restores the earlier VIP/Nest tradeoff.

An especially important omitted choice is to Bench **extra** Elgyem beyond the target of two on turn one. Poffin might enable an alternate multi-attacker continuation with less need for a recycled Basic. The current event deliberately leaves this for a future stateful turn-three model.

## Reproduce

Run `python results/beheeyem_poffin_eligibility/reproduce.py` and `python results/beheeyem_poffin_eligibility/monte_carlo.py`. The sibling `reproduce.py` asserts equality to the previous no-Poffin baseline and confirms both optima. The independent Monte Carlo checks exact values for representative cases using a fixed seed.

**Follow-up priorities:** represent spare Benched Elgyem as state and compare return/re-evolution against maintaining a third line; add actual turn-two Beheeyem/Triple Acceleration Energy access and Poffin's potential resource contention. Measure opponent-specific lock continuation before converting the raw access result into deck recommendations.
