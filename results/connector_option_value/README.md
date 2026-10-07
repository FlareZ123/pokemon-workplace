# Connector option value: when a payable universal search should be held

## Question

Can it be strictly optimal to hold a universal search connector even when it is already payable and both of its possible targets would be useful?

Yes.

This result isolates the option value of preserving a one-use Computer Search-like connector under uncertain future draws. It uses the finite-horizon optimizer in `tools/connector_competing_policy.py`.

Reproducer: `results/connector_option_value/reproduce.py`

## Canonical state

Consider a state after the current turn's natural draw with:

- 2 turns remaining including the current turn;
- 1 unresolved critical Prize;
- setup still missing;
- no rescue Supporter in hand;
- 1 universal connector in hand;
- exactly enough disposable cards to pay its two-card discard cost;
- 2 setup targets left in deck;
- 2 rescue Supporters left in deck;
- no second connector;
- 20 disposable cards and 16 other cards left in deck.

There are 40 cards in the deck.

Both missing channels are equally searchable now.

## Exact two-turn comparison

If the player **waits**, the next natural draw can hit either missing channel. There are 4 useful cards among 40.

If that draw supplies setup, the saved connector can search rescue. If it supplies rescue, the saved connector can search setup.

Therefore:

`P(success | wait) = 4 / 40 = 10%`

If the player **searches setup immediately**, the connector is spent and removed from the future decision. The next draw must be a rescue Supporter. After the search, 39 cards remain and 2 of them are rescue cards.

Therefore:

`P(success | search setup now) = 2 / 39 = 5.128205%`

By symmetry, searching rescue now has the same value.

Holding the payable connector therefore nearly doubles completion probability in this state.

## Longer horizons

The same state remains strongly wait-favored as the horizon grows.

| Turns remaining | Wait | Search either channel now |
| ---: | ---: | ---: |
| 2 | 10.000000% | 5.128205% |
| 3 | 19.230769% | 10.121457% |
| 4 | 27.732794% | 14.979757% |
| 5 | 35.545464% | 19.703104% |
| 6 | 42.707080% | 24.291498% |

Future turns are optimized after the first action.

The gap persists because the saved connector remains a flexible response to whichever channel natural draws fail to supply.

## Deadline states reverse the decision

Connector preservation is state-dependent.

With one turn remaining, if rescue is already in hand and setup is missing, searching setup and then playing the rescue Supporter completes both objectives with probability 100% in the modeled state.

Likewise, if setup is already secured and rescue is missing, searching the rescue Supporter and playing it immediately completes the objective with probability 100%.

So the same payable connector can have three qualitatively different best uses:

- hold it;
- spend it on setup;
- spend it on rescue.

The optimal choice depends on which channels are already satisfied and how much horizon remains.

## Strategic implication

A search graph that rewards a connector whenever it can immediately reach a useful card can destroy option value.

The relevant state variable is not merely whether Computer Search is available. The model needs to know whether it is still unspent, what alternatives remain in the deck, what the current hand already covers, and how many future draws or action windows remain.

This is a stronger form of connector domination. The opportunity cost of a search is sometimes the loss of **future target flexibility**, even when the immediate searched card is genuinely useful.

## Relation to prior results

`results/connector_domination/` showed that one universal connector cannot satisfy two simultaneously missing channels.

`results/connector_competing_policy/` showed that adaptive allocation across turns beats fixed setup-first or rescue-first priorities.

This result exhibits a concrete state where the optimal adaptive action is to spend the connector on neither target yet.

## Validation

`competing_action_values()` exposes exact state-action values from the already independently validated dynamic program.

The reproducer checks the two-turn canonical state against simple closed forms:

- wait: `4 / 40`;
- immediate search of either target: `2 / 39`.

It also asserts the longer-horizon values shown above and two one-turn deadline states where immediate connector use has value 1.0 while waiting has value 0.

## Limitations

The model remains abstract.

The setup target is considered secured as soon as one copy reaches hand. The model contains one universal connector, a binary disposable/protected split, one natural draw per turn, and no opponent interaction.

It does not model evolution, Bench space, Energy attachment, attacks, search chains into the connector, lock effects, ordinary Prize-taking, or matchup-specific target value.

## Next useful work

The immediate deck-construction question is whether adding redundancy to a target channel is more valuable than adding another disposable card that makes the connector easier to pay.

That comparison can quantify how connector capacity and DCI interact when allocating a single deck slot.
