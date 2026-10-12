# Playable 60-card competitive reference: 2026 Aichi Regidrago, 10th

**Published tournament evidence:** [Haruku Yoshioka, 10th place, 2026 CL Aichi Open League](https://limitlesstcg.com/decks/list/26816). This exact **20-Pokémon / 30-Trainer / 10-Energy** list is a historical real-tournament baseline against which the [champion Shadow Rider list and Regidrago temporal counterplay](../regidrago_shadow_rider_temporal_counterplay/) can be investigated.

### Pokémon (20)

- 4 Regidrago V
- 3 Regidrago VSTAR
- 2 Budew
- 1 Dragapult ex
- 1 Dialga-GX
- 1 Koraidon ex
- 1 Kyurem
- 1 Hisuian Goodra VSTAR
- 1 Dedenne-GX
- 1 Squawkabilly ex
- 1 Tapu Lele-GX
- 1 Latias ex
- 1 Marshadow
- 1 Wobbuffet

### Trainer (30)

- 2 Professor's Research
- 2 Guzma
- 1 Iono
- 1 Carmine
- 1 Lillie's Determination
- 1 Marnie
- 1 Raihan
- 1 Crispin
- 1 Faba
- 3 Quick Ball
- 3 Mysterious Treasure
- 3 Battle VIP Pass
- 3 VS Seeker
- 1 Hisuian Heavy Ball
- 1 Battle Compressor
- 1 Super Rod
- 1 Prime Catcher
- 2 Muscle Band
- 1 Parallel City

### Energy (10)

- 4 Double Dragon Energy
- 4 Grass Energy
- 2 Fire Energy

The [machine-readable manifest](yoshioka_regidrago_2026.json) maps each of 36 name/count entries to one English gameplay print. Representative prints are checked against the bundled 2026-09 card snapshot's Expanded legality flags. Physical card artwork at the original event is not implied by the chosen representative IDs. The [Windows regression](reproduce.py) checks the complete 60-count, card categories, copy limits, print identities, one ACE SPEC, key routing cards and exact supporting published per-list counts. It also tests the active-position Bide Barricade restriction.

## Unusually important card-choice interactions

### Wobbuffet is a polarized, self-inhibiting Ability lock

This published Regidrago list runs one Wobbuffet `xy4-36`, a **Psychic** Basic with **Bide Barricade**, active while Wobbuffet is Active. Its explicit exception for Psychic Pokémon makes its effect highly matchup-dependent.

- **Opposing champion Shadow Rider Calyrex VMAX is Psychic**, so its **Underworld Door** survives this Wobbuffet lock. This is a significant caveat: Wobbuffet cannot be credited with disabling that opponent's main draw/attachment Ability. Opposing Psychic Tapu Lele-GX and Psychic Latias ex also keep their Abilities.
- Regidrago VSTAR is Dragon, so **Legacy Star** is suppressed while its own Wobbuffet stays Active. Dedenne-GX (Lightning) **Dedechange** and Squawkabilly ex (Colorless) **Squawk and Seize** are similarly suppressed, including while those Pokémon are in hand.
- The list's own **Latias ex is Psychic**; its **Skyliner** Ability is exempt from Wobbuffet and gives the Basic Wobbuffet no Retreat Cost. Retreating Wobbuffet can reopen the above Regidrago and draw Abilities. Latias still does *not* provide free retreat to evolved Regidrago VSTAR.

Any optimization treating all Ability locks as fungible would badly value Wobbuffet here. Wobbuffet still can suppress non-Psychic Abilities, so it has significant potential against different opponents.

### The zero-Energy Budew data defect

The list has **two Budew** with **Itchy Pollen**, which in gameplay costs **zero Energy** and denies the opponent Item play on their next turn. Older legal Prismatic Evolutions print `sv8pt5-4` is encoded in the bundled English dataset with `["Free"]` and `convertedEnergyCost:1`, a phantom Energy symbol. We choose mechanically matching legal Budew `me2pt5-16` in this manifest because that reprint accurately has empty cost. The [general normalized-cost regression](../free_attack_cost_normalization/) proves the discrepancy and provides a non-mutating consumer-side repair.

### Timeless-GX extra-turn branches

This 10th-place list concretely has the resources whose game-state interactions were previously isolated:

- **Regidrago VSTAR, Dialga-GX**: copy Timeless-GX through Apex Dragon to gain an extra turn.
- **Budew (two)**: after safely promoting it, directly attack with Itchy Pollen to replace the recorded Apex Dragon attack history and Item-lock Shadow Rider.
- **Kyurem (one)**: another Apex Dragon can copy Trifrost during the bonus turn and deal 110 to an exposed 70-HP Mimikyu; this consumes Regidrago's attached Energy while retaining Apex Dragon in last attack history.
- **Koraidon ex (one)**: Retribution Strike is a direct alternative declared attack; a Double Dragon Energy on this Dragon Pokémon supplies its two-Colorless cost.
- **Crispin, Raihan, Double Dragon Energy**: conditional tools for post-Trifrost recovery. Raihan requires the relevant KO during the preceding *individual* opponent turn.
- **Two Guzma and one Prime Catcher**: a potential Budew promotion channel if the opponent has a Bench target and other board conditions permit it. They are not evidence that Budew is always promotable.

These are legal and potentially realistic lines conditional on Prize status, hand resources, attached Energy, board position, opponent effects, and timed one-use action budgets. The deck's event placement is evidence of tournament performance, though it cannot establish match-win probability against all future fields.

## Next empirical tests

This baseline makes matched-state Shadow Rider versus Regidrago experiments possible. Sample actual Prizes, opening setup, zone placements, Bench and Tool occupancy, last-attack history, Energy, and conditional Supporter quotas before comparing Budew history-cover, Kyurem snipe, and no-bonus-turn actions under a fixed opponent policy. Wobbuffet's type-selective suppression should be explicit; an ability-denial proxy without Pokémon types would be unsound.

## Sources

- [Complete public list](https://limitlesstcg.com/decks/list/26816)
- [Published CL Aichi 2026 nine-Regidrago analysis](../regidrago_budew_promotion_baselines/)
- [Champion counterpart and temporal research synthesis](../regidrago_shadow_rider_temporal_counterplay/)
- [Zero-Energy token finding](../free_attack_cost_normalization/)
- [Advanced Player's Rulebook, provided repository copy](../../resources/manual/)
