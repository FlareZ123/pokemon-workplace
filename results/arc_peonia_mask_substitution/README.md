# An accessible Trekking Shoes weakly dominates the final Arc Phone

## Resource-availability question

Previous results show four Arc Phones and three Arc Phones plus one Trekking Shoes have identical access to a singleton known to be Prized, provided all four Items are playable. Does this equality survive *missing* Items caused by uncertain natural access, including when the replacement Shoes is itself inaccessible?

**Yes, for every accessible Item subset** in the source-isolated model. The stronger result is pointwise, so it applies under arbitrary probability distributions over item-access masks.

## Fixed-mask theorem

Compare packages with four labeled Item slots:

- Old: A1,A2,A3,A4, all Arc Phone.
- New: A1,A2,A3,S4, replacing only A4 with Trekking Shoes.

Hold Peonia and one expendable filler for its hand replacement payment. One valuable singleton T exists, all other hidden cards are inert filler; cards outside the initially available Item subset are unavailable as actions. The initial deck has at least two positions.

For any binary access mask m of those four slots, let a be the number of held, usable Arcs among A1..A3 and x indicate whether slot 4 is accessible.

Under **K1**, T is uniformly Prized across n facedown Prize positions, and the deck is known filler. The two packages achieve exactly the same optimal T-retrieval probability:

\`P_K1(old|m) = P_K1(new|m) = min(n,3+max(0,a+x-1))/n\`.

The second expression remains valid for x=1,a=0 because Shoes without Arc does not touch the hidden Prize positions; when x=1 and a>=1, Shoes can acquire the top card after the final Arc exchange, offsetting the removed Arc. The equality is independent of the distribution of masks.

Under **K0** with T uniformly distributed among n Prize and d deck positions, d>=2:

\`P_K0(new|m)-P_K0(old|m) = x/(n+d)\`.

If x=0, the packages are identical. If x=1, Shoes can access one additional original deck position, without sacrificing any Prize coverage. This is one extra initial target location among the n+d equiprobable locations.

For an arbitrary zone prior p=P(T Prized), uniform conditional positions in each zone, the exact pointwise gain becomes

\`P(new|m,p)-P(old|m,p) = x*(1-p)/d\`.

This requires the access mask to carry no additional information about the target location. A source-aware planner could update p if obtaining a particular Item were correlated with target location.

## Hypergeometric natural-access projection

Assume the four labeled Item slots occupy random positions among an independent 57-location source population, with 53 other inert slots. Let h locations be uniformly visible/usable, and leave target location uncertainty independent of that source population. Then

\`P(S4 accessible) = h/57\`.

Averaging the exact pointwise identity over all 16 access masks yields

\`E[P(new)-P(old)] = (h/57)*(1-p)/d\`.

For n=6,d=46 and the uniform target prior p=6/52:

\`E[P(new)-P(old)] = h/(57*52)\`.

| h accessible source positions | Absolute improvement in target retrieval |
|---:|---:|
| 7 | 7/2964 = 0.236167% |
| 20 | 20/2964 = 0.674764% |
| 40 | 40/2964 = 1.349528% |
| 52 | 52/2964 = 1.754386% |

Under K1 (p=1), the expected gain is identically zero for every h. The stochastic source constraint does not destroy the pointwise equivalence. Under K0, the substitution is weakly positive and generally strictly improves target access.

## Exact verification

\`tools/arc_peonia_mask_substitution.py\` enumerates all 16 availability masks, compares the independently implemented physical K1 and K0 dynamic programs, and also compares posterior-weighted mixed-zone physical decisions.

- K1/K0: n=1..6, d=2..8, 16 masks per state, **672** exact mask configurations.
- Mixed prior: p in \`{0,1/10,1/2,9/10,1}\`, n=6,d=8 and 16 masks, **80** exact configurations.
- Natural-access projection: nine h values and three prior values, **27** exact hypergeometric identities.

The test checks **779** independently evaluated identities with \`Fraction\` arithmetic. Run \`python tools/arc_peonia_mask_substitution.py\` or inspect the shared Windows CI workflow.

## Scope of the conclusion

This is a pointwise *acquisition-probability* dominance under equal candidate accessibility, a single target, filler-only other card effects, and Peonia already in hand with feasible payment. Actual deck construction changes starting hands, Prize allocation, Item search chains and drawn Item reuse. Trekking Shoes may draw an additional usable resource, and an inaccessible Arc could later be recovered, violating the static-access assumption. The model also omits Item lock, sequencing time, Supporter contention, alternative targets and the opportunity cost of consuming Shoes.

The reliable design principle is narrower: in this Prize-recovery subsystem, replacing the final Arc with a Shoes does not sacrifice the known-Prized rescue axis under a matched Item-access mask. One can then evaluate Shoes' additional deck access and its other game functions using richer models.
