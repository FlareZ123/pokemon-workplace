# Hand-value-aware setup policy couples opening quality, mulligans, and Prize priors

## Question

The earlier optional-starter model showed that cards such as Luxray, Talonflame,
Manectric, Cinderace, and Snorlax Doll can make setup a strategic decision.
That model could express selective policies, but it did not derive which
optional-only hands should be kept.

This result asks a narrower question:

**If the player can assign a value to each grouped opening-hand state, and each
failed mulligan has a constant strategic cost, what stationary keep policy is
optimal?**

## Result

For a stationary policy with a constant utility penalty (c) per failed
mulligan, the optimal decision on an optional-only hand is a value threshold.

Let (J) be the expected utility of starting from a fresh shuffle and let
(v(h)) be the terminal value of keeping optional-only hand (h). Rejecting
that hand pays one mulligan penalty and returns to the same fresh-shuffle
problem, so its continuation value is

[
J-c.
]

Therefore the optimal action is

[
	ext{keep } h iff v(h) ge J-c.
]

The finite grouped hand state space means the optimum can be found exactly by
checking the distinct hand-value cutoffs. No Monte Carlo search is required.

Implementation:

- `tools/setup_hand_value_policy.py`
- `results/setup_hand_value_policy/reproduce.py`

The tool also computes the accepted-opening-conditioned Prize distribution for
the same hand-state policy. This is important because changing the setup
decision changes the K0 Prize prior.

## Policy value formula

For any stationary policy, let:

- (A) be the probability that one shuffled opening is accepted;
- (T) be the per-attempt probability-weighted terminal value of accepted
  hands;
- (1-A) be the rejection probability.

Repeated attempts are geometric, so

[
E[M] = rac{1-A}{A}
]

failed hands occur before acceptance on average. The expected terminal hand
value is

[
E[v mid 	ext{accepted}] = rac{T}{A}.
]

The policy objective under constant mulligan penalty (c) is therefore

[
J = rac{T}{A} - crac{1-A}{A}.
]

This makes the tradeoff explicit: a selective policy can improve the quality
of the accepted opening while increasing the expected number of mulligans.

## Exact illustrative benchmark

Consider an abstract 60-card deck containing:

- 4 forced Basic starters;
- 4 optional setup starters;
- 4 key opening cards;
- 48 filler cards.

Give a kept hand value 1 if it contains at least one key opening card and 0
otherwise. Forced-Basic hands must still be kept.

Two natural policies are:

1. **Selective:** keep an optional-only hand exactly when it also contains a
   key opening card.
2. **Accept all:** keep every optional-only hand.

The exact results are:

| Policy | Acceptance per attempt | Key card present among accepted hands | Expected failed mulligans |
| --- | ---: | ---: | ---: |
| Selective | 49.783383% | 48.960089% | 1.008702362 |
| Accept all | 65.359357% | 37.292272% | 0.530002810 |

The selective rule raises the accepted-hand key-card rate by about 11.668
percentage points, while adding about 0.479 expected failed mulligans.

With the linear mulligan penalty (c), the two policies have equal expected
utility at

[
c = 0.243739889.
]

Below that value, the selective policy is better in this benchmark. Above it,
accepting every optional-only hand is better. At the crossover they are
indifferent.

The number is expressed in the same utility units as the binary hand value. It
is a sensitivity boundary, not a claim about the real value of one opponent
bonus card.

## The optimal rule really is hand-state dependent

The benchmark produces:

- at (c=0), the optimizer keeps only optional-only hands containing a key
  card;
- at (c=0.10), it makes the same selective decision;
- at (c=0.25), it keeps all optional-only hands.

The decision changes because the continuation value of another shuffle is
being compared directly with the observed hand.

This formalizes a strategic effect that a scalar optional-starter keep
probability cannot represent. Two hands with the same optional starter count
can rationally receive different decisions because the rest of the seven-card
hand differs.

## Prize priors move with the optimized setup policy

The same accepted-opening event changes which cards are likely to remain among
the six Prize cards.

For the benchmark above:

| Card class | Selective policy | Accept-all policy |
| --- | ---: | ---: |
| Specific forced starter | 8.667752% | 9.299996% |
| Specific optional starter | 9.728156% | 9.299996% |
| Specific key opening card | 9.728156% | 10.107693% |
| Specific filler card | 10.156328% | 10.107693% |

The selective setup rule lowers the Prize probability of a key opening card
because key-containing optional-only hands are preferentially accepted.

In this symmetric 4-optional / 4-key benchmark, optional starters and key cards
have the same Prize probability under the selective rule. The accepted-opening
condition is symmetric between those two four-card classes:
a forced starter is present, or both an optional starter and a key card are
present.

The general implication is more important than that symmetry. **K0 Prize
priors can depend on strategic properties of cards that are not themselves
setup starters** whenever those cards influence whether an optional-only hand
is kept.

## Validation

The reproduction script performs two independent checks.

First, on a small deck it exhaustively enumerates every deterministic policy
over optional-only grouped hand states and confirms that the threshold optimizer
reaches the same maximum expected utility and the same tie-broken acceptance
probability.

Second, it exhaustively enumerates labeled opening hands and disjoint Prize
sets and compares that distribution with the analytic conditioned-Prize
calculation. The distributions match to floating-point precision.

The 60-card headline values are combinatorial calculations rather than Monte
Carlo estimates.

## Rules connection

The setup rule establishes repeated redraws after a failed opening, and the
opponent can receive optional bonus draws based on the other player's
mulligans. The existing `setup_mulligan_policy` result documents the optional
setup-card ruling basis and the fact that those cards can be declined.

This result treats the strategic cost of each failed mulligan as a parameter.
A constant cost is the simplest exact bridge between opening quality and the
mulligan externality.

## Limitations

The benchmark hand value is deliberately abstract. It demonstrates the
decision structure and the Prize-conditioning effect without claiming that a
particular Expanded archetype values its hands this way.

A constant per-mulligan penalty is also a simplification. Real opponent bonus
cards can have nonlinear marginal value, and the opponent may have mulligans of
their own. If the cost of the next mulligan depends on how many have already
occurred, the optimal policy can become count-dependent rather than stationary.

The grouped state representation is exact only at the chosen class resolution.
A deck-specific optimizer may need separate classes for individual singleton
resources, Energy, search cards, ALS pieces, matchup-dependent cards, or other
features.

The model also does not yet condition on information revealed by the opponent's
mulligan hand.

## Next work

The strongest next extension is a count-dependent dynamic program with an
arbitrary terminal penalty or opponent-card-value function (B(m)) for
realized mulligan count (m). That would test exactly when the stationary
threshold theorem breaks and quantify how rapidly the keep rule should loosen
after repeated mulligans.

A second useful extension is a concrete Expanded deck with an optional setup
card, where the hand-value function is derived from executable first-turn lines
rather than an abstract key-card indicator.
