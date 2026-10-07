# Trainer category boilerplate normalization audit

## Question

How much apparent card-identity fragmentation comes only from generic Item and Supporter reminder text that current rules define at the category level?

## Result

A narrow exact-string normalizer removes six generic category-rule strings:

- two Item play-count reminders;
- two modern Supporter play-count reminders;
- two historical Supporter handling templates that say to put the Supporter next to the Active Pokémon and discard it at the end of the turn.

Across the bundled archive, those strings affect **1,801 Trainer prints across 760 names**:

- 656 Item-subtype prints;
- 1,145 Supporter-subtype prints.

Within the effectively legal paper Expanded set, they affect **1,646 prints across 670 names**:

- 647 Item-subtype prints;
- 999 Supporter-subtype prints.

Removing only that boilerplate reduces the legal gameplay-fingerprint count from **10,416 to 10,389**. The 27-fingerprint reduction occurs in **26 merge groups**.

Concrete merge examples include:

- Copycat `sm7-127` and `swsh7-143`;
- Switch `bw1-104` and `sv1-194`;
- Crushing Hammer across templates;
- Energy Switch, Great Ball, Potion, Poké Ball, Judge, Shauna, Skyla, and other repeated effects.

## Why these exact strings are candidates for normalization

The current Advanced Player's Rulebook defines Item and Supporter category mechanics independently of those reminder lines:

- players may use any number of Items during their turn, and used Items are discarded;
- players may use only one Supporter during their turn, and a used Supporter is discarded after its effect resolves.

The old Supporter template also includes historical placement timing that no longer describes the current category procedure.

This audit treats only the enumerated generic strings as category boilerplate. It does not delete card-specific restrictions or effects.

For example, Charon's Choice `pl2-RT6` has a distinct rule saying the Supporter returns to the hand at end of turn. That rule is deliberately preserved because it is not one of the generic templates.

## Method

`tools/trainer_boilerplate_normalization.py`:

1. operates only on Trainer cards;
2. removes Item boilerplate only when the card has the Item subtype;
3. removes Supporter boilerplate only when the card has the Supporter subtype;
4. preserves every other rule line;
5. compares raw and normalized gameplay fingerprints;
6. audits legal merge groups and rejects any normalized merge that crosses card names.

The normalizer is currently an audit layer. It has not yet been composed into `current_card_semantics.py`.

## Evidence classes

**Rules evidence.** The current Advanced Player's Rulebook defines the Item and Supporter play/discard procedures globally.

**Repository computation.** The 1,801 / 1,646 print counts and 10,416 -> 10,389 fingerprint reduction are computed from the bundled card archive with the repository's effective Expanded legality overlay.

**Conservative implementation choice.** Only six exact generic strings are removed. Similar-looking card-specific text remains untouched.

## Reproduction

Run:

`python results/trainer_boilerplate_normalization/reproduce.py`

The regression also verifies the Copycat and Switch merge examples and ensures Charon's Choice's return-to-hand rule survives normalization.

## Interpretation

Raw gameplay fingerprints currently encode historical templating eras as though every generic category reminder were a card-specific mechanic. That inflates the number of apparent gameplay variants and obscures true reprints.

A category-aware semantic fingerprint should remove these generic reminders before comparing Trainer effects.

## Next work

Compose this normalizer into the canonical current-semantic fingerprint, then measure how many historical exact-reprint candidates it adds. Review every newly admitted historical candidate family before promoting the normalization into the resolver's high-confidence path.
