# Replacement reachability can fail under shared Supporter bandwidth

## Question

If a discarded required card can be searched again later in the same turn, is the discard automatically safe?

No.

A replacement route can be individually live while the combined endpoint is impossible because the replacement search competes for the same action window as another required search.

Implementation: `tools/bounded_state_planner.py`  
Reproducer: `results/replacement_connector_contention/reproduce.py`

## Bounded planner

`bounded_state_planner.py` is a small breadth-first planner over immutable states.

It receives named action generators that already enforce their own Pokémon TCG mechanics. The planner composes those validated transitions up to a finite action depth and returns one shortest goal witness.

The planner therefore does not duplicate Trainer rules, Energy rules, lock rules, or turn budgets. In this result, the action generators are exact `trainer_search_transaction.py` transitions.

## Concrete state

Before a one-card discard decision, the hand contains:

- one expendable fodder card;
- one current TM: Evolution;
- Arven;
- Colress's Tenacity;
- Guzma & Hala.

The deck contains:

- one replacement TM: Evolution;
- one Jet Energy.

The endpoint requires TM: Evolution and Jet Energy in hand before the current action window ends.

The two mechanical discard candidates are:

- fodder;
- the current TM: Evolution.

## Separate Supporter connectors

Arven can search the replacement TM: Evolution.

Colress's Tenacity can search Jet Energy.

After discarding the current TM, both endpoint resources are therefore **individually reachable** in one Supporter play.

Under the ordinary one-Supporter limit, the joint endpoint is unreachable:

- Arven restores TM but leaves Jet missing;
- Colress finds Jet but leaves TM missing;
- after either play, the Supporter quota is exhausted.

The continuation-aware discard policy therefore keeps only the fodder discard as safe.

This is a direct connector-contention counterexample: two true access edges do not compose when they consume the same action budget.

## Raising the Supporter limit

With `supporter_play_limit=2`, the bounded planner can play both Supporters in the same action window.

The TM discard becomes future-feasible.

The current card value has not changed. The legal continuation set changed because one shared action resource became larger.

## Multi-axis connector rescue

With the ordinary one-Supporter limit restored, the planner is also given Guzma & Hala.

Guzma & Hala's paid branch can search both:

- TM: Evolution;
- Jet Energy.

The exact transaction uses the available Arven and Colress's Tenacity as its two-card discard payment, then retrieves both endpoint resources in one Supporter play.

The TM discard becomes safe again.

This shows why multi-axis connectors can have value beyond raw search breadth. They can collapse several otherwise competing resource channels into one scarce Supporter action.

## Finding

Replacement existence is insufficient for discard safety.

A required current copy is safely expendable only when the replacement and every other deadline-bound obligation are **jointly reachable under shared action resources**.

This strengthens continuation-aware DCI:

- physical replacement copies matter;
- search eligibility matters;
- endpoint deadlines matter;
- Supporter contention matters;
- multi-axis output capacity matters.

An optimizer that checks each missing resource independently can still classify an unsafe discard as recoverable.

## Limits

The regression uses a synthetic one-card discard decision followed by real compiled Supporter searches. It isolates action-window contention rather than modeling a particular Item that causes the first discard.

The bounded planner is deterministic and finite-depth. It does not yet model hidden information, opponent responses, probabilistic branches, or turn-boundary deadlines.

## Next useful work

The next extension is deadline-aware planning across turn boundaries.

A replacement may be reachable eventually while still arriving too late for an attack, lock setup, Prize effect, or end-of-turn requirement. The same bounded planner can be composed with `turn_sequence_kernel.py` once endpoint deadlines are represented explicitly.
