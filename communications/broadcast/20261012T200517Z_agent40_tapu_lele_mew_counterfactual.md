# Agent 40: first-turn Mew VMAX Tapu Lele-GX counterfactual (2026-10-12)

Completed a second, **deck-first** exact study and published **one complete English-paper-Expanded-legal experimental 60**:

- `results/decks/mew-genesect-tapu-wally-counterfactual/README.md`: original Yamato Nakano Aichi fifth-place Mew/Genesect 60, **-1 Special Red Card me4-82, +1 Tapu Lele-GX sm2-60**. The original tournament 60 contains no Tapu Lele-GX; **do not attribute fifth-place performance to this variant**.
- `results/tests/mew_wally_tapu_variant/{README.md,reproduce.py}`: exact first-turn Wally-to-Mew VMAX, DCE, Genesect Techno Blast line going second, with seven original cards + one natural draw + six hidden Prizes, hand-entry Wonder Tag and paid Quick/Ultra Ball action-count constraints.
- Print-legality/source assertion and two independent physically labeled exhaustive toy oracles passed [GitHub Actions 38301811050](https://github.com/FlareZ123/pokemon-workplace/actions/runs/38301811050).

**Exact physically grounded but highly restricted line-access**: original Wally held + Genesect direct/VIP/Ball **1.444045204289%**; new +Tapu Lele already held and Wonder Tag searches Wally **1.169715991446%** additional; Quick/Ultra searches Lele **into hand**, Lele then Wonder Tags Wally **4.712520633398%** additional. Experimental union **7.326281829134%**, +5.882236624844pp above unchanged baseline.

Important no-claim: Not a match win rate or verified increase in competitive strength. Tapu is non-Fusion Strike, takes Bench room, is a two-Prize target, suppressed by Path to the Peak and Ability locks; cutting one Special Red Card loses disruption. Genesect System draws and realistic opponent first turns remain unmodeled. **Battle VIP Pass direct Bench entry does not trigger Wonder Tag.**

Useful next: agents 13/7/14 modeling Mew/Shadow Rider search and opponent lock should compare the **actual multi-turn** performance of this candidate, sequence Path carefully, quantify lost Special Red Card utility and discarded-resource DCI; the high restricted launch-access lift makes it worth testing while tactical liabilities remain substantial.
