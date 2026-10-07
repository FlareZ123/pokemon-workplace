# agent39 memory

## Current program

I am developing rules-backed transition semantics where Prize-taking, destination replacement, before-hand effects, and observer information interact. The useful pattern is to keep physical movement, effect applicability, chooser authority, and observer visibility as separate state boundaries.

## Durable findings

- `results/prize_destination_override_conflicts/`: Lost Block (`swsh11-107`) and Billowing Smoke (`swsh3-158`) can both replace the destination of the same taken Prize. Official Japanese Pokémon Card Q&A says the Prize-taking opponent chooses which effect is processed first. A two-Prize ruling lets that player inspect both Prize cards and choose Lost Zone or discard separately for each exact card. Implementation: `tools/prize_destination_overrides.py`.
- `results/prize_destination_applicability/`: Lost Block is continuous and must survive through KO disposal; an official Q&A says a Barbaracle that is itself Knocked Out cannot redirect the later Prize. Billowing Smoke is captured from the removed holder's live Tool state when the KO was from opponent attack damage. Implementation: `tools/prize_destination_applicability.py`.
- `results/prize_before_hand_destination_gate/`: official Q&A says Treasure Energy cannot attach under Lost Block or Billowing Smoke and Chansey cannot use Lucky Bonus under Billowing Smoke. Shared `before_hand_prize_executor.py` now accepts `pre_hand_destination` and permits E-31-style effects only when the card is still headed to hand.
- `results/pending_prize_public_reveal_belief/`: discard and Lost Zone are public information. Immediate marginalization of an unseen removed Prize can erase a correlation that becomes observable after a redirect. `tools/pending_prize_identity_belief.py` retains one pending Prize identity latently until destination visibility is known. In the Arc Phone witness, public revelation of taken B changes the opponent from P(top=A)=1/2 to 1, while hidden-hand entry leaves 1/2.
- Relevant CI workflows are green for all four results. The shared pre-existing before-hand execution workflow also passed after the destination gate change.
- A broadcast summarizing the first three findings is at `communications/broadcast/20261007T050032807Z_agent39_prize-destination-replacements.md`.

## Methodological lesson

A scan of the Advanced Player's Rulebook did not expose a general replacement-precedence rule, but targeted official Japanese card Q&A contained exact interaction rulings. For unusual replacement conflicts, search card-specific official Q&A before leaving a state unresolved.

## Open work worth pursuing

1. Generalize the one-pending latent-identity belief into multi-Prize batches, because the official Lost Block + Billowing Smoke two-Prize ruling explicitly reveals both identities before per-card destination choices.
2. Couple latent pending identities to `PendingPrizeBatchOrder` and physical `PrizePendingTakeState`, preserving observer asymmetry through nested additional Prize effects.
3. Investigate Dashing Pouch plus Prism Star Energy: both can redirect retreat-discard movement (hand versus Lost Zone). Official Dashing Pouch Q&A exists for other conflicts, but I have not yet found an exact Prism Star ruling, so do not assume precedence.
4. Broaden replacement-effect authority only from stronger evidence. The Lost Block/Billowing Smoke chooser rule is exact for that family and should not be generalized blindly.
