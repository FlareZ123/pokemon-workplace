# Agent45: Supporter effect copying bypasses play-from-hand lock channel

I added `results/supporter_effect_copy_channels/` and `tools/supporter_effect_copy_channels.py`.

The legal Expanded scan finds 11 direct copy-effect print rows across 8 names. Seven Pokémon names execute a Supporter body as an attack effect: Liepard, Mimikyu, Mr. Mime, Ninetales, Oranguru, Smeargle, and Sylveon. Sabrina's Suggestion is the Supporter-source family.

The important representation is physical card type + current execution class + turn-budget history. Mimikyu Impersonation can follow an ordinary Supporter play because it is an attack edge, preserving Supporter-play usage and then ending the turn.

Strong official Q&A evidence:
- Mimikyu vs Shiftry: Shifty Substitution's Supporter text replacement applies only while the card is in hand; after Impersonation discards it, the original copied body resolves.
- Liepard vs Stoutland: Silent Claw can discard and use a Supporter effect while Sentinel is active, directly proving the copied attack channel is outside the play-Supporter-from-hand lock.

CI run 37576136979 passes.
