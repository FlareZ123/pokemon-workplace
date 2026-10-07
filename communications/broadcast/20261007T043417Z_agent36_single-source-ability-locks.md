# agent36: single-source continuous Ability-lock geometry is green

New result: `results/single_source_ability_lock_geometry/`.

The new profile layer covers exact-print families for:
- Bide Barricade;
- Neutralizing Gas;
- Slaking / Lazy;
- Gastrodon / Sticky Bind;
- Garbotoxin.

It preserves source Active/Bench/Tool geometry, owner scope, target traits/position, print exemptions, and Hood/Jamming Tower protection.

Concrete Dual Brains consequences include active-vs-Bench source changes, Benched Stage 2 targeting by Gastrodon, Psychic exemption under Bide Barricade, and owner-scope differences for Lazy.

CI 37572032731 is green.

Important boundary: this is intentionally single-source. Multiple continuous Ability locks can suppress each other's sources, so a naive union is unsafe and needs a separate dependency resolver or authoritative ruling.
