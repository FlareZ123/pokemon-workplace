# Shadow Rider: Dialga-GX as a strategically useful Mysterious Treasure discard

## Question

In the [2026 Aichi champion Shadow Rider list](../competitive_deck_baselines/), how often does access to the singleton Dialga-GX in the hand turn a *resource-preserving* Mysterious Treasure payment into a valid Radiant Eternatus two-VMAX launch?

The [six-category Treasure payment study](../shadow_rider_treasure_discard_sensitivity/) established exact access under explicit hypothetical discard policies. Its stricter policy allows discarding a spare Mysterious Treasure or one Psychic Energy only when at least two Psychic Energy are held. The new experiment adds the option to **discard a held Dialga-GX** when that card is strategically useful as a Dragon attack payload.

This option matters specifically for the matchup-dependent line discussed in [human strategic prior](../../resources/human_concepts.md): after opposing Regidrago VSTAR uses Apex Dragon, Mimikyu may use Copycat to reproduce that non-GX attack, then copy Timeless-GX from a **Dragon Pokémon in the player's discard pile**. Dialga-GX `sm5-100` is a **Dragon-type Basic** with Timeless-GX. Mimikyu `sm2-58` is a Psychic Basic with Copycat. Both card identities are present in the champion list. This is a situational role; discarding Dialga need not be valuable against unrelated decks.

The executable extension is [`tools/shadow_rider_dialga_payload_discard.py`](../../tools/shadow_rider_dialga_payload_discard.py), with [reproduction regression](reproduce.py).

## Physical Active-Spot constraint

In the champion deck's 60 cards, the existing six-category model has 13 other opening-eligible Basics, **exactly one of which is Dialga-GX**. A card on the Active Spot cannot be discarded from the hand to pay Mysterious Treasure.

If the opening seven contain only one non-Radiant Basic and that Basic is Dialga, Dialga must start Active to preserve the modeled Radiant launch. Drawing another Basic on the first turn does not retroactively free that Dialga from the Active Spot under the experiment's no-switching policy.

If two or more non-Radiant Basics are in the *opening seven*, the player can start another one Active and preserve Dialga in the hand. If Dialga instead arrives as the first natural draw, an eligible non-Radiant Basic was already established Active.

For a grouped physical state with `b` other Basics in the initial seven, and `d=1` when the first draw is another Basic, the number of possible positions for the singleton Dialga that leave it **held and discardable** is

```text
eligible_positions = (b if b >= 2 else 0) + d
```

The original model only counts the Treasure route if `b >= 1`. Conditional on a particular six-category opening, Prize allocation and draw category, each of the 13 exact Basic identities is exchangeable. The conditional probability of a discardable Dialga is therefore `eligible_positions / 13`.

A tempting alternative count `(b-1) / 13` is **incorrect**: when Dialga is in an opening with two eligible Basics, either Basic could have occupied the selected Active role, and the player chooses the other one. The independent labeled-card oracle revealed this modeling pitfall.

## Exact probabilities

| Restricted first-turn route | Two-VMAX launch probability |
| --- | ---: |
| Radiant already held, unaffected | 12.017840120% |
| Treasure payable by at least two Psychic Energy or a spare Treasure | 16.072588787% |
| **Additional** Treasure successes from held, discardable Dialga-GX | **2.074551901%** |
| Treasure route with eligible Dialga added | 18.147140688% |
| **Total** with direct Radiant and guarded Treasure/Dialga payments | **30.164980808%** |

The expansion changes the prior guarded combined launch probability from **28.090428907%** to **30.164980808%**, under the stated matching-specific payoff assumption.

The increment is exactly `84865653/4090794400`. It is computed without Monte Carlo sampling, and the final combined fraction is `335644558019/1112696076800`.

## Validation method

The code uses the original full-deck source counts, original first-turn access classifier, and a conditional exact physical identity distribution over the 13 interchangeable non-Radiant Basics. Card data is inspected directly: exact print `sm5-100` must be a Dragon-type Basic with Timeless-GX.

Independent **labeled card enumeration** tests three toy decks with 1, 2, and 3 non-Radiant Basic identities, respectively. They cover **6,720**, **18,312**, and **41,328** accepted opening/Prize/draw deals, totaling **66,360** physically labeled cases. Each brute physical result must exactly match the conditional exchangeability calculation. The one-Basic toy provides the zero-benefit Active-constraint regression; the other toys confirm the nontrivial increment.

The extension also pins its full-deck exact rational fractions and the previously verified strict Treasure policy probabilities.

## Interpretation and limitations

This is a constructive example of matchup-dependent discardability: Dialga-GX can be an attractive discard when enabling Timeless-GX through a copied Apex Dragon line. The same Dialga may be strategically protected in another state. Mysterious Treasure itself has connector contention: using it to obtain Radiant Eternatus prevents that specific copy from also searching for Mimikyu or a Shadow Rider Pokémon.

The model assumes a legal non-Radiant starting Active, one natural first-turn draw going second, two VMAX still in deck, an unopposed Item and Ability, the supplied restrictive resource-preservation policy, and no other search/draw/switch effects. It does **not** test Regidrago's likelihood of attacking with Apex Dragon, Mimikyu's subsequent Energy requirements or board survival, or whether using Radiant immediately is the best choice.

In particular, this does **not** mean the champion's matchup-adjusted win probability increases by 2.07 percentage points. The number is the newly enabled fraction of conditional *opening access* states under a chosen strategic discard policy.

A next meaningful step would optimize the conflict between using the first Mysterious Treasure for Radiant versus fetching Mimikyu, while preserving Dialga as an Apex Dragon payload in the discard pile and honoring next-turn Attack/Supporter/Bench budgets.
