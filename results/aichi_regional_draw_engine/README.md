# Japanese-only draw engines restore missing Aichi Iron Thorns search edges

## Question

Do the Japanese-only cards missing from the bundled English snapshot materially affect the strategic model of the published Aichi Iron Thorns lists?

Yes. Every unresolved copy in the three preserved Iron Thorns non-Basic lists is a draw-engine card. Two of the three missing card names are also typed outputs of Guzma & Hala, which means an English-only card graph deletes real connector edges used by the Japanese lists.

The exact access model is implemented in `tools/aichi_regional_engine_access.py`. The regression is `results/aichi_regional_draw_engine/reproduce.py`.

## External card facts

The bundled English snapshot does not contain these three cards. Current Limitless Japanese-card references provide unofficial English translations and region-specific legality labels:

| Card | Type | Relevant effect | Expanded (JP) | International Expanded |
| --- | --- | --- | --- | --- |
| Palace Book | Item | Draw 3 cards, then the user's turn ends | legal | not legal / unreleased |
| Palace Belt | Pokemon Tool | While attached to the user's Active Pokemon, the normal beginning-of-turn draw becomes 2 cards | legal | not legal / unreleased |
| Player's Ceremony | Stadium | Once during each player's turn, that player may draw 2 cards; choosing the draw ends that player's turn | legal | not legal / unreleased |

References:

- Palace Book: https://limitlesstcg.com/cards/jp/XYP/NAN83?translate=en
- Palace Belt: https://limitlesstcg.com/cards/jp/BWP/153?translate=en
- Player's Ceremony: https://limitlesstcg.com/cards/jp/SP/127?translate=en

These translations are external evidence and are explicitly treated as unofficial translations.

## Local connector facts

The bundled English record for Guzma & Hala says to search for a Stadium. If its user discards 2 other cards, it can also search for a Pokemon Tool and a Special Energy.

The local Tag Call record can search for up to 2 TAG TEAM cards. Guzma & Hala is a TAG TEAM Supporter.

This creates a source-backed connector pattern:

`Tag Call -> Guzma & Hala -> Player's Ceremony + Palace Belt + Special Energy`

The full three-output version requires the optional two-card discard. Player's Ceremony alone is in the unconditional Stadium output channel.

Palace Book is an Item, so Guzma & Hala does not search it. The Aichi lists also contain Trainers' Mail, which can sometimes find Palace Book from the top four cards, but that probabilistic path is omitted from the exact model below.

## Deck counts

The exact published non-Basic count dictionaries already preserved in `tools/aichi_setup_inference.py` imply four Basic Pokemon in each 60-card Iron Thorns deck.

| List | Tag Call | Guzma & Hala | Palace Book | Palace Belt | Player's Ceremony | Japanese-only draw-engine copies |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Kazuma Kashi | 2 | 2 | 1 | 1 | 1 | 3 |
| Ryoya Fujii | 2 | 2 | 2 | 0 | 2 | 4 |
| Kohei Hamamichi | 2 | 2 | 0 | 2 | 1 | 3 |

The regional card-pool audit previously found exactly 3, 4, and 3 unresolved copies for those lists. This result identifies the strategic function of every one of those unresolved copies.

## Exact setup model

The model enumerates multivariate hypergeometric states instead of sampling.

For each list it:

1. draws a seven-card opening hand from 60 cards;
2. conditions on the hand containing at least one of the deck's four Basic Pokemon;
3. places six Prize cards from the remaining 53 cards;
4. optionally draws one normal card from the remaining 47-card deck;
5. checks whether Guzma & Hala is directly in hand or can be reached by Tag Call while at least one Guzma & Hala remains in the deck;
6. checks whether Player's Ceremony and Palace Belt are already in hand or remain searchable through that Guzma & Hala route.

The accepted-opening probability for a four-Basic 60-card deck is 39.9499626%.

### After the first normal draw

| List | Direct or Tag Call G&H access | Player's Ceremony ready | Palace Belt ready | Belt + Ceremony ready | End-turn draw option ready |
| --- | ---: | ---: | ---: | ---: | ---: |
| Kazuma Kashi | 40.9905423% | 44.4343565% | 44.4343565% | 33.7815057% | 51.6974395% |
| Ryoya Fujii | 40.9905423% | 55.0872073% | n/a | n/a | 66.4787229% |
| Kohei Hamamichi | 40.9905423% | 44.4343565% | 55.0872073% | 38.0806800% | 44.4343565% |

`End-turn draw option ready` means Palace Book is in hand or Player's Ceremony is in hand or searchable through the modeled Guzma & Hala route.

For Kazuma and Kohei, `Belt + Ceremony ready` means both regional pieces can be assembled from the current hand plus one modeled Guzma & Hala use. It includes states where one or both pieces were already drawn.

## Strategic interpretation

The regional gap changes the deck's associativity graph.

Kazuma and Kohei can use Guzma & Hala as a multi-axis connector that reaches a Stadium draw option, an Active-dependent Tool draw engine, and a Special Energy in one Supporter action when the discard branch is feasible. Ryoya uses the same connector for Player's Ceremony while reserving the Tool output for its other Tool package.

The two turn-ending draw cards also use different action channels from Supporters. Palace Book is an Item. Player's Ceremony is a Stadium effect. A control turn that has already spent its Supporter on disruption can therefore retain a late-turn draw option if ending the turn is strategically acceptable.

Palace Belt behaves differently. It consumes a Tool slot and depends on the holder being Active, but it increases the ordinary beginning-of-turn draw without ending the turn. That creates direct contention with Handheld Fan and Tool Jammer in the same lists.

A card-pool resolver that treats the three Japanese-only names as absent filler removes these strategic choices. The resulting simulator can still preserve a 60-card count while losing the actual draw and connector structure.

## Evidence classes

**Local database facts:** the exact Aichi list counts, Tag Call text, Guzma & Hala text, and the four-Basic deck structure come from repository resources and existing tools.

**External card-reference facts:** the three Japanese-only card types, translated effects, and current region-specific legality labels come from the Limitless Japanese-card references above.

**Mathematical result:** the setup percentages come from exact multivariate enumeration over accepted opening hands, Prize placement, and one normal draw.

**Strategic interpretation:** the action-channel and connector consequences follow from those card texts and the deck counts. They remain subject to real-game contention and matchup state.

## Model limits

The calculation deliberately leaves several effects outside the probability.

- Trainers' Mail access is omitted, so Palace Book reach is understated.
- Opponent mulligan bonus draws are omitted.
- Other draw and search effects are omitted.
- A reachable Guzma & Hala is treated as an available connector. Competing Supporter uses are not scored.
- Palace Belt search through Guzma & Hala requires two other cards to be discarded. The model does not judge DCI or AMR of those exact discards, so Belt-containing search lines are optimistic where the payment is strategically bad.
- Tool-slot competition with Handheld Fan or Tool Jammer is omitted.
- Player's Ceremony is symmetrical and can also be used by the opponent.
- The value of ending the turn depends on whether the player wanted to attack or take further actions.
- The model describes first-turn material readiness. It is not a match win-rate model.

## General lesson

Regional card-pool coverage belongs upstream of search-graph and simulator construction.

When a real tournament list contains a region-only card, treating the unresolved name as an inert unknown can erase typed search outputs and action channels. A robust pipeline should preserve the regional scope and external-card provenance before compiling deck connectivity.
