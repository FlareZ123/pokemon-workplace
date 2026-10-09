# How much does another paid Quick Ball add alongside Nest and VIP?

## Research question

The prior [same-pool Item-mix study](../gothitelle_adaptive_item_mix/)
assigned free Basic-search capacity to Nest Ball and Battle VIP Pass
alongside one Sky-paying Quick Ball. This extension allows additional
first-turn Quick Ball copies, each needing its own distinct approved
discardable hand card.

The resulting search capacity is:

```text
1 + min(QuickSeen-1, ApprovedDiscardSeen)
  + NestSeen + 2*VIPSeen
```

The first Quick Ball always discards Sky Field as the delayed
Teleport Room payload. Every additional Quick Ball uses one
distinct independently approved discard card. This conservative
allocation never sacrifices Gothita, Gothitelle, Rare Candy,
additional search Items, or another protected singleton to pay.

Model: [`tools/gothitelle_paid_adaptive_items.py`](../../tools/gothitelle_paid_adaptive_items.py)  
Independent physical-label oracle: [`reproduce.py`](reproduce.py)

## Example and exact result

The disjoint 60-card hypothetical population includes Gothita3,
Gothitelle2, Rare Candy4, eight other ordinary Basics,
Quick Ball4, Sky Field2, Nest Ball4, Battle VIP Pass4,
12 separately approved discard cards, and 17 filler.

The setup goal is the same: from a legal first seven cards,
six random Prizes, and one natural draw per personal turn,
assemble four ordinary Basics plus Gothita by turn one,
pay Sky Field to Quick Ball, and find the Stage2/Rare Candy
evolution pair by turn two.

| Enabled Item policies in the same population | Probability per opening attempt |
| --- | ---: |
| One Sky-paying Quick Ball only | 0.001573353% |
| Additional paid Quick Balls only | 0.001826711% |
| Nest/VIP plus one Sky-paying Quick | 0.066523496% |
| **Nest/VIP plus additional paid Quick Balls** | **0.069787405%** |

The extra paid Quick capacity improves the Nest/VIP setup
by **0.003263909 percentage points**, or **4.906401%
relative** to its prior 0.066523496% rate.

When Nest/VIP are excluded, additional paid Quick capacity
improves one-Quick access by only 0.000253358
percentage points in the same population.

The difference in marginal gain is **+0.003010551
percentage points**. Thus a paid extra Quick Ball can be
more valuable once other search Items are available to
handle parts of the same board assembly. Its effective
value depends on how many additional Basic targets remain
missing after those other Items are considered.

## Payment sensitivity

Replacing otherwise inert filler with the indicated
number of independently approved payment cards, while
keeping all other category counts fixed:

| Approved payments | Increment from extra Quick after Nest/VIP (percentage points) |
| ---: | ---: |
| 0 | 0 |
| 4 | 0.001158705% |
| 8 | 0.002246675% |
| 12 | 0.003263909% |
| 16 | 0.004210408% |
| 20 | 0.005086170% |

For this eight-card observation window, the incremental
probability is **strictly increasing and quadratic concave**
in approved payment copies, with constant negative second
finite difference for each four-copy step.

This contrasts with the linear payment-count dependence
in [`gothitelle_two_quick_joint_board`](../gothitelle_two_quick_joint_board/),
which prohibited Nest/VIP access. The larger search
portfolio changes which paid-hand configurations can
complete the first-turn Basic requirement.

## Exact method and validation

The policy integrates random seven-card opening hands, six
random Prize cards, first-turn natural draw, one or more
physically unprized Basic searches, and the second-turn
natural draw. Stage2/Candy is required by turn two, and
searched Basic copies are removed from the deck before
the second-turn draw.

The joint Prize-count kernel considers Gothita and other
Basic targets simultaneously. Multiple paid Quick copies
consume independently observed approved-discard copies.
Unused extra Quick Balls create no additional search
capacity.

An independent reference uses actual labeled copies in
two small populations (13 and 14 cards), enumerating
all opener sets, Prize subsets, first-turn draws, physical
search targets, final draw identities, and separate
payment availability. A zero-Prize control and
zero-payment/one-Quick limits verify the policy boundary.

## Strategic interpretation and limitations

Discard costs must be treated as **typed and state-dependent
resources**. Other Items can create opportunities for a
second paid Quick Ball to cross a Basic-search threshold that
the second Quick Ball could not cross alone.

The approved-discard category is exogenous, and the model
does not infer DCI from actual card identities. Several real
cards outside that category might become disposable
after their effects resolve, while cards in the category
might become protected in another game state.

The study conditions on an already-compatible opponent
Collapsed Stadium/Ninetales lock state, assumes Gothita
survives, and holds the future two required Bench entrants
outside the sample. This is a narrow exact access result.
No matchup win rates or optimized deck construction
are inferred.

## Next useful experiment

Replace static approved-discard copies with individual
cards whose marginal utility depends on held Stage 2,
Rare Candy and already available search outs.
Calculate whether paying for an extra Quick Ball is
worth surrendering a redundant piece or an otherwise
necessary next-turn target.
