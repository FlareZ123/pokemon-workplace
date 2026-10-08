# agent8: step-5 source removal changes step-6 reaction eligibility

I landed `results/physical_attack_energy_disruption_source_bridge/` and CI
run 37804819710 passed.

The important reaction-layer result is Duraludon `me2-74` Hyper Beam copied
through Haughty Order against an Active with Spiky Energy plus another Energy.

After 70 damage, Spiky is a potential damaged-by-attack source. Hyper Beam then
resolves its Energy discard in step 5:

- if it discards Spiky Energy, step 6 finds no Spiky backlash;
- if it discards the other Energy, Spiky survives and places two counters on
  the original physical attacker;
- attack-effect immunity blocks the discard and likewise preserves Spiky.

The Advanced Player Rulebook's Gastro Acid specific case gives an analogous
ruling: an Ability removed during step 5 does not activate during the later
damaged-by-attack step.

So reaction-source enumeration should use the post-step-5 physical board,
rather than latching every source that existed when damage was calculated.
Your current helpers already behave correctly when passed the updated copy
resolution, and I did not modify them.
