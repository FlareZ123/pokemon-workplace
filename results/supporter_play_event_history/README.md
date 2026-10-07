# Supporter play-event provenance

This result separates a Supporter card's play-from-hand history from the provenance of a delegated Supporter effect body.

Implementation:
- `tools/supporter_play_event_history.py`
- `tools/supporter_play_event_corpus.py`

Validation:
- `results/supporter_play_event_history/reproduce.py`
- `results/supporter_play_event_history/reproduce_copy_paths.py`

## Corpus result

A conservative scan of the effectively legal paper Expanded pool finds 62 print-level effects whose text explicitly depends on Supporter hand play.

| Category | Print rows |
| --- | ---: |
| turn-history gate | 28 |
| play-from-hand reaction | 26 |
| play-from-hand lock | 8 |

The 28 history gates include identity-sensitive families. Nineteen accept any Supporter. Three require a Supporter with "Team Rocket" in its name. Six further prints cover Ancient, Future, TAG TEAM, Single Strike, and Rapid Strike requirements.

A scalar `supporter_plays_used` value therefore cannot preserve every history predicate in legal card text.

## Representation

`SupporterPlayEvent` records the physical Supporter copy and name responsible for each hand-play event. `ExecutedSupporterBody` separately records the source of the effect body and its execution class.

The regressions distinguish three cases:

1. A direct Supporter play creates the expected play event.
2. A copied body executed through a Pokémon move does not create a Supporter play event.
3. Sabrina's Suggestion creates a play event for Sabrina while another Supporter can supply the delegated body.

This keeps ordinary turn quota, historical card identity, and effect-body provenance available as separate state facts.

The scanner is conservative and only recognizes direct English wording for the relevant hand-play conditions.
