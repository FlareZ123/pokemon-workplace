# Face-up Prize information can more than double Beheeyem packet access

## Research question and card basis

After a Beheeyem Mysterious Noise attack takes a Prize, knowing that a needed Beheeyem, Triple Acceleration Energy (TAE) or Computer Search was Prized does not normally tell the player which face-down Prize position contains it. The player may have K1 knowledge of the complete six-Prize **multiset** after searching their deck, but selection of a face-down Prize is still uncertain.

**Town Map (Black & White Plasma Storm, bw7-136)** is an Item whose English text says:

> Turn all of your Prize cards face up. (Those Prize cards remain face up for the rest of the game.)

With Town Map's effect already in place, a player taking one or more Prizes can identify and select specific Prize cards. This study models the upper bound on *next-turn attack packet access* from optimally choosing r=1 or r=2 known face-up Prize cards instead of taking them blindly.

The model assumes perfect Prize-position mapping is available for free. It does **not** include a physical Town Map in the 60-card list, the Item's search/access cost, its competition for Item search, or the tactical value of choosing other Prizes. It is therefore a **value-of-information upper bound**, not an argument to automatically add Town Map to a deck.

## Physical continuation model

Use the established board state of prior investigations: two mature Elgyem and an anchor Basic already in play; a 57-card residual population containing B Beheeyem, T TAE, one physical paid tutor, and neutral filler. Six cards are in the T2 residual hand, six are uniformly placed as Prizes, and 45 are in deck.

The first B+TAE Mysterious Noise attack can be direct or rescued by a physically held tutor that searches one missing packet category and pays its discard cost from neutral filler. The attack returns the Beheeyem, attached TAE and underlying Elgyem to the deck. There are 48 post-attack deck cards on the direct route, or 47 if the tutor first searched a missing card.

Condition on the first attack earning exactly **r in 0,1,2 Prizes**. The model compares:

- **Face-down baseline:** select r cards uniformly without replacement from the six original face-down Prizes, then receive d blind T3 deck cards.
- **Face-up mapping:** after seeing the full six-Prize composition and positions, select exactly r Prize cards whose categories maximize the exact probability of a second Beheeyem+TAE packet after the next d blind draws.

Every choice is made **before** the future random deck draw. The solver compares legal subsets of Prize categories and selects the highest expected attack-packet probability in each physically possible known-Prize state.

A complete second packet can be held directly or completed by a newly available one-copy tutor with enough discardable neutral filler. The solver tracks the tutor in the current hand, original Prizes and post-attack deck, including whether it was already spent to rescue the first attack.

## Exact results: four Beheeyem, four TAE, one Computer Search

With one additional T3 natural draw (d=1), all rates are joint T2-and-T3 packet access conditioned on an established three-Basic board:

| Prizes taken from first attack | Random face-down selection | Optimal known face-up selection |
| ---: | ---: | ---: |
| 0 | 0.662553% | 0.662553% |
| 1 | **1.125764%** | **2.926368%** |
| 2 | **1.679597%** | **4.452270%** |

The marginal value of optimal face-up selection is **+1.800604 percentage points** when taking one Prize, or **+2.772674 percentage points** when taking two. For one Prize, mapped selection multiplies the conditional packet incidence by approximately **2.60**.

This large potential benefit is an upper bound conditional on both making the initial attack and having mapped information beforehand. Any actual Town Map draw/search/use probability or other displaced deck card must be integrated before judging a decklist substitution.

The same comparison for four Beheeyem and four TAE with the one-discard Mysterious Treasure tutor gives **0.833836% blind** versus **2.229612% mapped** for one Prize and one T3 draw.

## A strong K1 witness

Consider the one-Prize case with four Beheeyem, four TAE, one Computer Search, and one ordinary T3 draw:

- T2 hand: **zero Beheeyem, two TAE, one Computer Search, three neutral filler**.
- The player spends Computer Search and two filler cards to fetch a Beheeyem from the deck, then attacks using that Beheeyem and one TAE.
- Remaining hand after the first attack: **one TAE and one filler**.
- Original six Prizes: **one Beheeyem and five filler**.
- The attack recycles the first Beheeyem, TAE and underlying Elgyem. T3 deck has **3 Beheeyem, 3 TAE and 41 filler**, totaling 47. Computer Search was already spent.

