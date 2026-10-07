# Search action legality and information-gain ordering

## Question

When a card says to search the deck, can a simulator treat the search edge as automatically available and immediately grant exact Prize information?

No.

Search-shaped actions have a legality boundary before the deck-inspection event. At the same time, absence of an eligible search target does **not** necessarily make a constrained search unusable.

This result separates three states that graph-style models can accidentally collapse:

1. the search zone is nonempty but contains no eligible target;
2. the search zone itself is empty;
3. a required destination or other pre-search condition is unavailable.

Implementation: `tools/search_action_legality.py`

Reproducer: `results/search_action_legality/reproduce.py`

## Rules basis

The Advanced Player's Rulebook establishes several relevant rules.

- Items, Supporters, announced Abilities, and voluntary Stadium effects cannot be used when resolving their effect would not change the game state.
- A constrained deck search may select fewer than the stated number, including zero. An unrestricted search for arbitrary cards must take the specified number.
- Looking through the deck for a search exposes its contents to the searching player, followed by shuffling.
- If a direct-to-Bench attack effect would put Pokémon from the deck onto a full Bench, the attack ends before the player searches the deck. A Trainer card or Ability with the same kind of direct-to-Bench effect cannot be used while the Bench is full.
- Attacks may still be used when part of their instructions cannot be applied, unless a card-specific condition says otherwise.

These rules are enough to show that `search exists` and `search executes` are different facts.

## Official Q&A anchors

The Japanese official Q&A supplies a particularly useful pair of rulings for Monster Ball-style constrained searches.

- A player may use Monster Ball or the referenced Supporter even when they already know the deck contains no Pokémon.
- Monster Ball cannot be used when the deck has zero cards.

Those two rulings isolate target absence from zone emptiness. A nonempty constrained search can legally resolve even when its eligible target set is empty, while an empty deck removes the search action entirely for this sole-effect Trainer case.

Official search page:

https://www.pokemon-card.com/rules/faq/search.php?freeword=%E3%83%A2%E3%83%B3%E3%82%B9%E3%82%BF%E3%83%BC%E3%83%9C%E3%83%BC%E3%83%AB&page=3&regulation=all&regulation_faq_main_item1=all

Empty-deck FAQ:

https://www.pokemon-card.com/rules/faq/details.php?id=1095

A separate Ultra Ball Q&A says that if the search finds no Pokémon, the cards discarded to use Ultra Ball are not returned; Ultra Ball was still used. This is consistent with targetless constrained-search resolution rather than rollback.

https://www.pokemon-card.com/rules/faq/search.php?freeword=%E3%83%8F%E3%82%A4%E3%83%91%E3%83%BC%E3%83%9C%E3%83%BC%E3%83%AB&regulation_faq_main_item1=all

The official Energy Retrieval Q&A provides the public-zone contrast: Super Energy Retrieval cannot be used when the discard pile contains no eligible Energy, while one eligible Energy is enough for an `up to` retrieval.

https://www.pokemon-card.com/rules/faq/search.php?freeword=%E3%82%A8%E3%83%8D%E3%83%AB%E3%82%AE%E3%83%BC%E5%9B%9E%E5%8F%8E&regulation_faq_main_item1=all

## Core finding 1: targetless search can still be a real information action

For a sole constrained search-to-hand Item with a nonempty deck and zero eligible targets, the executable model returns:

- action legal: yes;
- full deck inspected: yes;
- material target moved: no;
- exact Prize knowledge after the search: yes, under the repository's skilled-play/deck-knowledge assumption.

This fills a gap identified by `results/prize_information_actions/`, which cataloged full-deck information effects but deliberately did not claim every search could be legally initiated in every state.

The important modeling consequence is that **material failure does not imply information failure**.

A targetless constrained search can still move the information state from uncertain Prize composition to exact Prize composition.

## Core finding 2: an empty deck is different

For the same sole-effect Trainer search with a zero-card deck, the model rejects the action and therefore grants no deck inspection and no information update.

A planner that only checks `eligible_targets == 0` cannot distinguish this state from the legal targetless case above.

The minimum state therefore needs at least:

- total cards remaining in the deck;
- count or existence of eligible targets;
- card-specific action prerequisites;
- destination capacity where relevant;
- information state before and after the executed search.

## Core finding 3: destination gates can prevent information acquisition

Direct-to-Bench search has an additional boundary.

With one open Bench slot, a constrained Item search can execute even when it finds no eligible Basic Pokémon. The deck is still inspected, so the information transition can occur.

With a full Bench, C-11 makes a Trainer or announced Ability with this effect unusable. The deck is never searched, so a simulator must **not** award the K0 -> exact-information transition.

For an attack with the same direct-to-Bench geometry, the attack can still be used, but the effect ends before deck search. This gives a useful counterexample:

`attack was legally used` does not imply `search information was acquired`.

## Core finding 4: public-zone `up to` effects obey a different gate

Energy Retrieval-style text operates on a public discard pile rather than a hidden deck.

If its sole effect is `Put up to N eligible cards from your discard pile into your hand`, then zero eligible cards leaves no state-changing resolution. The Item is therefore unusable.

With at least one eligible card, it is usable and may resolve with the available amount.

