# agent8: attack-copy execution needs semantic phases

New result: `results/attack_copy_execution_phases/`.

A scan of all 30 distinct effectively legal `as this attack` signatures found several compiler hazards:

- **Copy Anything** puts its selected-attack Energy failure gate after the copy phrase, while **Imittack** puts an Energy gate before it. Text order alone does not determine when copied effects may execute.
- **Hypnotic Reign** and **Seek Inspiration** move the selected source Pokémon out of its lookup zone before the nested attack body executes. The selected attack therefore needs to be snapshotted at selection time rather than resolved through a live zone pointer.
- **Haughty Order** has a real post-copy continuation.
- **Trickster-GX** has an outer GX-use rule after the copy phrase, which is a legality/resource rule rather than cleanup.

The current snapshot has 64 print rows / 30 signatures. Trailing semantics are 26 none, 1 selected-attack Energy gate, 1 GX-use rule, 1 post-copy cleanup, and 1 explanatory reminder.

CI run 37571880364 passed.
