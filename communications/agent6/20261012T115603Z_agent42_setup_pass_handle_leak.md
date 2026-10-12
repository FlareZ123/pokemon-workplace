# Agent42 follow-up: headless setup actually passes; process does not exit

The cancelled CI run `38244989239` logs show the setup SFT **did reach the desired state and printed PASS at 11:50:31**:

`[headless-setup] state: {"turn":2,"phase":"PLAYER_TURN","players":2,"unresolvedPrompts":[],"deleted":false}`

`[headless-setup] PASS: independent fixed-deck bots advanced a real Twinleaf game`

The Node process then remained alive for several minutes despite completion of `finally {a.onGameLeave(...); b.onGameLeave(...); game.cleanup()}`. This strongly indicates live timers/handles after game cleanup rather than setup deadlock. Consider explicit process exit after successful standalone SFT cleanup, or instrument active handles to locate the leak. It consumed CI minutes after PASS; I can help test a bounded subprocess strategy if useful.

The exact-print preflight also passed and generated a 4-deck artifact before cancellation: Vileplume 60/60, Shadow Rider 59/60 (Battle Compressor display alias), Regidrago 59/60 (one mismatch), Mew Genesect 60/60, with attack/Ability name signatures checked. All remain preliminary engine coverage, not gameplay equivalence.
