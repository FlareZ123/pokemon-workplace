# agent36: Garbotoxin now causally suppresses board-derived Dual Brains quota

New result: `results/garbotoxin_quota_suppression/`.

A derived suppression overlay recognizes all four verified legal Garbotoxin prints and requires physical Tool attachment. It does not overwrite base board Ability state.

After one Supporter:
- opposing Garbotoxin: Dual Brains limit 2 -> 1;
- Stealthy Hood on Magnezone: protection restores limit 2;
- Jamming Tower: Hood has no effect, Garbotoxin suppresses again;
- same-side Garbotoxin: Hood does not protect because Hood is opponent-specific.

The key representation is attachment != Tool-effect operation. Jamming Tower leaves Garbodor's Tool attached, so Garbotoxin's condition remains met while Hood loses its protection.

Push CI 37571776027 is green; quota overlay support also passed board derivation CI 37571695639.
