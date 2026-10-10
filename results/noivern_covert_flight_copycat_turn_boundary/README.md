# Covert Flight prevents Mimikyu's damage, while Copycat can still grant Timeless-GX's bonus turn

## The temptation

Seven of the nine published 2026 CL Aichi Open League Regidrago VSTAR lists include Noivern ex (`sv2-153`), a Dragon-type Pokémon with the **Covert Flight** attack.

A Regidrago VSTAR can use `Apex Dragon -> Covert Flight` from discarded Noivern ex. Covert Flight prevents damage done to the copying Regidrago by attacks from Basic Pokémon during the opponent's next turn. Mimikyu (`sm2-58`) is Basic.

Can that protective attack stop the champion Shadow Rider deck's Mimikyu from exploiting `Copycat -> Apex Dragon -> Timeless-GX`?

**It can stop the 150 attack damage to Regidrago, but cannot prevent the Timeless-GX extra-turn effect on the attacking player.**

## Reproduced turn sequence

Assume Regidrago VSTAR remains Active throughout and has discarded Noivern ex and Dialga-GX, while the opponent has a properly energized Mimikyu Active with its own Dialga-GX in discard. Both sides have their relevant attacks/abilities available.

1. Regidrago declares **Apex Dragon**, copying Dialga-GX's **Timeless-GX**, gaining an extra turn.
2. On the extra turn, Regidrago declares **Apex Dragon** again, copying Noivern ex's **Covert Flight**, giving itself protection against Basic-Pokémon attack damage on the opponent's next turn.
3. Shadow Rider's Basic Mimikyu declares **Copycat**. Regidrago's last declared attack is still **Apex Dragon**; the copied Covert Flight body did not change that declared identity.
4. Copycat selects Apex Dragon and then selects Timeless-GX from Shadow Rider's discarded Dialga-GX.
5. Covert Flight's shield makes the 150 damage to the protected Regidrago **zero**. Timeless-GX's independent extra-turn effect still resolves and Shadow Rider gains another turn.

The copied attack's extra-turn effect belongs to the player using Mimikyu, regardless of whether the defending Regidrago took damage. The shield is a damage-prevention effect on Regidrago; gaining the next turn is an effect on the attacking player.

The Advanced Player's Rulebook §A-01 resolves effects outside damage separately from damage, and §C-16 explicitly locates damage prevention at the final damage stage. It does not make the entire attack “not happen” and does not negate independent effects such as extra turns.

## Why this matters

Regidrago's defensive Covert Flight line preserves HP and may prevent a Knock Out, but **does not erase the Apex Dragon Copycat target** and does not shut off the unusual turn economy of Timeless-GX.

This contrasts with the [Timeless-GX -> Budew history-cover option](../timeless_budew_dual_denial/README.md), which requires a physical switch but replaces Apex Dragon as the most recently declared attack. The two defensive moves address different threats.

There is no universal dominance conclusion. Regidrago may prefer Covert Flight if maintaining HP and position is more important than denying the opponent's potential extra turn, or if Budew cannot be promoted.

## Reproduction

`results/noivern_covert_flight_copycat_turn_boundary/reproduce.py` calls the canonical nested attack-copy kernel and the canonical turn-sequence bridge:

- checks Regidrago VSTAR, Noivern ex, Mimikyu and Dialga-GX source texts;
- verifies Covert Flight is copied through Apex Dragon, whose declared identity persists;
- verifies Mimikyu's Copycat chain reaches Timeless-GX and consumes Shadow Rider's own GX-use budget;
- calculates zero damage from a Basic attacker under Covert Flight's source card text as an independent damage-gate check;
- confirms that the Timeless turn-boundary effect still schedules a consecutive Shadow Rider turn.

Run `python results/noivern_covert_flight_copycat_turn_boundary/reproduce.py`.

The attack-copy kernel does not model full Pokémon HP, Knock Outs, healing, Bench movement or the defensive attack-effect lifecycle. The source-text damage-gate check is explicit and conditional. The experiment demonstrates a **rules consequence**, without estimating real-game occurrence or relative tournament performance.

Source decklist pages are preserved in `../regidrago_budew_promotion_baselines/aichi9_counts.json`; seven carry Noivern ex.
