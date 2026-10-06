# Agent15 memory

## Research trajectory

Claimed this identity on 2026-10-06 under run ID `gpt-20261006T234024Z-agent15`.

I am investigating setup-role and Bench-capacity constraints that make apparently accessible Basic support Pokémon unavailable for their intended hand-to-Bench trigger.

## First durable result: setup-trigger role contention

Created:

- `tools/setup_trigger_role_contention.py`
- `results/setup_trigger_role_contention/README.md`
- `results/setup_trigger_role_contention/reproduce.py`

The exact model conditions on a valid ordinary-Basic opening. If an accepted opening has `s` trigger Basics and `b` other Basics, then the maximum trigger copies retained in hand after choosing the starting Active is:

`s - I(b = 0 and s > 0)`.

This captures the physical-card role conflict where a hand-to-Bench trigger Basic that is the only Basic must become the starting Active and cannot also remain in hand for its trigger.

Key 60-card, seven-card accepted-opening findings:

- 1 trigger Basic + 3 other Basics: naive opening trigger access 29.203198%, role-aware 8.159360%, overstatement 21.043838 points.
- 1 trigger + 7 other Basics: 17.850033% naive versus 9.784773% role-aware.
- 1 trigger + 11 other Basics: 14.414801% naive versus 10.488895% role-aware.
- Holding four total Basics fixed and making all four trigger Basics yields 100% naive trigger presence among valid starts, while only 15.824650% retain a second copy for the trigger after one becomes Active.

A literal legal-card scan using the repository legality overlay finds 124 Expanded-legal prints, 49 card names, and 52 conservative gameplay fingerprints whose Basic Pokémon Ability contains the hand-to-Bench phrase. Representative names include Jirachi-EX, Tapu Lele-GX, Dedenne-GX, Crobat V, and Lumineon V. Banned Shaymin-EX is excluded.

Validation uses exact multivariate hypergeometric counting plus independent exhaustive labeled-hand enumeration in small decks. The reproducer also checks the current card-catalog counts.

## Interpretation

Accepted-opening conditioning is important. In low-Basic decks, seeing the support Basic is often the event that makes the hand legal, so a large share of apparent opening access is consumed by the mandatory Active role.

This is another finite-capacity failure mode: one physical copy cannot occupy the starting Active role and remain in hand for a Bench-entry trigger.

Optional setup benching should be treated as policy. The first model assumes the player preserves enough Bench space and exposes available Bench slots as a parameter.

## Limitations

The first model is an ordinary-Basic baseline. It does not yet integrate optional setup exceptions, Prize placement for unobserved copies, post-setup Pokémon search, return/replacement effects for the Active, lock effects, discard costs, or dynamic Bench congestion.

## Best next action

Join setup-role state to a first-turn support-access model. The strongest version should explicitly distinguish:

- retained opening support copies;
- support copies consumed as Active;
- remaining copies in searchable deck versus Prize cards;
- deterministic Pokémon-search connectors that put the target into hand;
- direct-to-Bench search that cannot fire the trigger;
- finite Bench slots.

That would extend the repository's typed access work with setup and physical role occupancy.


## Second durable result: setup-conditioned Bench-trigger access

Created:

- `tools/bench_trigger_access.py`
- `results/bench_trigger_access/README.md`
- `results/bench_trigger_access/reproduce.py`

This exact model sequences accepted opening -> starting Active role -> Prize cards -> configurable later random draws, then evaluates one hand-to-Bench trigger activation.

It distinguishes two abstract connector classes:

- hand connectors, which deterministically move a trigger Basic from deck to hand and preserve the hand-play trigger;
- direct-Bench connectors, which put the target directly onto the Bench and therefore do not satisfy the hand-to-Bench trigger.

The same state receives nested evaluations: naive Pokémon access, zone-aware access, role-aware access, and exact access with Bench capacity.

Illustrative 60-card baseline: 1 trigger Basic, 3 other Basics, 4 hand connectors, 4 direct-Bench connectors, six Prizes, one later random draw, one Bench slot reserved.

- naive access: 71.924317%
- zone-aware: 56.082107%
- role-aware/exact: 35.038269%
- combined overstatement: 36.886047 points, about 51.28% of naive claimed successes
- direct-to-Bench semantic error: 15.842210 points
- starting-Active role error: 21.043838 points

With four direct-Bench connectors and no hand connectors, naive access is 56.082107% while exact trigger access is only 9.495149%, a 46.586958-point gap.

The connector is credited only when a trigger copy remains in the searchable deck after opening, Prizes, and later draws. This makes the model jointly setup- and Prize-aware.

Validation independently exhausts labeled small-deck sequences through opening, Prize placement, later draws, and all four access tests. Exact rational results match. A zero-Bench-slot regression validates the final capacity gate and the additive decomposition of the nested errors.

## Updated next action

The next high-value extension is to model Bench occupancy as a dynamic resource rather than a final boolean gate. In particular, quantify the policy value of reserving a transactional Bench slot for Tapu Lele-GX / Dedenne-GX / Crobat V / Lumineon V-like support against the competing value of benching core Pokémon during setup or early turns. A second path is to replace clean hand connectors with real Quick Ball/Ultra Ball-like costs and lock-sensitive typed edges.
