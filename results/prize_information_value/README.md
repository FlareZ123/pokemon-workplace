# Value of initial Prize information: K0 to K1

## Question

How much strategic value can the first full deck search create purely by revealing the initial Prize configuration?

The answer can be substantial when a deck has multiple lines that depend on different fragile resources and the player can choose between those lines after learning which cards are Prized.

Implementation: `tools/prize_information_value.py`

Reproducer: `results/prize_information_value/reproduce.py`

## Rules and concept basis

The Advanced Player's Rulebook states that when a player searches their deck, they may look through its contents before choosing the searched card or cards. With accurate knowledge of the decklist and all already-visible zones, the player can infer which cards are absent from the remaining deck and therefore in the face-down Prize cards.

`resources/human_concepts.md` proposes the K0/K1 abstraction:

- K0: the player has not yet searched the deck and does not know the exact Prize composition.
- K1: the player has searched the deck and can infer the Prize cards.

This result treats that abstraction as a decision-information problem and quantifies one part of its value.

## Model

Suppose the player has `U` currently unknown cards split between the deck and `P` Prize cards.

For an ordinary 60-card game immediately after a seven-card opening hand has been observed, with no other known non-Prize cards removed from the unknown population:

`U = 53`

and

`P = 6`.

Named card groups are modeled explicitly. Everything else is pooled into filler. A strategic line can require a minimum number of unprized copies from one or more groups.

For each grouped Prize state `s`, the tool calculates its multivariate-hypergeometric probability exactly.

Each line has a utility `u_l(s)`, which is its supplied utility when its availability requirements are satisfied and zero otherwise.

K0 must choose one line before learning the Prize state:

`V_K0 = max_l E[u_l(s)]`

K1 may choose after learning the Prize state:

`V_K1 = E[max_l u_l(s)]`

Define the value of Prize information as:

`VPI = V_K1 - V_K0`

Since the maximum is taken after observing the state at K1, `VPI >= 0` for this model.

The tool also reports the probability mass of states where state-adaptive K1 choice strictly improves on the best fixed K0 line.

## Finding 1: two independent singleton lines make Prize knowledge highly valuable

Consider two equally valuable alternative lines:

- line A requires singleton A to be unprized;
- line B requires singleton B to be unprized.

With 53 unknown cards and 6 Prizes, either fixed line is live with probability:

`47 / 53 = 88.679245283%`

At K0, choosing either line therefore gives 88.679245283% Prize-state availability.

At K1, the player can use A when A is live and B when A is Prized but B is live. The adaptive policy fails only when both singletons are Prized.

Result:

| Policy | Availability |
| --- | ---: |
| Best fixed K0 line | 88.679245283% |
| K1 adaptive choice | 98.911465893% |
| Value of Prize information | +10.232220610 percentage points |

This gain comes entirely from information and adaptation. No Prized card is recovered.

## Finding 2: a third independent singleton line has diminishing but real value

With three equal alternative lines, each gated by a different singleton:

| Policy | Availability |
| --- | ---: |
| Best fixed K0 line | 88.679245283% |
| K1 adaptive choice | 99.914624776% |
| Value of Prize information | +11.235379493 percentage points |

The adaptive policy fails only when all three singleton line-enablers are Prized.

The second line contributes most of the information-enabled resilience. A third line pushes adaptive availability close to 100% under this narrow Prize-only model.

## Finding 3: a shared singleton connector destroys most diversification

Now consider two alternatives:

- line A requires singleton A and singleton connector C;
- line B requires singleton B and the same singleton connector C.

Each fixed line is available only if both of its required singletons are unprized:

`78.447024673%`

After K1, the player can choose between A and B, but both lines still fail whenever C is Prized.

Result:

| Policy | Availability |
| --- | ---: |
| Best fixed K0 line | 78.447024673% |
| K1 adaptive choice | 87.676086400% |
| Value of Prize information | +9.229061726 percentage points |

