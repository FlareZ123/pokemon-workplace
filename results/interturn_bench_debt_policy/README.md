# Inter-turn Bench debt can collide with future Supporter bandwidth

## Question

Can a one-shot Bench support Pokémon be strategically expensive even when a deterministic cleanup card exists later?

Yes. The relevant issue is not only whether the support Pokémon can eventually leave the Bench. If cleanup itself consumes a scarce action channel on the same future turn that another required action uses, the support Pokémon creates **inter-turn Bench debt coupled to action-budget contention**.

This result isolates one concrete Expanded pattern:

- Crobat V `swsh3-104` is a Basic Pokémon V whose Dark Asset Ability can provide immediate draw when it is played from hand to the Bench, after which Crobat remains in play and occupies a Bench slot.
- AZ `xy4-91` can return one of your Pokémon to hand, so it can remove a spent Crobat V, but AZ is a Supporter.
- Scoop Up Net `swsh2-165` is banned by the repository's paper-Expanded legality overlay; even as a text-level counterexample, it explicitly cannot target Pokémon V or Pokémon-GX, so its wording would not clear Crobat V or Dedenne-GX.
- Magnezone `bw8-46` / Dual Brains supplies a verified two-Supporter-per-turn exception, allowing the model to test whether extra Supporter bandwidth restores the line.

Implementation: `tools/interturn_bench_debt_policy.py`  
Regression: `results/interturn_bench_debt_policy/reproduce.py`

## Mechanical continuation result

The model begins a future turn with ordinary Bench capacity 5. A spent support Pokémon, when present, is the fifth Benched Pokémon. The future objective is to put one required Pokémon onto the Bench, and in the collision case also play one required Supporter that turn.

Using the repository's `TurnActionBudget` and bounded planner gives:

| Future state | Supporter limit | Shortest legal continuation |
| --- | ---: | --- |
| No spent support, required Supporter + Bench entry | 1 | required Supporter -> Bench required Pokémon |
| Spent support, Bench entry only | 1 | AZ -> Bench required Pokémon |
| Spent support, required Supporter + Bench entry | 1 | **No legal plan** |
| Spent support, required Supporter + Bench entry | 2 | AZ -> required Supporter -> Bench required Pokémon |

The failure at limit 1 is a resource collision, not a lack of cleanup access. AZ is physically available and legally removes the Bench occupant, but doing so consumes the only ordinary Supporter play. The second required Supporter therefore cannot be executed on that turn.

This is a concrete form of cross-turn connector realism: **future cleanup access is weaker than future cleanup executability under the complete action budget.**

## Exact probability layer

Let:

- `S0` be immediate setup success if the support Pokémon is not used;
- `S1` be immediate setup success if the support Pokémon is used, with `S1 >= S0`;
- `c` be the probability that the future continuation lands in the collision branch requiring both AZ cleanup and another Supporter before the required Bench entry.

Assume all non-collision future branches are solvable. Under the ordinary one-Supporter quota:

`no-support joint success = S0`

`support joint success = S1 * (1 - c)`

The support line is better exactly when:

`c < 1 - S0 / S1`

The model computes `S0` and `S1` exactly from a hypergeometric draw-to-out subproblem. For a 40-card remaining deck with four setup outs:

| Base draws | Support draws | Base success | Support success | Immediate gain | Break-even collision probability |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 2 | 5 | 19.230769% | 42.707080% | +23.476310 pp | 54.970535% |
| 4 | 5 | 35.545464% | 42.707080% | +7.161615 pp | 16.769152% |
| 5 | 6 | 42.707080% | 49.254842% | +6.547762 pp | 13.293642% |

As the immediate marginal benefit of the support Pokémon narrows, a smaller probability of future Supporter/Bench collision is sufficient to reverse the present-turn choice.

Under a two-Supporter quota, the planner verifies that AZ plus the required Supporter plus the Bench entry is executable. Within this isolated model, the future collision penalty becomes zero and the support line retains its full `S1` immediate advantage.

## Strategic interpretation

This adds a temporal dimension to Bench debt. A support Pokémon can be disposable in continuation value while still being expensive to remove because the removal action competes with another scarce channel.

A planner that records only:

- current Bench occupancy;
- existence of a cleanup card; or
- current-turn draw improvement

can therefore overvalue the support line. It needs to preserve at least the future Bench requirement, cleanup action class, future Supporter demand, and live Supporter quota.

The interaction also shows why action-capacity modifiers can have value outside their most obvious use. A second Supporter play can function as a **Bench-debt release channel** when the only practical cleanup is itself a Supporter.

## Evidence class

- Crobat V, AZ, Scoop Up Net, and Dual Brains properties are card-text facts from the bundled card pool.
- One-Supporter versus two-Supporter feasibility is a deterministic state-transition result using the repository's action-budget and bounded-planner infrastructure.
- The threshold values are exact mathematical derivations under the stated toy draw model.

## Limitations

This is a small semantic island, not a full match or deck win-rate model.

The future collision probability `c` is an external policy/environment parameter here. A deck-specific model would derive it from actual future hands, draws, Prize state, board state, matchup, and intended lines.

The model assumes AZ is available and the spent support Pokémon has no retained value worth preserving. It does not model AZ discarding attached cards, gust liability, Prize liability, Tingly Return-GX, Super Scoop Up, Stadium-based Bench contraction, Pokémon leaving play for other reasons, lock effects, or turn-specific information arrival.

Dual Brains is used only as a validated example of Supporter quota 2. Real use also depends on Magnezone being in play with its Ability active and on any relevant lock effects.

## Next useful work

A strong deck-specific extension is to fold this state variable into the Harto Miki Raichu/Crobat planner or another published Expanded list: measure how often a Crobat-enabled immediate access gain is later offset by a concrete Bench-entry + Supporter collision, rather than treating `c` as exogenous.
