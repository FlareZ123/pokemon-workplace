# Physical one-copy tutoring in the Beheeyem two-attack packet loop

## Question and conclusion

The earlier [multi-draw packet frontier](../beheeyem_multi_draw_packet/) calculated the chance of drawing Beheeyem plus Triple Acceleration Energy (TAE) for successive turns after Mysterious Noise recycles the first packet. How much does adding **one physical search card** help when that tutor may be Prized, unseen or unusable for lack of discard payment?

For four Beheeyem, four TAE and one T3 draw, the exact two-packet rate is **0.3163517%** with no tutor, **0.6177354%** with one physical Computer Search and two disposable cards, and **4.0846318%** if a free universal search is guaranteed after the draw. These are **joint card-access rates conditional on an established board**, not deck or match win rates.

## Card and rules basis

- Beheeyem (sm11-91) uses Mysterious Noise: shuffle itself and all attached cards into deck, applying an opponent-turn Item lock. The Elgyem underneath also returns.
- Triple Acceleration Energy (sm10-190) supplies three Colorless Energy to an Evolution Pokémon, and is discarded at turn end only if still attached; Mysterious Noise returns it first.
- Computer Search (bw7-137) is an ACE SPEC Item searching for any one card after discarding two other cards.
- Mysterious Treasure (sm6-113) is an Item that discards one other card to search for a Psychic or Dragon Pokémon, covering Psychic Beheeyem.
- Ultra Ball (bw5-102) searches for a Pokémon after discarding two other cards.
- Guzma & Hala (sm12-193) is a Supporter whose optional discard of two other cards permits searching for a Special Energy in addition to its Stadium/Tool channels, covering TAE.

These definitions come from the repository's supplied English card database. The Advanced Player's Rulebook establishes attack resolution and ordinary Trainer-use quotas. Printed variants of the same card name do not increase allowable deck copies.

## Conditioned exact model

Condition on three Basics already in play by T1: two old-enough-to-evolve Elgyem and an anchor Basic. Of the remaining **57** physical cards, there are B Beheeyem (1–4), T TAE (1–4), exactly one tutor, and 56-B-T neutral filler cards.

1. Six residual cards are in hand by T2, followed by six uniformly random Prizes and a 45-card deck. Require a Beheeyem and a TAE directly in the hand.
2. Execute the first attack, consuming one B and one T from hand. Return B, T and the Elgyem underneath it to the deck: 45 + 3 = **48** cards.
3. Shuffle, then draw d cards at T3. A second packet is in hand if one of each category remains.
4. Otherwise, the tutor may obtain **one** missing category if physically held or drawn by T3, if its search class supports that target, and if the hand contains enough neutral filler cards for its discard payment.
5. Integrate over the exact multivariate hypergeometric distribution of T2 hand, Prize composition and T3 drawn cards. Also calculate an optimistic ceiling where a free universal search is always accessible after the d draws.

The model conserves the physical tutor through Prizes, hand and deck. It conserves recycled B and T. If either category is missing from the T3 hand, at least its recycled copy is in the T3 deck and can be searched. For complete formula and exact rational arithmetic, see the linked implementation below.

The assumption that every neutral filler can be sacrificed is generous. The model leaves out UDP/DCI, Supporter contention, ACE SPEC slot competition, opposing locks, access to draw actions themselves, evolution and switching feasibility, and all other gameplay costs. Its outputs are conditional card-access events.

## Exact results

All probabilities are the joint T2 **and** T3 packet-access event after conditioning on the three Basic board cards.

| B / TAE | T3 draws | No tutor | Computer Search | Mysterious Treasure | Ultra Ball | Guzma & Hala |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 4 / 4 | 1 | 0.316352% | **0.617735%** | 0.467146% | 0.467044% | 0.467044% |
| 4 / 4 | 3 | 0.979864% | **1.619960%** | 1.299912% | 1.299912% | 1.299912% |
| 4 / 4 | 5 | 1.896601% | **2.865067%** | 2.380834% | 2.380834% | 2.380834% |
| 1 / 4 | 1 | 0.007920% | **0.057902%** | 0.053147% | 0.053120% | 0.012703% |
| 1 / 1 | 1 | **0%** | 0.002848% | 0.001424% | 0.001424% | 0.001424% |

For 4/4 and d=1, adding one Computer Search multiplies the modeled event by **1.952686**. The ideal guaranteed universal-search 4.084632% ceiling is **6.6123 times** the actual one-copy Computer Search rate, emphasizing physical availability over graph reachability.

When B=1 and T=4, Psychic-Pokémon search is especially important after the one Beheeyem is shuffled back. Mysterious Treasure yields 0.053147%, versus Guzma & Hala's 0.012703%; opposing card classes and other deck obligations remain omitted. When B=T=1, a universal tutor can break the two-draw-category impossibility at d=1, but only in a minuscule slice of hands.

The difference between one-discard Mysterious Treasure and two-discard Ultra Ball is small **under this neutral-filler model**. Real hands containing protected singleton cards can make that payment gap much more important.

## Reproducibility

- [Exact engine](../../tools/beheeyem_physical_tutor.py): all probabilities are exact Python Fractions, including a free-universal-search ceiling.
- [Deterministic regression](reproduce.py): all 16 B/TAE copy-count pairs, four modes and T3 draws 0–5. Compares with the existing blind-draw engine, checks bounds, monotonicity, known fractions, payment ordering, B/T symmetry, and 48-draw certainty.
- [Independent physical-shuffle validation](monte_carlo.py): 200,000 shuffled-deck trials for each of four cases, including six physical Prizes, explicit attack recycling, fresh reshuffle, tutor location and discard feasibility.
- [CI run 38093683090](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38093683090): **passed** deterministic and Monte Carlo checks on 2026-10-10.

## Next questions

The strongest next test is to assign realistic hand discard protection and evaluate Computer Search's opportunity cost when it could establish the T2 packet rather than being held for T3. A second step would give each tutor an actual access path and shared turn budget, instead of assuming all extra draws and the first attack's setup happen exogenously. These are needed before deriving concrete deck-slot recommendations.
