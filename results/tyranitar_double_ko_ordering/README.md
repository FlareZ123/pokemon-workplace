# Two simultaneous Knock Outs under Tyranitar-GX Dusty Ruckus

## Research question

When one Expanded-legal attack Knocks Out two opposing Pokémon simultaneously and multiple KO-replacement effects apply to separate victims, how many distinct conserved physical endpoint states are reachable under a chosen ordering? Does it matter whether one Pokémon's passive replacement effect is represented as a single grouped instance or one target-scoped instance per KO?

## Real card-text scenario

The fixture loads and verifies four print records directly from the repository's `resources/cards/en/*.json` and checks their effective paper-Expanded legality:

- Tyranitar-GX `sm8-121`, a Darkness Stage 2 attacker. Its *Dusty Ruckus* attack deals 130 to the Active and 30 to each Benched **Basic** Pokémon. Its *Lost Out* Ability replaces normal KO disposal by sending the opposing Knocked Out Pokémon and attached cards to the Lost Zone.
- Aegislash `sm11-95`, a Psychic Stage 2 with 130 HP and Darkness ×2 Weakness. Its *Durable Blade* Ability returns it to hand instead of discard when KO'd by opposing attack damage, discarding its attachments.
- Lapras `bw4-25`, a Water Basic with 100 HP. It begins on the Bench with 70 damage, two Basic Water Energy and one Double Colorless Energy.
- Huntail `sv10-55`, a Water Stage 1 with *Diver's Catch*. It remains on the Bench and can retrieve all Basic Water Energy attached to one of its Water Pokémon KO'd by an opponent's attack.

**One Dusty Ruckus:** Aegislash starts undamaged. Its Darkness Weakness doubles the 130 Active damage to 260, exceeding 130 HP. Lapras has 70 prior damage; the additional 30 Bench damage reaches 100 HP. Huntail is an Evolution Pokémon, so Basic-only Bench damage does not affect it. Both Aegislash and Lapras enter the same end-of-attack Knock Out batch.

The physical board includes the full Honedge -> Doublade -> Aegislash stack with one Muscle Band, Lapras with its three Energy cards, and Bench Clamperl -> Huntail. The pre-KO batch comprises Aegislash and Lapras, leaving Huntail to become the new Active. The attacking Tyranitar-GX is an explicit sourced attack-side predicate, while the physical executor materializes the defending board.

Sources: [Tyranitar-GX official card](https://www.pokemon.com/uk/pokemon-tcg/pokemon-cards/series/sm8/121), [Huntail official card](https://www.pokemon.com/uk/pokemon-tcg/pokemon-cards/series/sv10/55), and the provided card database for Aegislash and Lapras.

## Authority boundary

The Advanced Player's Rulebook v3.4 says the **current-turn player** chooses the order of effects triggered when *several* Pokémon are Knocked Out simultaneously. TPCi February 2026 Professor guidance also identifies the current-turn player for KO-trigger ordering during a turn. In this two-KO scenario these two sources agree: the attacking player is the chooser.

The fixture passes both sources simultaneously through `ko_redirection_authorized_order.py` for each candidate witness order. An attempt to submit the order as the defender is rejected. This does not establish whether every candidate effect-instance grouping used in the model is the unique correct formal interpretation of the passive Lost Out Ability; the experiment compares two such groupings explicitly.

## Two exact effect representations

Four destination interactions exist at the level of targeted physical cards:

- Durable Blade versus Lost Out for the Aegislash stack and Muscle Band.
- Diver's Catch versus Lost Out for Lapras's Basic Water Energy.

We examine:

**Grouped Lost Out**: one merged Lost Out destination program covering both Knocked Out targets, plus one Durable Blade program and one Diver's Catch program. There are three abstract effects and six possible total orders. Exactly four physical endpoint states result, with effect-order multiplicities **1, 1, 2, 2**.

**Per-target Lost Out**: one Lost Out program for Aegislash, another for Lapras, plus Durable Blade and Diver's Catch. There are four abstract effects and 24 possible total orders. The same four physical endpoint states result, with multiplicities **6, 6, 6, 6**.

| Aegislash evolution stack | Lapras's two Basic Water Energy | Final position |
| --- | --- | --- |
| Hand | Hand | Huntail promoted, Lapras Lost |
| Hand | Lost Zone | Huntail promoted, Lapras Lost |
| Lost Zone | Hand | Huntail promoted, Lapras Lost |
| Lost Zone | Lost Zone | Huntail promoted, Lapras Lost |

Aegislash's Muscle Band is discarded when Durable Blade acts first and goes to the Lost Zone when Lost Out acts first. Lapras itself and its Double Colorless Energy go to Lost Zone under both routes. All three evolution cards remain together, and all card-class totals are conserved.

**The endpoint reachability is representation-invariant in this witness while the number of abstract effect permutations differs.** This gives another reason not to treat raw effect-order multiplicity as a natural gameplay probability.

## Reproduce and limitations

`python results/tyranitar_double_ko_ordering/reproduce.py` validates exact card-text predicates and legality from the bundled database, checks the two-KO damage window, materializes both Pokémon stacks, prepares one two-Pokémon KO batch, constructs grouped/per-target destination programs, independently compares all endpoint states using full and signature-compressed physical kernels, checks every source-authorized witness, and verifies all card counts and promotion outcomes.

The code explicitly supplies the two victims after checking the attack's damage preconditions; it does not implement a complete two-player attack engine, Prize taking, card draw, or a tournament-resolution arbiter. The grouping variants are research representations. Confirmation of real simultaneous effects' granularity may require a separate card-specific ruling. The result models only the conditional destinations given the chosen program order.

## Broader implication

The mathematical number of orders depends on what counts as an effect instance, whereas strategic utility depends on reachable game states, authority to choose, and future actions. By keeping provenance, effect granularity, materialized card identity and terminal-state equivalence distinct, a rules-aware optimizer can avoid treating syntactic ordering counts as strength.
