# Aichi Mega Absol vs Regidrago: paired native-policy diagnostic

**2026-10-13**. [Pinned GitHub Actions trace, run 38398794746](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38398794746), artifact `twinleaf-full-deck-matchup-report` (SHA-256 in artifact metadata). Research revision `08bdcd646c03dbc643775d1455f60d09eb843113`, Twinleaf pin `3348ebdc898f175a2ed8f999133cd13d1afd01f5`, uniform shuffle, separated RNG streams, policy `native`, seed `20261013`, both seat orientations.

Both games terminated without errors and awarded wins to **Mega Absol/Garbodor**. However, the losing **Regidrago VSTAR never attacked in either game**. Native SimpleTacticsAi made 9 passes in the 18-turn first orientation and 23 passes in the 47-turn reverse orientation. It used Legacy Star once in each game but failed to generate any attacking response. Mega Absol took six Prizes in each; the attacker used Terminal Period twice in each orientation, but Prize captures were recorded later from Claw of Darkness.

This pair is **diagnostic evidence of policy failure/low adversarial pressure**, not evidence that Absol is favored against an optimally played Regidrago. With one seed pair and a documented unmasked hidden-information oracle, no match win percentage can be estimated. The paired evaluator itself reports a 95% conditional Hoeffding score interval [0,1].

**Next test:** inspect why native RetreatTactic, Supporter and Energy sequencing failed to move a functional Regidrago attacker Active; compare an explicit attacker-promotion policy with identical legality rules and seed pair. Keep engine-hook versions and source list fingerprints fixed.
