# Source-verified copied-attack Special Conditions on the physical board

## Question

Can a copied attack's actual printed text inflict Poisoned, Burned, Asleep,
Paralyzed or Confused on the opponent's Active Pokémon at the attack-effect
step while preserving immutable card-instance identities?

## Model

`tools/attack_status_text_contracts.py` recognizes exact source text
for unconditional and coin-gated ordinary conditions.

`tools/physical_attack_status_source_bridge.py` consumes the matching
executed copy-body event and preserves the physical card ledger. Its
inputs explicitly include:

- a preverified source contract whose body event actually appeared
  in the copied attack's resolution trace;
- the coin result for heads/tails clauses;
- attack-effect immunity for the affected opposing Active Pokémon;
- the existing typed Special Condition state when any conditions are
  already present.

The bridge uses the shared `special_condition_state` kernel to stack
Poisoned and Burned while replacing the mutually exclusive Asleep,
Paralyzed and Confused rotated-card condition. It projects the resulting
typed state to the physical board's legacy condition-name set. Existing
typed state is mandatory for an already conditioned Pokémon, because
reconstructing an irregular Poison/Burn payload from names would lose data.

Status application takes place after the source attack's damage phase,
before the damaged-by-attack reaction/Knock Out disposal steps. The bridge
preserves the original typed condition payload as a separate output for
later Checkup resolution.

## Card-grounded regression

The reproducible test copies five actual attack texts through the Haughty
Order copy engine, with physically materialized defending Pokémon.

1. Whirlipede Poison Sting inflicts Poisoned after 20 damage.
2. Darumaka Singe adds Burned despite having no printed damage.
3. Watchog Confuse Ray adds Confused.
4. Alomomola Water Pulse applies Asleep, replacing Confused while
   retaining Poisoned and Burned.
5. Servine Wrap applies Paralyzed on heads, replacing Asleep; tails
   leaves Asleep unchanged.

Negative cases reject absent coin results, inferred preexisting typed
condition payloads, and a contract whose attack was never copied.
Attack-effect immunity suppresses infliction without undoing damage.
The materialized card ledger is unchanged across the sequence.

## Validation outcome

[GitHub Actions run 37772749829](https://github.com/FlareZ123/pokemon-workplace/actions/runs/37772749829)
passed the five real source-card sequences, all three invalid-state
rejection controls, and ledger conservation checks. The final condition
stack contains Burned, Paralyzed, and Poisoned after the heads outcome
replaces Asleep. The same coin-gated attack on tails leaves the earlier
Asleep state unchanged.

## Boundaries

Only ordinary statuses from exact recognized full-text clauses are
supported. A condition's Checkup behavior is delegated to existing timed
Special Condition infrastructure. The bridge does not interpret Ability
lock, Tool prevention, a source's remaining Energy, or conditional
status text outside the exact grammar. Those are upstream eligibility
inputs or separate source contracts.

Passive damage-triggered status reactions are handled by agent48's
physical reaction modules at a different attack timing step.

## Reproduction

`results/physical_attack_status_source_bridge/reproduce.py`
provides the single-file test.
CI workflow: `validate-physical-attack-status-source.yml`.
