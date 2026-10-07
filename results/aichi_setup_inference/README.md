# Pre-turn inference from two published Aichi 2026 lists

## Question

How informative is the public mulligan transcript before the face-down setup cards are revealed, in a concrete high-level Expanded pairing?

This case study compares two exact published lists from the 2026 CL Aichi Open League: Takahiro Ando's runner-up Vileplume Control and Kazuma Kashi's sixth-place Iron Thorns.

Implementation: `tools/aichi_setup_inference.py`

Reproducer: `results/aichi_setup_inference/reproduce.py`

## Source counts

Limitless records the complete lists at:

https://www.limitlesstcg.com/tournaments/566/decklists

The Vileplume list contains 14 ordinary Basic Pokémon among 60 cards. The Iron Thorns list contains only four Pokémon, all four copies of Iron Thorns ex, so it has four forced Basics.

At card-name level, the two lists share these non-Basic names: Guzma & Hala, Guzma, Plumeria, Lusamine, Gladion, Faba, Tag Call, and Capture Energy.

Counting copies of those shared names gives 16 shared-name non-Basic copies in the Vileplume list and 17 in the Iron Thorns list. The remaining non-Basic cards are name-unique to one of these two exact lists.

The analysis is list-to-list classification. A card being unique here means absent from the other published list, rather than unique to the broader archetype or format.

## Finding 1: mulligan count alone is strong evidence

The exact per-attempt mulligan probabilities are:

| Exact list | Forced Basics | Mulligan probability |
| --- | ---: | ---: |
| Vileplume Control | 14 | 13.859068087% |
| Iron Thorns | 4 | 60.050037426% |

With equal prior probability on the two exact lists, the posterior probability of Iron Thorns after observing exactly `k` failed openings and then acceptance is:

| Mulligans | Iron Thorns posterior |
| ---: | ---: |
| 0 | 31.683463534% |
| 1 | 66.771789624% |
| 2 | 89.698087341% |
| 3 | 97.417777597% |
| 4 | 99.391966571% |
| 5 | 99.859011341% |

Using the exact mulligan count as the only observation raises Bayes-optimal list classification accuracy from 50% to **73.095484669%**.

## Finding 2: almost every mulligan hand contains a list-specific name

Condition on the event that the player mulliganed.

For Vileplume, only **0.021373318%** of revealed mulligan hands consist entirely of names also found in the Iron Thorns list.

For Iron Thorns, only **0.008385744%** of revealed mulligan hands consist entirely of shared names.

So within this exact two-list comparison, a Vileplume mulligan contains at least one Vileplume-list-specific name with probability 99.978626682%, while an Iron Thorns mulligan contains at least one Iron-Thorns-list-specific name with probability 99.991614256%.

## Finding 3: coarse content raises classification accuracy to 80.02%

Across the entire setup sequence, a list-specific name is exposed before acceptance with probability:

- **13.856516394%** for Vileplume;
- **60.048025587%** for Iron Thorns.

Using only three kinds of evidence is enough to reach **80.024012806%** equal-prior classification accuracy:

1. a name unique to the Vileplume list was revealed;
2. a name unique to the Iron Thorns list was revealed;
3. no list-specific name was revealed before setup completed, while retaining the count of all-common mulligans.

That is a **30.024012806 percentage-point** gain over the uninformed 50/50 decision and a **6.928528137 point** gain over using exact mulligan count alone.

The extra count information inside the rare all-common sequences changes only the final decimal places because such hands are extraordinarily rare.

## Finding 4: the result is stable across all three published Iron Thorns lists

The same event also published Iron Thorns lists from Ryoya Fujii in 24th and Kohei Hamamichi in 29th, and both also contain exactly four Iron Thorns ex as their only Pokémon.

Treat the three Iron Thorns lists as an equal-weight family. Relative to the union of those three lists, the Vileplume list has 18 non-Basic copies whose names occur in at least one Iron Thorns variant. The three Iron lists have 17, 16, and 17 non-Basic copies respectively whose names occur in the Vileplume list.

The equal-prior coarse content accuracy becomes **80.024150865%**.

That is only **0.000138059 percentage points** above the fixed Kazuma-list comparison. The event-level conclusion is therefore insensitive to which of these three published Iron Thorns lists is used.

This does not make the model archetype-complete. It does show that the fixed-list result survives the observed list variation inside this event.

## Strategic interpretation

The setup transcript can constrain the opponent before Active and Benched Pokémon are turned face up.

This timing matters because setup still contains decisions before the game begins. The Advanced Player's Rulebook allows additional Basic Pokémon to be placed onto the Bench until the game starts. A player can therefore receive opponent mulligan information while some of their own setup choices remain open.

This gives matchup-dependent DCI and AMR a concrete pre-turn observation channel. The information can matter when an opening commitment should differ between the candidate matchups.

## Prior sensitivity

The 50/50 prior is a neutral information benchmark, not a metagame estimate.

A strong prior can absorb the same evidence without changing the best classification. For example, if Iron Thorns begins at 75% prior probability in this two-list toy comparison, the count-only 0/1 classification action remains Iron Thorns even after zero mulligans. The posterior still moves, while the observation does not cross the action boundary.

This is the same distinction established in `results/setup_information_value/`: evidence magnitude and decision value are separate.

## Validation and limitations

All probabilities are exact combinations and geometric sums. No Monte Carlo sampling is used.

The reproducer checks the fixed list counts, posterior values, conditional all-common probabilities, match-level exposure probabilities, and both classification accuracies.

This result compares two exact lists. Archetype-wide inference is harder because card counts vary between players and many apparently distinctive cards are shared by other decks. A stronger model would use a prior over a family of plausible lists and card-name count vectors rather than a single representative list per archetype.
