# Prize dependency cut sets: measuring correlated line collapse

## Question

When a deck has several strategic lines, how can we tell whether those lines are genuinely resilient to Prize cards or merely look diverse because they have different endpoints?

A useful representation is a Prize dependency cut set: a componentwise-minimal Prize configuration that disables every modeled line.

Implementation: `tools/prize_information_value.py`

Reproducer: `results/prize_dependency_cutsets/reproduce.py`

## Reliability representation

Model each strategic line as a conjunction of resource requirements.

For example:

`Line A = A available`

`Line B = B available`

The K1 player may choose any line that remains available after the Prize state is known. The whole line system therefore behaves like an OR over line-availability conditions.

A failure state is any grouped Prize state in which every line is unavailable.

A minimal failure state is a failure state for which reducing the number of Prized copies in any required direction restores at least one line. These minimal failure states are the system's Prize cut sets.

This representation separates two questions:

1. What is the structural order of the smallest correlated failure?
2. What probability mass do all failure states carry under the actual deck and Prize counts?

The first question is graph-like. The second is combinatorial.

## Finding 1: independent singleton alternatives have a size-2 cut set

Suppose:

- line A requires singleton A;
- line B requires singleton B.

Either line can operate without the other.

The only minimal grouped failure state is:

`{A: 1, B: 1}`

Both singletons must be Prized simultaneously to disable every line.

With 53 unknown cards and 6 initial Prizes, the exact all-lines-blocked probability is:

`1.088534107%`

K1 adaptive availability is therefore:

`98.911465893%`

The alternative line raises the minimum blocking order from one Prized singleton to two.

## Finding 2: a shared singleton connector creates a size-1 cut set

Now suppose:

- line A requires A and shared connector C;
- line B requires B and shared connector C.

The minimal cut sets are:

`{C: 1}`

and

`{A: 1, B: 1}`

The first cut set dominates the structural picture. One Prized copy of C disables every line immediately.

The exact all-lines-blocked probability is:

`12.323913600%`

K1 adaptive availability is:

`87.676086400%`

This is lower than the 88.679245283% probability that a single arbitrary singleton is unprized, because failure can also occur through the second cut set when A and B are both Prized while C remains available.

## Common-dependency ceiling

If every viable line requires a singleton C, no amount of downstream line diversity can make Prize-only K1 availability exceed the probability that C is unprized.

For the 53-unknown, 6-Prize state:

`P(C unprized) = 47 / 53 = 88.679245283%`

This is a hard structural ceiling until the common dependency is duplicated, recoverable, bypassed, or replaced.

More generally, if every line requires at least `r` unprized copies from a group of size `g`, then all lines fail whenever at least `g - r + 1` copies from that group are Prized. That shared group induces a cut set even when the downstream lines are otherwise disjoint.

## Finding 3: copy redundancy raises cut-set order

Suppose line A can use either of two A copies and line B can use either of two B copies.

The only minimal grouped failure state is:

`{A: 2, B: 2}`

All four modeled cards must be Prized to disable both lines.

With 53 unknown cards and 6 Prizes, the exact all-lines-blocked probability is:

`0.005122513%`

K1 adaptive availability is:

`99.994877487%`

This demonstrates two different ways to improve Prize resilience:

- add a strategically independent line;
- add copy redundancy inside a line.

The cut-set representation shows how these methods change the order and composition of correlated failure.

## Why raw line count is insufficient

Two decks can each have two apparent lines while having very different Prize robustness.

| Structure | Smallest cut-set order | All-lines-blocked probability |
| --- | ---: | ---: |
| Two independent singleton lines | 2 | 1.088534107% |
| Two lines sharing singleton C | 1 | 12.323913600% |
| Two independent two-copy lines | 4 | 0.005122513% |

Counting paths or reachable endpoints would give all three systems a line count of two.

The dependency structure carries the important information.

This is closely related to connector domination. A connector used by every line is more than a popular node in an associativity graph. It can be a reliability bottleneck whose Prize failure collapses the entire strategic system.

## Relationship to multi-Prized collapse

Earlier Prize-rescue work in the repository studies configurations where critical cards and their rescuers can be Prized together.

Prize cut sets generalize the structural side of that phenomenon.

A cut set can include:

- multiple endpoint cards;
- shared connectors;
- duplicated resource groups;
- future rescue components, if those components are represented as line requirements.

This suggests a unified reliability model in which line feasibility is represented first, then exact Prize probabilities are placed over the failure sets.

## Method

`minimal_failure_states()` enumerates grouped Prize counts from zero through each modeled group's copy count.

For every state it asks whether at least one line remains available.

It retains only failure states that are componentwise minimal. A failure state is removed when another failure state exists with no larger Prized count in any group and a strictly smaller count in at least one group.

`all_lines_blocked_probability()` then uses the multivariate-hypergeometric Prize distribution to calculate the exact probability that every line is unavailable.

The cut-set calculation is structural and independent of deck size. The probability calculation depends on the actual unknown-card and Prize counts.

## Validation

The reproducer verifies three representative structures:

- independent singleton alternatives;
- alternatives sharing a singleton connector;
- independent two-copy alternatives.

For each case it asserts the expected minimal cut sets.

It also compares the exact all-lines-blocked probability against closed-form combinatorial expressions.

## Limitations

The current line model treats availability as a conjunction of minimum unprized-copy requirements.

Real strategic lines can also fail because of:

- action-window contention;
- discard costs;
- Bench capacity;
- Active Spot requirements;
- lock effects;
- Energy timing;
- evolution timing;
- matchup constraints;
- connector consumption;
- card zones other than initial Prizes.

Those constraints can be added to the dependency model, although a fully general game-state cut-set calculation can become much larger.

The current cut sets are also grouped. A state such as `{A: 2}` means two copies from group A are Prized without identifying which physical prints or copies they are.

## Next useful work

The strongest extension is to derive cut sets from typed strategic lines rather than hand-written resource requirements.

A combined system could:

1. generate feasible lines from the typed access network;
2. extract the resources and action capacities each line depends on;
3. compute minimal shared failure sets;
4. overlay exact Prize probabilities;
5. distinguish Prize cut sets from lock, Bench, Supporter, and discard cut sets.

That would turn line-search output into an explicit robustness analysis instead of reporting reachability alone.
