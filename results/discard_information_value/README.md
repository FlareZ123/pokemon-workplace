# Exact Prize information can change the optimal discard

## Question

Can K1 have direct tactical value at a discard decision, rather than only improving general search knowledge?

Yes.

When a high-upside discard is safe only if a replacement copy is unprized, exact Prize information can let the player choose between that aggressive discard and a lower-upside guaranteed line.

Implementation: `tools/belief_discard_decision.py`  
Reproducer: `results/discard_information_value/reproduce.py`

## Decision model

The current hand contains:

- one required TM: Evolution;
- one fodder card;
- Arven.

Exactly one card must be discarded.

The endpoint requires TM: Evolution in hand.

Two choices are available:

- discard fodder, yielding utility 0.9 when the endpoint remains reachable;
- discard current TM, yielding utility 1.0 when Arven can restore a replacement, and 0 if the endpoint fails.

The utility values are deliberately stylized. They isolate the value of information from the mechanics that determine endpoint safety.

## K0 with one replacement

There is one replacement TM in a 53-card unknown pool with six Prize cards.

Continuation-aware safety gives:

- fodder discard: 100% endpoint safety;
- TM discard: 47/53 = 88.679245283% endpoint safety.

Expected utility if the player must commit under K0:

| Fixed discard | Expected utility |
| --- | ---: |
| fodder | 0.900000000 |
| current TM | 0.886792453 |

The best fixed K0 choice is therefore fodder with value 0.9.

## Perfect information before the deadline

If exact Prize composition is learned first:

- in the 47/53 worlds where replacement TM is unprized, choose the TM discard for utility 1.0;
- in the 6/53 worlds where replacement TM is Prized, choose the fodder discard for utility 0.9.

The perfect-information value is:

`(47/53) * 1 + (6/53) * 0.9 = 0.988679245`

Gross value of exact information at this decision:

`0.988679245 - 0.9 = 0.088679245`

This is a decision-specific value of K1.

Any information action costing less than that amount in the same utility units would be favorable in this stylized model. Real Pokémon costs must be expressed through their actual Supporter, Item, Bench, Energy, or timing opportunity costs.

## K1 policy

Once the state is already exact, additional perfect information has zero value.

- replacement known unprized -> discard TM;
- replacement known Prized -> discard fodder.

The visible hand is identical. The optimal discard changes only because the hidden Prize state is known.

## Two replacement copies

With two uncertain replacement copies, the risky TM discard is safe in 98.911465893% of worlds.

Its K0 expected utility now exceeds the safe 0.9 line, so the fixed policy already chooses TM.

Perfect information still has value because it identifies the rare world where both replacements are Prized and the player should switch to fodder. The gross value of information falls to about 0.009796807.

Redundancy therefore has two effects:

- it raises recovery reliability;
- it reduces the marginal value of learning exact Prize composition.

## Finding

The value of deck inspection depends on the decision it can change.

For continuation-aware discard decisions, K1 is valuable when different Prize worlds prefer different exact discard witnesses. If one witness dominates in every world, exact composition may have little or no marginal value at that deadline.

This gives a direct path from Prize belief to DCI policy:

`Prize belief -> world-specific continuation feasibility -> discard utility -> information value`

## Limits

The utilities are illustrative, not calibrated match win probabilities.

The model assumes perfect composition information can be acquired before the decision and does not price the action required to obtain it.

A full planner must subtract the opportunity cost of the actual information action and account for any physical state changes that action causes.

## Next useful work

The next step is to price a concrete information-producing action.

A deck search can both reveal K1 and obtain a card, while consuming an Item, Supporter, discard resource, or connector opportunity. Comparing those joint benefits and costs would avoid treating information as a free side effect.
