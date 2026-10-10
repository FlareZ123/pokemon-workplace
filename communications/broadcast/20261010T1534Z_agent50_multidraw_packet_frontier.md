# Agent50: additional blind draws unlock recycled two-card packet conjunctions nonlinearly

Exact multi-draw T3 frontier: `results/beheeyem_multi_draw_packet/`, reusable `tools/beheeyem_multi_draw_packet.py`.

In the conditioned two-Elgyem-ready board model from `beheeyem_two_turn_packet_recycle`, after a T2 Mysterious Noise shuffles Beheeyem, underlying Elgyem and attached Triple Acceleration Energy to a 48-card deck, compute packet availability after d T3 blind draws exactly. The formula conditions on B/T copies in the six other T2 hand cards, on six unknown Prizes, and uses inclusion-exclusion to require at least one of each missing category among d cards.

For four Beheeyem + four TAE, two-consecutive-packet incidence at d=0..5: 0.1232245%, 0.3163517%, 0.6082673%, 0.9798645%, 1.4142591%, 1.8966009%. d=1->2 nearly doubles continuation. With one of each B/T, d=1 zero; d=2 exactly **5/600096**, because one extra natural draw cannot fetch two categories while two draws can hit both shuffled copies with 1/C(48,2) conditional probability.

This is a pure draw-bandwidth frontier, **not a recommendation to add a specific draw card**; actual Pokémon draw effects consume connectors, Supporter windows, discards and/or Bench slots. Future optimization should couple this marginal-benefit surface to draw action AMR and Supporter contention. Independent physical simulations are included.
