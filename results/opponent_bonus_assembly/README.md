# Opponent bonus draws give a non-monotone cost of mulliganing

Related extensions: [multi-role](multi_role_notes.md), [one-use](flexible_capacity_notes.md), [matching](matching_notes.md), [printed cards](card_text_examples.md), [safe-discard gate](payment_notes.md).

## Question and scope

A player can sometimes choose whether to keep an otherwise invalid opening
using a special setup effect (such as an optional non-Basic setup starter).
Rejecting such a hand produces an extra mulligan, allowing the opponent to
draw up to one additional bonus card after normal setup.

Earlier work in [setup_count_dependent_policy](../setup_count_dependent_policy/)
accepted an arbitrary per-mulligan cost sequence. This study derives one
specific sequence from the opponent's probability of assembling a
**multi-component hand**. It is an exact, deliberately abstract model and
does not assign a tournament win-rate value to that assembly.

Rules: the bundled *Advanced Player's Rulebook*, G. Setting Up to Play,
steps 5–7, allows bonus cards for the opponent's mulligans; the bonus is
selected after the normal opening and six Prize cards are established.

## Model and derivation

Assume the opponent has an N-card deck with B ordinary Basic Pokémon, an
accepted H-card opening containing at least one of those Basics, P uniformly
selected Prize cards, and r distinct required target groups of sizes
(k1, ..., kr). Target groups are mutually disjoint; a subset of each group may also be
an ordinary Basic starter. The opponent is assumed to draw all allowed bonus cards up to a
specified cap, with no other actions or future draws.

For a union of target groups containing K cards, of which T are ordinary
Basic starters, the probability of seeing
none in the opener and none in m bonus draws, conditional on a legal Basic
opener, is

    q(K,T,m) = [C(N-K,H) - C(N-B-K+T,H)] / [C(N,H) - C(N-B,H)]
             * C(N-H-K,m) / C(N-H,m).

The second factor is valid after marginalizing hidden Prize positions: a
random bonus sample from the post-Prize deck is exchangeable with a uniform
sample from the N-H cards excluded from the accepted opening. The probability
of holding at least one card from **every** required group follows by
inclusion-exclusion:

    A(m) = sum over S subset {1,...,r} (-1)^|S| q(sum(k_i for i in S),sum(t_i for i in S),m).

With opponent assembly utility L, the incremental external cost of the
(m+1)-th own mulligan is:

    c_m = L * [A(m+1)-A(m)].

Only the increment is charged. The constant baseline opponent probability
A(0) cancels when comparing own setup policies.

## Verified illustrative benchmark

Opponent: N=60, H=7, P=6, B=12, and two disjoint required families with
four copies each. Both families must be represented in the opponent's hand.

| Bonus cards m | P(both groups present) |
| ---: | ---: |
| 0 | 12.964829% |
| 1 | 16.753450% |
| 2 | 20.751200% |
| 3 | 24.891173% |
| 4 | 29.114847% |
| 5 | 33.371363% |
| 6 | 37.616851% |

The marginal gains rise from +3.788621 percentage points on the first draw to
a maximum +4.256516 points on the fifth draw, then decline. A single
four-copy target has diminishing marginal detection probabilities; requiring
both target families produces the initial complementarity.

As a separate hypothetical own deck, use 4 ordinary Basic starters, 4
optional setup starters, 4 key opening cards, and 48 other cards. Assign own
kept-hand utility 1 when at least one key is in the opening, otherwise 0.
Forced-Basic openings are always kept. Use L=6, cap the opponent's optional
bonus choice at 12 extra draws, and apply the exact count-dependent solver.

The optimal handling of *optional-only, no-key* hands is:

| Previous failed mulligans | Optimal decision |
| --- | --- |
| 0–1 | Reject |
| 2–5 | Keep |
| 6 or more | Reject |