If the player can **select the face-up Prized Beheeyem**, the hand contains both B and TAE before T3 drawing. The packet probability is **100%**.

If the Prize is selected blindly, the player hits the Beheeyem with probability one sixth. Otherwise, one T3 draw must obtain a Beheeyem from the 47-card deck. The exact resulting packet probability is **31/141 = 21.985816%**. The known-face advantage is **110/141 = 78.014184 percentage points** in this state.

This witness makes the value of mapping clear: information about the Prize *composition* alone is insufficient to choose its face-down physical position, while face-up mapping makes an otherwise unlikely critical recovery deterministic.

## Other copy counts and number of draws

| B / TAE | Tutor | T3 draws | Prizes taken | Blind | Face-up mapped |
| --- | --- | ---: | ---: | ---: | ---: |
| 4 / 4 | Computer Search | 0 | 1 | 0.600385% | 1.899603% |
| 4 / 4 | Computer Search | 1 | 1 | 1.125764% | 2.926368% |
| 4 / 4 | Computer Search | 1 | 2 | 1.679597% | 4.452270% |
| 1 / 4 | Mysterious Treasure | 1 | 1 | 0.093157% | 0.244499% |
| 1 / 4 | Mysterious Treasure | 1 | 2 | 0.131495% | 0.328521% |

In a finite scan of **1,152** parameter configurations (16 B/TAE copy pairs, four tutors, d=0–5, and Prize awards r=0–2), mapped selection is never worse than a blind selection, and gives a strictly positive improvement in **742 configurations**. The remaining zero-improvement cases include all r=0 scenarios and some states where the packet cannot be completed within the draw budget or all available Prize choices have equivalent value.

The mapped option is also monotone in number of Prizes awarded across the finite grid, because choosing more cards can retain all critical benefits of the smaller selection under the simplified immediate packet objective.

## Interaction with opponent hand resets

The value above assumes the selected Prize cards **remain in the hand** until the player's T3 access decision. If the opponent plays **Iono** or **Marnie** immediately after the first attack, the entire current hand, including the deliberately selected Prize cards, is bottomed before T3 draws. In this narrow packet-access model, each mapped choice then yields the same fresh top-deck hand distribution for fixed r, erasing the near-term selection advantage.

If the opponent instead plays **N**, the acquired Prize cards shuffle into the full deck and change its composition. In that case, optimizing Prize selection against N rather than against an uninterrupted hand would be a distinct information-sensitive policy problem.

This observation connects [opposing Supporter resets](../beheeyem_supporter_reset/) with the present Prize-map upper bound. It should not be interpreted as Town Map losing all value under disruption in a full match, because its face-up information remains available on future turns and some Prize selections have other tactical consequences.

## Methods and verification

- [Exact mapped-Prize engine](../../tools/beheeyem_mapped_prizes.py) enumerates T2 hand, Prize composition, legal first-packet source, 47/48-card T3 deck, each valid r-card Prize subset, and resulting T3 packet probability. It computes both the uniform face-down average and the best face-up selection with exact rational arithmetic.
- [Regression](reproduce.py) validates all 1,152 configurations, cross-checks the blind branch against the separately implemented Prize-award model, asserts optimal selection dominates random selection, and checks known exact rational witnesses and target-swap symmetry.
- [Independent physical-card Monte Carlo](monte_carlo.py) samples a fully shuffled residual population and actual face-down Prize cards. It compares random Prize pickup with the optimally selected face-up identities for the same physical state, and executes the T3 draw and tutor check. Four 200,000-trial scenarios test the theoretical rates.
- [CI workflow](https://github.com/FlareZ123/pokemon-workplace/actions/workflows/validate-beheeyem-mapped-prizes.yml) runs the exact and stochastic tests.

The model assumes a playable first attack that conditionally earns r Prizes, a ready board, no opponent interference before T3, all required T3 draw actions available, neutral filler discardability and optimal choice solely for the next packet. It does not evaluate the true frequency of winning those Prizes, the action and deck-slot costs of Town Map, or longer-horizon matchup goals.

A valuable next experiment is to model optimal face-up Prize selection **under an expected opponent N/Iono/Marnie reply** and under the physical probability of acquiring Town Map itself, thereby converting the free-information ceiling into an action-constrained deckbuilding metric.
