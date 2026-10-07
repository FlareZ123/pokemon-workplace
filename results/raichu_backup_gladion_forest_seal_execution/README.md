# Forest Seal Stone closes the timed backup-Gladion gap only when its physical gates are live

## Question

The timed Raichu result shows that, after Quick Ball establishes Alolan Raichu is Prized, a backup Gladion may be present in deck while random Dark Asset access is too slow.

Can Forest Seal Stone convert that deck presence into same-turn material access while preserving the later Gladion Supporter window?

Yes, when each physical prerequisite is satisfied.

Implementation: `tools/forest_seal_star_alchemy.py`  
Regression: `results/raichu_backup_gladion_forest_seal_execution/reproduce.py`

## Card-text basis

The bundled Expanded card data records:

- Forest Seal Stone `swsh12-156`: the attached Pokémon V can use Star Alchemy; Star Alchemy searches the deck for one card; only one VSTAR Power may be used in a game.
- Crobat V `swsh3-104`: a Basic Pokémon V.
- Gladion `sm4-95`: a Supporter that moves one face-down Prize into hand and shuffles the played Gladion into the remaining Prizes.

The current rules treat Pokémon Tool play through its own Tool channel, distinct from Item play.

## Successful physical line

The regression starts after Crobat V is already on the Bench and Alolan Raichu is physically Prized.

Forest Seal Stone is in hand and the backup Gladion is in deck.

The executed line is:

`attach Forest Seal Stone to Crobat V -> Star Alchemy: backup Gladion -> Gladion: Alolan Raichu`

The transition verifies that:

- Forest Seal Stone moves from hand to the attached zone;
- Crobat V gains the exact Tool attachment;
- Star Alchemy moves the backup Gladion from deck to hand;
- the VSTAR Power budget becomes spent;
- Gladion then moves Alolan Raichu from Prize to hand;
- played Gladion moves into Prize;
- the ordinary Supporter window is consumed only by Gladion.

This is the deterministic route anticipated by `raichu_backup_gladion_timing/`.

## Gate failures

The same regression rejects the route when:

- Tool play is locked;
- Crobat V already has a Pokémon Tool;
- the VSTAR Power has already been used;
- Crobat V's Abilities are suppressed;
- Forest Seal Stone's Tool effect is suppressed;
- Forest Seal Stone is attached to a non-V Pokémon;
- the backup Gladion is itself Prized.

The route therefore reaches the 90% post-search topology ceiling from the timing result only in states where Forest Seal Stone is actually available and every listed gate remains live.

## Why this matters for connector realism

The timing result separated deck presence from deadline access.

This execution result adds another layer: even a deterministic search effect is not automatically executable because the connector has a physical host, a Tool slot, an Ability state, a once-per-game budget, a Tool-effect state, and a target-zone requirement.

For this line, the useful representation is:

`backup in deck -> Forest Seal available -> Tool attachment legal -> Crobat V eligible -> Star Alchemy live -> VSTAR unused -> backup in hand -> Supporter window -> Prize rescue`

Skipping any of those transitions turns the connector back into theoretical access.

## Relationship to Computer Search

The existing Raichu physical Computer Search continuation already demonstrates the complementary deterministic route:

`Quick Ball -> Crobat V -> Dark Asset: Computer Search -> Computer Search: Gladion`

That route preserves the Supporter window as well, but it requires two residual discardable cards.

Forest Seal Stone therefore replaces a discard gate with a Tool/VSTAR/Ability gate. The two connectors reach the same material endpoint through different constrained resources.

## Limits

This result is an execution witness rather than a probability model.

It does not estimate how often Forest Seal Stone is in hand after the conditioned Quick Ball search, nor how often Tool lock, Ability lock, Tool-slot contention, or prior VSTAR use occurs in real games.

It also does not choose between Star Alchemy for Gladion and competing VSTAR targets.

## Next useful work

A high-value quantitative extension is a conditional connector race after K1:

- random Dark Asset exposure of the backup Gladion;
- Computer Search exposure plus its residual two-card discard gate;
- Forest Seal Stone exposure plus its Tool/VSTAR/Ability gates.

The event union should preserve overlap and connector opportunity cost rather than adding marginal probabilities independently.
