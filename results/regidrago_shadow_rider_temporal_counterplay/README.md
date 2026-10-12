# 2026 Aichi champion Shadow Rider versus Regidrago: playable list and temporal counterplay

## Empirical tournament anchor

Yasunori Kato won the **2026 CL Aichi May Open League** with Shadow Rider Calyrex VMAX. The [official winner interview](https://www.pokemon-card.com/info/005499.html) describes Mimikyu copying the opposing Regidrago VSTAR's Apex Dragon as a deliberate counter. The [published complete 60-card list](https://limitlesstcg.com/decks/list/26807) is reproduced here.

The [print-level manifest](shadow_rider_aichi_2026.json) records 33 card-name/count entries and an Expanded-legal English card ID for each. Mimikyu **sm2-58** has Copycat, Dialga-GX **sm5-100** has Timeless-GX, Girafarig **sm8-94** has Get Lost, and Marshadow **sm10-81** has Resetting Hole. Distinguishing prints is necessary because same-name Pokémon may have different attacks/Abilities or legality flags. Manifest IDs for otherwise equivalent printings are representative; the published source does not certify the physical artwork used.

The accompanying [one-file regression](reproduce.py) checks the bundled card pool's **Expanded: Legal** print flags, copy limits, Pokémon/Trainer/Energy categories, card-text identities, exactly one ACE SPEC and Radiant, and the 18/31/11 total. That is a reproducible **snapshot-based eligibility check**; event legality may also depend on contemporaneous or regional release/ban rules.

## Complete published 60-card list

### Pokémon (18)

- 3 Shadow Rider Calyrex V
- 4 Shadow Rider Calyrex VMAX
- 2 Lillie's Clefairy ex
- 2 Tapu Lele-GX
- 1 Trevenant & Dusknoir-GX
- 1 Latias ex
- 1 Dialga-GX
- 1 Mimikyu
- 1 Girafarig
- 1 Marshadow
- 1 Radiant Eternatus

### Trainer (31)

- 2 Lillie's Determination
- 1 Carmine
- 1 Iono
- 1 Teammates
- 1 Raihan
- 1 Acerola
- 1 Guzma
- 1 Tulip
- 4 Mysterious Treasure
- 4 Fog Crystal
- 3 VS Seeker
- 1 Quick Ball
- 1 Hisuian Heavy Ball
- 1 Battle Compressor
- 1 Field Blower
- 1 Night Stretcher
- 1 Unfair Stamp
- 1 Float Stone
- 1 Forest Seal Stone
- 2 Sky Field
- 1 Dimension Valley

### Energy (11)

- 11 Psychic Energy

This is a tournament-proven **historical 60-card reference**. The research does not establish that this unchanged list is optimal for the October 2026 metagame, nor does it establish a current match win rate.

## Regidrago's Timeless-GX bonus-turn branches

Assume Regidrago VSTAR has just declared **Apex Dragon** to copy discarded Dialga-GX's **Timeless-GX** and has gained a bonus turn. Attack-copy semantics preserve the **declared** name Apex Dragon as the last attack, even when it used another attack's effects and damage. Mimikyu's Copycat examines the attack the opponent used on their last turn, making the next Regidrago declaration a decisive resource.

| Regidrago action on bonus turn | Last declared attack | Benefit | Relevant physical cost / remaining exposure |
| --- | --- | --- | --- |
| Promote Budew, use **Itchy Pollen** | Itchy Pollen | Conceals Apex Dragon from immediate Copycat and inflicts Item lock | Requires available Budew and actual promotion. Guzma or Prime Catcher needs an opponent Bench target; Latias ex Skyliner does not remove evolved Regidrago VSTAR's retreat cost |
| Keep Regidrago Active, use **Apex Dragon -> Kyurem Trifrost** | Apex Dragon | 110 spread damage can KO an exposed unprotected 70-HP Benched Mimikyu | Discards Regidrago's attached Energy, while leaving Apex Dragon visible for a recovered Mimikyu |
| Keep Regidrago Active, use **Apex Dragon -> Noivern ex Covert Flight** | Apex Dragon | Shields Regidrago from damage by Basic Mimikyu's attack in the relevant turn | Prevents 150 attack damage, but the copied Timeless-GX extra-turn effect can still succeed |
| Promote Dragon Koraidon ex, use **Retribution Strike** | Retribution Strike | Covers Apex Dragon history with a different direct attack | Requires actual promotion and Energy; one Double Dragon Energy pays its two-Colorless attack cost on this Dragon |

**Observed opposing lists:** All nine individually published top-32 Aichi Regidrago lists contained Budew and Kyurem of Shrouded Fable. Seven had the specific Noivern ex with Covert Flight, five contained the Dragon Koraidon ex, and the nine totaled 19 Guzma, three Prime Catcher and nine Latias ex. These are observed card counts, not estimated availability, line execution or win probabilities. The tournament aggregation includes additional Regidrago placements without detailed published lists.

## Shadow Rider's tactical response bottlenecks

**Physical zone routing.** Copycat -> Apex Dragon -> Timeless-GX needs Mimikyu attacking and Dialga-GX in Shadow Rider's **own discard**. A Mysterious Treasure can pay with Dialga-GX from hand and retrieve Mimikyu from deck simultaneously. A prior exhaustive coarse zone-graph test reached the routing endpoint from **15/16** Mimikyu/Dialga zone pairs under its Item-unlocked, disposable-hand-resource assumptions. This is an abstract state count, not a 93.75% success probability.

**Budew's compounded denial.** Following the history-cover attack, Budew's Item lock also removes ordinary Quick Ball, Fog Crystal, Mysterious Treasure, Hisuian Heavy Ball, Battle Compressor and Night Stretcher routing edges. The same restricted graph has only **2/16** reachable endpoint pairs with Tulip available. Extra attack energy, Bench space, promotion and unused GX attack budget are additional constraints. Item lock is on the opposing *player* rather than solely the defending Pokémon.

**Bench readiness versus Trifrost exposure.** A pre-staged Mimikyu is easier to promote, yet can be KO'd by the 110-damage Trifrost copied on Regidrago's bonus turn if exposed and without damage prevention. Repeating the declaration Apex Dragon preserves the counter target. A return line exists: with Mimikyu and two Basic Psychic Energy discarded, a damaged active VMAX, no occupied Tool, live Bench space and standard attachment permissions, the bounded recovery planner finds exactly **two minimal coalitions**: {Tulip, Float Stone, Underworld Door} and {Tulip, Float Stone, Dimension Valley}. Tulip occupies the Supporter channel; Underworld Door needs Mimikyu Benched before attachment.

**Tool contention.** Forest Seal Stone attached to Active Shadow Rider VMAX cannot be replaced freely by Float Stone. Field Blower can clear it only if Items are playable. Under a pure Item lock, attaching Float Stone to an already-empty Tool slot remains possible, because older printed Tools are still Pokémon Tools, distinct from Items in current rules.

**Post-Trifrost energy debt.** Once Trifrost discards Regidrago's Energy, Apex Dragon needs Grass, Grass and Fire again. One Double Dragon Energy plus Basic Grass or Fire can pay; from zero cards attached, another attachment source in addition to the manual attachment is necessary. Crispin is one conditional Supporter solution. Raihan only works after a qualifying KO during the opponent's **most recent individual turn**, which matters following bonus turns.

**Prize collision.** With both critical singles in a 60-card shuffled list and six Prize cards, the initial probability Mimikyu and Dialga-GX are both Prized is `(6/60)*(5/59) = 0.8474576271%`. Neither this probability nor an abstract unreachable-zone cell constitutes a predicted loss rate.

## Model limitations and next tests

The linked programs mostly test discrete rule semantics, exact constrained reachability, or non-game-turn inventory opportunities. No reported number establishes the probability of executing all these sequences on a real turn, and no complete representative head-to-head win-rate study has been demonstrated.

A high-value next experiment would sample full opening/Prized inventory, Bench state, turn/attack history, Tool occupancy, attacker Energy, unused Supporter/manual quotas and opponent Bench. Under the **same sampled initial states**, compare the concrete bonus-turn policies: cover with Budew or Koraidon; snipe with Trifrost; shield with Covert Flight. Evaluate survivability, Prize tempo, Shadow Rider recovery, Regidrago energy rebuilding and whether the opposing deck has alternative attackers. Only extrapolate win rates after a verified physical game-state implementation supports all relevant effects.

## Evidence index

- [Original Shadow Rider zone routing and nested Copycat](../shadow_rider_regidrago_counter_als/README.md)
- [Apex Dragon attack-history and bonus turn](../regidrago_attack_history_evasion/README.md)
- [Budew promotion constraints and nine-list observations](../regidrago_budew_promotion_baselines/README.md)
- [Budew joint Item and attack-history lock](../timeless_budew_dual_denial/README.md)
- [Kyurem Trifrost bench-snipe option](../regidrago_bonus_turn_mimikyu_snipe/README.md)
- [Shadow Rider post-Trifrost recovery witness](../shadow_rider_post_trifrost_recovery/README.md)
- [Recovery-coalition exhaustive search](../shadow_rider_recovery_coalitions/README.md)
- [Forest Seal Stone Tool-slot repair](../shadow_rider_tool_slot_repair/README.md)
- [Noivern ex Covert Flight counterexample](../noivern_covert_flight_copycat_turn_boundary/README.md)
- [Regidrago post-Trifrost energy rebuild](../regidrago_post_trifrost_recharge/README.md)
- [Raihan's bonus-turn Knock Out deadline](../raihan_extra_turn_ko_deadline/README.md)
- [Champion print and 60-card validation](reproduce.py)

**Evidence classification:** deck contents and placing are published empirical observations; card effects and quotas are game-rule/text facts; zone reachability and minimal coalitions are bounded computational results. Forecast match strength remains an untested hypothesis.
