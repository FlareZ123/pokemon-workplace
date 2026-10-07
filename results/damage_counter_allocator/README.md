# Exact attack-effect damage-counter allocation

## Question

For attacks that place a fixed number of damage counters "in any way you like," is the tactical choice captured by a single splash-damage value?

No. The distribution itself is a decision variable, and different objectives can prefer different exact allocations.

Implementation: `tools/damage_counter_allocator.py`  
Regression: `results/damage_counter_allocator/reproduce.py`

## Phantom Dive basis

The bundled Expanded-legal Dragapult ex `sv6-130` has Phantom Dive:

`Put 6 damage counters on your opponent's Benched Pokémon in any way you like.`

The allocator enumerates every integer composition of the fixed counter budget across caller-supplied eligible targets. For three targets and six counters there are 28 exact requested allocations.

Counter placement remains an attack effect, so a target that prevents effects of attacks can receive a requested share while zero counters are actually placed.

## Tactical counterexample

The regression uses three damaged Benched targets:

- A needs three counters to be Knocked Out and is worth one Prize;
- B needs three counters and is worth one Prize;
- C needs six counters and is assigned a three-Prize tactical value.

With six Phantom Dive counters:

- allocating 3/3/0 to A/B/C produces two Knock Outs and two Prize units;
- allocating 0/0/6 produces one Knock Out and three Prize units.

So maximizing the number of Knock Outs and maximizing immediate Prize yield select different lines.

This is a concrete example of discrete tactical value. A planner should retain the objective and the allocation decision rather than reducing the effect to an average amount of Bench damage.

## Effect-immunity witness

When C is marked immune to effects of attacks, the requested 0/0/6 allocation remains syntactically representable, but all six counters assigned to C place zero counters. The best available Prize yield falls from three to two in the regression.

This preserves the rule distinction established by the board-damage bridge: effect immunity acts on counter placement independently of ordinary damage prevention.

## Representation

Each `CounterAllocationOutcome` records:

- requested counters per target;
- counters actually placed per target;
- targets newly crossing their KO threshold;
- caller-supplied immediate Prize value.

The scorer counts only newly crossed KO thresholds, which prevents an already-doomed target from being credited again.

## Limits

The Prize-value input is a tactical utility supplied by the caller. The kernel does not yet derive Prize count from Rule Boxes, Legacy Energy, replacement effects, or the current Prize state.

Target eligibility is also upstream. Phantom Dive restricts the effect to Benched Pokémon, while other cards use different target domains.

The enumerator is exact and therefore grows combinatorially with target count and counter budget. Six counters across a legal five-Pokémon Bench is still small, while larger generic effects may need dynamic programming or dominance pruning.

A useful next step is to compose the allocator with the main 200-damage portion of Phantom Dive and the existing position/gust infrastructure, allowing a planner to compare complete double-KO lines rather than the Bench-counter subproblem alone.
