# Expanded Trainer gust sources: typed target geometry and errata-corrected semantics

## Research problem

A model awarding one identical generic gust token for each card containing the word "switch" is unreliable. Some effects let **you** choose an opposing Bench target; others let the **opponent** choose its next Active. Others switch only your own Pokémon, select a narrow Pokémon type, require a pair of Item cards, consume discard fuel, or are governed by an erratum absent from historical raw print data.

This catalog is intended as a conservative and auditable entry point for connecting the prior `gust_prize_minimax`, `counter_catcher_prize_timing` and `pokemon_catcher_coin_minimax` tactical results to printed Expanded Trainer cards.

## Source and scope

`tools/trainer_gust_catalog.py` scans bundled `resources/cards/en/*.json` only for cards in sets marked Expanded-legal by `resources/sets/en.json`, excludes prints marked Banned by `classify_effective_legality`, and selects Trainer cards whose literal rules contain both "switch" and "opponent". This is a **high-recall lexical seed**, manually classified by source card name.

The snapshot includes English-language releases only. It is not a complete census of Japanese-only tournament-legal prints. Cards whose text does not include both lexical seeds, particularly Pokémon attacks or Abilities, are outside this Trainer-only survey. Any new name discovered on a later database refresh remains `unclassified` for review.

The advanced player's manual distinguishes:
- C-03: switching the current Active with one's own Bench;
- C-04: the opponent selects a replacement after their Active is forced out;
- C-05: the effect user chooses which opposing Benched Pokémon comes Active;
- II-A: current errata overrides superseded text;
- B-01/B-03: Items and Supporters have different action-window budgets.

## Corpus result

There are **75 legal Trainer print records** over **22 distinct database card names** containing the two lexical seeds.

Manual role classification:

| Semantic family | Print records | Distinct card names | Tactical treatment |
| --- | ---: | ---: | --- |
| Player chooses an existing opposing Benched target | 57 | 16 | Targeted gust with additional gates |
| Opponent chooses the replacement Active | 9 | 3 | Cannot assume the target can be selected |
| Place a Basic from opponent hand onto Bench, then promote | 3 | 1 | Different target zone and first-stage effect |
| No opposing Pokémon switch occurs | 5 | 1 | Self-switch with opponent referenced only in damage bonus |
| Switch refers to non-Pokémon cards | 1 | 1 | Prize/hand card exchange |
| **Total** | **75** | **22** | |

Among the **57 player-selected existing-Bench target print records**, the text-constrained target types are:

| Target eligibility | Print records | Examples |
| --- | ---: | --- |
| Any opposing Benched Pokémon | 46 | Boss's Orders, Counter Catcher, Pokémon Catcher, Guzma |
| Basic Pokémon | 3 | Lisia's Appeal |
| GX or legacy EX | 2 | Great Catcher |
| Mega Evolution | 1 | Mega Catcher |
| Pokémon V family | 3 | Serena |
| 50 HP or less remaining | 2 | Toy Catcher |

A card-name's different print arts typically share effects, so **print count is not the number of unique strategic actions**.

Special payment, permission and interaction gates are retained. Examples: two simultaneous Cross Switcher cards; two Custom Catcher copies to select an opposing target rather than drawing; Counter Catcher requires being behind on remaining Prizes; Great Catcher discards two hand cards; Prime Catcher uses the ACE SPEC slot; Team Rocket's Giovanni must first switch two eligible own Team Rocket's Pokémon; and Shauntal has a coin-flip branch that can switch your own Active instead.

The catalog intentionally tracks a multi-function Supporter such as Serena with its draw alternative, and does not flatten it into an unconditional gust.

## Critical historical-text correction: Pokémon Catcher

The bundled cards `bw2-95`, `bw5-111` and `bw10-83` retain old deterministic wording in their original rules fields. Eight later Pokémon Catcher print records explicitly say to flip a coin.

The **official Pokémon TCG Errata**, https://assets.pokemon.com/assets/cms/pdf/tcg/tcg_errata.pdf, page 1, specifies that Pokémon Catcher now requires a coin flip and uses the same switching semantics as Pokémon Reversal. The current Play! Pokémon errata page, https://play.pokemon.com/fr-ca/resources/documents/tcg-errata/, corroborates the rule.

`GustPrint.raw_text` preserves original source material, while `GustPrint.effective_text` substitutes the updated effect for those three older prints. All 11 Pokémon Catcher records are therefore marked as coin-flip-dependent.

**Consequence:** treating obsolete BW Pokémon Catcher print text as a guaranteed gust would inject a systematic probability and tactical value error into current Expanded simulations.

## Reproduction

`results/trainer_gust_catalog/reproduce.py` verifies all 75 print records, 22 human-reviewed names, 57 targeted instances, target-family distributions, structural negative controls (Repel, Escape Rope, Ryme, Kieran, Bother-Bot), permission gates, and the three official Pokémon Catcher errata updates.

Run `python results/trainer_gust_catalog/reproduce.py` from the repository root. To print the full catalog summary, use `python tools/trainer_gust_catalog.py`.

## Limits and next work

These are **text-based category labels**, not proof that a given turn can use the corresponding Trainer. Current Supporter quota, target state, Items locked, card access, hand payment, remaining Prize eligibility, mandatory coeffects, and ACE SPEC exclusivity all require integration with the corresponding state kernels.

The source selection specifically uses two text fragments, so it does not enumerate every Pokémon attack/Ability that moves an opposing target. A later broader database scan could compile target permissions from those sources.

The next meaningful model extension is to pass these `target_scope` and `gates` labels into an exact opponent-aware tactical planner and compare restricted-target gusts to unconditional ones, under a separately specified public board classification.
