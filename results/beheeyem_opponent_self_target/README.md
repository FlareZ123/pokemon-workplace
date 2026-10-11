# Opponent self-setup can reverse hand-reset decisions even with known Beheeyem packet risk

## Purpose

The [physical opposing Supporter model](../beheeyem_opponent_supporter_access/) asks whether the opponent can play Judge or Ace Trainer to disrupt Beheeyem after the first Mysterious Noise attack, allowing a no-reset action and optionally observing the first attack's visible paid-tutor line.

That model optimizes only **denial of the next Beheeyem+Triple Acceleration Energy packet**. An opposing Supporter also refreshes **its own** hand. Such self-setup value can rationally justify a play that strengthens Beheeyem's immediate hand supply. Conversely, discarding a Supporter to redraw can lose an already available own critical card.

We isolate this tension in a two-objective, exact physical-availability model, using one hypothetical **X target** (four non-Basic copies) as a proxy for the opponent's next-turn setup.

## Physical opponent deck and exact hand distribution

The opponent's full 60 cards consist of 12 Basics, four Ace Trainer, four Judge, four **own target X**, and 36 neutral filler. Seven opening cards are uniformly drawn, conditioned on containing a Basic. Six original Prizes are set face-down, followed by `k=2` naturally drawn deck cards and `s` uniformly awarded original Prize cards.

The observed opponent hand has `h = 7+k+s` identities. Conditional on Basic-valid opening, the observed count multiset is not an unconditional h-card hypergeometric sample: the first seven must contain a Basic. For observed b Basics among h, the correct factor is

```text
P(Basic in opener | observed h including b Basics)
  = 1 - C(h-b,7)/C(h,7).
```

The engine enumerates all physical `(Basics,Ace,Judge,X,filler)` hand-count configurations, weights by multivariate hypergeometric multiplicity, and normalizes by the opening-Basic probability. The count distribution sums **exactly to one**, and each four-copy marginal matches the independent [physical Supporter access formula](../../tools/beheeyem_opponent_supporter_access.py).

Before deciding, the opponent knows which Supporters and how many X are **in its own hand**, but does not know which X copies remain in its original Prize cards (K0). For each possible face-down Prize allocation, the engine computes its posterior probability and evaluates an actual full-hand shuffle. The played Supporter is first removed to the discard pile, then the rest of the hand is shuffled into the remaining deck. Ace Trainer draws **six** for its player and **three** for Beheeyem; Judge draws **four** for each.

The exact K0 target-recovery probability after playing a Supporter with redraw quota n is

```text
sum_z P(z unobserved X copies Prized | observed X count)
      * [1 - C(N-(4-z),n)/C(N,n)]

where N = 60-(6-s)-1 = 53+s.
```

The subtraction of one accounts for the played Supporter, which is distinct from X. A no-reset action leaves X in hand if and only if at least one is already held.

## Explicit two-objective policy

Given its own visible hand, public Prize counts and optionally the public Beheeyem first-packet route, the opponent selects one legal action:

```text
no hand reset
Judge, if held
Ace Trainer, if held and opponent Prizes remaining > Beheeyem Prizes remaining
```

It maximizes the deliberately chosen utility

```text
P(own target X in hand after response)
  - lambda * P(Beheeyem next packet available | first packet succeeded).
```

`lambda` is a nonnegative value-of-denial weight. This scalar objective is **not a game-winning probability or a calibrated metagame utility**. It is useful for computing a frontier of physically available response policies. The Beheeyem term is the previously validated exact conditional packet rate, with the direct-from-hand versus paid-tutor-rescue branch distinguished when observed.

## Representative frontier: B4/TAE4/C1/d1, Beheeyem r=1, opponent q=6

The opponent's Ace Trainer is currently **legal** because it has all six original Prizes and Beheeyem has taken one. The table shows actions chosen after observing the Beheeyem first-packet route.

