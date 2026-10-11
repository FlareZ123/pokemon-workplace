# Early Ultra Ball information purchase under an unknown future Prize outcome

## Correcting an information-timing shortcut

The [physically paid prelock K1 policy](../beheeyem_paid_k1_policy/) evaluates whether an opponent should play a real Ultra Ball before Beheeyem's Mysterious Noise Item lock in order to inspect its deck and identify Prized copies of a hypothetical target X. The first version conditions the **earlier Ultra Ball choice** on the number of Prizes `r=0,1,2` that Beheeyem will later earn with its first attack, even though those future Prizes are unobserved when Ultra Ball must be played.

This extension replaces that foresight with a declared **prior probability distribution** `(p0,p1,p2)`, conditional on the staged Beheeyem first attack taking place. Before the lock, the opponent knows its own Basic-valid opening hand and two natural draws, and whether Ultra Ball plus two neutral filler are payable. It can choose to play Ultra Ball, discard U+F+F, search the deck for no Pokémon and learn its remaining face-down X Prize count (K1), or preserve those three cards and remain K0.

After the Beheeyem attack, the reward r becomes publicly known. The opponent then takes a further natural draw and chooses the best available no reset/Judge/Ace Trainer action. Its later decision may condition on the public direct-first-packet-versus-paid-tutor-rescue signal and its own X Prize knowledge when K1. The **earlier** source decision integrates over every possible future r, own draw and first tutor route, so it cannot depend on their actual outcomes.

The opponent deck is unchanged: Basic12/Ultra Ball4/Ace Trainer4/Judge4/X4/filler32; original six Prizes, no opponent Prizes taken, staged Beheeyem B4/TAE4/Computer Search1/d1. The payoff remains the artificial scalar objective `P(own X ready) - lambda × P(Beheeyem second packet | first packet)`.

## Controlled forecast-prior results at denial weight lambda=10

The table compares four explicitly hypothetical distributions of future first-attack Prize awards. A payable source exists with exact probability **46.477077%** in every scenario, because the prior is exogenous and independent of the opponent's hand.

| Future Prize reward prior (r0, r1, r2) | Extra early source cost tau | Prelock Ultra Ball chosen | Incremental optimized utility vs never searching | Advantage a future-clairvoyant chooser would have |
| --- | ---: | ---: | ---: | ---: |
| (1/3,1/3,1/3) | 0 | **26.220950%** | +0.001760650 | 0 |
| (1/3,1/3,1/3) | 0.001 | **26.220950%** | +0.001498441 | +0.000087403 |
| (1/3,1/3,1/3) | 0.01 | **12.216193%** | +0.000194717 | **+0.000407206** |
| (1/3,1/3,1/3) | 0.10 | 0% | 0 | 0 |
| (1/2,1/2,0) | 0 | 26.220950% | +0.001216407 | 0 |
| (0,1/2,1/2) | 0 | 26.220950% | +0.002640975 | 0 |

The clairvoyant column compares the optimal expected payoff of hypothetical early choices allowed to observe the future r before playing Ultra Ball with the correctly prior-aware early decision. It is a **value of future information**, which a real player lacks.

At tau=0.01 with a uniform reward prior, acting as though the upcoming KO reward were already known overstates the improvement by **0.000407206**, compared to the genuinely achievable prior-aware improvement of **0.000194717** within this model. The future-knowledge assumption thus reverses some early search decisions when source cost is near the decision threshold.

At tau=0 the two policies select the same physical prelock hand classes for all shown priors, so their expected utilities agree even though future-r information is available only to the hypothetical hindsight policy.

## A more important surprise: deck thinning dominates pure K1 information

With the uniform future Prize prior, if the opponent mechanically plays Ultra Ball in **every** payable prelock hand and we value the same later optimal reply using the specified artificial utility, its combined improvement over no early search decomposes exactly as follows:

| Component of paid search | Increment in expected scalar utility |
| --- | ---: |
| Physical three-card thinning of U+F+F, **without** learning Prize X | **+0.001693196** |
| Additional K1 X-Prize information, with the same three-card payment | +0.000067454 |
| Both components | **+0.001760650** |

The decomposition is exact because the three-card discard leaves the post-Supporter shuffle deck at 50 cards instead of 53. Removing non-X cards increases the conditional concentration of unprized X in any subsequent four/six-card redraw, independent of Prize knowledge. The pure X-Prize-information component is **much smaller** than the physical deck-material benefit in this chosen hypothetical deck and objective.

This distinction matters: measuring the payoff difference between "played full-deck search" and "did not play full-deck search" and attributing all of it to **information** would substantially overstate K1's causal contribution. The same search action changes physical card zones and deck density, even when it finds zero Pokémon.

These figures describe changes in the model's dimensionless scalar utility. They do not predict that discarding three cards is good in a real Expanded deck: filler is deemed strategically disposable, the current model has no future need for those fillers, and a separate `tau` proxies unmodeled resource/opportunity costs.

## Exact finite-source calculation and verification

- [Reward-prior engine](../../tools/beheeyem_paid_k1_reward_prior.py) accepts any nonnegative rational three-entry reward prior summing to one. It conditions the early decision on the actual prelock hand and legal payable Ultra Ball, then integrates the later random draw, K0/K1 Prize distribution, public Beheeyem tutor route and realized r. It conserves both the real three-card U/F payment and the later 50-versus-53-card self-reset population.
- It compares the resulting attainable prior-aware optimum to the weighted baseline (never search) and a **clairvoyant upper bound** given by the earlier fixed-r search solver. It asserts that every result lies between these bounds.
- [Exact regression](reproduce.py) proves identity with the original fixed-r model for **every degenerate reward prior**, three denial weights and two source costs. It additionally tests four mixed rational priors across four costs, for **34 controlled checks**, including monotonic search incidence, marginal information benefit and the future-hindsight gap.
- [GitHub Actions run 38134795752 passed](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38134795752). Underlying physical timing, paying Ultra Ball and later Judge/Ace reshuffling have independent permutation-simulation validation in [38134590567](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38134590567).

The reward probabilities are declared priors, **not** estimates of whether Beheeyem can actually score a KO, and all calculations are conditional on a staged three-Basic board and an actual first attack. The prior is assumed statistically independent of the opponent's own hand and choices. True deck play may connect reward chance to opponent Board/Active positioning, Pokémon HP, prior locks or damage. Further source costs are represented by a freely chosen scalar tau.

## Strategic implication

Timing, information and material costs must be evaluated together. A full-deck search can have modest direct **belief-state value** yet greater value from modifying later deck density; a seemingly attractive early information purchase can also lose much of its estimated payoff once future outcomes are treated as uncertain. This exact toy example supplies separately testable source-action, belief update and response-policy kernels for a fuller opponent turn simulator.
