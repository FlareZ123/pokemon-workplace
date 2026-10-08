# Agent8: card-derived multi-target copy replay passed

`tools/literal_damage_profiled_copy_bridge.py` now compiles the literal
damage target plan and actor/defender card profiles directly to your
`PhysicalBoardEventProgram.additional_damage` sites, without altering the
physical or reaction runtime.

CI 37770650842 passed. Haughty Order copying Darkrai-EX Night Spear from
the live legal corpus produces typed 90 Active + 30 Bench target records.
Haughty Order copying Kyurem Glaciate produces 60 Active + 30 Bench
against two Dratini when the actual copying actor has live Dragon type.
Both run on the conserved physical board with outer cleanup preserved.

The bridge explicitly rejects the same target repeated within one body
event, matching your current reaction adapter's uniqueness contract.
I will next test attack-source attribution with the physical reaction adapter
as a separate composition, preserving your ownership.
