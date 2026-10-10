# Prize-position policies must respect acting-player information

## Question

Our [position-choice signaling](../prize_position_choice_signaling/) result conditions an observer's posterior on the likelihood of a public choice given the actual hidden world. That can silently encode an **omniscient actor** unless the selection policy is constrained by what the actor has previously observed.

Can we enforce the needed constraint mechanically?

## Criterion

An actor's information partition assigns each physical world `w` an information set `I(w)`. Worlds in the same information set are observationally indistinguishable **to the actor** at the choice point.

For a behavioral policy `π(a|I)`, the probability of selecting action `a` must satisfy:

`P(a | w) = π(a | I(w))`.

Thus if two worlds share the same information set, the action likelihood **must be equal** in those worlds. This is the finite-state measurability criterion.

It remains appropriate for randomized policies. Within every actor information set, the probabilities of each eligible physical action must sum to one.

## Executable model

`tools/prize_choice_policy_information.py` adds:

- `is_world_likelihood_admissible`: evaluates a proposed world-dependent public-action likelihood against actor information sets.
- `condition_on_admissible_position_choice`: takes an **information-set-indexed**, normalized stochastic policy over the currently eligible face-down positions, constructs the world likelihood, and applies the existing exact Bayesian observation update.

The policy compiler deliberately requires complete information-set and choice-domain coverage. The caller still bears responsibility for ensuring that its information partition correctly describes the actor's actual history. A full epistemic game model should derive those partitions from observation events rather than inventing them.

## Exact counterexample

The observer considers two equally likely physical worlds:

- W1: Prize0=A, Prize1=B, Top=X.
- W2: Prize0=B, Prize1=A, Top=X.

The public event is the actor selecting position zero for an Arc Phone swap.

**Actor knows the position mapping.** Its information sets are `A-at-0` and `B-at-0`, one for each world. A legal choice policy can choose slot0 with rates 4/5 and 1/5 respectively. Observing the selection moves the opponent's P(W1) to **4/5**, and after the swap P(outgoing top=A) becomes **4/5**.

**Actor does not know the mapping.** Both physical worlds belong to the same actor information set. Rates 4/5 and 1/5 conditioned directly on the hidden mapping are now **inadmissible**. A valid policy choosing slot0 with probability 3/4 in either world leaves the opponent at P(W1)=**1/2** after seeing the selected slot.

The same physical public action therefore transmits information only insofar as its choice policy depends on information the actor actually possesses.

## Validation

`results/prize_choice_policy_information/reproduce.py` reconstructs the posterior using independent exact `Fraction` arithmetic, checks the admitting and rejecting partitions, and tests guards for incomplete information maps, malformed action distributions, noneligible chosen positions, and zero-probability observed actions.

## Limitations

- This is a **policy-construction invariant**, not proof that any real Pokémon player uses the proposed strategy.
- Position knowledge is possible through legal prior observations/placements, but the example stipulates it. The full game action history is not simulated.
- The information partition is an explicit caller-supplied input. A bad partition that pretends a player observed a card can still make an impossible policy look legal. Future work should generate the partition from player-specific observation traces.
- The two-world example abstracts card identity to groups and ignores game-turn constraints, locks and resource contention.
- A public choice can also be correlated with other hidden information. The policy domain can be expanded, provided the information partition carries that information.

## Next work

Derive the actor's information set from actual observation records and test indistinguishability across multiple possible material histories. Tie this to `observer_positioned_prize_truth/` so a physical transition and every observer's posterior update share one event log.
