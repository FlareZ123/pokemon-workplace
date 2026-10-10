# Prize-card awards during a two-turn Beheeyem packet cycle

## Question

Earlier Beheeyem packet experiments model six face-down Prize cards that remain inaccessible through T3. In actual gameplay, a Knock Out by the first Mysterious Noise attack can award one or more Prize cards, and those cards enter the player's hand after attack resolution. A newly obtained Beheeyem, Triple Acceleration Energy (TAE), Computer Search or payment filler may help make the following turn's attack feasible.

**How much does a known one-Prize or two-Prize reward change next-turn packet availability, if the actual cards taken are still face down until chosen and revealed?**

The experiment conditions on an otherwise successful first attack and an **exogenous Prize reward count r in {0,1,2}**. It does not infer KO likelihood, opponent HP or how 90 damage could KO a damaged multi-Prize Pokémon. Two Prizes are a conditional state, not the expected outcome of an ordinary attack.

## Rules and strategic context

The supplied Advanced Player's Rulebook resolves an attack's damage and other effects before checking Knock Outs, then transfers appropriate Prize cards into hand during Knock Out resolution. Face-down Prize identities are hidden from the player until picked up. A skilled player may know which cards were Prized from inspecting the deck (K1), but without an independent revealing or arrangement effect that does not identify which face-down position holds which card.

The exact model therefore conditions on the full six-Prize multiset while drawing **r uniformly random physical Prize positions**. This is a clear distinction between player knowledge of the Prize composition and randomness in the newly obtained hand cards.

Mysterious Noise (Beheeyem sm11-91) returns itself and attached TAE (sm10-190), together with the underlying Elgyem, into the deck before the next turn. Consequently, the first packet is recyclable while the earlier Prized packet/tutor cards can simultaneously be released into the hand.

## Exact physical model

The starting condition matches [T2 rescue versus T3 defer](../beheeyem_tutor_timing/):

- A two-Elgyem-plus-one-anchor board was set up earlier. The Elgyem are old enough to evolve. These three Basics are removed from the remaining 57-card population.
- Six remaining cards are in the T2 hand, the next six are randomly Prized and 45 remain in the deck. Packet counts are B Beheeyem (1–4), T TAE (1–4), one physical search tutor, and 56-B-T neutral filler.
- First packet access is possible when both B and TAE are directly in hand, or when exactly one is held and a physically held tutor is both able to search the missing type and payable with neutral filler.
- A direct attack returns B+TAE+Elgyem into a **48-card** deck. A tutor-rescued T2 attack removed one card from the deck by search first, so it returns that same attacking stack into a **47-card** deck.
- The player is awarded exactly r random physical cards from the **six originally placed Prizes** after the first attack, leaving 6-r face-down. Awarded B, TAE, tutor or filler are added to hand.
- On T3, draw d cards uniformly without replacement from the fresh 48- or 47-card shuffled deck. Check whether the hand has both packet categories directly, or has exactly one category plus an available tutor with sufficient filler to discard. A tutor already spent on T2 cannot reappear from Prizes or deck.

The probability weights the T2 hand by a multivariate hypergeometric distribution, the complete six-Prize composition conditional on the hand, r randomly taken Prize cards and d randomly drawn T3 cards. All intermediate probabilities are exact fractions. Drawing Prizes does not affect the T3 deck size, since Prized cards are in a separate zone.

We assume that a won Prize reward has no adverse consequence for the player, that any neutral filler can be discarded, and that opponent actions and all remaining attack prerequisites are favorable. That makes this a pure **resource-supply** study.

## Findings

B=4 Beheeyem, T=4 TAE, one Computer Search and one T3 natural draw, conditional on the established three-Basic board:

| Prize cards awarded by first attack | First-packet incidence | Joint consecutive-packet incidence |
| ---: | ---: | ---: |
| 0 | 16.893119% | **0.662553%** |
| 1 | 16.893119% | **1.125764%** |
| 2 | 16.893119% | **1.679597%** |

Awarding one random Prize increases the joint packet event by **0.463211 percentage points**, approximately **69.9% relative** to zero awarded Prizes. Two awarded Prizes increase it by **1.017044 percentage points**, approximately **153.5% relative**. First-packet incidence is identical across rows since awards occur **after** that first attack, conditional on it being possible.

The effect is visible even when the T3 player has no blind draw:

| T3 blind draws | 0 Prizes awarded | 1 Prize awarded | 2 Prizes awarded |
| ---: | ---: | ---: | ---: |
| 0 | 0.272430% | 0.600385% | 1.042626% |
| 1 | 0.662553% | 1.125764% | 1.679597% |
| 2 | 1.214069% | 1.782826% | 2.418890% |
| 3 | 1.890632% | 2.536582% | 3.229858% |

For a constrained B=1/T=4 deck with Mysterious Treasure and d=1, joint access is 0.059878% with no T2 Prize, 0.093157% with one, and 0.131495% with two. The increase here depends on whether the single Beheeyem and the tutor are in hand, Prizes, or recycled deck.

**Prize-taking has resource timing value beyond progressing toward the six-Prize win condition.** A successful first attack can return otherwise inaccessible search or attack packet cards to hand in time for the next turn, partially replacing an extra blind draw. The exact value is strongly state-dependent.

## Validation

- [Exact engine](../../tools/beheeyem_prize_packet.py) enumerates complete physical hand, six-Prize, awarded subset and T3 draw category counts. It returns first-packet, direct-second, tutor-rescued-second and total two-packet exact probabilities.
- [Reproduce](reproduce.py) checks all 16 B/TAE copy-count pairs, all four one-copy tutor modes, T3 draw budgets 0–3, and awards r=0,1,2. It enforces parity with the earlier zero-award engine, first-packet invariance, monotonic Prize benefit and interchange symmetry of the two-discard single-category searchers.
- [Independent Monte Carlo](monte_carlo.py) physically shuffles the residual 57 cards, marks six as Prizes, searches and consumes a T2 tutor if needed, returns the first attacker and its attached cards, randomly awards Prize identities, reshuffles and draws T3 cards, then checks the next packet. Four cases use 200,000 simulations each and compare against exact values within sampling tolerance.
- [GitHub Actions workflow](https://github.com/FlareZ123/pokemon-workplace/actions/workflows/validate-beheeyem-prize-packet.yml) runs the exact and independent physical-shuffle checks.

## Limitations and next directions

The exact conditional model does not estimate the chance of actually earning one or two Prizes with Mysterious Noise. A real match demands opponent HP/damage, Weakness/Resistance, damage reduction and KO timing, plus defender choice and alternative attacks. It also assumes the first attack's Item lock has no effect on the *player's own* subsequent Item access, while the opponent may establish further locks during its reply.

A stronger continuation is to make the award count depend on opponent state and attack target, then feed the revealed Prize cards into a policy that can react to the random reward before selecting T3 actions. Another line is to add conditional opponent disruption that removes the newly acquired hand cards. These steps are necessary before estimating sustained lock incidence or match outcomes.
