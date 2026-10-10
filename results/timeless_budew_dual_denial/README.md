# Timeless-GX into Budew: the same cover attack denies two Shadow Rider response channels

## Motivating matchup

The CL2026 Aichi-winning Shadow Rider Calyrex strategy employed Mimikyu's Copycat to copy an opposing Regidrago VSTAR's Apex Dragon and, through its own discarded Dialga-GX, Timeless-GX.

Previous reproduced results:
- [Regidrago attack-history cover](../regidrago_attack_history_evasion/README.md): Apex Dragon copying Timeless-GX grants an extra turn. A different *declared* attack on that bonus turn overwrites the last attack that Mimikyu can Copycat.
- [Shadow Rider counter-ALS](../shadow_rider_regidrago_counter_als/README.md): When Items are available, the champion's named payload-routing package can get Mimikyu to hand and Dialga-GX to discard from 15 of 16 coarse ordered zone pairs under its explicit permissive assumptions.

**New observation:** Budew's Itchy Pollen is particularly powerful as the alternative declared attack because it simultaneously overwrites the Copycat target and Item-locks the Shadow Rider player during their next turn.

## Rules grounding

Budew `sv8pt5-4` has a Free attack, **Itchy Pollen**, which does 10 damage and prevents the opponent from playing Items from their hand during their next turn.

The prior Regidrago history-cover regression confirms the executable attack sequence:

1. Active Regidrago VSTAR declares `Apex Dragon -> Timeless-GX`.
2. The extra turn belongs to Regidrago.
3. Regidrago promotes Budew through a separate, required action and declares `Itchy Pollen`.
4. Mimikyu's next-turn Copycat sees **Itchy Pollen**, not Apex Dragon.

Under the Advanced Player's Rulebook §C-19, Item lock is an effect on the player. It does not disappear merely because the defending Pokémon is immune to effects of attacks.

The resulting response turn has two distinct pressures:
- **History denial:** the previous Apex Dragon is no longer the last declared opponent attack.
- **Routing denial:** the Item-lock effect suppresses Mysterious Treasure, Fog Crystal, Quick Ball, Battle Compressor, Hisuian Heavy Ball, and Night Stretcher used by the original bounded routing model.

The second effect can matter independently, including to setup and alternative tactical lines that would not themselves use Copycat. A direct attack with Budew requires separately placing it Active, as explored in [Budew promotion baselines](../regidrago_budew_promotion_baselines/README.md).

## Coarse state-space experiment

Composition reuses `tools/shadow_rider_regidrago_counter_als.py` without modifying its semantics, plus the validated history test from `results/regidrago_attack_history_evasion/reproduce.py`.

The payload-only state pairs are:

`Mimikyu zone × Dialga-GX zone` where each zone is deck, hand, discard, or Prize.

A successful *routing* endpoint requires Mimikyu in hand and Dialga-GX in discard. All named connector cards are available, one generic disposable card exists, Bench placement is permitted, and the count is **reachability, not probability**.

| Model variant | Coarse payload pairs with a route |
| --- | ---: |
| Items available, Tulip available | **15/16** |
| Budew Item lock, Tulip available | **2/16** |
| Budew Item lock, Tulip unavailable because Supporter is reserved for Guzma | **1/16** |

Under Item lock, the two surviving payload pairs are:

1. Mimikyu already in hand and Dialga-GX already in discard (no payload route needed).
2. Mimikyu in discard and Dialga-GX in discard (Tulip retrieves Mimikyu, spending the Supporter).

When the subsequent attack also requires Guzma promotion, Tulip and Guzma cannot ordinarily both be played in the same turn. Thus only the already-ready hand/discard pair survives under that additional assumption.

**Important:** The endpoint is Mimikyu in hand, not already fully energized and Active. These counts are not actual probabilities, and many other strategic routes and game-state considerations remain outside the bounded model. Applying Item lock does not imply that the opponent has zero ways to attack.

## Reproduction

`python results/timeless_budew_dual_denial/reproduce.py`

The test reads source card text, calls the existing Regidrago history-cover regression, and checks the exact reachable 16-pair matrices under the named resource variants.

## Strategic interpretation

Budew's value after copied Timeless-GX is unusually concentrated in a narrow temporal window:

- the bonus turn permits overwrite of an otherwise dangerous historical attack;
- the replacement attack imposes Item lock on the opponent's response turn;
- the opponent may be relying on Item-based payload routing and can be forced to use Tulip, consuming the Guzma Supporter channel.

A static graph that treats Budew as merely a 10-damage Item-lock attacker or simply as an alternative declared attack misses the **coupled history-and-routing denial**.

This is an illustrative legal sequence with state-dependent payoff, **not proof that choosing Budew is superior** to using Apex Dragon again. The huge lost attack damage and promotion cost may outweigh the denial, and the opponent may already have Mimikyu ready or have a different game plan. See the adjacent physical-promotion benchmark for limitations.

## Follow-up

Build a conditioned game-state analysis with real card locations and the opponent's prior Item-lock timing, then compare the expected Prize race between a second high-impact Apex Dragon attack and a Budew cover. This requires opponent board and hand information, not only card access.
