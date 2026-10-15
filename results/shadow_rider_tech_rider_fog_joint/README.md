# Shadow Rider versus Iron Thorns: Fog Crystal connector contention for two Basic Psychic targets

## Question

The single-tech initial access study finds 43.311704% of Basic-valid initial-seven arrangements have a singleton Wobbuffet or Flutter Mane directly or via a Fog Crystal search with the target still in the deck. How often can that opening also obtain **at least one Shadow Rider Calyrex V**, while respecting the fact that each Fog Crystal searches for only one target?

This is an exact constrained turn-inventory calculation using the two [verified experimental full 60s](../decks/shadow-rider-single-psychic-thorns-tech/). It does not assert either Pokémon is Active or ready to attack.

## Physical model

The hypothetical 60-card list contains:

- 1 singleton Basic Psychic anti-Thorns tech, either Flutter Mane or Wobbuffet;
- 3 Shadow Rider Calyrex V, the central Basic attacker;
- 10 other Basic Pokémon;
- 4 Fog Crystal Items;
- 42 other cards.

Randomly sample a 7-card hand and six Prize cards without replacement. Reject openings with no Basic. Demand access to **both** target classes from hand, or by searching one missing class from the remaining deck for each Fog Crystal consumed from the initial hand.

For each accepted initial hand, the required search count is the number of target classes absent from that hand: 0, 1, or 2. The hand must contain at least that many Fog Crystals. Every missing target must remain in the unprized deck, and at least one of the three Riders must remain if the Rider class is missing. This enforces distinct use of search sources for distinct targets.

The exact enumerator partitions the hand into five disjoint categories (tech, Rider V, other Basics, Fog Crystal, other cards), weights each hand category with multivariate hypergeometric counts, and explicitly enumerates the six-Prize distribution of the remaining singleton tech and Rider copies. It sums exact integer world counts and only divides at the end.

## Results conditional on Basic-valid opening seven

| Connector uses needed | Both target classes accessible through that route |
| --- | ---: |
| 0, both naturally in hand | 3.784103% |
| 1 Fog Crystal | 14.323005% |
| 2 Fog Crystals | 2.965589% |
| **Any feasible route** | **21.072697%** |

As expected, a requirement to access **two** strategically distinct Basic classes under finite search resources is much tighter than a singleton's 43.311704% stand-alone access. This illustrates connector contention, though the comparison adds a second strategic goal and must not be interpreted as the causal cost of using a Fog Crystal.

## Validation

- Implementation: [tools/shadow_rider_tech_rider_fog_joint.py](../../tools/shadow_rider_tech_rider_fog_joint.py).
- Independent [single-file exhaustive oracle](reproduce.py) enumerates fully labeled hands and Prize assignments for three separate toy decks. It agrees exactly with the closed combinatorial state enumerator.
- The regression checks three Shadow Rider Calyrex V, four Fog Crystal and the Basic/Psychic typing of Shadow Rider V, Flutter Mane and Wobbuffet using exact print IDs.

## Practical boundaries

The 21.07% figure requires an independently valid initial seven, but excludes the first natural turn draw, opponent mulligan bonus cards, Mysterious Treasure, Quick Ball, Tapu Lele Supporter searches, Forest Seal Stone, and further gameplay. It presumes a Fog Crystal in hand can be used to fetch its designated target. The model does not allocate search to alternative key demands such as Psychic Energy, nor track how retrieved targets are moved into the Active Spot.

Fog Crystal's search to hand is separate from a starting-Active choice. Even if both target classes are accessible, the model does not show a legal sequence enabling the counter's Active-only lock at the needed moment. Wobbuffet also disables Radiant Eternatus while Active, unlike Flutter Mane, as shown in the [position-aware source regression](../wobbuffet_flutter_thorns_continuation/).

These are exact **access prerequisites under a deliberately restricted policy**, useful for identifying bottlenecks before testing real full-game policies. They do not estimate the probability of winning or indicate that either deck improves on the tournament champion.
