# Information value of knowing the target's zone before sequencing Items

## Two distinct information advantages

This controlled experiment separates two benefits often conflated in deck optimization:

1. **Sequence-selection information:** knowing whether a singleton T is in the Prizes or deck before playing a *fixed* hand of Arc Phone and Trekking Shoes.
2. **Inventory-selection flexibility:** the hypothetical ability to choose a different four-Item hand after knowing that zone, rather than committing to one inventory beforehand.

The first is an actionable notion of K1 information under a fixed Item pool. The second is a theoretical upper bound on a much stronger decision privilege and is generally unavailable in ordinary play.

The state has six facedown Prizes and d unknown deck positions. T is uniformly distributed among Prize positions with prior p, or among deck positions with prior 1-p. All other hidden cards are inert F. Peonia, sufficient replacement F, and a fixed inventory of a Arc Phone and 4-a Trekking Shoes are held and playable. There is no separate deck-search cost in this information-only experiment.

## Exact within-inventory K1 premium

For each fixed Item inventory, compute two policies:

- **Before zone information:** optimize one posterior-aware sequence; observing card text effects updates the state normally.
- **After free zone information:** reveal whether T is Prized or in the deck *before* choosing the first action, then optimize the resulting conditional sequence.

For mixed inventories a=1,2,3, the two legal modes differ by one Prize position versus one deck position. Their actual coverage pairs are recorded in [the two-dimensional phase study](../arc_peonia_two_dimensional_phases/).

If d>2(4-a), the fixed-inventory information gain is exactly

\`I_fixed(a,d,p)=min[p/6, (1-p)/d]\`.

Otherwise, or if a=0 or a=4, it is zero under these assumptions: either the action inventory has just one efficient mode, or the deck is small enough that the Prize-heavy mode also sees every reachable deck card.

The peak premium for each eligible mixed inventory occurs where

\`p/6=(1-p)/d\`, i.e. \`p=6/(d+6)\`,

and the maximum equals \`1/(d+6)\`.

For d=46, the uniform-location prior is p=6/52=3/26; every mixed inventory a=1,2,3 gains exactly **1/52 = 1.923077 percentage points** from a free upfront zone revelation, while pure 0-Arc and 4-Arc inventories gain zero. This benefit comes solely from selecting between two action sequences, with no additional cards or change in physical resources.

## Inventory-selection information ceiling

Now consider a stronger thought experiment in which the player can choose the initial four-Item inventory itself *after* learning T's zone. At d=46:

- A fixed inventory selected before zone revelation has global optimum
  \`V_prior(p)=max[p/2+8(1-p)/46, p+2(1-p)/46]\`.
- Selecting the best inventory separately in each zone has upper bound
  \`V_choose_after(p)=p*1+(1-p)*8/46\`.

The gap is

\`I_inventory(p)=min[p/2, 6(1-p)/46]\`.

It peaks at p=6/29, with a **3/29 = 10.344828 percentage point** hypothetical information advantage: fixed optimal target access is 7/29 and full after-zone item selection yields 10/29.

This 3/29 comparison is *not* the value of a normal deck search. It requires a subsequent inventory-choice opportunity and assumes whichever four Items would be most useful can be obtained with no resource, timing, draw or Supporter penalty. A real Pokémon TCG player typically has to work with cards already drawn.

## Exact adaptive checks

\`tools/arc_peonia_zone_information_premium.py\` compares the rational coverage-pair formulas against the independent full physical-world, observation-respecting Bellman solver \`tools/arc_peonia_mixed_prior.py\` for d=1..8 and d=46, all five Item inventories, and a rational grid containing both structural thresholds. It separately checks the maximum gain and mixed-inventory no-cost information formula.

The Windows regression workflow verifies these exact results. Reproduce with \`python tools/arc_peonia_zone_information_premium.py\`.

## Interpretation and next investigation

Knowledge changes actions only if different observable states favor different decisions. Multiple individually useful sequencing options create a genuine information premium, while a single dominant option can make that same information economically worthless under the chosen objective.

The calculations deliberately leave out the **physical cost** of becoming K1: a real deck search may require an Item, discarded cards, a once-per-turn Supporter, or a usable search target, and it physically changes deck composition. The result is an information-only upper bound for this subsystem. A next study should add a physically payable search before the first Item action and distinguish the information component from thinning and discarded-resource effects.
