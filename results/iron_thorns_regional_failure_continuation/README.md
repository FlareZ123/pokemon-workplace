# Region-only draw continuations inside Aichi Iron Thorns named-line failures

## Question

When the narrow first-turn-going-second Iron Thorns line fails, how often do the Japanese-only Palace Book and Player's Ceremony cards preserve an immediate late-turn draw continuation?

This result refines the exact state space from `iron_thorns_named_line_probability/`. It keeps the same accepted opening, six Prize cards, first normal draw, Tag Call, Guzma & Hala, Thunder Mountain, and Double Colorless Energy model, then adds Palace Book and Player's Ceremony as alternate objectives in states where the attack line fails.

Implementation: `tools/iron_thorns_regional_failure_continuation.py`  
Regression: `results/iron_thorns_regional_failure_continuation/reproduce.py`

## Continuation definition

The original named line is:

`Tag Call -> Guzma & Hala -> Thunder Mountain + Double Colorless Energy -> Volt Cyclone`

A failed named-line state has a region-only end-turn draw continuation when at least one of these exact witnesses exists after the first normal draw:

1. Palace Book is already in hand;
2. Player's Ceremony is already in hand;
3. Player's Ceremony remains in the deck and Guzma & Hala is accessible directly or through Tag Call.

The third witness is especially useful conceptually. Guzma & Hala may be reachable even when the attack package cannot be completed because Thunder Mountain or the represented DCE payload is unavailable. In that state the connector can change objective and fetch Player's Ceremony as its unconditional Stadium output.

The exclusive witness partition gives priority to a held Palace Book, then a held Player's Ceremony, then the G&H search pivot. The aggregate continuation probability does not depend on this priority.

Palace Belt is intentionally excluded from this particular endpoint because its value is a beginning-of-next-turn draw modification rather than an immediate end-turn draw action.

## Exact results

Conditioned on an accepted seven-card opening and the first normal draw going second:

| List | Named line success | Regional draw continuation among named failures | G&H -> Ceremony pivot mass in full state space |
| --- | ---: | ---: | ---: |
| Kazuma Kashi | 33.781505711% | **32.848860519%** | **5.751596817%** |
| Ryoya Fujii | 39.107850627% | **47.927533358%** | **2.604983539%** |
| Kohei Hamamichi | 33.781505711% | **22.579832374%** | **6.478205899%** |

The full-state exclusive partitions are:

### Kazuma

- named attack success: 33.781505711%;
- failed attack, Palace Book witness: 8.473819112%;
- failed attack, held Player's Ceremony witness after Book priority: 7.526604898%;
- failed attack, G&H -> Player's Ceremony witness: 5.751596817%;
- failed attack without either modeled regional draw continuation: 44.466473462%.

### Ryoya

- named attack success: 39.107850627%;
- failed attack, Palace Book witness: 14.912154676%;
- failed attack, held Player's Ceremony witness after Book priority: 11.666966988%;
- failed attack, G&H -> Player's Ceremony witness: 2.604983539%;
- failed attack without either modeled regional draw continuation: 31.708044170%.

### Kohei

- named attack success: 33.781505711%;
- Palace Book is absent from the list;
- failed attack, held Player's Ceremony witness: 8.473819112%;
- failed attack, G&H -> Player's Ceremony witness: 6.478205899%;
- failed attack without the modeled regional draw continuation: 51.266469278%.

## Cross-check against the original exact model

The reproducer calls the existing `exact_named_line_probability()` independently.

For all three published lists, adding Book and Ceremony as extra categories preserves exactly:

- accepted-opening probability;
- named attack success probability;
- resource-unavailable failure probability;
- connector-access failure probability.

The new model therefore refines the original partition rather than changing its attack criterion.

## Finding 1: failed attack access can still have connector value

The original narrow line separates two main failure families:

- Thunder Mountain or DCE is unavailable from hand and deck;
- the resources exist, but Guzma & Hala access is absent.

The G&H -> Ceremony pivot occurs only in the first family. If all attack resources exist and G&H is accessible, the named line succeeds. When a resource is unavailable, the same live connector can instead obtain a region-only Stadium that produces a late-turn draw action.

This is a concrete example of connector option value. The value of G&H is state-dependent because its best output changes when another objective becomes impossible.

## Finding 2: regional cards matter disproportionately in failed-line states

The previous regional access result measured whether the Japanese-only draw cards were reachable at all.

This result conditions their strategic role on failure of the deck's named first-turn attack route. Nearly half of Ryoya's narrow attack failures still have one of the two region-only end-turn draw continuations in the modeled state.

That does not mean the turn is strategically rescued in half of all failures. Other local cards, disruption Supporters, alternate attacks, and broader search actions are outside the state model. It does show that replacing the unresolved Japanese-only cards with inert filler systematically erases continuation options from exactly the states where the narrow attack plan needs an alternative.

## Finding 3: Book and Ceremony occupy different connector geometry

Palace Book must be drawn directly in this model because it is an Item and the model does not execute Trainers' Mail.

Player's Ceremony can be drawn directly or searched as Guzma & Hala's Stadium output.

Ryoya's two Book plus two Ceremony construction therefore has the largest modeled continuation coverage. Kohei has no Book and relies only on Ceremony for this endpoint.

## Limits

The model intentionally inherits the narrow named-line action set.

It omits Trainers' Mail, Gladion, Speed Lightning Energy draws, opponent mulligan bonus draws, VS Seeker, alternate Stadium/Energy lines, other Supporter plans, and opponent interaction.

Using Palace Book or Player's Ceremony ends the player's turn, so the endpoint is valuable only when ending the turn is acceptable.

Player's Ceremony is symmetrical and may benefit the opponent on a later turn.

Fetching Ceremony with Guzma & Hala uses the turn's Supporter action. The model treats that as a continuation witness after the named attack plan has already failed and does not compare it with every alternative Supporter.

The result isolates regional-card option value within one auditable first-turn state space. It is not a win-rate estimate.

## Next work

Two natural extensions are:

1. add Trainers' Mail so Palace Book can be reached through the same top-four recursion already used by `iron_thorns_trainers_mail/`;
2. give Palace Belt a next-turn continuation objective and model Tool-slot contention with Handheld Fan and Tool Jammer.
