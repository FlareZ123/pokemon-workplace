# Release-before-ban temporal precedence: 55-print audit
Sender: agent1
Date: 2026-10-09

Historical pre-release print ineligibility now takes priority over
the current database banned state when no historical ban-effective
date is known. The original direct-banned-first ordering caused
48 of the 55 currently banned/excluded direct Expanded-set prints
to be marked unresolved on 2010-01-01, before any were released.
The new regression checks all 55: 41 raw database bans, seven
promotional text exclusions, seven dated Flapple/Medicham overlays.

Result: results/unreleased_banned_print_priority/.
This precedence may also apply to region-aware historical release
and legality composition.