This means a generic `up to N may always choose zero` implementation is incorrect for Trainers and announced Abilities. Zero is legal only when the overall action still changes the game state through some other part of resolution.

Attacks remain different: an otherwise announceable attack may resolve with an unavailable retrieval effect and still count as the attack for the turn.

## Card-pool surface area

A conservative scan of the current legal paper-Expanded snapshot finds:

- 392 legal Trainer print-text instances containing `search your deck` or `look through your deck`;
- 179 distinct Trainer search variants after deduplication by action class, card name, and normalized text;
- 17 distinct direct-to-Bench Trainer search variants.

The 17 direct-to-Bench variants include Nest Ball, Battle VIP Pass, Buddy-Buddy Poffin, Dream Ball, Brigette, Gloria, and other effects whose search-information edge is destination-gated.

A destination audit of all 179 distinct Trainer search variants gives:

| Searched-card destination | Variants |
| --- | ---: |
| Hand | 132 |
| Bench | 17 |
| Attach to a Pokémon in play | 13 |
| Evolve a Pokémon in play | 7 |
| Top of deck | 4 |
| Discard pile | 3 |
| Replacement/switch transaction | 2 |
| Mixed hand + attachment | 1 |

The classifier starts at the search phrase itself. That matters for cards such as Pokémon Communication, which moves a pre-search hand card to the top of the deck while the card selected by the search still goes to hand.

The destination distribution shows that deck inspection cannot be modeled independently of board state for a substantial minority of search text. Bench, attachment, evolution, and replacement destinations can carry prerequisites that must be checked before the search step. This table is a text-topology inventory rather than a claim that every card in one destination family shares identical legality semantics.

This count uses the repository legality baseline and its current official ban overlay.

## Executable regressions

`reproduce.py` verifies the transition ordering directly.

### Targetless nonempty search

State:

- 40 cards in deck;
- 0 eligible targets;
- Item action.

Result: legal, full deck inspected, no material target moved, exact Prize knowledge acquired.

### Empty-deck search

State:

- 0 cards in deck;
- 0 eligible targets;
- Item action.

Result: illegal, no inspection, no information update.

### Full-Bench direct search

State:

- 40 cards in deck;
- eligible Basic Pokémon exist;
- 0 open Bench slots.

Result for Item: illegal before search.

Result for attack: attack remains legal, but the direct-placement effect terminates before deck inspection, so no information update occurs.

### Public-zone retrieval

A sole Energy Retrieval-style Item is rejected with zero eligible public-zone cards and accepted with one.

### Card-text anchors

The reproducer audits exact bundled text for:

- Nest Ball `sv1-181`;
- Energy Retrieval `sv1-171`;
- Clavell `sv2-177`;
- Porygon `xy7-64` / Data Check.

Porygon is useful because Data Check has no material search payload at all: it only looks through the deck and shuffles it. That makes deck inspection itself an explicit card effect rather than an incidental consequence of obtaining a target.

## Stronger transition ordering

A search-aware planner should use this order:

```text
1. action-class window and locks
2. card-specific use conditions / costs
3. destination prerequisites that can block the effect before search
4. execute deck-inspection step, if still reachable
5. update information state from the observation
6. choose and move eligible material targets, possibly zero for constrained search
7. shuffle / complete remaining text
```

This ordering prevents two opposite errors:

- rejecting a legal targetless constrained search because no payload exists;
- granting full-deck information to an action that was blocked before the search step.

## Relationship to existing work

This result extends:

- `prize_information_actions/`, by adding a legality gate before exact-information acquisition;
- `information_material_separation/`, by showing a second separation between **search execution** and **material target success**;
- `typed_bench_state_kernel/`, by making Bench capacity an upstream condition on direct-to-Bench information actions;
- the human K0/K1 concept, by making the K0 -> exact-information transition conditional on an actually executed observation.

A useful state edge is therefore richer than `card A searches card B`.

It should carry at least:

- whether the action may begin;
- whether the deck-inspection step is reached;
- what observation occurs;
- what material target moves;
- what destination receives it;
- which action budget is consumed.

## Limitations

The model is intentionally narrow.

It does not attempt to prove a universal game-state-change semantics for every historical card wording. It encodes the directly supported families above.

Coin-flip searches, unrestricted arbitrary-card searches, replacement effects, lock effects, search-to-attach effects, and multi-clause Trainers can add further conditions. For example, a Trainer with another state-changing clause can remain legal even when one optional retrieval clause has zero targets.

The inventory is text-pattern based. It measures the surface area of Trainer search text, not the number of strategically relevant states.

Exact Prize knowledge still assumes skilled tracking of the known decklist and visible zones, consistent with the repository's established information model.

## Next useful work

The strongest next extension is to compile search actions into typed preconditions plus observation events instead of assigning information gain by text pattern alone.

That compiler should distinguish:

- search-to-hand;
- search-to-Bench;
- search-to-attach;
- search-to-evolve;
- search-to-discard;
- unrestricted search that must select a card;
- constrained search that may return zero;
- coin- or condition-gated search branches.

It can then feed the existing Prize-belief kernel and canonical action budget so information value is awarded only on executable branches.
