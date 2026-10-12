# Vileplume runner-up's Stoutland Wild Tackle: pinned Twinleaf self-damage error

## Paper rule and source witness

The published 2026 Aichi runner-up Vileplume control 60-card list contains one **Stoutland** (`bw7-122`, Boundaries Crossed 122). Its **Sentinel** Ability, while Active, prevents the opponent from playing Supporter cards from hand. Its **Wild Tackle** attack deals 90 to the opponent and, on a tails coin flip, **20 self-damage** to Stoutland.

The pinned Twinleaf Stoutland `ptcg-server/src/sets/06-black-and-white/set-boundaries-crossed/stoutland.ts` implements this tails callback by constructing `new DealDamageEffect(effect, 10)` targeting the player's own Active Pokémon. That is **10 damage too little** and can understate self-KO risk if Stoutland repeatedly attacks to keep Sentinel in the Active position.

This claim follows directly from the bundled English `bw7-122` attack text and the pinned upstream implementation. This is an engine rule mismatch; no claim about likely game outcomes follows from the difference alone.

## Research-owned correction

The [Stoutland runtime adapter](../../../simulation/twinleaf/hooks/stoutland-wild-tackle.cjs) overrides only Wild Tackle's attack effect for the pinned class. It uses Twinleaf's original `COIN_FLIP_PROMPT` and `DealDamageEffect` interfaces, preserving coin arbitration, target location, damage reducer, and the rest of Stoutland's abilities and attacks. On tails, the damage becomes 20. The hook is idempotent and leaves upstream code untouched.

The [single-file attack-level regression](../../../simulation/twinleaf/test-stoutland-wild-tackle.cjs) tests the old pinned source before installation (10), the corrected tails outcome (20), the heads outcome (zero self-damage), one-time installation and the self-targeting slot. The standard [bounded tournament runner](../../../simulation/twinleaf/tournament-bounded-match.cjs) installs this third semantic correction alongside the Underworld Door and Celestial Roar hooks before each game, and includes `stoutland_wild_tackle_self20_v1` in its per-trace/report `engine_hooks` label.

Both Twinleaf manual workflows run the Stoutland SFT before producing headless matchup diagnostics.

## Executed validation

[Paired manual CI 38302051788](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38302051788) passed the Stoutland old-versus-fixed coin branch regression, the real bounded-runner hook-installation test, both earlier source-specific hook tests and a physical Vileplume vs Shadow Rider 60-card pair. The runs finished normally with three installed `engine_hooks` labels.

The native AI did **not** choose Wild Tackle in either game: the Vileplume side's recorded attacks were Roar, Massive Bloom, Allergic Explosion-GX, Collect and Itchy Pollen. Thus the full-game pair validates safe integration but does not observe the corrected Stoutland damage during gameplay. Both wins belonged to the Shadow Rider bot under its weak native policy. Those outcomes cannot rank the two published archetypes.

## Boundaries

This regression isolates the printed self-hit and native `DealDamageEffect` payload. It is deliberately agnostic about whether a particular control bot elects to attack with Stoutland, whether the opponent creates enough damage to KO it, and the comparative value of Item and Supporter locks. Real game matchups still need a legal policy against a varied field. Engine outcomes from older unguarded traces should not be treated as identical-semantic samples.
