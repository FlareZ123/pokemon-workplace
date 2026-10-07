# Ability suppression can expand or contract Bench capacity

## Question

What happens when Ability lock interacts with Expanded cards whose Abilities change Bench capacity?

## Finding

Ability suppression is not monotonic with respect to Bench space. Suppressing an Ability-based restriction can increase the affected player's capacity, while suppressing an Ability-based expansion can decrease it.

The current Bench-capacity catalog contains three Pokémon Ability sources:

- Eternatus VMAX, Eternal Zone: self expansion to eight under its Darkness-only condition;
- Sudowoodo, Roadblock: opponent restriction to four;
- Glimmora ex, Dust Field: opponent restriction to three while Glimmora ex is Active.

The Stadium sources are a different channel and do not depend on their Pokémon having Abilities.

## Capacity direction under generic Ability suppression

Consider Sky Field supplying an eight-slot expansion.

- Sky Field plus active Roadblock gives the affected player capacity four because the smaller restriction wins. If Roadblock is suppressed while Sky Field remains effective, capacity rises from four to eight.
- Sky Field plus active Dust Field gives the affected player capacity three. If Dust Field is suppressed while Sky Field remains effective, capacity rises from three to eight.
- Eternal Zone alone gives its player capacity eight when its condition is satisfied. If Eternal Zone stops working, Eternatus VMAX's own text instructs the player to discard down to five, so effective capacity contracts from eight to five.

This means a generic state variable such as `abilities_allowed = false` cannot be interpreted as simply adding more constraints. It can remove a restriction source or remove an expansion source, with opposite consequences for board capacity.

## Concrete lock-source coverage

The legal Expanded lock catalog contains several relevant Ability suppressors:

- Garbodor's Garbotoxin removes Abilities broadly except Garbotoxin itself, so it can suppress Roadblock, Dust Field, and Eternal Zone while its condition holds.
- Galarian Weezing's Neutralizing Gas suppresses the opponent's Pokémon Abilities while Weezing is Active, so the direction depends on which opponent capacity Ability is present.
- Wobbuffet's Bide Barricade exempts Psychic Pokémon. The three capacity Ability sources above are outside that exemption in the bundled card data, so their capacity effects are vulnerable while Bide Barricade is active.
- Iron Thorns ex's Initialization suppresses non-Future Rule Box Pokémon Abilities. It reaches Eternatus VMAX and Glimmora ex, while ordinary Sudowoodo has no Rule Box and therefore keeps Roadblock under Initialization.

These are card-text reachability statements. A real board still has to satisfy each lock source's activation geometry and conditions.

## Discrete contraction after suppression changes

Capacity changes are path-dependent because discarded Pokémon do not return if capacity later increases.

A full eight-slot Eternal Zone board that loses the Ability must discard three Pokémon. A Sky Field board temporarily freed from Roadblock can grow to eight; if Roadblock later becomes active again, the same board can be forced from eight to four, discarding four. Re-activating Dust Field can force an eight-to-three contraction, discarding five.

The affected player chooses the discarded Pokémon under these capacity texts, so the stale-occupant buffer from `results/bench_capacity_geometry/` still applies. A dramatic numeric contraction does not guarantee equal strategic damage.

## Active-position coupling

Dust Field adds another dynamic channel because Glimmora ex has to be Active. Switching, retreating, gusting, or Knocking Out the source can remove the three-slot restriction without any Ability lock. Returning Glimmora ex to the Active Spot can reimpose it.

This is another reason capacity should be derived from the full board state at each transition rather than stored as a permanent deck-level parameter.

## Validation

`results/bench_capacity_lock_interactions/reproduce.py` reads the legal capacity catalog and verifies the direction and magnitude of the core transitions:

- Sky Field plus Roadblock: 4, then 8 when the restriction is absent;
- Sky Field plus Dust Field: 3, then 8 when the restriction is absent;
- Eternal Zone: 8, then the normal 5 when the expansion is absent;
- contractions from 8 to 5, 4, and 3 force 3, 4, and 5 discards respectively before stale-buffer valuation.

## Limitations

The reproducer treats suppression as an input state and does not implement the full lock dependency graph. Cards such as Stealthy Hood, Jamming Tower, source positioning, and asymmetric opponent-only suppression can determine whether a specific Ability is actually suppressed.

A combined engine should first resolve lock-source activity and suppression, then derive active capacity effects, then enforce any resulting contraction. That ordering preserves the separation already established by the repository's typed lock kernel.
