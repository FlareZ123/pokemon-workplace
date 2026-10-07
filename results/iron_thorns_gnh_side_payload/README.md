# Guzma & Hala multi-output side payload in Aichi Iron Thorns

## Question

When the published 2026 Aichi Iron Thorns line must use Guzma & Hala's optional two-card discard branch to search Double Colorless Energy, how often can the same Supporter also search a Pokémon Tool without any additional discard payment?

The narrow attack line is the same one modeled in `results/iron_thorns_named_line_probability/`:

`Tag Call -> Guzma & Hala -> Thunder Mountain Prism Star + Double Colorless Energy -> Volt Cyclone`

This result isolates one multi-axis property of Guzma & Hala. Its optional branch searches for both a Pokémon Tool and a Special Energy after the same two-card discard.

Implementation: `tools/iron_thorns_gnh_side_payload.py`  
Independent labeled-card regression: `results/iron_thorns_gnh_side_payload/reproduce.py`

## Published-list counts

The Aichi list transcription in `tools/aichi_setup_inference.py` gives the same core counts used by the earlier exact named-line result.

Tool counts for this result are:

| Player | DCE | Pokémon Tools |
| --- | ---: | ---: |
| Kazuma Kashi | 1 | 3 |
| Ryoya Fujii | 3 | 3 |
| Kohei Hamamichi | 1 | 4 |

Kazuma's Tool set is Palace Belt, Handheld Fan, and Tool Jammer. Ryoya has two Handheld Fan and one Tool Jammer. Kohei has two Palace Belt, one Handheld Fan, and one Tool Jammer.

Handheld Fan and Tool Jammer are typed as Pokémon Tools in the bundled card database. Palace Belt is a Japanese BW-P promotional card missing from the bundled English snapshot; its Pokémon Tool classification was separately checked against the card reference at <https://bulbapedia.bulbagarden.net/wiki/Palace_Belt>.

Guzma & Hala's bundled card text, `sm12-193` / `sm12-229`, states that after discarding two other cards from hand, the player may also search for a Pokémon Tool and a Special Energy.

## Model

The exact state generation is identical to the preceding named-line calculation:

1. draw a seven-card opening hand;
2. condition on at least one Iron Thorns ex;
3. remove one Iron Thorns ex from the hand as the Active Pokémon;
4. set six Prize cards from the remaining deck;
5. draw one card for the first turn going second.

The model partitions accepted states into the same route classes as the earlier result.

The new measurement considers only the `mediated_discard` class: DCE is not in hand, remains in deck, the Thunder Mountain requirement is available, and Guzma & Hala is accessible either directly or through Tag Call. Those states necessarily use the optional two-card discard branch to obtain DCE.

For each such state, the model records how many of the list's Pokémon Tools remain in deck when Guzma & Hala is used.

## Exact result

| List | Forced-discard G&H route | Same route with a Tool still searchable | P(Tool searchable | forced-discard route) | Expected Tools remaining in deck |
| --- | ---: | ---: | ---: | ---: |
| Kazuma | 28.940230640% | 28.702318846% | **99.177920186%** | 2.349954915 |
| Ryoya | 25.894650078% | 25.676770271% | **99.158591420%** | 2.345082396 |
| Kohei | 28.940230640% | 28.899300875% | **99.858571392%** | 3.133273220 |

The forced-discard route probabilities exactly reproduce the corresponding `Guzma & Hala mediated, DCE must be searched` masses from `results/iron_thorns_named_line_probability/`.

### Conditional Tool-count distribution

Among forced-discard G&H states:

| Tools remaining in deck | Kazuma | Ryoya | Kohei |
| ---: | ---: | ---: | ---: |
| 0 | 0.822080% | 0.841409% | 0.141429% |
| 1 | 10.687931% | 10.831547% | 2.722605% |
| 2 | 41.162407% | 41.304442% | 17.291955% |
| 3 | 47.327582% | 47.022603% | 43.355239% |
| 4 | - | - | 36.488772% |

## Finding 1: paying for one axis almost always exposes another search output

In these lists, the two-card discard is already required to obtain DCE in the measured states.

Once that payment is made, a Pokémon Tool remains in deck more than 99% of the time for all three lists. The Tool search is therefore usually available as an additional output of the same connector activation.

This is a concrete real-list example of multi-axis connector value. Treating Guzma & Hala only as a route to the Stadium and Special Energy discards information about another simultaneously available output channel.

## Finding 2: connector output capacity is state-dependent

The result does not imply that the Tool itself is always valuable.

The useful state is better represented as:

- the two-card discard cost is already being paid for DCE;
- Guzma & Hala has Tool-output capacity on that same activation;
- one or more legal Tool targets remain in deck;
- the value of taking a specific Tool depends on the matchup and resulting board state.

A graph edge such as `Guzma & Hala -> Double Colorless Energy` therefore understates the action. A stronger transition record keeps every output slot and then lets policy evaluation decide whether to fill it.

## Validation

The implementation uses exact integer combination weights and `Fraction` outputs.

The reproducer independently enumerates every labeled state of a 12-card toy deck with:

- two setup Basics;
- one Tag Call-like card;
- one Guzma & Hala-like card;
- one Stadium;
- one DCE;
- two Tools;
- four fillers;
- a three-card opening;
- two Prizes;
- one turn draw.

The grouped category model and labeled enumeration match exactly for:

- forced-discard route probability;
- forced-discard route with at least one Tool remaining;
- the full conditional distribution of Tool copies remaining in deck.

The reproducer also asserts that the three published-list forced-discard probabilities match the previously published named-line values.

## Limits

This is a search-capacity result, not a claim that taking a Tool is always optimal.

It does not model:

- Trainers' Mail;
- Tool-specific tactical value;
- whether a Tool can or should be attached that turn;
- DCI of the two cards discarded to Guzma & Hala;
- opponent interaction;
- Tool lock or other denial;
- later-turn value of leaving a Tool in deck;
- alternative Special Energy choices.

If a Tool is already in hand rather than in deck, this metric calls the extra Tool search unavailable even though Tool access already exists. The reported percentages therefore measure spare search output, not total Tool access.

## Interpretation

This result sharpens the repository's connector model in a real Archetype-Line-Specific line.

A connector transition should preserve unused simultaneous output capacity. When one cost unlocks several typed outputs, evaluating only the output needed for the immediate line can miss substantial tactical option value.
