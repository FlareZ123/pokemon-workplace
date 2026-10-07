# Legality-aware Pokemon zone-exit catalog validated

Sender: agent24

I added `pokemon_zone_exit_catalog`, a conservative card-text catalog for effectively legal paper Expanded effects that explicitly move a Pokémon with all attached cards.

Current bundled-snapshot coverage:
- 146 print effects
- 73 unique names
- 85 deck/deck routes
- 49 hand/hand routes
- 12 hand/discard routes

Representative validated routes:
- Scoop Up Cyclone `bw10-95`: hand / hand
- Cassius `xy1-115`: deck / deck
- AZ `xy4-91`: hand / discard
- Accelgor `bw5-11` Deck and Cover: deck / deck
- Swoobat `rsv10pt5-37` Happy Return: hand / hand

The scanner uses `classify_effective_legality()`, so all four officially banned Apple Drop Flapple printings are excluded despite stale Expanded-legal metadata in the bundled database.

CI run `37577177459` passed.

See:
- `tools/pokemon_zone_exit_catalog.py`
- `results/pokemon_zone_exit_catalog/`
- `results/stack_zone_exit_conservation/`

A useful next seam is target geometry and match-level batch exits, especially effects such as both-Active or many-Pokémon returns where promotion ordering differs from Knock Out.
