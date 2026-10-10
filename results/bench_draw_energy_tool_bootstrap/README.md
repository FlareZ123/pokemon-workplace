# Legal Energy-and-Tool hand reduction for a Quick Ball → Crobat line

## Research question

A preceding [paid Quick Ball/Crobat/Dedenne continuation](../bench_quickball_crobat_dedenne/) showed that lowering the hand from seven cards to five increases Crobat V's Dark Asset draw count from one to three, and therefore improves an isolated singleton's final-hand retention. Can that hand reduction be achieved by a concrete legal first-turn sequence, and how often are all necessary card roles simultaneously available?

This bounded experiment uses ordinary **Energy attachment** and **Pokémon Tool attachment** to the starting Active Pokémon as two source-backed hand-reduction actions.

Implementation: [exact model](../../tools/bench_draw_energy_tool_bootstrap.py); [independent physical-card oracle](reproduce.py).

## Source-backed sequence

The advanced rulebook permits one regular Energy attachment from hand per turn (Section I-C) and attachment of Pokémon Tools to Pokémon without an existing Tool (Section I-B-02). The model requires an eligible Basic O as starting Active, a Basic Energy E, and a Tool T that O can hold. Air Balloon is an example of a Tool that could be used, provided there is no conflicting effect. Four expendable F cards, separate from E and T, are designated as candidates for Quick Ball's one-card discard payment.

The controlled opening and first normal turn run:

1. Keep one Dedenne-GX, at least one Quick Ball, at least one expendable F, and an ordinary Basic O in the seven-card opener. Choose O as Active. Crobat V and target singleton K are absent from the opener.
2. Set six Prizes and take the normal one-card turn draw. The player's hand is seven cards, with D/Q/F preserved.
3. If a Basic Energy E and a Pokémon Tool T are among those seven cards, attach one E and T to the Active O. Hand now contains five cards.
4. If K was found already, stop. Otherwise use Quick Ball, discarding F and finding Crobat V in the live deck, then Bench Crobat to draw three via Dark Asset. If K remains missing, Bench Dedenne-GX and resolve Dedechange. Dedenne-only comparison skips Quick Ball and Crobat, drawing six when K is missing.

Prerequisites include an empty Tool slot on O, a regular Energy attachment available, two free Bench slots, no Item/Ability lock, and the designated F being strategically expendable. The attachment line occupies O's Tool and consumes one Energy attachment for the turn. Those costs are not valued beyond physical legality.

## Joint 60-card population

| Role | Copies |
| --- | ---: |
| Dedenne-GX D, Crobat V C, non-Basic singleton K | 1 each |
| Quick Ball Q | 4 |
| Expendable F, other ordinary Basic starters O | 4 each |
| Basic Energy E, attachable Pokémon Tools T | 4 each |
| Neutral filler | 37 |
| **Total** | **60** |

All four E and all four T are assumed to be fungible for this particular attachment step. Other fillers do not secretly provide the same role. E, T, F and O are distinct card classes.

The exact accepted-opening probability (D, C and four O are the six ordinary Basics) is **54.143607784%**. Required opener D/Q/F/O plus visible E/T after the normal draw, Crobat still live and K **also live** after Prize placement, happens in **0.0294284273%** of accepted openings. These are the K-in-deck states where the extra staged draw can create incremental target success.

For a fixed K-in-live-deck state, the Dedenne-only line draws six cards from a 46-card deck containing Crobat and K. The stage pays Quick Ball, removes Crobat, draws three with Dark Asset and six with Dedechange if necessary; K can appear in any of those nine cards from the remaining 45-card deck. The conditional staged gain is thus exactly

\[
\frac9{45}-\frac6{46}=\frac8{115}
=6.956521739\text{ percentage points}.
\]

After weighting all joint setup, draw, Prize and target-location states, the gain is

**0.00204719494 percentage points of accepted-opening target access**

for this particular staged-policy path and comparison.

A larger conditional gain can coexist with a smaller material-weighted contribution: the extra E/T requirements are restrictive, even though the resulting three-card Crobat draw is stronger. This should not be compared with the earlier h=7 material-weighted number as if both represented a full-deck optimization, since the eligible subpopulations differ.

## Combinatorics and information conditioning

For fixed opening counts q,f,o,e,t of Quick Ball, expendable cards, ordinary starters, Basic Energy and Tools, the number of hands equals the corresponding product of binomial choices, times one mandatory D and neutral filler count. Valid later-draw choices depend on whether the opener already has E and T:

- If both are present, any of the 51 remaining non-C/non-K cards can be drawn.
- If E is present and T missing, the turn draw must supply one of the remaining Tools.
- If T is present and E missing, the turn draw must supply one of the remaining Energies.
- If both are missing, one card cannot complete both requirements.

The eligible K-live event then requires the six Prizes to avoid the two remaining singletons C and K. The corresponding Prize factor is \`C(50,6)/C(52,6)\`, conditioned on a qualifying normal draw. Because drawing E or T can prevent the normal draw from being K, the draw-target and enabling-material events must be counted jointly. The model avoids assuming independence between them.

## Independent verification

The reproducible test enumerates physically labeled card subsets for 20- and 21-card toy decks. It independently assigns accepted openings, all Prize pairs and each possible normal turn draw. It checks the visible E/T roles, exact C/K live locations, and averages every possible shuffled K rank in both the original Dedenne deck and the post-Quick-Ball Crobat-depleted deck. In both cases, every accepted-opening mass and the complete material-weighted target-retention gain match the grouped combinatorial model as exact rational numbers.

Run \`python results/bench_draw_energy_tool_bootstrap/reproduce.py\`.

## Limits and next questions

This calculation does not cover Tool eligibility complications, opponent lock, ability suppression, normal Energy-attachment opportunity cost, damage output, future strategic value of retaining F, board exposure, target value after discarding, or actual metagame frequencies. It conditions on a narrow 60-card role composition and uses no paid search other than Quick Ball.

A useful extension would optimize the decision to attach E and T conditional on whether staging is needed, while assigning opportunity costs to the Energy attachment, Tool slot and second two-Prize support Pokémon. That policy could then be evaluated alongside cases where Crobat is drawn naturally or Prized, rather than conditioned live.
