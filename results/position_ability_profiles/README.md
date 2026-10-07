# Position-changing Ability semantic island

## Question

Can common movement Abilities be compiled into executable position transitions while preserving whether the Ability is a free turn action, tied to an event, constrained by the source Pokémon's position, or controlled by the opponent?

Implementation: `tools/position_ability_profiles.py`  
Regression: `results/position_ability_profiles/reproduce.py`

## Method

The compiler uses an exact whitelist of pure movement Ability texts. It reuses the repository's legality baseline plus the corrected Ability geometry and activation classifiers.

The profile retains:

- self-switch, targeted gust, or opponent-chosen force-out semantics;
- chooser authority;
- source geometry such as Active-only, Bench-only, hand-to-evolve trigger, or hand-to-Bench trigger;
- event-triggered versus freely callable turn-action timing;
- whether a self-switch promotes the source Pokémon or allows any Benched replacement.

The executor operates on conserved `BoardState` objects. Ability lock is an explicit gate. Event-triggered profiles also require an explicit `trigger_satisfied=True`, preventing them from being treated as ordinary turn actions.

## Result

The current clean-text semantic island contains **52 legal print-level profiles across 23 card names**:

| Movement kind | Profiles |
| --- | ---: |
| self switch | 22 |
| actor-chosen targeted gust | 17 |
| opponent-chosen force-out | 13 |

Representative cases:

- Keldeo-EX `bw7-49` / Rush In is a Bench-only self-promotion turn action;
- Solgaleo-GX `sm1-89` / Ultra Road is an in-play turn action that may choose any Benched replacement;
- Umbreon VMAX `swsh7-95` / Dark Signal is a hand-evolution-triggered targeted gust;
- Hariyama `me1-73` / Heave-Ho Catcher is also hand-evolution-triggered despite beginning with “Once during your turn”;
- Mabosstiff `sv1-137` / Intimidating Howl gives replacement choice to the opponent;
- Salamence `sm7-106` / Dragon Wind requires the source to be Active;
- Swellow `xy1-103` / Drive Off is tied to hand-to-Bench entry.

## Strategic interpretation

Movement Ability access is a conjunction of effect semantics and activation geometry.

Dark Signal and an ordinary gust Item may create the same physical opposing switch, but Dark Signal requires the evolution-from-hand event and can disappear under Ability lock. Rush In and Ultra Road both move the player's Active Pokémon, but Rush In can only promote the source Pokémon from the Bench while Ultra Road can choose among available Benched Pokémon.

This affects AMR and graph search. A planner should avoid exposing every movement Ability as a generic edge whenever the source card is in play. Event history, source position, Ability lock, and chooser authority all change the reachable state set.

The timing-classifier correction matters directly here. “Once during your turn” is a frequency cap when followed by a specific event clause. It does not make an evolution-triggered or movement-triggered Ability freely callable.

## Scope

This is deliberately conservative. The whitelist excludes movement Abilities bundled with resource movement, Special Conditions, discard costs, coin flips, target restrictions, self-removal, VSTAR quotas, and multi-step movement programs.

The executor does not spend once-per-turn history, perform trigger-generating actions, or evaluate card-specific resource predicates. Those remain upstream. It only refuses event-triggered execution until the caller proves the event happened.

## Reproduction

Run `python results/position_ability_profiles/reproduce.py`.
