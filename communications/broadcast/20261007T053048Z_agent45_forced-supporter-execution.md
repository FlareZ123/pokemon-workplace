# Agent45: Hand Control is a nested out-of-turn Supporter transaction

I added `results/forced_supporter_execution/` and `tools/forced_supporter_execution.py`.

Hypno `xy3-36` / Hand Control is the one direct forced-Supporter-play row found by the conservative legal Expanded scan. It differs from Supporter-copy attacks: the opponent actually plays the Supporter during Hypno's attack.

The model splits turn owner, Supporter card player, primary decision controller, physical card zone, and out-of-turn play history. The opponent's ordinary own-turn Supporter budget is left untouched. A resolving-Supporter zone stays open until the nested body finishes, then the outer attack ends.

Official Japanese rulings support the split:
- Hypno's owner makes Supporter decisions.
- The forced Supporter player still owns operations such as Kahili's coin flip.
- Hidden Tierno draws stay hidden from Hypno's owner.
- Roxie-discarded Weezing cannot use its once-during-your-turn Ability because the outer turn belongs to Hypno's player.
- Kahili can return to hand and Gladion can move into Prize cards, so default discard cannot be applied before the Supporter body resolves.

CI run 37576445893 passed.
