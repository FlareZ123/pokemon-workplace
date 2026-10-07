# Dream Ball lock-bypass candidate catalog

## Question

Among effectively legal Evolution Pokémon with lock effects, how many have Ability geometry compatible with Dream Ball placing them directly onto the Bench, and how many still require another recognized activation condition?

The cross-catalog finds a small, strategically concentrated surface.

Implementation: `tools/dream_ball_lock_bypass_catalog.py`  
Regression: `results/dream_ball_lock_bypass_catalog/reproduce.py`

## Method

This result joins two existing conservative catalogs at exact print ID plus Ability name:

- the Dream Ball Evolution-Ability geometry catalog;
- the lock-effect catalog.

The join preserves the lock dimensions, target scope, and lock activation class rather than flattening every result into "Dream Ball establishes a lock."

A row is Dream Ball geometry-compatible only when the Evolution Ability's own entry/position wording is compatible with direct Bench placement. The lock catalog then supplies any recognized activation requirement such as:

- `active`;
- `tool_attached`;
- `stadium_required`;
- `bench`;
- `passive`.

This remains a conservative candidate screen. A `passive` row can still have conditions outside the lock catalog's activation taxonomy.

## Audited counts

The current effectively legal paper-Expanded card pool contains 50 exact Evolution-Pokémon lock rows across 50 exact prints.

Of those:

- 22 exact rows are compatible with Dream Ball's direct Bench geometry;
- all 22 are also positionally compatible with remaining on the Bench;
- 11 have no recognized extra activation prerequisite;
- 10 require a Pokémon Tool;
- 1 requires a Stadium.

Among the 22 Dream Ball-compatible rows, lock dimensions occur as follows:

- Ability suppression: 13;
- Item restriction: 2;
- Special Energy attachment restriction: 1;
- Special Energy effect suppression: 2;
- Stadium restriction/effect: 1;
- Tool attachment restriction: 1;
- Tool effect suppression: 2.

Dimension counts can exceed row counts when one Ability affects several channels.

The compatible target scopes split evenly in this catalog:

- 11 affect both players or a global scope;
- 11 affect the opponent.

## Boundary witnesses

Vileplume `xy7-3`, Irritating Pollen:

- Dream Ball geometry-compatible;
- lock activation `passive`;
- Item lock dimension;
- no recognized extra activation prerequisite.

This is the line already executed in `dream_ball_vileplume_lock_line/`.

Alolan Muk `sm1-58`, Power of Alchemy:

- Dream Ball geometry-compatible;
- lock activation `passive`;
- Ability-suppression dimension;
- no recognized extra activation prerequisite.

Garbodor `xy9-57`, Garbotoxin:

- Dream Ball geometry-compatible;
- Ability-suppression dimension;
- still requires `tool_attached`.

Dream Ball can bypass the Trubbish evolution prerequisite, but Dream Ball alone does not complete Garbotoxin.

Galarian Weezing `swsh2-113`, Neutralizing Gas:

- Evolution lock row;
- activation `active`;
- not Dream Ball Bench-geometry-compatible.

Dream Ball can place the card on the Bench, while the lock does not become live until the Pokémon reaches the Active Spot.

## Finding

"Dream Ball can fetch this lock Pokémon" is too coarse for an executable strategy model.

There are at least three distinct cases:

1. direct Bench placement is positionally compatible and no recognized extra activation prerequisite remains;
2. direct Bench placement is compatible, while another resource such as a Tool or Stadium is still required;
3. the lock itself requires a different position, such as the Active Spot.

The distinction is an AMR issue as much as a connectivity issue. A search graph can connect Dream Ball to all of these Evolution Pokémon, while their realistic lock establishment costs differ sharply.

## Limits

The 11 rows with no recognized extra activation prerequisite should be read as "no prerequisite recognized by the current lock activation taxonomy." This is not proof that every other card-text or game-state condition is satisfied.

The result counts exact prints, not unique gameplay variants.

It does not model whether the selected lock harms the Dream Ball player's own board, whether the opponent can immediately remove or suppress the lock, or whether allocating deck space to Dream Ball plus the lock target is competitively worthwhile.

It also does not rank the 22 candidates. A useful follow-up is to execute additional high-impact lines such as Dream Ball into Alolan Muk, then test how that lock interacts with support Pokémon, opposing Ability engines, and the Dream Ball player's own board.
