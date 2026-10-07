# Cost-before-search Trainer catalog

## Question

Which legal paper-Expanded Trainer cards expose an explicit hand-discard decision before the first printed deck-search instruction?

This is the broad card-pool surface where K0/K1 timing can matter to discard policy. If the player has not already inspected the deck, a selective payment can be chosen while replacement copies and search targets are still uncertain in the Prize cards.

Implementation: `tools/cost_before_search_catalog.py`  
Reproducer: `results/cost_before_search_catalog/reproduce.py`

## Conservative scan

The scanner uses the bundled Black & White-onward Expanded card database plus the repository's effective-legality classifier.

It retains legal Trainer prints when:

1. the rules text contains an explicit hand-discard instruction;
2. that instruction appears before the first literal `search your deck` clause.

The scan is intentionally conservative. It does not reinterpret effects whose printed search clause occurs first even if a separate timing clause might resolve at play time.

## Result

The current bundled paper-Expanded card pool contains:

- **54 legal prints** matching the conservative pattern;
- **16 distinct card names**;
- **23 distinct gameplay fingerprints** across those prints.

The 16 names are:

Adaman, Canari, Computer Search, Cram-o-matic, Crasher Wake, Earthen Vessel, Electromagnetic Radar, Fiery Flint, Larry's Skill, Mysterious Treasure, Peony, Quick Ball, Red's Challenge, Secret Box, Techno Radar, and Ultra Ball.

At name level, the payment surface is:

- 11 unrestricted selective discard names;
- 3 typed selective discard names;
- 2 whole-hand discard names.

The typed selective names are Adaman, Cram-o-matic, and Crasher Wake. Cram-o-matic is also the only cataloged name whose post-discard search is gated by a coin flip.

The whole-hand names are Larry's Skill and Peony.

## Information-policy interpretation

Selective payments are the main K0 policy hazard. The physical hidden state may determine which discard is recoverable, while a legal pre-search policy must choose using only information available before the deck inspection.

Whole-hand costs behave differently. There is no composition choice inside the payment because every remaining hand card is discarded. Hidden information can still change whether playing the Trainer is desirable, so action selection remains belief-dependent.

Typed selective costs sit between those cases. Their candidate set is narrower, while exact card identity can still matter when multiple eligible cards have different continuation value.

## Relationship to the local information-gap result

`k0_discard_reacquisition_bias/` quantifies the information advantage once a selective discard is forced onto endpoint-critical candidates.

The catalog shows that this is a reusable modeling concern across the Expanded card pool. Computer Search, Ultra Ball, Quick Ball, Mysterious Treasure, Secret Box, Red's Challenge, and several Energy or archetype-specific search cards all have the relevant literal ordering.

The Aichi clean Secret Box audit then supplies a useful qualification: a card can belong to this timing class while a particular deck-state distribution has enough discard slack that the information privilege produces no measurable immediate endpoint gain.

## Deliberate omission: conditional TAG TEAM text

Guzma & Hala is absent from this literal-order catalog because its printed Stadium-search clause precedes the later `When you play this card, you may discard 2 other cards` clause.

Repository transaction tooling already models that optional discard as part of the Supporter's resolution cost for the conditional Tool and Special Energy outputs. Determining the exact information boundary for this TAG TEAM wording requires a timing-specific rules treatment rather than silently folding it into a text-order regex.

This omission keeps the catalog reproducible and prevents the scanner from turning a semantic timing assumption into a card-pool fact.

## Methodological consequence

Search planners should annotate two separate facts:

- exact material state, including the real Prize allocation;
- the actor's information state at the payment deadline.

A transition can mutate the exact hidden world after a payment while the policy that selected that payment remains constrained by the preceding observation.

A useful next compiler layer would attach an explicit information deadline to each cost and search effect so that policy search cannot read future inspection results backward through the transition.
