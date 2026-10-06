# Prize-rescue deadline access: from topology to timely availability

## Question

The existing Prize-rescue results answer whether enough Gladion-like rescue cards begin outside the Prize cards. How much does that overstate practical rescue reliability when the rescue card must actually reach the hand and be played by a deadline?

This result adds a second gate after Prize topology: **timed hand access**. It models valid-start conditioning, the initial Prize state, the accepted opening hand, later random card exposure, and the one-Supporter-per-window rate limit.

Implementation: tools/prize_rescue_deadline.py

Reproducer and exhaustive validation: results/prize_rescue_deadline/reproduce.py

## Card and rules basis

The bundled card pool contains Expanded-legal Gladion prints sm4-95 and sm4-109. Gladion looks at the face-down Prize cards, puts one into the hand, then shuffles the played Gladion into the remaining Prize cards. Its text also requires it to have been played from the hand.

The bundled advanced manual states that only one Supporter may be used during a turn. This creates two distinct constraints. Capacity asks how many usable Gladion copies begin outside the Prize cards. Timing asks how quickly enough of those copies reach the hand across separate Supporter windows.

The earlier result in results/prize_rescue_start_condition already models capacity while conditioning the Prize distribution on a legal opening hand. This result keeps that exact Prize-state distribution and adds access timing.

## Model

The deck remains partitioned into critical setup-eligible starters, critical non-starters, rescue starters, rescue non-starters, filler starters, and filler non-starters. Gladion belongs in the rescue non-starter category.

For each valid-start-conditioned Prize state, let c be the number of critical cards Prized, g the number of rescue copies Prized, G the total rescue copies in the deck, and W the number of Supporter windows before the deadline.

The earlier topology gate is:

c <= G - g

The Supporter-rate gate also requires:

c <= W

If either condition fails, rescue by the modeled deadline is impossible.

### Random card exposure

The caller supplies a nondecreasing sequence cards_seen_by_window = (k1, k2, ..., kW).

Each k value is the cumulative number of non-Prize cards randomly exposed into the hand by that Supporter window, including the accepted opening hand. For example, 8 / 9 / 10 means the accepted seven-card opening hand plus one additional random non-Prize card by each of three successive Supporter windows.

This abstraction uses unbiased without-replacement exposure and is exact under that assumption. Targeted search requires a separate model because a search card has different semantics from several random draws.

### Opening-hand conditioning

For a fixed Prize state, the non-Prize cards are aggregated into rescue starters, rescue non-starters, other starters, and other non-starters. The exact multivariate-hypergeometric opening distribution is conditioned on containing at least one setup-eligible starter.

After the opening hand is fixed, the remaining rescue cards occupy uniformly random positions in the remaining deck. For exposure segment sizes d1 through dW and an unseen remainder u, a rescue allocation r1 through rW has probability proportional to:

prod_j C(d_j, r_j) * C(u, R - sum_j r_j)

with denominator C(M, R), where M is the number of cards remaining after the opening hand and R is the number of rescue copies remaining there.

### Deadline scheduling condition

The first Gladion play need not occur in the first Supporter window. If c critical cards must be rescued by window W, a schedule exists exactly when cumulative rescuers seen by every window j reaches:

max(0, c - (W - j))

For two required rescues across three windows, at least one rescuer must have appeared by window 2 and at least two by window 3.

## Main finding

Consider a 60-card deck with six Prize cards, a seven-card opening hand, 12 setup-eligible starters, four critical non-starter singletons, two non-starter Gladion-like rescuers, and three Supporter windows with cumulative random exposure 8 / 9 / 10.

After conditioning on a valid start:

- probability that at least one modeled critical card is Prized: **35.383108%**
- topology-only collapse given that a critical is Prized: **2.989209%**
- deadline failure given that a critical is Prized: **73.622439%**
- overall deadline failure: **26.049907%** of valid starts

The difference is large because a Gladion existing outside the Prize cards is much weaker than a Gladion reaching the hand in time.

These rates describe only the random-exposure baseline. Real Expanded decks can search, draw more cards, take ordinary Prize cards, use alternative recovery, or change which singleton is actually urgent.