| Weight on Beheeyem denial `lambda` | Opponent owns X after reply | Beheeyem joint two-packet probability | Play no reset | Play Judge | Play Ace Trainer |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 0 | **59.871555%** | 1.252222% | 59.571376% | 14.036294% | 26.392330% |
| 1 | **59.871555%** | 1.252222% | 59.571376% | 14.036294% | 26.392330% |
| 10 | 56.410922% | 1.144932% | 73.607670% | 0% | 26.392330% |
| 1,000,000 | 44.337605% | **1.089143%** | 66.492306% | 0% | 33.507694% |

Action frequencies are over the opponent's own Basic-conditioned hand states and the Beheeyem first-attack-route distribution. The next-packet rate remains a **joint** Beheeyem T2+T3 event probability in its separate, conditioned three-Basic-board model. Opponent X readiness is conditional on the Beheeyem first attack occurring (and the opponent's own legal opener). Their denominators differ, so compare changes and chosen policies rather than multiplying the two columns.

The own-X starting **no-reset** acquisition probability is 47.143530% under this deck and draw model. Optimizing just X access (`lambda=0`) improves it to **59.871555%** by using accessible resets when X is absent. Yet the policy gives Beheeyem a stronger packet event (1.252222% versus 1.125764% if no reset were ever used). A very large denial weight has the opposite behavior: many useful own hands are willingly disrupted to improve the chance of denying the next Beheeyem packet, and X readiness falls to 44.337605%.

The other example with `r=2, q=6` shows the same Pareto pressure:

| `lambda` | Own-X readiness | Beheeyem joint packet event |
| ---: | ---: | ---: |
| 0 | 59.871555% | 1.579416% |
| 10 | 58.870599% | 1.552544% |
| 1,000,000 | 44.337605% | **1.436326%** |

At equal Prize races, Ace Trainer becomes illegal, and the model can instead choose to play Judge for X while leaving a larger fraction of Beheeyem packet opportunities intact. A single "disruption strength" feature cannot capture all these effects.

## Independent validation and limitations

- [Exact K0 engine](../../tools/beheeyem_opponent_self_target.py) computes Basic-conditioned hand-category probabilities, hidden Prize posterior, physical reshuffled-deck draw probabilities, and response selection against the independent Beheeyem direct/rescue-route solver.
- [Exact regression](reproduce.py) verifies probability conservation, equal four-copy target/Supporter marginal access, greater X recovery with six draws than four, optimal utility weakly improving with public route observation, and convergence at extremely high denial weight to the earlier source-access-only optimal policy. It evaluates 60 representative setting/policy combinations.
- [Physical independent simulation](monte_carlo.py) samples real 60-card arrays, opens a Basic-containing seven-card hand, prizes six, draws two, awards up to two prizes, discards a non-X played-card proxy, shuffles the residual hand into deck, and checks X acquisition with four or six replacement draws. Three seeded 160,000-trial cases agree with the exact K0 source-availability probabilities. All [passed CI 38133471853](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38133471853).

The opponent's X is a hypothetical abstract card, with no printed effect or card-specific Energy/evolution prerequisites. Its possession is used as a proxy for the opponent's next-turn ability to execute some plan. This model intentionally avoids estimating real match win rates; the relative weight `lambda` is an input for sensitivity analysis rather than an empirical estimate. Both opponent hands and the Beheeyem packet distribution are treated independent. The opponent retains seen Supporters until its reply. Bench, Active, opponent draw opportunity, prior Supporter use, other search, and the actual first-attack KO probability remain outside scope.

## Research implication

Access to a "disruptive" Supporter can be valuable because of the **resources it finds for its own player**, even when it improves the opposing packet access. A payoff model should evaluate both sides' resulting hands and future actions. The physical source-access and public first-tutor route are enough to produce exact, testable policy changes under this simplified two-objective model; extending to board-level rewards is a natural next step.
