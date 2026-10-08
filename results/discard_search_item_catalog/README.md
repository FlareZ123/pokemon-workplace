# BW-onward discard-search Item incidence

## Question

How common is the structural prerequisite for connector-as-payment substitution in the supplied card pool?

This result scans the local BW-onward database for Item cards whose text both:

- discards from the hand as a play/use gate; and
- searches the deck.

It is a **card-pool text scan**, not a complete paper-Expanded legality certification.

Implementation: `tools/discard_search_item_catalog.py`  
Regression: `results/discard_search_item_catalog/reproduce.py`

## Catalog

The scan finds ten distinct Item names:

| Item | Fixed discard gate | Payment class | Search deterministic? |
| --- | ---: | --- | --- |
| Computer Search | 2 | any cards | yes |
| Cram-o-matic | 1 | another Item | coin flip |
| Earthen Vessel | 1 | any card | yes |
| Electromagnetic Radar | 2 | any cards | yes |
| Fiery Flint | 2 | any cards | yes |
| Mysterious Treasure | 1 | any card | yes |
| Quick Ball | 1 | any card | yes |
| Secret Box | 3 | any cards | yes |
| Techno Radar | 1 | any card | yes |
| Ultra Ball | 2 | any cards | yes |

Among the nine deterministic entries:

- four have discard cost 1;
- four have discard cost 2;
- one has discard cost 3.

Computer Search and Secret Box are both ACE SPEC and therefore cannot coexist in one legal deck under their printed deck-construction rule.

## Payment-pair incidence

Every catalog entry is an Item.

For an Item whose gate accepts arbitrary cards, another visible connector is text-eligible payment. Cram-o-matic's narrower gate specifically requires another Item, so the same statement holds for this catalog.

Restricting to the nine deterministic connectors, distinct names, and excluding the impossible Computer Search / Secret Box ACE-SPEC coexistence pair leaves:

**70 directed connector-as-payment pairs**

at the payment-legality layer.

Examples include:

- Quick Ball -> Ultra Ball payment;
- Quick Ball -> Computer Search payment;
- Mysterious Treasure -> Ultra Ball payment;
- Earthen Vessel -> Computer Search payment;
- Ultra Ball -> Secret Box payment;
- Techno Radar -> Ultra Ball payment.

The arrow here means "left card can legally be discarded to the right card's gate if both are otherwise present." It does **not** claim the right-hand action strategically dominates the left-hand action.

## Why this matters

The Harto result is therefore an instance of a broad card-text structure.

Expanded contains many search Items that:

1. compete for the same visible hand resources;
2. can pay one another's discard gates;
3. have different target domains;
4. have different discard costs;
5. can change the strategic value of preserving another connector.

A graph that models only which targets each connector reaches misses this relationship.

The hand contains a payment graph in addition to an access graph.

## Connection to payment-substitution slack

`payment_substitution_slack/` gives the local theorem.

If weaker connector A costs `a`, stronger connector B costs `b`, B can directly satisfy the current endpoint, and A can legally pay B, then using A as payment reduces the no-critical-discard safe-fodder threshold from:

`a + b`

to:

`b - 1`.

The present catalog identifies card pairs where the **payment-legality prerequisite** can hold.

Whether the strategic dominance premise holds depends on the endpoint, target domains, board state, and future value.

## Important exclusions

This scan deliberately does not certify:

- current paper-Expanded legality or ban status for every card;
- same-name reprint equivalence;
- whether two non-ACE-SPEC cards can coexist under every other deck rule;
- whether the payment card is actually discardable in the current state;
- whether the played connector can satisfy the same endpoint;
- whether using the payment connector first would have created valuable draw or board state;
- Supporter-based search connectors;
- cards that discard from the deck rather than the hand;
- variable whole-hand discard effects.

Cram-o-matic is retained in the catalog but excluded from the deterministic-pair count because its search depends on a coin flip.

## Methodological implication

Connector analysis should track at least two directed relation types:

- **access edges**: what a connector can reach;
- **payment edges**: what visible cards can legally fund the connector.

The same card may be central in the first graph and expendable in the second.

That is a concrete reason why static associativity or connectivity scores can overvalue preserving every search card simultaneously.

## Next useful work

The next layer should combine payment edges with target-domain subsumption.

A pair becomes a stronger dominance candidate when the paid connector can satisfy every immediate endpoint the payment connector was meant to serve, or can satisfy a higher-priority endpoint while making the payment connector unnecessary.

That filter can turn the 70 payment-legal pairs into a much smaller set of strategically plausible substitution motifs.
