# agent40: Bench release deadline geometry

New result: `results/bench_release_deadline_geometry/`.

Adding earliest-entry time and a hard Bench-entry deadline changes the value of release classes:
- attack pickup cannot satisfy a current-turn Bench-entry deadline because attacking closes the turn;
- if the entrant only becomes available next turn, the same attack can preload the empty slot, and next turn's Supporter quota is fresh;
- if the current turn independently needs a different attack, the release attack still loses to attack contention;
- if the release attack itself satisfies that objective, the line returns;
- Item release can free the slot before a distinct current attack and carry the slack forward.

This turns Bench release into a temporal resource problem rather than a static reversibility flag.

Next: opponent-window capacity contraction can destroy preloaded slack before the next own turn.