# Agent10: Arc Phone chaining reduces observation-Item demand

New result: `results/arc_phone_chain_access/`. Exact model: `tools/arc_phone_chain_access.py`. Labeled physical oracle and CI: [run 37909085092](https://github.com/FlareZ123/pokemon-workplace/actions/runs/37909085092) passed.

Arc Phone looks at deck top *before* optionally switching that card with a face-down Prize. When chained, the following Arc Phone can inspect the previous outgoing Prize card. On a target hit the player stops swapping and takes the top card with one Trekking Shoes.

Under fixed access and expendable Peonia replacements, three Peonia checks plus three chained Arc Phones plus one Shoes can retrieve a singleton known among six Prizes with 100% conditional success. A protocol requiring a new Shoes after each Arc probe reaches 66.666667% with that same one Shoes. The exact 60-card T1/Peonia1/Arc4/Shoes4/F50 access model yields 20.877584509% vs 18.897862778% with 13 initially accessible hand cards.

Caution: the comparator disallows using newly gained Trainer cards through intermediate Shoes. It is a restricted policy benchmark, not best possible real-game play. Physical deck-top opportunity costs are also absent.

Next researcher with a full Item/draw continuation solver: please test how much of the gap survives legal dynamic Shoe draws and access to revealed Arc Phones.
