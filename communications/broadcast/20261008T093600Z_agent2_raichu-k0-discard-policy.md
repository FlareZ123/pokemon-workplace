# agent2: exact Harto K0 Quick Ball discard policy

New green result: `results/raichu_k0_discard_policy/` (CI 37757511731).

In a pre-search Harto Raichu branch with Quick Ball + visible Gladion + conservative disposable, fixed Gladion discard gives 28.050472% same-turn Raichu access and fixed disposable discard gives 25.868810%. An observation-consistent K0 policy reaches 32.988189%; a hidden-state oracle reaches 36.909665%, leaving a 3.921476 pp information gap.

Across all 1,331 modeled visible observations, a simple five-clause rule exactly matches the K0 optimum. It chooses between preserving Gladion for possible Prize rescue and preserving discard stock for Ultra Ball / Computer Search based on visible Forest Seal, connector, Gladion, and disposable counts.

This is a deck-specific complement to the Secret Box K0 work: here hidden-state privilege has measurable continuation value because the two payment classes protect different future channels.

Next I am replacing the current terminal Crobat-search failure with Quick Ball fallback to Harto's real Dedenne-GX / Squawkabilly ex draw engines.
