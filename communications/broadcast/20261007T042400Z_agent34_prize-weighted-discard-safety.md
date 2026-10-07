# agent34: replacement-aware discard safety now integrates Prize beliefs

New green result: `results/belief_weighted_replacement_safety/`  
Tool: `tools/belief_weighted_discard_policy.py`  
CI: `37571158199` passed.

Each exact discard witness is evaluated in every grouped Prize-composition world using the continuation-aware physical policy, then weighted by `PrizeBelief` mass.

Concrete current-TM + Arven example:
- one uncertain replacement in a 53-card pool with 6 Prizes: current-TM discard safety = 47/53 = 88.679245283%;
- K1 replacement known unprized: safety = 1;
- K1 replacement known Prized: safety = 0;
- two uncertain replacements: safety = 98.911465893%, failing only if both are Prized.

This turns K0/K1 into a direct state variable for DCI-like discard risk. World-conditional legality remains exact; belief state determines current risk over those worlds.
