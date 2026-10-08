# A known Item play can have an unknown physical-card identity

## Correction to earlier interpretation

The preceding [partial-play-history result](../partial_play_history/) treated a successful Prime Catcher effect lacking materialized Item copy identities as an unknown Item play. This was overly conservative. The source-specific physical action tells us the **Item card name and number of required copies** even when the game-state model has not materialized exact source instance IDs.

A practical strategy analyzer needs to distinguish two forms of observability:

1. **Occurrence**: which type/name of Trainer was played, and how many simultaneous physical cards were involved;
2. **Materialization**: the actual physical copy IDs that moved from hand to discard.

An opaque copy identity does not erase evidence that the Item action occurred.

## Representation

`UnmaterializedPlay(player, kind, card_name, copies)` records the source of a successful action whose exact physical instance IDs have not been supplied. In a paired-switch Item transaction, that witness is attached to the first effect boundary with `play_record_complete=False`.

`CausalEventJournal.occurrence_history_complete` is independent of `play_history_complete`, the latter asking for complete **copy-ID** capture. Every submitted boundary may have complete occurrence evidence while some lack physical instance IDs.

`queried_play` returns:

- `True` for a witnessed matching name/kind in either materialized or unmaterialized evidence;
- `False` when no match exists and all submitted boundaries have full occurrence classification;
- `None` when no match exists and an unclassified boundary could contain it.

For a known opaque Prime Catcher action, the Item query returns `True`, while both a Supporter query and a Cross Switcher query return `False`. An independent unidentified future action makes those unwitnessed negatives indeterminate, while leaving the known Prime positive.

## Regression

The [reproducer](reproduce.py) uses the same validated Prime Catcher physical transaction to construct a copy-opaque journal and a fully materialized journal. Their final Pokémon boards and Ability-lock overlays are identical. Their Item-play occurrence queries agree; their physical copy provenance differs.

The regression also verifies replay, invalid mixed coverage claims, known positives amid later missing observations, and false negatives being rejected where source kind is genuinely unidentified.

## Limits

The system still trusts callers to provide all source-relevant event boundaries. This result concerns the **information representation** of supplied physical actions. Additional in-game triggered effects of playing Items are separate questions, especially simultaneous two-card Items such as Cross Switcher.

To reproduce: `python results/play_occurrence_identity_separation/reproduce.py`.

Related implementation: `tools/causal_event_journal.py`, `tools/paired_switch_event_bridge.py`.
