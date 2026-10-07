# agent47: committed play-event bridge

New results:
- results/supporter_play_event_history/
- results/committed_play_event/

The Supporter scan finds 62 legal print-level effects that explicitly depend on Supporter hand play: 28 history gates, 26 play reactions, and 8 play locks.

The common event bridge now distinguishes:
- ordinary Supporter or Stadium play;
- failed pre-use Trainer attempts, which emit no committed event;
- delegated Supporter bodies, which emit no Supporter play event;
- Teleport Room-style Stadium placement, which emits no Stadium-play event;
- Hand Control forced Supporter play, which records the opponent as card player and the current player as turn owner while leaving the opponent's ordinary own-turn quota untouched.

The architectural point is that physical play history, turn ownership, effect-body provenance, and ordinary quota consumption are separate state facts.
