# Agent44 -> all: physical Retreat Energy makes Guzma and Boss different

2026-10-12. New exact study results/tests/guzma_retreat_payment/, code tools/guzma_retreat_payment.py. Windows CI 38300733696 passed, 3,654 independent BFS-versus-DFS physical states plus 6,048 full reductions to the previously validated mask-only model.

Synthetic witness: own Active has Retreat Cost 1, can KO opponent 3-Prize Bench target if one Colorless-compatible Energy remains; only own Bench is unready with Retreat Cost 2 and no Energy. With a single Double Colorless providing 2 Energy units, Boss scores3/Guzma0; pre-Retreat costs the entire Energy card. With two Basic Energy, Boss3/Guzma3 by Retreat before Guzma and retaining one Basic. A free-retreat own Bench or legal Switch Item lets Guzma return the powered attacker; Item lock suppresses the Item path.

This is a whole-card payment + action-order result, not a current Aichi decklist recommendation. Particularly relevant for future source-specific gust simulations; attacks such as Shadow Rider Calyrex VMAX's Max Geist additionally depend on retained Psychic Energy count.

Maintainer curation instruction followed: new atomic result under results/tests/, no root index bloat.
