# A disruption weight makes K1 information value nonmonotonic

## Question

The [three-Supporter information envelope](../three_supporter_information_envelope/) values only the player's own immediate useful-out access. Iono and N also redraw the opponent's hand, while Professor's Research leaves the opponent's hand intact. Does the value of inspecting our own deck increase as we place more weight on disrupting the opponent?

**No.** For a constructed two-objective scalar payoff, the information premium is zero with no opponent-denial weight, positive at intermediate weights, and zero again at sufficiently large weights. Its global maximum is certified by exact rational action-line intersections.

## Card-text basis and state

Printed card sources in the repository are Iono (sv2-185), N (bw3-92), and Professor's Research (Professor Magnolia, swsh1-178). Each uses the single Supporter window. The comparison conditions on legal access to all three options and on deciding to play one Supporter.

Own side: old deck D=46, P=6 still-hidden Prize cards, U=10 target outs in the deck-plus-Prize unknown pool, old hand H=5 containing R=1 target out, and six remaining Prizes for own Supporter redraw. The opponent's old hand has Q=5 cards.

Opponent side: old deck 46, still-hidden remaining Prizes 6, four outs somewhere in those deck-and-Prize cards, and five old-hand cards including one stipulated target out. Opponent readiness is measured after the Supporter takes effect **and their next ordinary turn-start draw**, with other actions excluded.

- Iono puts both old hands below their original decks. Opponent draws six under Iono and one next turn. Their seven-card sample comes from the original deck.
- N shuffles both old hands into their respective decks. Opponent draws six under N and one next turn. Their seven-card sample comes from the 51-card combined deck.
- Research affects only our own hand and deck. The opponent retains the stipulated target in hand, so their readiness is one.

We **integrate out the opponent's hidden Prize composition**. Their four unspecified deck-or-Prize outs follow the exact hypergeometric prior Pr(L) = C(46,L) C(6,4-L) / C(52,4). An inspection of our own deck does not reveal L.

This gives the following marginal probabilities that the opponent will hold or draw a useful out by their next draw:

| Our chosen Supporter | Opponent readiness |
| --- | ---: |
| Iono | **44.964447%** |
| N | **49.953439%** |
| Professor's Research | **100.000000%** |

These are conditional access rates, not estimates of an actual opponent's attack capability.

## Exact weight frontier

Let p_a(K) denote our own conditional immediate new-hand target-hit probability, where K is the unobserved number of our outs in deck. Let q_a be the opponent's readiness probability above. For a nonnegative hypothetical weight lambda define

**u_a(K,lambda) = p_a(K) - lambda q_a.**

Before searching our deck (K0), we choose one action for all feasible K. After searching (K1), we can condition our choice on K. The *incremental* value of the information is

**V(lambda) = E_K[max_a u_a(K,lambda)] - max_a E_K[u_a(K,lambda)].**

Every individual utility is affine in lambda. Thus both fixed and observed action choices can change only where two action lines cross. The experiment enumerates **22 exact nonnegative candidate crossing weights, including zero**, and independently checks affine interpolation across the **21 intervening intervals**.

| Opponent-denial weight | K1 information premium | Best fixed K0 action |
| ---: | ---: | --- |
| 0 | **0.000000 pp** | Research |
| 0.1 | **+0.085210 pp** | Research |
| 0.101780177265 | **+0.118470 pp (global maximum)** | Iono / Research tied |
| 1 | **0.000000 pp** | Iono |

The maximum occurs at the exact rational weight **1873495/18407268**, approximately 0.101780177264763, with exact premium **33577741865080051/28342923657960857400** in probability units, or **+0.118469577346 percentage points**.

At the maximizing weight, an informed choice uses **N for K=4..6, Research for K=7..8, and Iono for K=9..10**. At weight zero, Research is best for every K. At weight one, Iono is best for every K. The intermediate region admits different best responses to our own Prize knowledge, producing positive option value.

The piecewise-affine calculation is a conditional utility frontier and does **not** imply a real metagame strength ranking. It excludes choosing no Supporter, card-acquisition probabilities, opponent search and attacks, the feasibility of observing the opponent's hand out, damage, prize race and future turns beyond the specified draw.

## Reproducibility

- [Opponent-weighted exact frontier](../../tools/supporter_opponent_tradeoff_frontier.py) integrates the opponent's unknown Prizes, evaluates the three-action objective in exact Fraction arithmetic, and enumerates rational action-line crossings.
- [Independent reproducer](reproduce.py) verifies **600** physical small-model opponent Prize/draw allocations and **960** exact own-state utility-policy cases. It verifies all **21** affine intervals and pins the stated high-dimensional witness.
- [Windows regression workflow](../../.github/workflows/validate-agent2-supporter-opponent-frontier.yml) executes the reproducer with Python 3.13.

This extends the earlier result without introducing clairvoyance about the opponent's hidden cards. Further work should model passing the Supporter window, card-specific downstream usefulness, and real action access costs.
