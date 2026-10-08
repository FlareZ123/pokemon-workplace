# Source-scoped lock permissions on physically conserved gust transactions

## Question

The [physical paired-switch ledger bridge](../paired_switch_identity_bridge/)
handles exact in-hand Trainer instance spending and two-sided board movement.
However, whether a Trainer card can be played from hand depends on its
current legal print, exact action class, and any active opponent or
player-wide restrictions.

Can that complete source-card transaction reuse the repository's audited
source-scoped permission system, including ACE SPEC-specific restrictions?

## Implementation

`tools/paired_gust_source_permissions.py` is a thin adapter between:

- the exact print `CardActionMetadata` index;
- `project_source_scoped_permissions()` and
  `action_allowed()`, retaining residual fine-grained selectors;
- the materialized paired-switch hand-to-discard executor.

It checks the source print name and action class against the requested
paired-switch program, projects already-active restrictions, and executes
the immutable transaction only when permission is granted. The resulting
state spends the correct Supporter quota and hand source card identities
without storing stale lock bits inside the board or ledger.

The caller remains responsible for determining which lock sources are
actually active on the current board. No speculative lock activation is
introduced here.

## Card-grounded permission matrix

Source Trainer cards are real effectively legal print metadata:

| Gust action | Example print | Card kind | Important tags |
| --- | --- | --- | --- |
| Prime Catcher | `sv5-157` | Item | ACE SPEC |
| Cross Switcher | `swsh8-230` | Item | Fusion Strike |
| Guzma | `sm3-115` | Supporter | None of those selectors |
| Team Rocket's Giovanni | `sv10-174` | Supporter | Name identifies a Team Rocket card |

The restrictions come from real source card text in the same snapshot:

- Vileplume `xy7-3`, Irritating Pollen: Item lock.
- Stoutland `bw7-122`, Sentinel: Supporter lock.
- Spiritomb `bw11-87`, Sealing Scream: ACE SPEC lock.
- Darkrai & Umbreon-GX `sm11-125`, Dark Moon-GX: Trainer-wide lock.

These are **already-active** restrictions in this matrix. For example,
Stoutland must actually satisfy its Active-only condition before its
Supporter lock applies. This test does not pretend that the above
sources all coexist as an unconditionally persistent board.

| Active restriction on acting player | Prime Catcher | Cross Switcher | Guzma | Giovanni |
| --- | --- | --- | --- | --- |
| None | Allowed | Allowed | Allowed | Allowed |
| Vileplume Item lock | Blocked | Blocked | Allowed | Allowed |
| Stoutland Supporter lock | Allowed | Allowed | Blocked | Blocked |
| Spiritomb ACE SPEC lock | Blocked | Allowed | Allowed | Allowed |
| Trainer-wide lock | Blocked | Blocked | Blocked | Blocked |
| Item and Supporter lock | Blocked | Blocked | Blocked | Blocked |

The Spiritomb row provides an important exception to broad action-class
logic: Prime Catcher and Cross Switcher are both Item actions, but
Spiritomb's ACE SPEC selector blocks only Prime.

A full physical transaction on an allowed source still has to pass
the usual own/opponent switch eligibility, source copy count, and
Supporter quota checks. The latter can reject Guzma even without any
opposing Supporter lock if a different Supporter was already played.

## Validation

`results/paired_gust_source_permissions/reproduce.py`:

- loads current-legal print metadata from the bundled cards;
- compiles each actual restriction source text through
  `source_scoped_action_restrictions`;
- checks all **24 source-by-restriction scenarios** against the
  independent `restrictions_block_attempt()` predicate;
- verifies expected physical hand-to-discard and two-sided switch
  execution for the **11 authorized** states;
- checks rejection of mismatched print metadata and an exhausted
  Supporter quota.

All assertions operate on real current-semantic source identities and
physical Trainer card instance IDs.

## Boundaries

The wrapper accepts a set of restrictions already active against the
acting player. It does not decide whether source Pokemon are in play,
Active, suppressed by Ability lock, or otherwise disabled. An
unresolved alternative restriction effect must be resolved upstream
before its permission predicate is meaningful. It also does not
represent target immunity or coin-gated play attempts.

A next extension should derive the restrictions from actual physical
source boards and the causal Ability-lock state, re-evaluating them
after switch actions that move lock sources out of Active.
