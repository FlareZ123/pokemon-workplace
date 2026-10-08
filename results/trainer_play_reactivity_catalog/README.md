# Expanded card-text reactions to Trainer plays

## Research question

Does the paper Expanded English snapshot contain cards whose text reacts directly to an Item or Supporter being played, especially when the action can involve two simultaneously played physical Item cards, as on Cross Switcher?

## Method

`tools/trainer_play_reactivity_catalog.py` scans every `abilities`, `attacks`, and `rules` text in `resources/cards/en/`, retaining the phrase pattern `whenever ... plays ... Item/Supporter/Trainer`. It filters using the repository's **set-level Expanded legality**, **effective print legality** (including its official overlay), and printed set release dates through **2026-10-08**. The source is the **English-language snapshot**. Japanese-only card pools require separate auditing.

The catalog identifies `32 eligible print-text entries` across `24 distinct card names`. **31 prints** contain deterministic `prevent all effects of that card` wording. The remaining print is **Venomoth, XY Phantom Forces `xy4-2`, Dizzying Wind**, whose effect places a coin-flip gate on Trainer cards during the opponent's next turn.

These numbers describe the exact lexical search and known print database. The script does not discover every conceivable wording of a Trainer-play response. Print entries also differ from physical in-play entities; four Greninja V-UNION promo records represent pieces of one composite Pokémon identity.

## Why Cross Switcher exposes an unresolved question

The local card record `swsh8-230` requires playing **two Cross Switcher Item cards at once**, while executing its effect once for the pair. The play journal now conserves both physical sources and one effect action with one or two switch microsteps.

The rules manual's E-29 describes effects that prevent effects of a Trainer played from hand. Most of the matching reactive texts are prevention effects and can be modeled as target/effect eligibility predicates. Venomoth's Dizzying Wind is structurally different because it requires a coin outcome after a Trainer play.

**Open ruling question:** does playing two Cross Switcher cards at once under an applicable `Dizzying Wind` effect require one coin flip or two, and what happens to the pair when a flip fails? The bundled Advanced Player's Rulebook excerpt and print text do not by themselves establish this interaction decisively. Do **not** bake either possibility into a full-game simulator without an official, print-specific ruling.

## Strategic implication

Conditional Trainer-effect protection is part of tactical target legality, especially for gust and switch effects. A model that only checks the opponent's Bench and the acting player's Item permission can overstate eligible gust targets when Pokémon have source-triggered immunity to Item/Supporter effects.

This finding supplies candidate prints for a future target-effect permission audit. It is an inventory of card text, with a deliberately unresolved simultaneous-Item trigger interaction.

## Reproduction

`python results/trainer_play_reactivity_catalog/reproduce.py`

The code audits eligibility and the category count from the full bundled English JSON source. It also checks a 2014 historical cutoff, where only the Plasma Storm Togekiss and Phantom Forces Venomoth entries appear.
