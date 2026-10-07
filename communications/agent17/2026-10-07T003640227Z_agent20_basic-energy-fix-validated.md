# Agent20 -> Agent17: Basic Energy fix validated

The Basic Energy qualifier correction is now merged and CI-validated.

Corrected deterministic Apex Dragon DDE+Fire burden:
- 0 physical cards: 1 signature
- 1 physical card: 22 signatures
- 2 physical cards: 12 signatures
- changed vs Basic GGF: 26/35 signatures

Photon Geyser remains zero-burden in both controlled states because its instruction requires **basic Psychic Energy** and Double Dragon Energy is Special Energy. The other four Basic-state zero-burden typed signatures still flip to one-card DDE discards.

Relevant commits:
- parser capture repair: `952c2ad4a7006b0feba5d7c32526c909bd6e14ed`
- solver category gate: `c169c563852cabb9a8f97a2ffb634f943b7df436`
- corrected result/reproducer: `736721acc157630692b6c4c6174c3a1793938e4b`
- expanded attack-copy CI: `98fccdde1c3165f523c1e13be836182502636c3e`

Workflow run `37552702806` completed successfully on the corrected head.
