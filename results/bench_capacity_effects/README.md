# Dynamic Bench capacity in paper Expanded: 3, 4, 5, and 8 are distinct states

## Question

The ordinary Pokémon TCG Bench holds five Pokémon, but Expanded contains effects that change how many Benched Pokémon a player may have. Which legal cards do this directly, and how much can that change the realism of transactional support lines?

Implementation: `tools/bench_capacity_effect_catalog.py`  
Reproducer: `results/bench_capacity_effects/reproduce.py`

## Conservative card-pool census

A literal scan of legal Black & White-onward card text finds 17 legal prints, 8 conservative text signatures, 7 unique card names, and 9 conservative gameplay fingerprints.

| Card | Capacity | Scope | Geometry |
| --- | ---: | --- | --- |
| Parallel City | 3 | chosen side | Stadium restriction |
| Glimmora ex | 3 | opponent | Active-dependent Ability restriction |
| Collapsed Stadium | 4 | both players | Stadium restriction |
| Sudowoodo | 4 | opponent | Ability restriction |
| Eternatus VMAX | 8 | self | conditional Ability expansion |
| Area Zero Underdepths | 8 | both players meeting its condition | conditional Stadium expansion |
| Sky Field | 8 | both players | Stadium expansion |

Area Zero Underdepths appears as two conservative text signatures and more than one gameplay fingerprint because the bundled prints differ in wording or metadata. The strategic capacity effect is the same eight-slot class here.

## Capacity changes support-chain feasibility

Use the typed Bench scheduler from `bench_capacity_schedule/`. Hold four persistent core Bench slots and ask for three transactional support activations with no release resources.

| Current Bench capacity | Transactional slots | Maximum support activations | Three-support line feasible? |
| ---: | ---: | ---: | --- |
| 4 | 0 | 0 | No |
| 5 | 1 | 1 | No |
| 8 | 4 | 3 | Yes |

This is a discrete state change. A fixed “Bench cost” on a support Pokémon is insufficient unless current capacity and occupancy are also represented.

At capacity five, a four-slot core leaves one support slot. Reusing that slot requires a real release transition. At capacity eight, the same three support Pokémon can coexist with the four-slot core without cleanup. At capacity four, the assumed core board fills the entire Bench.

## Expansion is conditional state

**Sky Field** expands both players to eight while it remains in play and specifies collapse to five when it leaves play.

**Area Zero Underdepths** gives eight slots only to a player with a Tera Pokémon in play. Losing the condition or Stadium can collapse the Bench to five.

**Eternatus VMAX** gives its player up to eight only under its Darkness-only board condition. If the Ability stops working, its text instructs the player to discard back to five.

A state model therefore needs the source and condition of expanded capacity. Recording only “capacity = 8” loses the dependency that can later force a discard transition.

## Restriction is interaction

**Collapsed Stadium** reduces both players to four. **Parallel City** can impose three on the chosen side. **Sudowoodo's Roadblock** restricts the opponent to four. **Glimmora ex's Dust Field** restricts the opponent to three while Glimmora ex is Active.

These states can invalidate a support chain immediately. They can also force a player to choose existing Bench occupants to discard when capacity shrinks.

That forced discard can destroy a board. In some states a player may deliberately use a self-affecting contraction to remove an unwanted support Pokémon, which should still be represented as a real Stadium or capacity transition.

## Relation to Bench debt

Capacity expansion offers an alternative to immediate release pressure because it increases simultaneous residency. Capacity contraction creates mandatory cleanup pressure.

A complete occupancy model therefore needs current capacity, the source and condition maintaining it, current occupants and roles, collapse behavior when the source disappears, and target geometry for self, opponent, both players, or a chosen side.

## Method and validation

The scanner searches legal Expanded Trainer and Ability text for literal wording that allows or forbids a numerical number of Benched Pokémon. It uses the repository's existing print-level legality overlay.

The reproducer asserts the seven names, their numerical capacities and target scopes, then feeds capacities four, five, and eight into the exact Bench scheduler.

A broader text search was used to distinguish real capacity effects from unrelated text that merely mentions several Benched Pokémon.

## Limits

The census is conservative and wording-based. It does not treat one-time effects such as Avery or Bellelba & Brycen-Man as persistent capacity changes because those effects discard down to a number without changing the ongoing maximum.

It does not yet simulate simultaneous capacity effects, Ability suppression, Stadium replacement, Tera or Darkness-board maintenance, or the exact discard policy when capacity contracts.

## Next useful work

The strongest next step is a capacity-transition kernel. It should change capacity while preserving explicit occupants, then require a discard policy whenever occupancy exceeds the new maximum.

Such a kernel can quantify which support or core occupants are sacrificed, how much prior setup value is lost, and whether deliberately collapsing capacity is a viable way to repay Bench debt compared with spending a Supporter or attack on pickup.
