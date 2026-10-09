# Rules-grounded Switch and Energy Switch wording

The paper Expanded board has one Active Pokémon. The historical Item
Switch phrase "Switch 1 of your Active Pokémon with 1 of your Benched
Pokémon" therefore describes the same transition as the current
"Switch your Active Pokémon with 1 of your Benched Pokémon".

The historical Energy Switch Item phrase "Move a basic Energy card
attached to 1 of your Pokémon to another of your Pokémon" also describes
the current C-10 Energy-card movement. The HGSS print hgss1-91
accidentally omits the word "to" after "attached", without changing
the indicated source and destination.

The exact text canonicalizer tools/basic_switch_rule_semantics.py
modifies only these full strings when they occur on Item Trainers
named Switch or Energy Switch. It leaves other card texts, non-Item
historical prints, costs, and action classes unchanged.

Fifteen archived Item prints match: eight Switch and seven Energy
Switch. Thirteen were previously supported only by 2012 historical
official no-reference reprint evidence; two previously unresolved HGSS
prints now acquire an exact current-semantic equivalence to BW1
counterparts.

The current resolver accordingly has 149 exact candidates,
26 historical-only candidates, 3,961 semantic-review records, and
222 high-confidence candidates. Its total outside same-name pool
remains 4,260.

Evidence: bundled card text; bundled Advanced Player's Rulebook A-03,
C-03 and C-10; existing historic no-reference evidence; current
semantic fingerprint witnesses.

Reproduce with python -m results.basic_switch_rule_semantics.reproduce.