Compare the K1 availability:

- two independent singleton alternatives: 98.911465893%;
- two alternatives sharing singleton C: 87.676086400%.

This is a correlated-collapse effect. Apparent line diversity does not create strong Prize resilience when the alternatives depend on the same fragile connector.

This gives a quantitative companion to connector-domination and multi-Prized-collapse reasoning. An optimizer should care about dependency overlap between lines, not only how many nominal lines exist.

## Finding 4: internal copy redundancy reduces the marginal value of K1 information

Consider two alternative groups A and B with two copies each. Each line requires at least one unprized copy from its own group.

A fixed line already succeeds unless both copies of its group are Prized:

`98.911465893%`

K1 can switch between the two groups and fails only if all four modeled cards are Prized:

`99.994877487%`

Result:

| Policy | Availability |
| --- | ---: |
| Best fixed K0 line | 98.911465893% |
| K1 adaptive choice | 99.994877487% |
| Value of Prize information | +1.083411594 percentage points |

K1 information is most valuable when individual lines are Prize-fragile and the deck contains genuinely different alternatives. Copy redundancy inside each line already handles much of the Prize risk before information is used.

## Strategic consequence: first-search timing can matter before card access does

A deck search can have strategic value even when the searched card is not the main reason for the action.

If an irreversible choice between lines must be made before the first deck search, the player operates at K0 for that decision.

If a full deck search occurs first, the player can choose with K1 Prize knowledge.

Examples of irreversible or costly commitments can include:

- spending a unique connector on one target;
- choosing one Supporter line for the turn;
- filling a constrained Bench slot;
- discarding a payload or protected resource;
- committing Energy to one attacker;
- selecting an ALS branch that cannot be cheaply reversed.

A simulator that records only the card fetched by a search effect can miss this informational consequence. The first-search event can change the policy even if the search target itself is strategically ordinary.

## Relationship to other repository work

This result complements several existing lines of research:

- `results/typed_access_network/` models whether a line is mechanically reachable under zone, timing, Bench, and lock constraints.
- `results/supporter_connector_temporality/` models whether a connector preserves the action window needed to use the target.
- the Prize-rescue results model recovery and collapse when important cards are actually Prized.

Prize information value is a separate layer. It asks whether knowing the Prize state changes which reachable line should be selected before any rescue is attempted.

A stronger future state model should combine all of these layers.

## Validation

The reproducer checks each reported result against closed-form combinatorial expressions.

It also performs an independent exhaustive validation on a labeled eight-card population with two Prize cards. Every possible labeled Prize subset is enumerated, collapsed into grouped states, and compared against the tool's multivariate-hypergeometric state probabilities.

The grouped support and every state probability match to floating-point precision.

## Limitations

This is a Prize-state decision kernel rather than a game simulator.

The model assumes:

- the player knows the relevant deck composition exactly;
- the search reveals the full remaining deck contents;
- the player can infer the Prize state correctly;
- line availability depends only on the modeled Prize groups;
- line utilities are fixed when available;
- the cost and timing of reaching K1 are external to this calculation.

The default `U = 53` is appropriate for a standard seven-card observed opening before additional known non-Prize cards alter the unknown population. If extra cards are known to be outside the Prizes, or relevant cards have moved between visible zones, callers should supply the correct current unknown-card count and group sizes.

Real lines can also differ in damage, tempo, matchup value, DCI, AMR, Supporter contention, Bench cost, lock exposure, and future resource consumption. The utility parameter can represent some of that asymmetry, but those utilities need evidence from a richer game model.

## Next useful work

The highest-value extension is to add a first-search information state to the typed access model.

A combined state should track:

- whether exact Prize information has been acquired;
- which irreversible line commitments have already occurred;
- which connectors remain available;
- whether the first search itself consumes a strategically important connector;
- the actual grouped Prize state after K1.

That would allow a search algorithm to value a line for both material card access and the policy improvement created by Prize knowledge.
