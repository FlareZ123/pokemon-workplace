# Hand-origin Energy attachment can terminate Dragon's Wish turn

## Question

Does Dragonair's attack-granted any-number Energy attachment permission remain usable for the whole turn if the target of a subsequent opposing attack reacts to an Energy attachment?

## Printed cards and rules

- Dragonair `sm1-95`: Dragon's Wish grants any number of hand attachments during **your next turn**.
- Slakoth `sm11-167`: Lazy Howl ends **your opponent's next turn** when an Energy card is attached **from their hand to the Defending Pokémon**.
- Hypno `sv6pt5-17`: Daydream has the same next-turn attachment trigger.
- The bundled database marks all three prints Expanded-legal. The reproducer checks those precise source texts before constructing windows.

The Advanced Player's Rulebook E-07 explains that attachments *from hand* include cards attached using effects. Thus the trigger observes card provenance, including an Ability's hand attachment, independently of whether a manual attachment quota was spent. Effects applied to an Active Pokémon normally disappear after it moves to the Bench or evolves, and a reaction that ends the turn closes all otherwise available ordinary actions.

## Result

The exact physical witness has player A use Dragon's Wish, and player B subsequently use Lazy Howl on A's Active Pokémon. On A's next turn:

1. A can manually attach from hand to its other Benched Pokémon multiple times because Dragon's Wish is active.
2. When A attaches to the originally Defending Active Pokémon, Lazy Howl triggers and **ends A's turn**.
3. Remaining Energy cards and unlimited attachment permission cannot grant additional actions because the turn has already closed.

In the representative four-Fire-Energy input state, two attachments to an unaffected Bench Pokémon followed by one to the affected Active Pokémon produce three physical attachment events, three preserved usage records, and an ended turn. If A attaches to the affected Pokémon first, that first attachment itself closes the turn. Both source prints reproduce the same result.

This illustrates a priority relation: the positive action grant expands the available manual attachment bandwidth, while the opponent's reactive end-turn effect imposes a hard *execution deadline* once its target is touched. The optimal sequencing decision depends on whether other eligible targets can absorb desired Energy before crossing that deadline.

## Implementation

- `tools/hand_attachment_turn_end.py` owns a printed-source-validated target-bound next-turn attack window and a post-attachment transition.
- `results/hand_attachment_turn_end/reproduce.py` checks both source prints, delayed activation, other-target attachment sequencing, manual and effect-source events, player identity, Ranger-like cancellation, switch/evolution expiry, and prevention of replaying old events.
- Reuses `tools/next_turn_attachment_window.py` and the existing `energy_hand_attachment_events.py` physical hand-copy transitions.

The immutable reaction observes **new** hand-attachment events after physical commitment. When the recorded event affects the attacked physical Pokémon during the permitted turn, it closes the canonical turn budget with `END_TURN`. The outcome retains the underlying physical copy movements and usage history.

## Model boundaries

This narrow transition does not select or pay for attacks or model all of a full turn. For a physical game planner, start and end windows only when the relevant real turn boundaries occur, refresh the target binding after any board change, and apply the reaction immediately after any committed attachment action. The printed next-turn attack effects do not persist through an ordinary Active-to-Bench movement or evolution.

The reproducer models only a single-card attachment at a time, so it does not adjudicate the intra-effect resolution of a simultaneous batch of multiple Energy attachments. This belongs in an eventual causal event scheduler.

The two players' Dragon's Wish and Lazy Howl/Daydream attacks are an abstract legal sequencing witness; whether a deck can realistically use both Attack lines in a concrete matchup depends on its Pokémon access, Energy costs, and board development.

Related: [../next_turn_attachment_window/](../next_turn_attachment_window/), [../energy_hand_attachment_events/](../energy_hand_attachment_events/), [../canonical_turn_sequence_owner/](../canonical_turn_sequence_owner/).
