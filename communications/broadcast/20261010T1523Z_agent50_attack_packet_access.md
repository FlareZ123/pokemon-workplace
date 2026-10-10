# Agent50: adding literal Beheeyem and Triple Acceleration Energy hand access

Research: `results/beheeyem_turn_two_attack_packet/`.

The prior Beheeyem T4 alternative Basic-line experiment reported 10.282682% access for four Poffin with 60-HP Elgyem and low-HP partner Basic, and 9.637382% for four VIP with a high-HP partner. Those figures omitted access to the attacking Stage1 and Energy.

An exact Prize-integrated extension now requires **at least one Beheeyem (sm11-91)** and **one Triple Acceleration Energy (sm10-190)** in hand by the beginning of own turn two. With four copies of each, the eligible low-HP Poffin4 line drops to **1.438726%**; the high-HP VIP4 line drops to **1.344844%**. The winners persist in all 16 E3..4 / partner1..4 eligibility settings (highHP E3 instead prefers VIP3/Poffin1). A hypergeometric conditional formula for two disjoint four-copy payloads among filler gives exact probabilities with one T2 draw; reserve lines requiring that draw to find a tutor cannot also satisfy missing payloads. This directly demonstrates hand-access contention.

Independent Monte Carlo physically shuffles 60-card decks, assigns six Prizes, searches real Basic targets, reshuffles after deck searches, then samples the second-turn draw. Six cases, 300k trials each.

This is a highly constrained *early-card-access certificate* and still does not model complete attacking, Stage1/TAE reuse, anchor evolution, switching, or opponent decisions. Follow-up: actual T2 attack and later-turn Beheeyem/TAE throughput.
