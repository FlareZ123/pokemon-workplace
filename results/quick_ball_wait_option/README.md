# Quick Ball one-draw option value

## Question

The post-draw allocation frontier shows that Quick Ball contention can become more common after a small amount of random exposure.

Can that effect be isolated analytically in a concrete state?

Yes. A one-draw microstate gives a closed-form example where preserving Quick Ball until after the next natural draw is strictly more valuable than committing it immediately, provided neither objective expires before that draw.

Implementation: `tools/quick_ball_wait_option.py`  
Reproducer: `results/quick_ball_wait_option/reproduce.py`

## State

Assume the current hand contains one Quick Ball and one acceptable discard card.

Assume the remaining deck has `N` cards containing one required Basic attacker, one Tapu Lele-GX, `g >= 1` Gladion copies, and `F = N - g - 2` other cards.

Neither attacker setup nor Gladion access is currently complete. Quick Ball can be spent immediately on the attacker or Tapu Lele-GX. If it searches Tapu Lele-GX, Wonder Tag then searches a Gladion from the deck.

Alternatively, the player can preserve Quick Ball for one natural draw and choose the search target after seeing that draw.

This state assumes the discard payment, Item permission, Ability permission, and Bench slot are already available. It isolates the value of target-choice information.

## Outcome probabilities

If the player waits one draw, drawing the attacker solves attacker setup, drawing Tapu Lele-GX enables the rescue route, and drawing any Gladion provides direct rescue access. In each of those cases Quick Ball can solve the other channel.

Therefore:

`P(both | wait) = (g + 2) / N`

`P(choice | wait) = F / N`

If Quick Ball searches the attacker immediately, the next draw comes from `N - 1` cards. Gladion access then arrives by drawing Tapu Lele-GX or one of the `g` Gladion copies:

`P(both | eager attacker) = (g + 1) / (N - 1)`

If Quick Ball searches Tapu Lele-GX immediately, Wonder Tag removes one Gladion as well. The next draw comes from `N - 2` cards, and only the attacker completes both channels:

`P(both | eager Gladion) = 1 / (N - 2)`

The physical deck-size differences matter. Immediate search changes the population from which the later natural draw is sampled.

## Additive continuation value

Let `A > 0` be the downstream value of attacker completion and `G > 0` the downstream value of Gladion access.

The three policies have expected additive value:

`E_attacker = A + G * (g + 1) / (N - 1)`

`E_gladion = G + A / (N - 2)`

`E_wait = ((g + 2) * (A + G) + F * max(A, G)) / N`

The wait policy observes the natural draw before deciding which search deserves the one physical Quick Ball.

## Finding 1: waiting has strictly positive option value

When `A >= G`, the wait policy assigns filler-draw states to the attacker. Its advantage over immediate attacker search simplifies to:

`G * F / (N * (N - 1))`

This is strictly positive whenever `G > 0` and at least one filler card remains.

For `G >= A`, the same one-draw policy also exceeds both eager commitments under the modeled state. The reproducer checks this property across a grid of deck sizes, Gladion counts, and value ratios.

The result is a concrete form of connector option value. Preserving Quick Ball retains the right to allocate it after a future draw reveals which channel still needs the search.

## Baseline example

Use `N = 40`, `g = 2`, and `A = G = 1`.

| Policy | P(both) | Expected completed-channel units |
| --- | ---: | ---: |
| Search attacker now | 7.692308% | 1.076923 |
| Search Tapu Lele-GX now | 2.631579% | 1.026316 |
| Wait one draw, then allocate | 10.000000% | 1.100000 |

The wait policy gains **0.023077 expected completed-channel units** over the better eager commitment.

This is an abstract continuation metric rather than a match win-rate estimate.

## Finding 2: the option value comes from newly observed redundancy

Waiting is useful because several future draws make one of the two Quick Ball targets redundant.

If the next card is the attacker, searching the attacker would waste the connector. If the next card is Gladion or Tapu Lele-GX, allocating Quick Ball to the rescue channel would be redundant.

A future random draw therefore has decision value beyond the raw probability of drawing a useful card. It can change which existing search edge is worth consuming.

This helps explain the post-draw frontier result. Small amounts of exposure can create more states where several lines are live while only one search is available.

## Finding 3: an immediate deadline removes the right to wait

The positive option value depends on both objectives surviving until after the natural draw.

If attacker establishment is required before that draw, waiting is infeasible for the attacker objective. The player must search the attacker now if that objective is mandatory.

If Gladion access is required before the draw, the player must commit Quick Ball to Tapu Lele-GX now.

If both missing objectives expire immediately, one Quick Ball cannot satisfy both in this state.

The deadline does not change Quick Ball's search text or physical capacity. It removes a future decision branch from the policy.

This is the concrete Quick Ball analogue of the repository's generic connector-deadline results.

## Validation

The formulas are mathematical derivations from the stated card populations.

The reproducer independently enumerates labeled decks for multiple small `N`, Gladion counts, and value ratios. It calculates all three policies from physical target removal and natural draws, then matches the analytic formulas to floating-point precision.

It also verifies the 40-card, two-Gladion baseline and checks a grid of states with positive attacker and Gladion values where at least one filler card remains. In every tested state, waiting one draw has greater expected value than either eager commitment when no deadline forbids waiting.

## Interpretation

A search connector can have value as an unspent decision right.

This value is separate from the connector's immediate reachability and from the strength of either target. It depends on future observations, physical target removal, timing, and the relative continuation values of the target channels.

A finite-horizon optimizer should preserve unspent connector state when future information can alter target priority.

## Limits

This is a deliberately narrow state theorem.

It assumes Quick Ball and an acceptable discard are already in hand. It excludes Prize uncertainty inside the microstate, competing Quick Ball targets beyond the two modeled channels, lock effects, Bench saturation, ordinary Prize-taking, multiple future draws, and opponent interaction.

The result also treats attacker completion and Gladion access as additive terminal values. A real Archetype-Line-Specific objective can have nonlinear interactions between them.

## Next useful work

The natural next step is to embed this decision right into the exact setup-conditioned frontier model.

That policy should allow Quick Ball to be spent at several possible windows, give attacker and rescue separate deadlines, and compare eager commitment with adaptive preservation across the actual opening, Prize, and draw distribution.
