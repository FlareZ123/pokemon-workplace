# Competing connector policy: setup versus Prize rescue

## Question

How should one universal search connector be allocated when it can serve either a setup requirement or a Gladion-like Prize-rescue line?

The preceding connector-domination result established a same-window feasibility problem. One Computer Search-like card can appear to reach several resources while still producing only one searched card.

This result adds time and policy choice.

Implementation: `tools/connector_competing_policy.py`  
Reproducer and independent labeled validation: `results/connector_competing_policy/reproduce.py`

## Model

The deck contains:

- critical non-starter singletons that matter if Prized;
- copies of one abstract setup target;
- Gladion-like rescue Supporters;
- one Computer Search-like universal connector;
- currently disposable non-starters;
- protected setup starters;
- protected non-starters.

The opening hand is conditioned on containing a setup-eligible starter. Prize cards are sampled from the remaining deck.

The reported success probability conditions on at least one critical singleton being initially Prized.

Each modeled turn begins with one natural draw.

The setup target is an abstract non-Supporter resource. Once one copy reaches hand, the setup requirement is considered secured.

A rescue Supporter can resolve one modeled critical Prize. At most one rescue Supporter is played per modeled turn.

The connector can search either the setup target or one rescue Supporter. It preserves the Supporter play and requires a fixed number of currently disposable cards. With discard cost two, this is a narrow Computer Search-like action model.

## Policies

The exact optimizer evaluates all modeled legal choices after each natural draw:

- wait and preserve resources;
- play a rescue Supporter already in hand;
- spend the connector on setup;
- spend the connector on rescue;
- combine a setup search with a rescue Supporter already in hand;
- search a rescue Supporter and play it immediately;
- search a rescue Supporter and hold it.

The action with the highest probability of completing both objectives by the horizon is selected.

Three comparison policies are also evaluated.

**Setup priority** greedily spends a payable connector on setup whenever setup is missing and searchable. If that route is unavailable, it can search rescue.

**Rescue priority** greedily searches a rescue Supporter when one is needed and none is in hand. If that route is unavailable, it can search setup.

**No connector** never uses the universal connector.

The two priority policies are simple heuristics rather than claims about optimal real play.

## Illustrative baseline

Use:

- 60 cards;
- 6 Prize cards;
- a valid 7-card opening;
- 12 protected setup starters;
- 4 critical non-starter singletons;
- 4 setup-target copies;
- 2 rescue Supporters;
- 1 universal connector;
- 20 disposable non-starters;
- discard cost 2.

The probability that at least one modeled critical singleton is Prized, conditional on the accepted opening, is 35.383108%.

The following table conditions on that event.

| Horizon | Optimal policy | Setup priority | Rescue priority | No connector |
| ---: | ---: | ---: | ---: | ---: |
| 1 turn | 11.687613% | 11.687613% | 11.687613% | 8.201849% |
| 2 turns | 15.387245% | 15.050208% | 15.216836% | 10.437978% |
| 3 turns | 19.122464% | 18.417392% | 18.771042% | 12.761371% |
| 4 turns | 22.939036% | 21.854304% | 22.407582% | 15.212943% |
| 5 turns | 26.776821% | 25.313424% | 26.072215% | 17.769949% |
| 6 turns | 30.594978% | 28.763804% | 29.728458% | 20.411409% |

## Finding 1: connector value depends on allocation policy

By turn 4, the adaptive policy reaches 22.939036% conditional joint success.

The no-connector policy reaches 15.212943%.

The shared connector therefore contributes 7.726093 percentage points in this abstract state distribution when its use is optimized together with future draws.

The value cannot be assigned permanently to either target channel because the best use changes with what the opening, Prize cards, and later draws already supplied.

## Finding 2: a fixed priority loses option value

At turn 4:

- optimal: 22.939036%;
- rescue priority: 22.407582%;
- setup priority: 21.854304%.

The adaptive policy gains 0.531454 points over the stronger fixed priority.

By turn 6, the adaptive advantage over the stronger fixed priority grows to 0.866520 points.

The difference arises from state dependence. A connector held for later can cover whichever channel natural draws fail to supply. Spending it as soon as one search looks useful can remove that insurance.

This extends the option-value correction already found in the repository's earlier turn-by-turn connector work.

## Finding 3: first-window priority can be irrelevant while later policy still matters

All three connector-using policies have the same one-turn success in the baseline.

A one-turn objective leaves little room for option value. If both channels are missing, one connector cannot satisfy both. If only one is missing, every useful policy searches that missing channel.

From turn 2 onward, natural draws can alter which future shortage matters. Policy differences then appear.

A static classification such as "Computer Search is an out to Gladion" therefore loses information. The connector is better represented as an unspent resource whose best target depends on state and horizon.

## Rules interpretation

The model relies on two ordinary timing facts represented in the bundled rules material.

Computer Search is an Item in the bundled Expanded card data. Its `bw7-137` text discards two cards and searches the deck for one card.

Items can be played during the turn without consuming the one-Supporter allowance. A Computer Search-like Item can therefore find a Gladion-like Supporter and still allow that Supporter to be played in the same modeled turn.

The model keeps the connector and rescue actions separate so the one-Supporter-per-turn constraint is preserved.

## Validation

The main calculation is exact.

Initial hands and Prize states use multivariate hypergeometric probabilities. Future natural draws are handled by a memoized finite-horizon dynamic program.

An independent labeled-card validator uses:

- a 10-card deck;
- a 3-card accepted opening;
- 2 Prize cards;
- 2 critical cards;
- 1 setup target;
- 1 rescue Supporter;
- 1 universal connector;
- 2 disposable cards;
- 2 setup starters;
- 1 protected card;
- discard cost 1;
- a 3-turn horizon.

It enumerates every accepted labeled opening and every disjoint labeled Prize set. Future draws are averaged over individual labeled cards. Connector searches explicitly remove a matching labeled card from the remaining deck.

The labeled calculation matches the category dynamic program for:

- optimal policy;
- setup-priority policy;
- rescue-priority policy;
- no-connector policy;
- the probability that any critical card is initially Prized.

Total setup-conditioned state mass is asserted to equal one.

## Relation to prior repository work

`results/connector_domination/` measures same-window overstatement when one connector is counted independently for two simultaneous channels.

`results/prize_rescue_discard_connector/` models a discard-gated preserving connector for one rescue objective across turns.

`results/prize_rescue_connector_turns/` established that eager connector use can lose future option value even before a competing target is introduced.

The present result combines those ideas by giving the same one-use connector two strategically useful destinations.

## Limitations

The setup target is abstract and is considered complete as soon as a copy reaches hand.

The model omits:

- evolution and Bench requirements;
- Energy attachment timing;
- attacks;
- targeted search for the connector;
- multiple universal connectors;
- graded DCI values;
- target copies becoming discard fodder;
- alternative Prize recovery;
- ordinary Prize-taking;
- lock effects;
- matchup-specific target value;
- competing non-rescue Supporters;
- a setup target that itself consumes the Supporter play;
- a setup target whose value depends on board state after acquisition.

The critical cards and setup target are disjoint categories.

## Next useful work

A stronger model should replace the abstract setup target with a concrete Expanded line.

A practical candidate is a deck-specific state where Computer Search can either secure an attacker or Energy requirement, or obtain Gladion for a Prized singleton. The state should include the actual search network and discardable cards in that list.

Another useful extension is to derive action-value maps from the dynamic program. Those maps would show the exact states where preserving Computer Search is optimal, where setup search is optimal, and where rescue search is optimal.
