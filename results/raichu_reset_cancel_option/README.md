# Harto Raichu: K1 creates option value to cancel a destructive reset

## Question

The search-before-reset material theorem assumes the player is already committed to Dedechange or Squawk and Seize after Quick Ball.

A real player can make another choice after Quick Ball has inspected the deck.

If K1 reveals that the residual hand already reaches Alolan Raichu, the player can skip the destructive reset.

How much is that option worth inside the same modeled Harto branch?

Implementation: `tools/raichu_reset_cancel_option.py`  
Preserved run: `results/raichu_reset_cancel_option/five_million_seed_20261008.json`  
Regression: `results/raichu_reset_cancel_option/reproduce.py`

## Policy comparison

The calculation uses the same opening, Prize, first-draw and observable-branch model as `raichu_draw_engine_fallback/`.

Visible deterministic Ultra Ball / Computer Search and hosted Forest Seal Stone lines remain outside this subcomparison because they already reach the local endpoint with probability one.

For the remaining Quick Ball states:

1. pay Quick Ball with the validated K0 payment policy;
2. inspect the deck and establish K1;
3. check whether the residual hand already reaches Raichu through the modeled Gladion / Ultra Ball / Computer Search / Forest Seal channels;
4. if it does, the adaptive policy stops;
5. the comparison policy is forced to use an available six-card hand reset anyway.

The later-turn comparison treats held Dedenne-GX as the reset source.

The first-turn comparison also admits held or already-in-play Squawkabilly ex.

Each forced six-card reset is integrated exactly over the remaining deck composition.

## 5-million-state result

The run reuses seed 20261008 and contains 163,231 observable-branch states.

### Later turns

Held Dedenne-GX remains available after Quick Ball in **11.581746%** of branch states.

Within those reset-capable states:

- K1 says the residual hand already succeeds in **11.594816%**;
- if the player were forced to reset, mean success would be only **25.623804%**;
- preserving the option to stop adds **9.654847 percentage points** of access conditional on reset capability.

Across the entire observable branch, the cancellation option is worth:

**+1.118200 percentage points**

with 95% simulation interval:

**+1.071493 to +1.164906 points**.

### First turn

Adding Squawk and Seize expands reset-capable mass to **18.410106%** of the branch.

Within those states:

- the residual hand is already successful after K1 in **11.653522%**;
- forced-reset mean success is **25.407091%**;
- the stop option adds **9.713452 percentage points** conditional on reset capability.

Across the whole observable branch, the cancellation option is worth:

**+1.788257 percentage points**

with 95% simulation interval:

**+1.729409 to +1.847104 points**.

## Interpretation

Information value can arise through **action cancellation**.

Quick Ball's search does more than improve the choice of what to fetch. It can reveal that the player should decline a powerful draw Ability that was attractive under K0.

This is a different mechanism from the earlier paired engine gain:

- the six-card reset supplies fresh random access;
- K1 can make the reset unnecessary;
- retaining the right to stop prevents the reset from discarding an already-winning residual hand.

A planner that automatically fires Dedechange or Squawk and Seize whenever available therefore loses value even inside this narrow target-access objective.

## Relation to search-before-reset dominance

The material-state theorem compares two committed sequences using the same fresh draw.

This result adds a decision node between search and reset.

The search-first line can keep the material-equivalence option if a reset remains desirable, then abandon the reset when K1 reveals a better continuation.

Under the same no-topdeck-order projection, this turns weak material dominance into measurable strategic option value.

The separate `pre_reset_shuffle_value/` result remains an important counterweight when a mandatory shuffle destroys useful deck-position information.

## Limitations

This is still the local "put Alolan Raichu into hand this turn" endpoint.

It does not price future card preservation, Bench capacity, Ability lock, newly drawn Quick Ball chains, the full Electrode-GX / Electro Rain combo, or known top-deck order.

## Next work

The reusable abstraction is now a three-term pre-reset action value:

1. material payment relative to the planned reset;
2. information-driven option to cancel or redirect the reset;
3. shuffle effect on deck-position belief.

Composing those terms with explicit future-resource utility would move the model beyond the current one-turn access endpoint.
