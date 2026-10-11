# An accessible Trekking Shoes can replace the final Arc Phone

## Pointwise source-mask result

Compare four labeled prospective Item slots in a one-target Peonia recovery model:

- Package A: four Arc Phone.
- Package B: three Arc Phone plus one Trekking Shoes, replacing only the fourth slot.

A binary mask determines which of the four candidate Item slots is **already available**. Every other hidden card has inert filler behavior; unavailable Items cannot become playable later. One Peonia and sufficient replacement filler are held. The one valuable singleton is either certainly Prized among n facedown Prize positions (K1), or uniformly distributed among n Prize and d deck positions (uniform K0), with d>=2.

Let a be the accessible count among the first three Arc Phone slots and x be 1 if the replacement slot is accessible and 0 otherwise.

**K1, certainly Prized:** Every single mask produces exact equality:

\`P(B|mask,K1) = P(A|mask,K1) = min(n,3+max(0,a+x-1))/n\`.

When x=1 and at least one Arc is available, Shoes takes the final Arc-displaced Prize card directly from the deck top, replacing the observation that an additional Arc would have provided. When the substituted slot is inaccessible, the action inventories are identical. This equality therefore holds under **any probability distribution over masks** that is shared between the packages.

**Uniform K0:** Every single mask has

\`P(B|mask,K0)-P(A|mask,K0) = x/(n+d)\`.

Shoes can access one additional *initial deck position*, while the optimal total number of equiprobable target locations covered increases by one whenever the substituted slot is available. The formula concerns the uniform target-location prior. With a nonuniform Prize/deck prior, an adaptive planner may choose a deck-heavy line that trades away Prize coverage to see two extra deck positions, so the **exact** one-position increment does not automatically carry over.

## Exact sampled-source overlay

Under a deliberately separated access model, the four labeled candidate Item slots are placed in a uniformly shuffled population of 57 positions with 53 inert source positions. A random h-subset of those positions is accessible. Target-location uncertainty is independent of this source mask, and there is no subsequent Item acquisition. Thus

\`P(x=1) = h/57\`.

For K1, the two packages continue to have exactly equal expected success, regardless of h.

For a uniform K0 target among six Prizes and 46 deck positions, the **expected absolute improvement** of Package B over Package A is

\`E[P(B)-P(A)] = h/(57*52)\`.

| Accessible source positions h | Expected absolute advantage |
|---:|---:|
| 7 | 7/2964 = 0.236167 percentage points |
| 20 | 20/2964 = 0.674764 percentage points |
| 40 | 40/2964 = 1.349528 percentage points |
| 52 | 52/2964 = 1.754386 percentage points |

This is an *access projection*, with Peonia and payment assumed available and all nonavailable source copies abstracted as inert. It is not a sample of actual live draws which can acquire additional Arc Phone, Shoes, or Supporters.

## Independent physical verification

\`tools/arc_peonia_mask_substitution.py\` enumerates every mask and runs both separately developed exact physical-world adaptive solvers:

- 672 n=1..6, d=2..8, 16-mask cases check K1 equality and uniform-K0 increment.
- 18 population h cases check the exact full hypergeometric mask mixture and equality / expected increment.

All 690 identities use \`Fraction\` arithmetic. Reproduce with \`python tools/arc_peonia_mask_substitution.py\`, also executed by the Windows GitHub Actions workflow.

## Limits and implications

This establishes a robust *within-subsystem* K1 substitution equivalence and a strict K0 improvement under equal starting access. Real deck changes can change hand/Prize distributions, Item search links, Bench cost, opportunity costs and opponent lock exposure. Trekking Shoes may draw another actionable card, which is beyond this static-mask experiment.

The generalized lesson is that an identical K1 outcome under uncertain availability need not imply equal value under partial information about whether the target remains in the deck. Follow-up work should allow the access mask to reveal target-location information and should model newly drawn usable Trainers physically.
