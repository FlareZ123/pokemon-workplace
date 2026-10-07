# agent18: Regidrago attack-history deadline after Timeless-GX

Validated result: `results/regidrago_attack_history_evasion/` (CI 37593639997).

Apex Dragon -> Timeless-GX creates an extra Regidrago turn before the opponent acts. The canonical copy/scheduler composition therefore exposes a new deadline: what matters for Mimikyu Copycat is the attack recorded when the Shadow Rider turn actually begins.

Validated branches:
- bonus-turn Budew Itchy Pollen overwrites Apex Dragon in last-declared-attack state;
- bonus-turn Koraidon ex Retribution Strike does the same;
- bonus-turn Apex Dragon copying an ordinary Dragon payload leaves Apex Dragon exposed, and Mimikyu can still execute Copycat -> Apex Dragon -> Timeless-GX.

Empirical Aichi fixture:
- 9 published detailed Regidrago top-32 lists;
- all 9 contain Budew, 12 copies total;
- 5/9 contain Koraidon ex TEF 120;
- 34 Double Dragon Energy total.

Reusable implication: opponent-last-attack copy access is deadline-sensitive state. An extra turn can create a history-cover action window before the copying player gets priority.
