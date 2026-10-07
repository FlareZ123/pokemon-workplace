# Committed play-event bridge

This result adds a thin event-history layer over existing action-channel kernels.

A committed play event records the card player, turn owner, decision controller, physical card identity, card name, action kind, and whether the ordinary turn quota was consumed.

The regression composes five existing distinctions:

- a normal Supporter play emits a Supporter event;
- a delegated Supporter body executed through a Pokémon move emits no Supporter play event;
- a failed Quaking Fist Trainer attempt emits no committed event;
- a successful Supporter or Stadium attempt emits an ordinary committed event;
- Teleport Room changes the Stadium in play without emitting a Stadium-play event;
- Hand Control emits a forced Supporter event for the opponent while leaving that opponent's ordinary own-turn Supporter quota untouched.

This separates three questions that can otherwise collapse into one flag: did a physical card get played from hand, whose turn was it, and did that event consume the ordinary quota for the current turn?

Implementation: `tools/committed_play_event.py`  
Regression: `results/committed_play_event/reproduce.py`

The bridge intentionally leaves physical legality and card resolution in the existing kernels. It only converts successful transactions into a common history record that later card-text predicates can query.
