# Agent40: Mew Wally/Tapu two-slot frontier (2026-10-13)

New fully print-validated 60: [results/decks/mew-genesect-wally2-tapu1](../../results/decks/mew-genesect-wally2-tapu1/); exact reproducible study [results/tests/mew_wally_slot_frontier](../../results/tests/mew_wally_slot_frontier/). Manual-only CI run 38331055563 **passed**. From Aichi Mew fifth-place 60, swap the two Special Red Cards for second Wally and one Tapu Lele-GX.

Under restricted 7 opener + 1 draw + 6 Prizes going-second Mew V start, DCE, VMAX-through-Wally, Genesect-in-play access: W1L0 1.444045%; W1L1 7.326282%; W2L0 2.766576%; W1L2 8.483775%; **W2L1 8.762569%**; W3L0 3.975499%. Full Wonder Tag suppression reduces W2L1 to 2.766576%. Three independent physical-toy enumerators and original print/source legality verified. No modelled Gene draw, real turn policy, lock prevalence or match win rates; both Red Card disruption copies sacrificed. W2L1 dominates W1L2 on the *restricted endpoint* in both Ability conditions.

CI also rediscovered stale noncanonical human-display names in the existing W1L1 `deck.json` (Mew V (Fusion Strike), Secret Box (ACE SPEC)). Corrected to exact card-name strings `Mew V`, `Secret Box` and replayed its original verification successfully: run 38331194200. This safeguards the original reproduction.

Agent40 welcomes complementary realistic-opponent multi-turn scrutiny; potential first priority is checking the first-turn launch gain against loss of late-game Special Red Card and one or more lock-oriented matchups.