Optional-only hands *with* a key are kept throughout. Thus an increasing
mulligan count does not imply a progressively more permissive keep policy.
The intermediate range is worth keeping because opponent bonus draws have
a temporarily higher marginal assembly value. As the multi-component
completion curve flattens, the player's quality criterion becomes more
selective again.

The exact discounted-by-increment objective at m=0 is approximately
0.252107 in these normalized utility units. The opponent assembly payoff
L=6 is a stress-test parameter, with no claim that it is a calibrated
competitive matchup value. Large mulligan counts are also rare.

## A crucial distinction: required components can be Basic starters

The event of opening at least one ordinary Basic is correlated with target
group possession when some target cards are themselves eligible Basics.
The generalized formula includes T, the number of Basic-starter cards in
the excluded target-group union. Ignoring this overlap can substantially
misestimate the marginal value of opponent bonus draws.

For the same N60/H7/P6/B12 and two four-copy required groups:

| Overlap with ordinary Basics (first, second target) | Both present at m=0 | First bonus gain | Peak marginal gain |
| --- | ---: | ---: | --- |
| (0,0) | 12.964829% | +3.788621 pp | Fifth draw, +4.256516 pp |
| (4,0) | 17.965662% | +3.886300 pp | Fourth draw, +4.123062 pp |
| (4,4) | 17.965662% | +4.738821 pp | First draw, +4.738821 pp |

The identical m=0 probability for the last two rows is structural: when
either fully required group consists of ordinary Basics, satisfying both
required groups already guarantees a valid Basic opener. Conditioning on
starter eligibility therefore divides the same unconditioned joint
assembly probability by the same valid-opening probability.

**Strategic implication:** whether a combo piece can serve as the opening
Active Pokémon changes the shape of the mulligan externality, even at
identical printed family counts. The initial increasing marginal-benefit
pattern can disappear. Exact small-deck enumeration validates overlapping
Basic/target roles separately from the disjoint benchmark.

## How often the middle window matters

Mixing the exact optimal policy over its accepted-opening-count distribution
gives 0.889726493 expected own mulligans, 46.060173% expected own key-hand
quality, and a 16.439749% probability that the opponent has both target
groups after the awarded bonus draws. The chance that the policy actually
accepts an optional-only, no-key hand at mulligan count 2–5 is 5.923021%.
The resulting incremental net objective is 0.252106552.

With the identical payoff and bonus cap, *always rejecting* optional-only
no-key hands has objective 0.251230181; *always accepting* them has 0.249479258.
The exact count-adaptive improvement over the better stationary alternative
is therefore only about 0.000876371 utility. The policy reversal is a
mathematical existence result; its advantage is small in this benchmark.

## Verification

- [tools/opponent_bonus_assembly.py](../../tools/opponent_bonus_assembly.py)
  computes rational inclusion-exclusion probabilities and converts them into
  costs for the existing setup solver.
- [reproduce.py](reproduce.py) exhaustively enumerates accepted opening
  hands, Prize subsets, and bonus subsets in several small decks, requiring
  exact rational agreement. It checks the peak and optimal policy.
- An independent Bellman recurrence over grouped own opening hands reproduces
  every state value of the existing count-dependent solver.
- [GitHub Actions workflow](../../.github/workflows/validate-opponent-bonus-assembly.yml)
  runs the reproducer.

## Limits and follow-ups

The bonus policy is hypothetical and capped; an opponent is allowed to
choose fewer bonus cards. The model ignores deck-out risk, the opponent's own
mulligan decisions, extra Basic bench placements, search effects, lock
states, and the strategic quality of the rest of both hands. Required families may include explicitly counted Basic starters, provided
target families are mutually disjoint. The probability measures
hand possession, not execution of a legal attack or complete board line.

A stronger next step would value a concrete Expanded archetype-line-specific
objective and calculate the opponent's optimal choice of bonus draws,
including Bench space and Prize-dependent search. The resulting matchup
calibration could replace the illustrative L.
