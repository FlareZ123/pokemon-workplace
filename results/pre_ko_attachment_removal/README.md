# Pre-Knock-Out attachment removal

## Question

How often can a damaging attack remove Energy or Pokemon Tools from the
opponent's Active Pokemon before the game reaches the Knock Out check?

Implementation: `tools/pre_ko_attachment_removal_catalog.py`  
Regression: `results/pre_ko_attachment_removal/reproduce.py`

## Rules basis

The bundled Advanced Player's Rulebook gives attack resolution a strict order:

1. announce the attack;
2. check conditions and effects on the attacker;
3. apply text introduced by `Before doing damage`;
4. calculate damage;
5. apply effects outside damage;
6. apply effects that activate when a Pokemon is damaged;
7. check for Knock Outs.

The Knock Out process begins only after that final attack-resolution check.
Effects activated by the Knock Out are then applied before the Knocked Out
Pokemon and its remaining attached cards are discarded.

This creates an important snapshot boundary. A card that was attached when the
attack began may be gone by the time a Knock Out trigger asks what is still
attached.

## Inventory

The catalog scans the effective legal paper Expanded card pool from Black &
White onward. It uses the shared legality baseline, including the current
official ban overlay, and keeps only attacks with a printed damage field whose
text contains a discard clause targeting Energy or Pokemon Tools on the
opponent's Active or the Defending Pokemon.

The current snapshot contains:

| Category | Distinct attack signatures |
| --- | ---: |
| Before damage, Tool removal | 25 |
| Before damage, Energy removal | 1 |
| Before damage, Energy + Tool removal | 1 |
| Effects outside damage, Energy removal | 188 |
| Effects outside damage, Energy + Tool removal | 1 |
| **Total** | **216** |

Those 216 signatures are represented by 334 legal print instances in the
bundled card pool.

## Representative timing cases

### Dedenne, Energy Munch

`sv1-94` Dedenne's Energy Munch does 30 damage and then has a coin-dependent
effect that can discard an Energy from the opponent's Active Pokemon.

Because the discard is not introduced by `Before doing damage`, the attack
damage is calculated first and the Energy-discard effect is applied in the
effects-outside-damage step. The KO check still happens later.

If the 30 damage is lethal and the discard succeeds, the selected Energy is
already gone when Knock Out-triggered recovery effects are evaluated.

### Galarian Zapdos V, Thunderous Kick

`swsh10tg-TG19` Galarian Zapdos V explicitly discards a Special Energy from
the opponent's Active before doing 170 damage.

The attachment is removed even earlier, in the before-damage phase.

### Mow Rotom and Scizor V

`sv7-8` Mow Rotom removes both Pokemon Tools and Special Energy before damage.

`swsh3-118` Scizor V removes a Pokemon Tool and a Special Energy as ordinary
effects outside damage. The two attacks reach similar resource destinations
through different timing phases.

## Strategic and simulator consequence

A KO-trigger model must inspect the board state that exists after all earlier
attack phases have resolved.

Using the pre-attack attachment set as the trigger input can create impossible
recovery. Examples include effects that try to move or save Energy from a
Pokemon when the relevant Energy was already discarded by the attack that
caused the Knock Out.

This is a general form of Active Move Realism. A recovery effect can be present
and legally triggered while still having less material to recover than a
static card-interaction graph suggests.

## Method

The text classifier splits normalized attack text into clauses and retains a
clause only when it:

- contains `discard`;
- refers to the opponent's Active Pokemon or the Defending Pokemon;
- refers to Energy, Pokemon Tools, or both.

The timing label is derived from whether the matched discard clause itself uses
`Before doing damage`.

Signatures are deduplicated by attack name, printed damage, and normalized
attack text. The full signature list is emitted by the tool for audit.

## Limits

The catalog is deliberately narrow.

It does not include non-damaging attacks, attachment movement that uses verbs
other than discard, effects that remove the Pokemon itself before the KO check,
or indirect state changes that can alter which attachments remain eligible.

A damaging attack having a removal clause also does not mean the removal always
occurs. Coin flips, target availability, optional text, and other conditions
still matter.

The next useful layer is a physical-state regression that removes an attachment
during attack resolution and then prepares the KO batch, proving that the later
KO trigger sees only the surviving attachments.
