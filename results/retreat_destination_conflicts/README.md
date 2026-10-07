# Retreat Energy destination conflicts: Dashing Pouch, Scoop-Up Block, and Prism Star

## Question

How should a simulator represent retreat Energy when Dashing Pouch proposes hand, the Prism Star rule proposes Lost Zone, and Scoop-Up Block can prohibit the hand route?

The currently supported answer is partly resolved and partly an explicit evidence gap.

Implementation: `tools/retreat_destination_conflicts.py`  
Regression: `results/retreat_destination_conflicts/reproduce.py`

## Exact card texts in the bundled pool

- Dashing Pouch `sm4-92`: if its holder discards Energy for Retreat Cost, put that Energy into hand instead of the discard pile.
- Mr. Mime `sm9-66`, Scoop-Up Block: the opponent's damaged Pokémon and cards attached to them cannot be put into the opponent's hand.
- Super Boost Energy Prism Star `sm5-136` and Beast Energy Prism Star `sm6-117`: if a Prism Star card would go to the discard pile, put it in the Lost Zone instead.

All are inside the paper Expanded Black & White-onward scope represented by the repository.

## Authoritative boundary

The official Japanese Pokémon Card Q&A has an exact Dashing Pouch plus Scoop-Up Block ruling. If the damaged Active holder retreats while opposing Scoop-Up Block is active, the Energy paid for retreat is discarded. This establishes that the hand route is unavailable in that state.

Source:

https://www.pokemon-card.com/rules/faq/search.php?freeword=%E3%83%80%E3%83%83%E3%82%B7%E3%83%A5%E3%83%9D%E3%83%BC%E3%83%81

This is also consistent with the Advanced Player's Rulebook rule that when "do" and "can't do" effects conflict, "can't" takes priority.

## Supported deterministic cases

The analyzer resolves:

- ordinary paid Energy -> discard;
- ordinary paid Energy with live Dashing Pouch -> hand;
- ordinary paid Energy with Dashing Pouch blocked by Scoop-Up Block -> discard;
- Prism Star Energy without Dashing Pouch -> Lost Zone;
- Prism Star Energy with Dashing Pouch plus a live damaged-holder Scoop-Up Block prohibition -> Lost Zone, because the hand proposal is removed and the remaining discard-bound Prism Star rule redirects to Lost Zone.

The last branch is a rules/card-text derivation from the exact Dashing-Pouch prohibition plus the printed Prism Star rule. It is not claimed as a located card-specific Q&A.

## Unresolved case

Dashing Pouch plus Prism Star Energy without Scoop-Up Block currently remains unresolved in this model.

Dashing Pouch proposes hand instead of discard. The Prism Star rule also reacts to a card that would go to discard and proposes Lost Zone instead.

A targeted search of the official Dashing Pouch Q&A returns three interactions: failed retreat under Slick Slip, Scoop-Up Block, and paying a two-Energy Retreat Cost with two Double Colorless Energy cards. I did not find an exact official Dashing Pouch plus Prism Star Energy ruling.

That search failure is evidence of an unresolved source gap, not evidence that no ruling exists.

## Rescue Scarf is a different timing class

Official Q&A says a Solgaleo Prism Star with Rescue Scarf can return to hand when Knocked Out by attack damage.

That case should not be used mechanically as Dashing Pouch precedence. Rescue Scarf moves the Knocked Out Pokémon during the pre-disposal Knock Out effect window, while Dashing Pouch and the Prism Star rule are both worded around the retreat discard destination.

Source:

https://www.pokemon-card.com/rules/faq/search.php?freeword=%E3%82%BD%E3%83%AB%E3%82%AC%E3%83%AC%E3%82%AA%E2%97%87&regulation_faq_main_item1=all

## Architectural implication

A destination analyzer needs more than candidate zones.

It should represent:

- the underlying movement event;
- conditional replacement applicability;
- prohibitions that remove candidate destinations;
- effect timing class;
- authority for resolving surviving conflicting replacements.

A prohibition can sometimes collapse a multi-destination conflict into one deterministic route. When two legal replacement routes survive and authority is unknown, the state should remain unresolved instead of inventing precedence.
