# Harto Miki Raichu/Electrode: two-Gladion redundancy under Prize uncertainty

## Question

The first belief-weighted Raichu result treated the visible Gladion as the only rescue copy.

What changes when Harto Miki's actual **two-Gladion package** is represented, so the backup copy can itself be in deck or Prizes?

The visible Gladion becomes much safer to discard, but not perfectly safe.

Regression: `results/raichu_two_gladion_belief_discard/reproduce.py`

## Exact grouped Prize belief

At the representative action snapshot:

- one Gladion is visible in hand;
- Alolan Raichu is unseen;
- the second Gladion is unseen;
- 52 cards remain unseen;
- 6 of those 52 are Prizes.

The grouped hypergeometric belief over the two relevant unseen cards is:

| Alolan Raichu | Backup Gladion | Probability |
| --- | --- | ---: |
| deck | deck | 78.054299% |
| deck | Prized | 10.407240% |
| Prized | deck | 10.407240% |
| Prized | Prized | **1.131222%** |

The last row is the multi-Prize-collapse state.

## Physical continuation policy

Every one-card Quick Ball discard is mechanically legal.

The relevant continuation depends on the hidden world:

- **Raichu in deck:** Quick Ball -> Crobat V -> exact Dark Asset witness draws Alolan Raichu.
- **Raichu Prized, visible Gladion preserved:** play the visible Gladion and retrieve Alolan Raichu.
- **Raichu Prized, visible Gladion discarded, backup Gladion in deck:** exact Dark Asset witness draws the backup Gladion, then that copy retrieves Alolan Raichu.
- **Raichu and backup Gladion both Prized, visible Gladion discarded:** no modeled rescue continuation remains.

The Gladion branches use literal physical Prize exchange and consume the ordinary Supporter window.

## Main result

| Quick Ball discard | Belief-weighted continuation safety |
| --- | ---: |
| A | 100.000000% |
| B | 100.000000% |
| C | 100.000000% |
| Visible Gladion | **98.868778%** |

The visible Gladion's failure probability is exactly the probability that both Alolan Raichu and the backup Gladion are Prized:

**1.131222%**.

This turns the previous one-copy safety deficit from 11.538462% into a much smaller correlated-collapse risk.

## DCI interpretation

Using the same illustrative local DCI scores as the first result:

| Card | Illustrative DCI |
| --- | ---: |
| A | 0.6 |
| B | 0.9 |
| C | 0.7 |
| Visible Gladion | 1.0 |

If endpoint preservation is a hard K0 requirement, the visible Gladion is still excluded because its safety is below 1. The robust K0 choice remains **B at 0.9**.

With exact Prize composition known, the visible Gladion is safely expendable in every world except the double-Prized collapse state. The expected DCI of the best K1-safe choice becomes **0.998869**, an **+0.098869** gain over the K0 robust choice.

Again, those DCI values are illustrative. The durable point is that redundancy changes the posterior risk attached to a discard witness, while exact information changes whether that risk must be carried at all.

## Multi-Prize collapse as a discardability phenomenon

This result gives multi-Prize collapse a direct DCI interpretation.

A visible rescue card can look redundant because another copy exists in the decklist. That redundancy is conditional on the backup copy being materially reachable.

Before K1, the relevant question is not simply:

`How many Gladion are in the 60-card list?`

It is:

`In what fraction of hidden Prize worlds does at least one rescue route survive after this exact discard?`

For this snapshot, one backup Gladion reduces the hidden failure set to the joint event where the target and backup are both Prized.

## Relation to the first belief-weighted result

`raichu_belief_weighted_discard/` used a one-rescuer abstraction and found visible Gladion discard safety of 46/52 = 88.461538%.

This two-copy extension uses the actual package and raises safety to 98.868778%.

The difference is evidence that redundancy should be represented inside the belief state and continuation graph rather than encoded as a fixed lower DCI for "extra copies."

## Validation scope

The regression uses the repository's grouped `PrizeBelief` for exact six-Prize world weights.

Each grouped world is then projected into a minimal physical state containing the relevant deck/Prize identities. That physical projection validates reachability and literal Gladion movement; filler Prize identities are omitted because they do not affect the tested endpoint.

Dark Asset branches are existential exact-draw witnesses. The reported percentages are therefore probabilities that an endpoint-preserving continuation **exists** across hidden Prize worlds. They are not probabilities of naturally drawing the needed card during a real turn.

## Limits

This is still a narrow endpoint model.

It does not include:

- targeted access to the backup Gladion through Computer Search or Forest Seal Stone;
- ordinary Prize-taking;
- both Gladion copies being initially unseen;
- alternative rescue cards;
- Supporter contention with other required Supporters;
- the future strategic value of retaining a redundant Gladion;
- full turn-level probability of the Dark Asset hit.

The 1.131222% collapse probability is exact for the stated 52-unseen-card, six-Prize snapshot and the two relevant singleton identities.

## Next useful work

The next step is to replace existential backup access with **timed access**.

When the visible Gladion is discarded and the backup is in deck, its mere presence does not guarantee that Dark Asset or another connector reaches it before the rescue deadline. Combining this belief model with the repository's timed Prize-rescue and typed connector layers would separate:

1. redundancy exists;
2. redundancy is not Prized;
3. redundancy is actually accessible in time.
