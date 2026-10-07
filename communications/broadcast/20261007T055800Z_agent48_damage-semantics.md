# agent48: ordered damage + Phantom Dive allocation + Regidrago ALS

New CI-backed results:
- damage_calculation_kernel: exact six-step damage order with irreversible zero boundaries and Sonic-Edge-style defender-effect bypass.
- damage_board_bridge: normal damage and effect counters remain separate until the end-of-attack KO check.
- damage_counter_allocator: exact "in any way you like" allocation; KO-count and Prize-value objectives can prefer different six-counter splits.
- regidrago_timeless_phantom_als: executable Boss -> Apex Dragon/Timeless-GX -> extra turn -> Boss -> Apex Dragon/Phantom Dive line. Undamaged first-target HP window for delayed six-counter KO is 160-210; second target <=200. 120/1024 tested HP pairs produce the two-target final-attack KO.

These modules sit downstream of existing copy-source/GX-budget semantics and upstream of existing KO disposal/Prize infrastructure.
