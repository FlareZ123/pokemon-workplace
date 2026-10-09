# Natural four-singleton Peonia packet is rare without connectors

## Question

How often can the Peonia + Greedy Dice + Dream Ball + Jirachi Prism Star hand packet used in [the known-position E-31 example](../e31_peonia_seed_execution/) arise from ordinary opening and draw alone?

The answer is very rarely under a concrete 60-card toy deck. This is a **direct-hand-only baseline**, useful for qualifying the active-move realism (AMR) of the otherwise deterministic Peonia setup.

Implementation: [tools/e31_peonia_packet_availability.py](../../tools/e31_peonia_packet_availability.py).  
CI: [passing run 37977070987](https://github.com/FlareZ123/pokemon-workplace/actions/runs/37977070987).

## Controlled 60-card population

- One Peonia Supporter.
- One Greedy Dice Item.
- One Dream Ball Item.
- One Jirachi Prism Star Basic Pokémon.
- `B` additional, ordinary Basic Pokémon capable of satisfying the opening-Active requirement while leaving Jirachi in hand.
- `56-B` inert, non-Basic fillers.

Only seven opening cards and exactly one normal start-of-turn draw are observed. Neither search nor extra draw effects are allowed. A legal opener has at least one Basic card, which includes Jirachi.

The packet succeeds if all four distinguished singleton cards are in the first eight cards **and** at least one *other* Basic was in the initial seven. This is necessary because Jirachi must remain available in hand for Peonia's Prize-placement effect; if it is the only Basic in the initial seven, it must start Active.

The calculation is conditional on having accepted a legal opening hand, including Jirachi-only legal hands where this particular packet cannot succeed.

## Exact probabilities

| Other Basic starters `B` | Four-card natural packet probability, conditional on legal opening | Approximate accepted openings per successful packet |
| ---: | ---: | ---: |
| 4 | 0.00704277% | 14,199 |
| 8 | 0.00867454% | 11,528 |
| 12 | 0.00988219% | 10,119 |
| 16 | 0.01092218% | 9,156 |

For eight other Basics, the exact probability is:

`310828 / 3583221615 = 0.008674540215397757%`.

The raw probability of all four distinguished cards among any eight random cards, without conditioning on legal opener or preserving Jirachi off the Active Spot, is:

`14/97527 = 0.01435499912844648%`.

The legal opening and packet-preservation constraints substantially reduce the raw number.

## Two independent exact derivations

Let `F=56-B` count inert non-Basic fillers. All four packet cards are physically distinguished singletons. The eighth drawn card is selected from the 53 cards remaining after the opening seven.

The allowed first-seven hands fall into two disjoint categories:

1. All four packet cards are in the opening seven, accompanied by three nonpacket cards, including at least one of the `B` alternative Basics. The eighth draw is unrestricted.
2. Exactly three packet cards are in the opening seven, accompanied by four nonpacket cards including at least one alternative Basic. The eighth draw must be the one missing packet singleton.

Writing `C(n,k)` for binomial coefficients, the first route counts

`53 * sum_{b=1}^3 C(B,b) C(F,3-b)`

opening-hand-plus-eighth-draw pairs.

The second route counts

`4 * sum_{b=1}^4 C(B,b) C(F,4-b)`

pairs.

The denominator is the total number of accepted seven-card openings times their 53 possible next draws:

`[C(60,7)-C(59-B,7)]*53`.

The implementation constructs this exact rational value using `fractions.Fraction`.

An independent conditional approach first computes `P(all four among eight)=C(56,4)/C(60,8)`. Conditional on that event, half of their positional arrangements place four packet cards in the opening seven, leaving three ordinary slots; the other half place three packet cards in the first seven, leaving four ordinary slots. The probability of one alternative Basic among those `k` slots is `1-C(56-B,k)/C(56,k)`. Average over `k=3,4` and divide by the accepted-opener probability `1-C(59-B,7)/C(60,7)`.

Both independent derivations agree **exactly as fractions** for every tested Basic count, and the code asserts the four displayed reference fractions.

## Strategic interpretation

The established [Peonia-seeded E-31 winline](../e31_peonia_seed_execution/) is a mechanically meaningful tactical option. A state that already holds every necessary card can execute a line that will be unrepresentative of a random initial hand.

Without any search or additional draws, four singleton cards in the first eight and another opening Basic appear approximately once per 11,528 accepted openings for the illustrative eight-other-Basic deck. Even then, the actual Prize-seeding line would still need the right board state, a legal Supporter opportunity, and a same-turn two-Prize Knock Out. The probability above is therefore the probability of the **required natural-hand packet only**. It does not estimate the probability of executing the complete combo.

Draw Supporters, search Items, hand manipulation, card-copy redundancy, and subsequent turns can dramatically change accessibility, so this result cannot be used as a win-rate estimate or an upper bound for realistic deck designs.

The main methodological consequence is that a high-value terminal line and a realistic setup policy must be evaluated separately. This distinguishes what is possible once the pieces are present from how costly it is to make those pieces simultaneously available.

## Reproduction

`python tools/e31_peonia_packet_availability.py`.

The test is also covered in the E-31 validation workflow `.github/workflows/validate-e31-greedy-order-option.yml`.
