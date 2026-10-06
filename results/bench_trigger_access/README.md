# Setup-conditioned Bench-trigger access: zone and role semantics

## Question

How much can a Pokémon-access graph overstate access to a Basic Pokémon's **hand-to-Bench Ability trigger** when it ignores two facts at once?

1. A trigger Basic that is the only Basic in the accepted opener must become the starting Active, so that physical copy is no longer in hand for its trigger.
2. A connector that puts the target directly from the deck onto the Bench does not satisfy wording that requires playing the Pokémon **from hand** onto the Bench.

This result joins setup-role contention to a prize-aware connector model.

Implementation: `tools/bench_trigger_access.py`  
Independent labeled-state reproducer: `results/bench_trigger_access/reproduce.py`

## State process

The deck is partitioned into trigger Basics, other ordinary Basic starters, **hand connectors** that are idealized deterministic non-Supporter effects moving a trigger Basic from deck to hand, **direct-Bench connectors** that put a trigger Basic directly from deck onto the Bench, and filler.

The exact sequence is:

1. draw the opening hand;
2. condition on at least one ordinary Basic being present;
3. choose the starting Active to preserve trigger Basics when possible;
4. set Prize cards from the remaining deck;
5. expose a configurable number of later random draws;
6. test whether one hand-to-Bench trigger activation is available.

The default examples use one later random draw. No search, draw engine, mulligan bonus cards, or other effects are silently added.

## Nested access definitions

The same exact state is evaluated four ways.

**Naive Pokémon access** counts a trigger Basic already seen in the opening/draw cards as usable. Either connector class also counts if a trigger Basic remains searchable in the deck.

**Zone-aware access** stops crediting direct-Bench connectors. Only a connector that moves the target into hand can enable the required hand-to-Bench transition. The opening-copy Active-role conflict is still ignored.

**Role-aware access** removes a trigger Basic consumed as the mandatory starting Active. A later-drawn trigger Basic still counts normally, and a hand connector can search another copy if one remains outside the Prize cards.

**Exact access** additionally requires at least one available Bench slot. The default examples deliberately reserve one slot, so exact and role-aware access coincide there.

These definitions are nested, which lets the probability gap decompose exactly into direct-to-Bench semantic error, starting-Active role error, and Bench-capacity error.

## Illustrative baseline

Use:

- 60 cards;
- 7-card accepted opening;
- 6 Prize cards;
- 1 later random draw;
- 1 trigger Basic;
- 3 other Basics;
- 4 hand connectors;
- 4 direct-Bench connectors;
- at least one Bench slot available.

The valid-opening probability is 39.949963%.

Conditional on an accepted opening:

| Evaluation | Trigger access |
| --- | ---: |
| Naive Pokémon access | 71.924317% |
| Zone-aware | 56.082107% |
| Role-aware | 35.038269% |
| Exact with one Bench slot | 35.038269% |

The naive model overstates trigger access by **36.886047 percentage points**. About 51.28% of its claimed successes are false positives under the modeled semantics.

The gap decomposes into 15.842210 points from crediting direct-to-Bench connectors as if they preserved the hand-play trigger, 21.043838 points from treating the opening trigger Basic as usable even when it must be the starting Active, and 0 points from Bench capacity because this baseline reserves a slot.

## Connector-class sensitivity

Keep the same one trigger Basic and three other Basics.

| Connector package | Naive | Zone-aware | Role-aware/exact | Combined overstatement |
| --- | ---: | ---: | ---: | ---: |
| 4 hand + 4 direct-Bench | 71.924317% | 56.082107% | 35.038269% | 36.886047 pp |
| 4 hand only | 56.082107% | 56.082107% | 35.038269% | 21.043838 pp |
| 4 direct-Bench only | 56.082107% | 30.538987% | 9.495149% | 46.586958 pp |

The direct-Bench-only row shows why generic Pokémon reachability is especially dangerous for zone-triggered Abilities. The connector can be excellent at putting the Pokémon into play while contributing nothing to the required hand-to-Bench trigger.

## Connection to real Expanded cards

This model is deliberately typed rather than card-specific, but the semantic distinction maps to familiar lines.

A Quick Ball-like effect searches a Basic Pokémon into hand. If costs and locks are satisfied and Bench space exists, the player can then manually play a Tapu Lele-GX-like target from hand to the Bench and receive its trigger.

A Nest Ball-like effect puts a Basic Pokémon directly from the deck onto the Bench. That can establish the Pokémon in play, but it does not perform the "play this Pokémon from your hand onto your Bench" transition required by Wonder Tag, Dedechange, Dark Asset, Luminous Sign, and similar Abilities.

`results/typed_access_network/` already preserves this distinction at the deterministic transition level. The present result quantifies how much it can matter after accepted-opening conditioning and Prize placement are added.

## Prize awareness

Connectors receive credit only when at least one trigger Basic remains in the searchable deck after the opening hand, Prize cards, and later random draws are removed.

This matters most with low target counts. A connector in hand is not itself a trigger out if the only copy of the target is already Active, in hand, Prized, or otherwise absent from the deck.

For the one-trigger-Basic baseline, if that single copy is forced Active, a hand connector cannot rescue the state because there is no second copy left to search. That is why the 21.043838-point setup-role error from the earlier result survives even after four clean hand connectors are added.

## Strategic interpretation

### Zone is part of card identity in a line

"Can access Tapu Lele-GX" is underspecified. A line that ends with Tapu Lele-GX in hand has different strategic meaning from a line that ends with it already on the Bench.

### Physical copies have roles

A support Pokémon can be a setup-enabling Basic and a tactical trigger card, but one physical copy cannot simultaneously be the starting Active and remain in hand for a later Bench-entry trigger.

### Marginal outs can be semantically wrong

Adding four generic Pokémon-search outs can appear to improve a trigger line dramatically. If those outs move the target to the wrong zone, the apparent consistency gain can be largely fictitious for that purpose.

### Prize and setup conditioning should be joint

The model samples Prize cards only after the accepted opener is fixed. It does not treat the opening and Prize state as independent uniform samples.

## Validation

The category model uses exact integer combinatorics for the accepted opening, Prize cards, and later random draws.

The reproducer independently enumerates labeled cards in small decks through the full sequence:

`opening -> accepted start -> Prizes -> later draws -> access test`

It checks the naive, zone-aware, role-aware, and exact probabilities as exact rational numbers. A zero-Bench-slot case also validates the final capacity gate and the additive decomposition of the nested errors.

## Limits

The hand connector is intentionally cleaner than a real Quick Ball or Ultra Ball. The model omits discard costs, Item lock, Ability lock, Supporter timing, stochastic search, search for the connector itself, Active-switch/recovery effects, optional setup exceptions, opponent mulligan bonus cards, and dynamic Bench occupancy.

Direct-Bench connectors are treated only as semantically invalid for the hand-play trigger. Their other strategic value is outside this question.

The analysis asks whether one trigger activation is available, rather than whether using it is strategically correct.

## Next useful work

A stronger turn-one support model should replace the abstract connector counts with typed real-card lines from `typed_access_network.py`, then add discard gates for Quick Ball/Ultra Ball-like effects, Item/Ability lock state, support-Pokémon search Abilities with their own Bench-slot cost, optional setup starters and policy, explicit core-board Bench reservations, and a value model for the liability of leaving multi-Prize support Pokémon in play.

That would connect setup, zone semantics, connector cost, lock state, and Bench AMR in one state-transition model.
