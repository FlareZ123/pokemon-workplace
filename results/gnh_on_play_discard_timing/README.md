# Guzma & Hala payment timing: official pre-search boundary

## Question and result

The English Cosmic Eclipse Guzma & Hala text opens with a Stadium search,
but its optional discard clause specifies **"When you play this card"**.
Does an initially K0 player get to inspect the deck and learn Prizes before
deciding which two other hand cards to discard for the Pokémon Tool and Special
Energy bonus?

**No.** The Pokémon Company Japan's official FAQ explicitly rejects
searching a Stadium first and then deciding to discard two cards. The player
chooses whether to discard at the moment Guzma & Hala is played.

Official Q&A (search phrase `グズマ`):
https://www.pokemon-card.com/rules/faq/search.php?freeword=%E3%82%B0%E3%82%BA%E3%83%9E&regulation_faq_main_item1=all

The relevant question asks whether a player may first add a Stadium from the
deck, then discard two cards to retrieve a Tool and Special Energy. The answer
says this is disallowed and that the discard decision is made when the
Supporter is played. The corresponding 2019 Cosmic Eclipse TPCi FAQ likewise
explains the on-play discard precedes the Stadium search:
https://pokegym.net/wp-content/uploads/2019/10/FAQ-SM12-Cosmic-Eclipse.pdf

Printed source: `resources/cards/en/sm12.json`, `sm12-193` and `sm12-229`.
See Advanced Player's Rulebook B-03 for ordinary Supporter action limits,
H. Deck for full-deck search and shuffle behavior, and the card's own
on-play timing clause.

## Required phase order

1. Play Guzma & Hala and spend the Supporter allowance.
2. Decide whether to make the optional two-card payment **from the hand
   before any new deck inspection**. If chosen, commit both discards now.
3. Search the deck for a Stadium (the first full-deck inspection reveals the
   remaining deck; a skilled player can infer initial Prizes, K0 -> K1).
4. If the payment was made, search for the additional Pokémon Tool and
   Special Energy.
5. Complete the search and shuffle as instructed.

The ordered subsequence is `play -> optional discard -> first search -> K1`.
There can be earlier full-deck searches, in which case the player starts
Guzma & Hala already in K1. A prior Tag Call searching for a TAG TEAM
Supporter provides exactly that kind of prior inspection. K1 gained during
Guzma & Hala's Stadium search cannot retroactively change the payment.

## Concrete counterexample

A player has Guzma & Hala and one otherwise discardable card in hand.
An Artazon Stadium, Technical Machine: Evolution, and Jet Energy are in deck.
A mistaken sequential-text interpreter might fetch Artazon first, then
discard Artazon plus the old hand card to access the Tool and Energy.
The official timing disallows this: the two-card cost is unpayable at the
moment the Supporter is played. The Stadium can still be found.

A different start holds Guzma & Hala, Tag Call, and one other card. A legal
Tag Call searches for Bellelba & Brycen-Man before Guzma & Hala is played,
adding a second hand card and establishing K1. That enables a subsequent
two-card on-play payment if spending Bellelba is strategically acceptable.

## Regression and limits

`results/gnh_on_play_discard_timing/reproduce.py` implements a small
typed physical-zone and phase contract. It covers an unfundable payment,
an ordinary payable payment, prepayment K0 versus preexisting K1, and eight
exhaustively chosen payment subsets. The script preserves distinct physical
cards and prevents fetching a Stadium to finance the same Supporter's cost.

This is a targeted rules and scheduling regression, with hand/deck material
and event order modeled. It omits the full Aichi board setup, opponent lock,
specific Prize configurations, stochastic reshuffles, and strategic valuation.
Its role is to prevent an impossible late-choice action from entering a
larger optimization or simulation.

The existing `tools/gnh_tool_thinning_information.py` K0/K1 abstraction
remains appropriate for an initial Guzma & Hala play; a model granting the
first G&H play an information-informed payment must explicitly show an
**earlier** deck inspection.
