# Physically conserved self-shuffling Active Pokémon: Beheeyem into Stoutland

## Question

Beheeyem \`sm11-91\` uses *Mysterious Noise* to impose a next-opponent-turn Item restriction, then shuffle itself and all attached cards into its owner's deck. The earlier strategic calculation assumed it could leave a lock anchor Active while reusing the same Triple Acceleration Energy \`sm10-190\`. This regression checks the **physical-card conservation** underlying that assumption.

The established \`tools/stack_knockout_conservation.py\` removes whole evolution stacks upon Knock Out by routing them and all attached cards to discard. Reusing that Knock Out operation for Beheeyem would be an incorrect state transition. A self-shuffle must return the entire evolution stack and attachments to the **deck**, with no Knock Out or Prize award.

## Implemented transition

New reusable \`tools/active_self_shuffle_conservation.py\` composes the existing \`StackBoardMaterialState\` (a full physical-stack board and \`IdentityLedger\`) with a source-destination change:

1. Require a live Active Pokémon.
2. Validate the chosen new Active is an existing Benched Pokémon, unless no Pokémon survive; in that case retain the terminal board as \`None\` for the game's win/loss handler.
3. Remove the complete current Active Pokémon object from play.
4. Route every physical card in its evolution stack from \`in_play\` to \`deck\` and dematerialize the now-exchangeable copies.
5. Route each attached Energy, Tool or other attachment from \`attached\` to \`deck\` and dematerialize.
6. Keep all other Pokémon and attached cards in place, and assert per-class card totals are exactly conserved.

This is a mechanical transition. Attacker eligibility, Energy-cost validation, attack damage, player-level lingering Item restriction, deck shuffle randomness, future turn-end effects, and win/loss resolution remain owned by other modules. The function does not imply that ordinary evolution or other attack prerequisites have already been satisfied.

## Regression witness

A concrete miniature board has:

- Active Elgyem A evolved into Beheeyem, with one attached Triple Acceleration Energy;
- Benched Lillipup -> Herdier -> Stoutland, with a physical Float Stone attached;
- Benched Elgyem B.

All eight Pokémon/attachment card instances are materialized in the ledger. Applying the active self-shuffle and choosing Stoutland as the new Active:

| Card or state | Before | After |
| --- | --- | --- |
| Elgyem A | lower card of Active evolved stack | One exchangeable Elgyem returned to deck |
| Beheeyem A | top card of Active evolved stack | One exchangeable Beheeyem returned to deck |
| Triple Acceleration Energy | attached to Beheeyem A | One exchangeable TAE returned to deck |
| Stoutland line | Benched complete three-card evolution stack | Same physical line Active |
| Float Stone | attached to Stoutland | Same physical instance still attached |
| Elgyem B | Benched Basic | Same physical instance remains Benched |
| Discard pile | no cards in miniature ledger | no cards |
| Prize award | no Knock Out | none |

The transition also rejects invalid promotions. A separate lone-Active scenario verifies that self-shuffling the only Pokémon produces a terminal \`board=None\` while putting its physical card back into the deck. The game-resolution owner must separately evaluate the resulting no-Pokémon loss condition.

## Strategic and modeling implications

The principal strategic distinction is **card conservation across the self-vacating attack**: the attacker Pokémon, its underlying Elgyem, and Triple Acceleration Energy genuinely become searchable deck resources again. The Stoutland source and attached Float Stone remain in play. The earlier alternating-Elgyem access burden therefore refers to deck retrieval, not replacement copies permanently lost to discard.

The next integration is to marry this physical shuffle with the already-existing \`AttackRestrictionWindow\` for Mysterious Noise and board-derived continuous restrictions for Stoutland's \`Sentinel\`. It should verify that the attack-applied Item restriction persists into the next opponent turn despite the source leaving the board, while Stoutland's Active-dependent Supporter restriction is reevaluated from the promoted board.

## Reproduction

Run:

\`python results/beheeyem_physical_self_shuffle/reproduce.py\`

The script asserts full-stack, Energy and Tool routing, board validity, invalid-promotion rejection, and exact physical/exchangeable card-count conservation.
