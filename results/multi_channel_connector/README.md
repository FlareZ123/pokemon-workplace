# Multi-channel connector capacity: when Secret Box scales beyond Computer Search

## Question

How does a one-output universal search connector compare with a Secret Box-like multi-output connector as the number of simultaneously required eligible channels increases?

The two-card comparison already showed a crossover between lower discard cost and higher output capacity.

This result extends the same exact model to two, three, and four required channels.

Implementation: `tools/multi_channel_connector.py`  
Reproducer: `results/multi_channel_connector/reproduce.py`

## Interpretation of the connectors

The **capacity-one, cost-two** connector is a Computer Search abstraction:

- discard two;
- search one card;
- the one output can satisfy any one modeled target channel.

The **multi-output, cost-three** connector is a Secret Box abstraction:

- discard three;
- every modeled target channel maps to a different eligible Secret Box category;
- one use can satisfy all missing modeled channels if each remains searchable.

For the four-channel case, the intended mapping is one required Item, one Pokémon Tool, one Supporter, and one Stadium.

The model does not turn Secret Box into unrestricted four-card search.

## Baseline

Hold fixed:

- 60 cards;
- 6 Prize cards;
- accepted 7-card opening;
- 12 protected setup starters;
- 20 disposable non-starters;
- 1 ACE SPEC connector;
- 2 outs in every required target channel.

At D=20:

| Required channels | Direct joint access | Capacity 1, cost 2 | Multi-output, cost 3 |
| ---: | ---: | ---: | ---: |
| 2 | 3.799330% | 5.564306% | 6.655194% |
| 3 | 0.575181% | 0.865215% | 3.420250% |
| 4 | 0.068233% | 0.091320% | 2.885121% |

## Finding 1: one-output search collapses rapidly as simultaneous requirements grow

With four required channels, direct access is only 0.068233%.

A one-output connector raises that to 0.091320%.

The connector can repair only states where at most one required channel is missing. States missing two, three, or four channels remain unsolved even when every target is searchable and the discard cost is payable.

This is multi-channel connector domination.

## Finding 2: multi-output search attacks the combinatorial bottleneck

In the four-channel state, the Secret Box-like abstraction reaches 2.885121% joint access at D=20.

That is over thirty times the capacity-one result.

The mechanism is structural. One paid action can satisfy several missing categories at once.

The relative advantage grows sharply with the number of simultaneous requirements because the one-output connector is increasingly likely to face more missing channels than it has output capacity.

## Finding 3: the disposable-density crossover moves earlier with more channels

Using the same two-outs-per-channel composition, the first nontrivial integer disposable count where the cost-three multi-output connector strictly beats the cost-two one-output connector is:

| Required channels | First positive crossover D |
| ---: | ---: |
| 2 | 13 |
| 3 | 4 |
| 4 | 3 |

For four channels, the multi-output connector becomes favored as soon as its three-card discard requirement starts becoming payable in some accepted openings.

For two channels, the cheaper connector retains an advantage much longer because its one-card output is sufficient in a larger share of states.

## Strategic implication

The value of Secret Box's extra discard cost cannot be judged independently of how many categories a deck line genuinely needs at once.

In a line requiring only one missing card, its cost can be a liability.

In a line with several eligible missing Trainer categories, the simultaneous output can be the dominant feature.

This is an Archetype-Line-Specific effect. A deck with a concrete line such as "Supporter + Stadium + Tool + Item" can assign Secret Box far more value than a generic one-target consistency model would.

## Mathematical method

For a fixed accepted opening-hand composition, let each missing target channel (i) have (k_i) copies left before Prize placement.

The model needs the probability that every missing channel retains at least one searchable card after Prizes are set.

It uses inclusion-exclusion over the events:

`E_i = all remaining copies of target channel i are Prized`.

For any subset of missing channels, the intersection probability depends only on the total number of selected copies, so it has a hypergeometric closed form.

This keeps the calculation exact without enumerating every Prize composition.

## Validation

The two-channel capacity-one rows agree with the previously validated connector-domination implementation.

The reproducer asserts all displayed two-, three-, and four-channel values and independently locates the integer disposable-density crossover for each channel count.

No Monte Carlo sampling is used.

## Limitations

The target channels are abstract and independent.

For Secret Box, each channel must correspond to a distinct eligible search category. Two required Supporters, for example, cannot both be obtained by the one Supporter output.

The model does not include:

- strategic value of optional extra Secret Box outputs;
- the fact that some searched cards may themselves unlock further searches;
- sequencing after the cards reach hand;
- Supporter contention;
- Stadium replacement rules;
- Tool attachment constraints;
- graded DCI;
- lock effects;
- Bench constraints;
- attacks;
- Energy timing;
- matchup-specific value.

The comparison therefore measures access capacity, not total card strength.

## Next useful work

Apply the four-channel model to a concrete Archetype-Line-Specific sequence from the local card pool.

A useful case should specify an actual Item, Tool, Supporter, and Stadium package, then test which of those pieces are genuinely independent requirements and which can substitute for or search one another.
