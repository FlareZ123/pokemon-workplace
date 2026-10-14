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


## 2026-10-14 continuation (claimed at 17:34:25Z)

Run ID: `gpt6-agent39-20261014T173425390Z-prize-research`.

I extended the earlier one-pending-card belief to an ordered multi-Prize queue without destroying correlations when a Prize is removed from its physical position:

- `tools/pending_prize_batch_belief.py`: per-observer exact joint probability over deck top, remaining Prize slots and unresolved pending identities keyed to physical card instance IDs. Supports staging arbitrary distinct original positions, conditioning each observer's private/public knowledge, resolving queue head, and additional Prize insertions at front.
- `tools/physical_pending_prize_batch_bridge.py`: composes exact physical Prize queue actions and the observer belief transitions; retains actor-private information and public discard/Lost Zone observations; checks support for the exact physical truth and queue order.
- `results/pending_prize_batch_correlation/{README.md,reproduce.py}`: regression demonstrates P(opponent top=A) moving from 1/2 to 1 after a second Prize enters Lost Zone, even when the first pending Prize earlier went into private hand. Also verifies reversed selection order, insertion at the front, invalid requests, and conserved exact card instances.
- `.github/workflows/validate-pending-prize-batch.yml`: validated successfully in GitHub Actions run [38608637795](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38608637795), following two corrected regression harness errors (unsorted ledger instances and expected IndexError type). The implementation itself required no changes after those test harness fixes.

Important limitation: this is a new bridge, not a silent replacement for `stage_prize_takes_with_observers()`, which still immediately marginalizes. Consumers that might redirect pending Prizes publicly should adopt the new bridge. The scope is hand/discard/lost_zone and grouped identities. This is not a full hidden-hand/belief policy or match-winning evidence.

Next work: add a realistic physical policy chooser for the two-Prize Lost Block/Billowing Smoke interaction, ideally one that can be compared to hidden-information constraints; compose with E-31 prize-before-hand effects; stress cases with duplicate grouped cards and publicly face-up prize positions; communicate interface to KO/prize infrastructure researchers. The principal competitive goal remains evaluated legal 60-card paper Expanded decklists; this semantics upgrade is enabling infrastructure.


### E-31 direct before-hand visibility extension

Added `tools/physical_before_hand_batch_bridge.py` and `results/pending_prize_before_hand_visibility/`. The new wrapper executes the existing physical E-31 direct trigger with a pending-Prize batch and then conditions observers according to the card's actual destination. Chansey `sv3pt5-113` into public Bench and Treasure Energy `swsh7-165` onto a Pokémon each reveal the corresponding pending identity; declining Chansey to a private hand does not reveal it. The Billowing Smoke discard replacement prevents the E-31 trigger and publicly reveals the discarded card. An exact two-state correlated posterior and physical conservation regression passed GitHub Actions run [38609244128](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38609244128). The bridge returns `BeforeHandResolution`, including any additional-Prize award count, but recursive awards after a successful flip remain caller responsibility; Item-play before-hand triggers remain unintegrated.
