# Opposing Supporter accessibility and the public tutor-use signal

## Research question

Previous conditioned Beheeyem Mysterious Noise studies identified Judge and Ace Trainer as especially restrictive hand-reset Supporters for preventing the next Beheeyem + Triple Acceleration Energy packet. The [no-reset option comparison](../beheeyem_optional_supporter_response/) then found that replenishing a draw-starved Beheeyem hand can be strategically counterproductive.

**Can the opposing player actually access those Supporters?** When does Ace Trainer's Prize-race restriction enable or disable the response? Can the opponent exploit the visible use of a paid tutor in the Beheeyem player's first attack?

The answers require two physical decks, a legal-response filter and a limited public-information policy. This study composes independent, exact finite models for all three, while retaining the earlier packet-model limitations.

## Opponent's independent 60-card deck

For the opponent's model, take an illustrative disjoint categorical deck containing:

- 12 Basic Pokémon.
- 4 Ace Trainer.
- 4 Judge.
- 40 neutral filler.

Condition a uniformly dealt seven-card opening hand on containing at least one Basic. Place six random original Prize cards, then draw `k=2` additional cards from the remaining deck. When the opponent has taken `s` of its own Prizes, those `s` randomly chosen original Prize identities enter its hand. Once a named Supporter has appeared in that cumulative seen set, the opponent is assumed to retain it until the reply.

The exact probability that none of `m` copies of a specified **non-Basic**, disjoint Supporter category is seen is

```text
P(no m) = [C(60-m,7)-C(60-m-12,7)] / [C(60,7)-C(48,7)]
          × C(53-m,2+s)/C(53,2+s).
```

The first factor handles the valid opening, and the second handles the union of later deck draws and earned Prize identities as an exchangeable sample from the other 53 cards. Inclusion-exclusion supplies the exact joint distribution of holding neither, either or both named Supporters.

| Opponent's Prizes taken | Remaining Prizes | Probability Ace Trainer seen | Probability Judge seen |
| ---: | ---: | ---: | ---: |
| 0 | 6 | 47.143530% | 47.143530% |
| 1 | 5 | 51.289136% | 51.289136% |
| 2 | 4 | 55.186005% | 55.186005% |

The equality of these two marginal probabilities comes from equal copy counts and symmetric category roles. Having already *seen* Ace Trainer does **not** mean it can be legally played.

## Timing and Prize-race legality

Let the Beheeyem player take `r` hypothetical Prizes with the first Mysterious Noise, leaving `6-r`. Let the opponent retain `q=6-s` Prizes. Ace Trainer is playable by that opponent only when `q > 6-r`, equivalently `r > s`. Judge is an unrestricted Supporter when held. The opponent may also choose **no hand reset**; this is an action alternative within the isolated response problem.

For each physical held-Supporter subset, the opponent chooses the action that minimizes the **joint probability of an available first and second Beheeyem+TAE packet**, assuming it knows the parameterized deck model and public remaining Prizes but not the hidden Beheeyem hand/Prize composition. We calculate both:

1. **Aggregate-access policy:** ignores whether the first Beheeyem packet was played directly from hand or rescued by playing a one-copy tutor.
2. **Public-route policy:** conditions the decision on observing that tutor being played. This observation is public at the time of the attack, under the deterministic policy that only uses a tutor when the direct packet is absent.

Both policies minimize the conditional expected joint packet event, with an independent opponent deck and Supporter availability. They do not inspect the player's hidden cards.

## Exact example: Beheeyem B4, TAE4, Computer Search1, T3 d=1

The opposing deck is B12 / Ace4 / Judge4 / filler40, with `k=2` opponent extra draws. The prior Beheeyem model assumes three established Basics, a six-card T2 residual hand and six Prizes. All rates below are joint packet access, conditioned on an exogenously fixed T2 first-attack Prize reward.

| Beheeyem Prizes taken `r` | Opponent Prizes remaining `q` | No reset | Access-aware aggregate policy | Public tutor-observation policy |
| ---: | ---: | ---: | ---: | ---: |
| 0 | 6 | 0.662553% | 0.662553% | 0.662553% |
| 1 | 6 | 1.125764% | 1.125764% | **1.089143%** |
| 1 | 5 | 1.125764% | 1.125764% | 1.125764% |
| 2 | 6 | 1.679597% | 1.450037% | **1.436326%** |
| 2 | 5 | 1.679597% | 1.429851% | **1.414934%** |
| 2 | 4 | 1.679597% | 1.679597% | 1.679597% |

Several conclusions follow under the explicitly limited packet objective:

- One early Prize award can **unlock Ace Trainer** for the opponent while it is behind on Prizes. If the opponent has earned an equal number, that same Ace Trainer becomes illegal, even as seeing more cards makes possessing it more likely.
- For r=1,q=6, **aggregate-only** policy rationally keeps the Beheeyem hand intact: the strongest available reset improves its overall packet availability. After a publicly observed **direct first packet**, the opponent sometimes benefits from playing the accessible Ace. If a tutor was consumed to rescue the first packet, the opponent should preserve the depleted hand. Recognizing the public route lowers the event by **0.036621 percentage points**, about 3.25% of the previous no-reset event.
- At r=2,q=6, introducing finite opponent card access raises the optimal event to 1.450037%, versus the 1.192659% hypothetical universal/free Ace response in the earlier model. The public tutor signal further reduces access to 1.436326%.
- For r=2,q=4, Ace Trainer is illegal on a tied Prize race and Judge only increases next-packet availability in this example, so the best modeled response is no reset.

## Finite validation and scope

The [exact regression](reproduce.py) sweeps all **1,152** Beheeyem model configurations (B,TAE=1..4; four one-copy tutor types; d=0..5; r=0..2) at `q=6` and the example opponent deck. It finds **207** scenarios in which finite-access hand resets outperform no reset under aggregate optimization, and **346** in which conditioning on publicly used tutor/direct first-packet route improves the expected event further. This counts parameter configurations and is not a metagame weighting.

The code independently enumerates every Basic-valid hand, Prize subset, draw and awarded-Prize selection for a small ten-card toy game to verify the combinatorial access formula (`92/357` probability of not observing two named Supporters). A second [physical 60-card Monte Carlo](monte_carlo.py) samples 200,000 complete independent shuffles for each of zero, one, two earned opposing Prizes, checking exact four-category Supporter visibility against six-standard-error tolerances. All comparisons and simulations [passed GitHub Actions run 38133018466](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38133018466).

The [opponent access engine](../../tools/beheeyem_opponent_supporter_access.py) is a first two-deck **source-access** model. It leaves out actual Beheeyem Knock Out feasibility, opponent board development, opponent supporters spent on other turns, previous hand resets, opponent prize-taking probability and timing, opponent draw search engines, Supporter slot contention with other strategies, card-based retrieval from Prizes, and the cost of withholding a Supporter. It assumes disjoint 12 Basic/8 targeted Supporter cards in a hypothetical deck, independent opposing players' draws and hands, and a deterministic Beheeyem first-packet tutor policy. Those simplifications should remain visible when interpreting the exact percentages.

## Further work

Make the opponent's future turns and support access **sequential**, tracking a persistent hand, the possibility of spending Supporters on earlier turns, actual search connectors and card expenditures. Then include an opponent's other tactical actions and game-winning objectives. The present public-observation benchmark makes one narrow prediction that a realistic solver can be required to reproduce: knowing that a singleton paid tutor was used can change the correct response despite unchanged visible Prize totals.
