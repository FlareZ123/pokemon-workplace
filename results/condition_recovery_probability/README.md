# Exact Special Condition recovery odds

## Question

How strongly do Expanded-legal cards that modify Special Condition coin tests
change spontaneous recovery during Pokémon Checkup?

Implementation: `tools/condition_coin_models.py`  
Regression: `results/condition_recovery_probability/reproduce.py`

## Card anchors from the supplied database

The reproducer verifies four Expanded-legal examples directly from
`resources/cards/en/`:

- Slaking `sv2-162`, **Stir and Snooze**: while Asleep, flip 2 coins instead
  of 1 during Pokémon Checkup; if either is tails, Slaking stays Asleep.
- Slumbering Forest `sm11-207`: the same two-coin/all-heads wake structure
  using the older "between turns" wording.
- Centiskorch `swsh5-30`, **Overheater**: an opponent's Burned Pokémon does
  not recover even when its Checkup coin is heads.
- Wela Volcano Park `sm75-63`: the analogous Burn recovery suppression using
  older "between turns" wording.

This pair of old/new phrasings is useful evidence that a text compiler needs a
timing-normalization layer rather than treating literal wording as separate
mechanics.

## Exact probabilities

For fair independent coins:

### Ordinary Sleep

One coin, recover on heads:

`P(recover) = 1/2`.

If nothing else can remove Sleep and the same recovery chance persists, the
geometric mean waiting time is:

`E[Checkups] = 1 / (1/2) = 2`.

### Two-coin all-heads Sleep

Effects such as Stir and Snooze require both coins to be heads:

`P(recover) = (1/2)^2 = 1/4`.

The corresponding geometric mean is:

`E[Checkups] = 1 / (1/4) = 4`.

Thus changing one fair coin to two fair coins with "either tails stays Asleep"
halves the per-Checkup wake probability and doubles the mean number of Checkups
to coin-based recovery.

### Ordinary Burn

The basic heads-recovery rule gives:

`P(recover) = 1/2` and `E[Checkups] = 2`.

### Burn recovery suppression

Overheater or Wela Volcano Park makes the coin unable to remove Burn even on
heads:

`P(coin-based recovery) = 0`.

The geometric waiting time through that recovery channel is therefore
unbounded while the suppressor remains applicable. Other legal ways to clear
the Special Condition, such as movement/evolution effects, are outside this
single-channel calculation.

## Modeling consequence

The deterministic status resolver should consume a resolved coin outcome rather
than own the random process.

A separate outcome layer needs to determine:

1. how many coins are flipped;
2. what success predicate applies, such as one heads or all heads;
3. whether a nominal success is suppressed;
4. the resulting recovery event passed to the deterministic resolver.

This keeps card-specific probability manipulation separate from status-state
mutation.

## Validation

The regression uses exact `Fraction` arithmetic and verifies:

- ordinary Sleep recovery = `1/2`;
- two-coin all-heads Sleep recovery = `1/4`;
- ordinary Burn recovery = `1/2`;
- suppressed Burn coin recovery = `0`;
- geometric means 2, 4, 2, and infinity for those four channels.

## Scope and limits

The model assumes independent fair coins and a constant recovery profile from
Checkup to Checkup. Cards that change coin bias, change the number of flips
dynamically, leave play, or become suppressed require state-dependent profiles.

The infinite value for a suppressed Burn channel is a statement about that
single recovery mechanism while suppression persists. It is not a claim that
Burn is globally permanent.
