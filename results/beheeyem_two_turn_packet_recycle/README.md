# Two consecutive Beheeyem attacks: exact effect of recycling the Stage 1 and TAE packet

## Research question

Beheeyem `sm11-91` has **Mysterious Noise**, a three-Colorless attack that shuffles itself and attached cards into the deck while imposing next-opponent-turn Item lock. Triple Acceleration Energy `sm10-190` supplies exactly three Colorless Energy when attached to an Evolution Pokémon. Beheeyem's attack moves the attached Energy into the deck as part of attack resolution, **before** the end-of-turn discard instruction would apply to a still-attached Triple Acceleration Energy.

Can the same recycled Beheeyem/Energy help a second, already mature Elgyem attack one turn later, with only one natural card drawn on that turn? The hand must be able to supply another Beheeyem *and* another TAE to evolve and power the second Elgyem.

This exact model isolates that limited packet-acquisition problem. It demonstrates why access to one attacking packet by T2 does not guarantee another packet for T3, even with recycling.

## Conditioned physical board and sampling assumptions

Assume a 60-card deck in which **three Basic Pokémon are already guaranteed to have been acquired and put into play by T1**: an opening-active Elgyem, a second Elgyem, and a partner Basic that serves as a lock anchor. Both Elgyem are old enough to evolve during T2 and T3 respectively.

Remove those three known board cards from consideration. Among the residual **57 physical cards** are `B` Beheeyem copies, `T` Triple Acceleration Energy copies and `57 - B - T` other inert cards. By the beginning of T2, there are exactly **six other cards remaining in hand**, after the initial seven and two natural turn draws minus the three Basic cards put in play. These six are drawn uniformly without replacement from the 57-card pool. Six Prize cards are drawn uniformly from the remainder. The resulting physical deck has **45 cards** before the first attack.

A first T2 attack requires a Beheeyem and TAE in hand. The evolved attacking Pokémon shuffles its Elgyem base, Beheeyem Stage 1 and attached TAE into the 45-card deck, producing **48 cards** in the post-attack deck. The player then draws **one** natural card at the beginning of T3. To execute the second attack, the remaining hand plus that card must contain another Beheeyem and another TAE. The second Elgyem is assumed established and able to evolve and attack on T3 under all other game conditions.

There are no searches, Supporters, Abilities, extra draws, opponent interactions, switching costs, damage/KO resolution, further Prizes, additional evolution restrictions, or missing hand attachments. This conditional packet model does not estimate tournament-level consistency.

## Exact derivation

If `b` Beheeyem and `t` TAE appear in the six T2 hand cards, their joint probability is the multivariate hypergeometric distribution

\[
P(b,t)=\frac{\binom{B}{b}\binom{T}{t}\binom{57-B-T}{6-b-t}}{\binom{57}{6}}.
\]

The T2 attack is possible precisely when `b ≥ 1` and `t ≥ 1`.

Conditional on that first attack, there are four relevant cases:

- `b ≥ 2, t ≥ 2`: a second packet is already in hand; the T3 draw is irrelevant.
- `b ≥ 2, t = 1`: only TAE is missing. The returned TAE contributes **one guaranteed deck out**; the other `T-1` copies are in the 51 previously unseen cards, each unprized with probability `45/51`. The T3 TAE draw probability is `[1 + (T-1)·45/51] / 48`.
- `b = 1, t ≥ 2`: symmetric case requiring a Beheeyem draw.
- `b = 1, t = 1`: both types are missing. A single natural draw cannot restore two separate card identities, so the T3 attack is impossible under the assumptions.

Each branch is weighted by the exact `P(b,t)` to produce the two-attack probability. The code computes exact rational values using Python `Fraction`.

For a comparator, a hypothetical attack **discards** its spent Beheeyem and TAE instead of returning them to deck. Those cards then cease to be T3 draw outs. This is expressly a **counterfactual accounting benchmark** rather than a legal substitute for Mysterious Noise. With one category missing, its T3 out probability is `(T-1)/51` or `(B-1)/51`.

## Findings with four Beheeyem and four TAE

Metric | Exact probability |
| --- | ---: |
| First T2 attack packet available | **12.006938%** |
| T2 and T3 packets available, actual shuffle effect | **0.316352%** |
| T2 and T3 packets available, hypothetical discard | 0.272742% |
| Second packet conditional on first, actual shuffle | **2.634741%** |
| Second packet conditional on first, hypothetical discard | 2.271539% |

The shuffle improves the two-attack packet event by **15.9892% relative** to the hypothetical discard, but the unconditional probability remains only **0.316352%** under this exceptionally draw-starved, fully conditioned setup. The improvement is real yet much too small to rescue the overall consistency of a line dependent on repeated blind draws.

## Singleton and copy-count consequences

The exact catalog scans all **16** pairs of `B=1…4` and `T=1…4`; `reproduce.py` emits the full matrix and checks symmetry.

| Beheeyem / TAE copies | First packet by T2 | Second consecutive packet with recycling | Hypothetical discard comparator |
| --- | ---: | ---: | ---: |
| 1 / 1 | 0.9398% | **0%** | 0% |
| 1 / 4 | 3.3643% | **0.00792%** | 0% |
| 2 / 2 | 3.4898% | **0.01392%** | 0.00886% |
| 3 / 3 | 7.2844% | **0.09318%** | 0.07380% |
| 4 / 4 | 12.0069% | **0.31635%** | 0.27274% |

**Two independently required singleton packet cards cannot support consecutive T2 and T3 attacks with only one T3 draw**, even though both shuffle back. If Beheeyem is a singleton but there are several TAE copies, T3 can sometimes redraw the recycled Beheeyem, conditional on keeping another TAE in hand; this route has zero success in the no-recycle comparator. These are exact statements within the model's one-natural-draw and no-search constraints.

The model shows that a renewable attack's resource bottleneck can be the **simultaneous reacquisition of card categories**. Physical conservation of cards in the deck by itself says little about their short-horizon availability.

## Verification and interpretation

- `tools/beheeyem_recycle_packet_probability.py` implements the exact hypergeometric calculation.
- `results/beheeyem_two_turn_packet_recycle/reproduce.py` checks all 16 copy-count configurations, full exact rational reference values for the four/four case, and the singleton boundary.
- `results/beheeyem_two_turn_packet_recycle/monte_carlo.py` independently shuffles residual 57-card physical pools, puts six cards in hand and six in Prizes, resolves one recycling attack by returning exact card copies plus the Elgyem base into the deck, and samples T3 draws. The comparator keeps the consumed packet out of the deck. Five representative copy-count pairs use 500,000 sampled games each with a fixed seed.

The next step for realistic deck engineering is to combine this packet probability with **Supporter/Item retrieval paths**, discard-cost resources, and actual search sequencing. A repeatable Beheeyem line should search or otherwise recover relevant packet cards without consuming the same connectors needed to establish the next evolution. The exact bound here isolates the otherwise obscured cost of relying on blind recirculation.
