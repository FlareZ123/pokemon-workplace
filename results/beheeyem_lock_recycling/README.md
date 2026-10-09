# Renewable Beheeyem Item lock: physical pipeline and Prize collapse

## Question

\`Mysterious Noise\` shuffles Beheeyem \`sm11-91\` and **all attached cards** into the deck while imposing Item lock for the opponent's next turn. Triple Acceleration Energy \`sm10-190\` supplies its three-Colorless attack requirement. Is the attack renewable on consecutive turns without spending a fresh Beheeyem or Triple Acceleration Energy copy each time?

## Rules and card basis

- Beheeyem \`sm11-91\`: three Colorless Energy for Mysterious Noise; the attacking Pokémon and attached cards shuffle into the deck as part of the attack effect.
- Triple Acceleration Energy \`sm10-190\`: supplies three Colorless Energy on an Evolution Pokémon, and discards at end of turn **if still attached**. It returns to the deck with Beheeyem before the turn-end discard condition could apply.
- Ordinary evolution restriction: a Basic played this turn cannot evolve during that same turn. Evolution on your own first turn is also ordinarily disallowed.
- Float Stone \`bw9-99\` makes the attached Pokémon have no Retreat Cost. The lock anchor retains its Pokémon Tool when it moves between Bench and Active. This gives one free ordinary retreat from the anchor to Beheeyem on each later turn, if no outside retreat prohibition applies.
- The anchor can be Stoutland \`bw7-122\` for Supporter lock, Honchkrow-GX \`sm10-109\` for Tool/Stadium/Special Energy lock, or Galarian Weezing \`swsh2-113\` for opposing Ability suppression.

## Ideal-access construction

Assume a fully established anchor with Float Stone is available when turn-two Beheeyem attacks. An oracle may retrieve exact cards from the deck into hand at no cost, the opponent does not intervene, and only ordinary evolutions, one manual Energy attachment per turn, and one ordinary retreat per turn are used.

Initially, Elgyem A occupies the Active Spot and Elgyem B has already entered the Bench on turn one. Both have the opportunity to evolve on turn two or later.

| Own turn | Ready Elgyem | Action | End-state |
| --- | --- | --- | --- |
| 2 | A | Evolve A into Beheeyem; attach TAE; Mysterious Noise | A, Beheeyem, TAE return to deck; anchor becomes Active; B remains Bench |
| 3 | B | Replay A onto Bench; evolve B; attach recycled TAE; freely retreat anchor; Mysterious Noise | B, Beheeyem, TAE return to deck; A remains Bench; anchor becomes Active |
| 4 | A | Replay B onto Bench; evolve A; attach recycled TAE; freely retreat anchor; Mysterious Noise | A, Beheeyem, TAE return to deck; B remains Bench; anchor becomes Active |
| 5+ | Alternate | Repeat the two-Basic pipeline | Item lock reapplied for each opponent turn |

**Result under these assumptions:** one Beheeyem print, one Triple Acceleration Energy, two physical Elgyem, one persistent anchor, and one Float Stone can support arbitrarily many consecutive Mysterious Noise attack turns, subject to the stated oracle and absence of interference.

**Conditional necessity:** With only one Elgyem and ordinary evolution, after it shuffles away on turn two it can be replayed on turn three but cannot evolve again that same turn. Consecutive turn-two/turn-three Mysterious Noise attacks therefore require at least two Elgyem (or additional effects that explicitly bypass evolution restrictions, outside this model).

## Access throughput matters

Renewing cards through deck shuffles does not renew access automatically. At the start of each later turn, the singleton Beheeyem and Triple Acceleration Energy are back in the deck, and the prior attacker's Elgyem must also be retrieved and played to keep the next-turn evolution pipeline alive. Thus, with these singleton counts, **three specific recycled card identities must be reacquired during each cycle**, plus an ordinary evolution, an Energy attachment, and movement of the anchor from Active to Bench. These may be met by drawing several cards or by using search effects; they are not three compulsory separate search actions.

No actual Trainer/Supporter search lines, discard payments, opponent interaction, or Prize-recovery cards are modeled. In particular, the example is a mechanical feasibility witness, not a claim that a competitive deck can meet this throughput reliably.

## Exact initial Prize collapse

With six random Prize cards among 60, the chance that **all copies** of a named component are Prized is \`C(60-k,6-k)/C(60,6)\` when that component has \`k\` copies. For disjoint Beheeyem and Triple Acceleration Energy categories, inclusion-exclusion gives the chance that either entire component is Prized.

| Beheeyem copies | Triple Acceleration Energy copies | At least one component entirely Prized |
| ---: | ---: | ---: |
| 1 | 1 | 19.152542% |
| 2 | 2 | 1.691839% |

This is initial Prize configuration risk if the deck cannot access the Prize zone. Prize taking, Gladion-style recovery, or other effects can later change actual availability. The two-copy setup also changes access throughput because backup copies can remain in the hand.

## Reproduction and limits

\`results/beheeyem_lock_recycling/reproduce.py\` simulates ordinary evolution-age constraints and physical Elgyem alternation for turns two through eight. It asserts that one Elgyem attacks only on turn two, while two Elgyem permit the sequence \`A,B,A,B,A,B,A\`. The calculation uses exact rational combinatorics to validate the joint Prize collapse.

Reproduce:

\`python results/beheeyem_lock_recycling/reproduce.py\`

Further work should replace the oracle with the repository's legal search executors and card-level resource accounting, incorporating Prize uncertainty, the initial anchor-setup burden, Supporter contention, real retreat access, and the opponent's ability to KO or gust either pipeline Pokémon. In a metagame setting, the restriction combination's tactical value depends on which channels the opponent actually needs during each locked turn.
