# Energy-from-hand events

This result separates Energy attachment event history from the ordinary manual attachment quota.

A conservative legal Expanded scan finds 55 print rows across 33 card names that react to Energy being attached from hand.

The regression uses Alolan Exeggutor ex. Its Tropical Frenzy effect attaches two Basic Energy cards from hand. The model records two hand-attachment events while leaving the ordinary manual attachment unused. A later normal attachment records a third event and consumes the manual quota.

This matches the Advanced Player's Rulebook example that several Energy cards attached from hand by an effect can each activate relevant attachment-triggered effects.

Implementation:
- `tools/energy_hand_attachment_events.py`
- `tools/energy_hand_attachment_corpus.py`

Regression:
- `results/energy_hand_attachment_events/reproduce.py`

The resulting rule for state design is simple: source-zone event history and action quota are separate facts.