## Rescue-copy sensitivity

Hold the same four critical singletons, 12 starters, and exposure windows 8 / 9 / 10:

| Rescue copies | Topology failure given a critical Prized | Deadline failure given a critical Prized | Overall deadline failure |
| ---: | ---: | ---: | ---: |
| 1 | 21.076758% | 85.933840% | 30.406063% |
| 2 | 2.989209% | 73.622439% | 26.049907% |
| 3 | 0.287137% | 62.876087% | 22.247514% |
| 4 | 0.017244% | 53.522274% | 18.937844% |

Extra copies solve topology much faster than early access. Four rescuers nearly eliminate pure capacity collapse, while more than half of critical-Prized states still miss the modeled deadline under only 8 / 9 / 10 random exposure.

## Exposure sensitivity

Hold two rescue copies and four critical singletons:

| Cumulative cards seen by Supporter window | Deadline failure given a critical Prized | Overall deadline failure |
| --- | ---: | ---: |
| 8 / 9 / 10 | 73.622439% | 26.049907% |
| 8 / 9 / 10 / 11 / 12 | 68.595518% | 24.271226% |
| 10 / 13 / 16 | 59.083758% | 20.905670% |
| 12 / 18 / 24 | 42.182300% | 14.925409% |

The topology-only conditional failure remains 2.989209% in every row. Access velocity is a separate axis.

## Number of critical singletons

With two rescue copies and exposure 8 / 9 / 10:

| Critical singletons | Topology failure given a critical Prized | Deadline failure given a critical Prized |
| ---: | ---: | ---: |
| 1 | 0.593561% | 69.802771% |
| 2 | 1.190747% | 71.083050% |
| 3 | 1.989357% | 72.356917% |
| 4 | 2.989209% | 73.622439% |
| 5 | 4.189200% | 74.877615% |

Even one modeled critical singleton has a large random-exposure deadline gap in this sparse two-rescuer package.

## Strategic interpretation

Prize protection needs separate treatment of capacity, access timing, and available Supporter windows. A future deck evaluator should avoid giving full rescue credit immediately after checking only initial Prize topology.

This is another concrete form of the human-concepts warning that theoretical access can overstate realistic success.

The result also points toward connector domination. A card that searches a Supporter could make Gladion reachable, while that connector may consume an Item search, Ability, hand resource, Bench slot, or another channel with a stronger competing use. The current model leaves those connector costs for the next layer.

The model enforces at most one rescue Supporter play per modeled window. The opportunity cost of spending that window on Gladion instead of draw, Energy acceleration, gust, disruption, or setup remains outside this layer. For a fixed random-exposure process, the result is therefore optimistic about playable rescue opportunities once Gladion is in hand.

## Validation

The implementation is deterministic and uses no Monte Carlo sampling for the reported values.

The reproducer performs independent exhaustive checks on two small eight-card decks. It enumerates every labeled deck permutation, applies the legal-opening condition to the opening segment, treats the next cards as Prizes, preserves the remaining order for later draws, and evaluates the rescue schedule directly.

The exact combinatorial model matches the exhaustive permutation frequencies to floating-point precision in both regression cases, including a case where some critical and rescue cards are setup-eligible starters.

## Scope limits

A complete turn simulator would additionally need targeted Supporter search, shuffle-draw effects, ordinary Prize-taking, alternative Prize manipulation, Supporter lock, Item or Ability lock, competing Supporter requirements, matchup-dependent criticality, and game-state changes that alter whether a singleton remains urgent.

The caller supplies the Supporter windows and cumulative random exposure, leaving turn structure configurable.

## Next useful work

The strongest extension is an access-network model that adds explicit non-Supporter outs to Gladion while preserving connector costs. The next layer should distinguish direct rescue copies, targeted Item or Ability access, Supporter-search routes that consume the same Supporter window, lock-sensitive edges, and dominated routes whose connector is better spent on another required piece.

A second extension should combine timed rescue with ordinary Prize-taking so a critical card needed later can sometimes be reached naturally before a Gladion line is required.
