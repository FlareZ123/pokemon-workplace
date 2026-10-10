# Grand Tree builds its own Teleport Room sources, but copy limits bind

## Research question

Suppose Grand Tree (`sv7-136`) evolves an eligible Gothita through
Gothorita into Gothitelle (`xy3-41`) using its optional Stage 2 continuation.
The newly evolved Gothitelle supplies a fresh Teleport Room Ability. Can the
new source help recover Grand Tree from discard later in the same turn, and
how many such evolutions can a physical Expanded deck support?

This result models the resource feedback under explicit assumptions. It
does not resolve the official rule question of whether returning the *same
physical Stadium copy* makes its voluntary effect usable again in that turn.

## Interacting constraints

1. Grand Tree's Stage 1 and optional Stage 2 chain is one voluntary Stadium
   effect use. The selected Gothita must be eligible and the requisite
   Gothorita and Gothitelle must be accessible in deck.
2. A newly established Gothitelle is one independent Teleport Room source
   during the active turn, subject to ordinary Ability suppression.
3. Teleport Room is source-specific once per turn. A return path requires
   two Teleport Room source uses (Grand Tree to Brooklet Hill, Brooklet Hill
   back to Grand Tree), except that one available ordinary Stadium play
   can pay the first removal from Grand Tree.
4. Four-copy deck-name limits matter. In this model each resident Gothitelle
   arose from its own Gothita, so initial Gothitelle plus unevolved Gothita
   plus newly evolved Gothitelle cannot exceed four copies of Gothita.
   Total Gothitelle sources also cannot exceed four.
5. Ordinary board capacity is six Pokémon, minus other residents.

The model retains exact physical Stadium copies and independent Teleport
Room source IDs, but symmetry-reduces otherwise identical ready Gothita
into a count. A completed Grand Tree activation reduces ready Gothita by
one and introduces one new Gothitelle source ID. It cannot reuse a source
that has already activated Teleport Room during the turn.

## Exact bounded result

Let n be the number of existing Gothitelle, with 0 <= n <= 4, and r the
number of other permanent non-target residents. Then the initial number
of Gothita that can be ready in this particular ordinary-evolution line is

`B = min(4-n, 6-n-r)`.

If one ordinary Stadium play is available and can replace Grand Tree with
Brooklet Hill, the per-entry re-use assumption allows at most

`K_entry = min(B, n+2)`

new Gothitelle to be built within the turn. If Brooklet Hill is already in
discard and the ordinary Stadium play has been spent, the per-entry
assumption instead allows

`K_entry = min(B, n+1)`.

The source bound follows by counting required Teleport Room activations.
To achieve k >= 2 Grand Tree activations, each activation creates one source,
while returning Grand Tree requires 2(k-1)-1 source uses if a normal
Stadium play supplies the first removal, or 2(k-1) source uses without it.
By the time activation k is reached, at most n+(k-1) sources have been made
available. This yields k <= n+2 with a normal play, or k <= n+1 without one.

If the physical-copy activation interpretation proves to be the correct
ruling, additionally cap the result by the number of distinct Grand Tree
copies available in the modeled material state (one or two).

Under per-entry semantics and **one physical Grand Tree**, with r=0:

| Initial Gothitelle | Gothita available | One normal Stadium play | All-Teleport only |
|---|---:|---:|---:|
| 0 | 4 | 2 | 1 |
| 1 | 3 | **3** | 2 |
| 2 | 2 | 2 | 2 |
| 3 | 1 | 1 | 1 |
| 4 | 0 | 0 | 0 |

The best population in this restricted model is **one established
Gothitelle plus three ready Gothita**. It can hypothetically produce
three additional Gothitelle during the turn by continually turning the
fresh Pokémon into the next source pool. Starting with two Gothitelle
reduces the amount of Gothita and Stage 2 capacity remaining, yielding
a lower limit of two additional sources.

An apparently more powerful source-only calculation without the
four-copy limit would predict four newly built Gothitelle starting with
two originals. That would require six Gothitelle copies and six Gothita
ancestral copies across the field, which violates ordinary deck
construction. The name-copy constraint decisively changes the optimum.

## Exact implementation and verification

`tools/stadium_gothitelle_bootstrap.py` integrates the existing physical
Stadium entry/usage kernel. It adds `BootstrapState` with ready Gothita,
new Gothitelle count, other residents, and the live source set.

`python results/stadium_gothitelle_bootstrap/reproduce.py`

The reproducer exhaustively searches the state transitions for 176
configurations across one or two Grand Tree physical copies, two explicit
reuse policies, both Stadium replacement channels, initial source counts
0..4, and reserved board occupants 0..4 where the initial board is legal.
It verifies the bounds and an actual feedback trace starting with zero
Gothitelle sources.

## Scope and uncertainty

These are **conditional effect-access and board-population maxima**.
The executable model does not physically search the deck or prove that
Gothita, Gothorita, Gothitelle, Brooklet Hill and both necessary card-copy
stocks are available in a particular draw/Prize state. The initial state
assumes eligible Basics that were already in play before the turn; normal
first-turn and newly played evolution restrictions still apply. Locks,
opposing disruption, and real setup costs are outside this model.

The direct same-physical-copy Stadium re-entry case remains unsettled;
the two usage scopes must not be silently collapsed.

Supporting repository work:
[Grand Tree one-activation evolution chain](../grand_tree_chain_execution/),
[physical chain](../grand_tree_materialized_chain/),
[Stadium reentry identity policy](../stadium_reentry_usage_bounds/),
[mixed replacement channels](../stadium_mixed_entry_frontier/).

Official Japanese Q&A confirming multiple Gothitelle can each activate their
own Teleport Room once:
https://www.pokemon-card.com/rules/faq/search.php?freeword=%E3%82%B4%E3%83%81%E3%83%AB%E3%82%BC%E3%83%AB&page=2&regulation=all&regulation_faq_main_item1=all

Rulebook basis: I-A-02, I-A-04, I-B-04, I-H, and II-E-12; the Expanded
legal snapshot includes Grand Tree, Gothitelle, and Brooklet Hill.
