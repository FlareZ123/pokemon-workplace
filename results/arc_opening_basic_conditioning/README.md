# A required starting Basic changes conditional Prize rescue access

## Question

How does the obligation to begin the game with a Basic Pokémon affect the apparent access rate of a Prize-rescue package?

The previous [Arc Phone chaining study](../arc_phone_chain_access/) samples a fixed hand window without requiring a legal starting Pokémon. A real opening hand must contain a Basic; one selected Basic enters the Active Spot and ceases to be available as a Peonia replacement. This result quantifies that constraint in the same stylized target-Prized benchmark.

## Exact population

The 60-card illustrative deck has:

- one singleton target `T`, conditioned to be among the six Prizes;
- one Peonia Supporter, four Arc Phone, four Trekking Shoes;
- `b` Basic Pokémon, where `1 <= b <= 50`;
- `50-b` other filler cards.

The unopened deck is sampled exactly without replacement. The six initial Prizes include `T` and five other cards from the remaining 59, and the opening seven cards are sampled from the 54 non-Prized cards. The model conditions the opening hand on having at least one Basic, then commits exactly one opening Basic to the Active Spot. All other Basic cards are treated as freely expendable fillers for this narrow access calculation.

The player's Prize *composition* is assumed known when choosing the line, while positions remain unknown. Peonia can select up to three positions; Arc Phone can chain distinct probes, and Shoes supplies the final draw. Every Peonia return payment is counted from usable hand cards. The model does not price the value of playing extra Basic cards or a valid Bench.

## Exact result

| Basics `b` | Probability of valid seven-card opening, conditional on T Prized | Target retrieval given both T Prized and valid opening |
| ---: | ---: | ---: |
| 1 | 11.864407% | 7.592762% |
| 4 | 40.516472% | 7.831433% |
| 8 | 66.063231% | 8.129563% |
| 12 | 81.564825% | 8.394993% |
| 16 | 90.554253% | 8.618828% |
| 20 | 95.491437% | 8.795731% |
| 30 | 99.542494% | 9.041152% |
| 50 | 99.999989% | 9.106095% |

The earlier seven-card benchmark, without the opening Basic requirement and with all seven cards usable, was **9.106103%** in this same artificial package. With eight Basics, the exact conditioned target retrieval is **8.129563%**, a reduction of about **0.97654 percentage points**. The probability is conditional on the target starting in the Prizes, so it is not a real-game absolute rescue frequency.

The valid-opening probability independently follows the closed-form identity

`P(valid opening | T Prized) = 1 - C(59-b,7)/C(59,7)`.

## Methodology and verification

`tools/arc_opening_basic_conditioning.py` integrates the joint Prize/hand multivariate hypergeometric mass using exact rational arithmetic. Only states with at least one Basic in the starting hand are retained, and its active-position commitment is removed from available hand payments.

`results/arc_opening_basic_conditioning/reproduce.py` independently enumerates individual labeled cards for three small-deck configurations with three Prizes and four-card opening hands. All exact output fractions agree with the grouped population integrator. The regression checks the closed-form opening acceptance probability and eight 60-card sensitivity points.

## Scope and next work

The comparison isolates conditioning and a single Active Pokémon commitment. It does not model all opening Pokemon/Bench choices, opponent bonus draws from mulligans, further natural draws, all real card text in every deck, or full adaptive feedback from intermediate Shoes. A model using an archetype's actual Basic counts should retain which Basics are needed in play and which are expendable, rather than treating all extra Basics as interchangeable Peonia payment.
