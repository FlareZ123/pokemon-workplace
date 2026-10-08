"""Prime Catcher opponent-gust / mandatory own-switch sequencing geometry.

Assumptions: the opponent has a legal Benched gust target; the current
attacker can KO that target if ready when the turn's attack is declared.
Ready is a supplied board predicate, not inferred from actual Energy/HP.
No lock prevents the represented Item actions.
"""
from collections import deque
from dataclasses import dataclass, replace


@dataclass(frozen=True)
class OwnTurn:
    active_ready: bool
    bench_ready: tuple[bool, ...]
    hand_ready: tuple[bool, ...] = ()
    prime_ready: bool = True
    gusted: bool = False
    switches: int = 0


def legal_actions(state: OwnTurn):
    """Generate ordinary Bench entries, Prime, and finite self-switch actions."""
    for i, ready in enumerate(state.hand_ready):
        if i and ready in state.hand_ready[:i]:
            continue
        if len(state.bench_ready) < 5:
            hand = state.hand_ready[:i] + state.hand_ready[i + 1 :]
            bench = tuple(sorted(state.bench_ready + (ready,)))
            yield f"Bench {ready}", replace(
                state, bench_ready=bench, hand_ready=hand
            )

    if state.prime_ready and not state.gusted:
        # Prime Catcher's opponent switch resolves first. If our Bench is
        # empty, its conditional own-switch clause cannot resolve.
        if not state.bench_ready:
            yield "Prime (no own Bench)", replace(
                state, prime_ready=False, gusted=True
            )
        for i, ready in enumerate(state.bench_ready):
            bench = list(state.bench_ready)
            bench[i] = state.active_ready
            yield f"Prime -> own {ready}", replace(
                state, active_ready=ready, bench_ready=tuple(sorted(bench)),
                prime_ready=False, gusted=True
            )

    if state.switches and state.bench_ready:
        for i, ready in enumerate(state.bench_ready):
            bench = list(state.bench_ready)
            bench[i] = state.active_ready
            yield f"Switch -> own {ready}", replace(
                state, active_ready=ready, bench_ready=tuple(sorted(bench)),
                switches=state.switches - 1
            )


def attack_witness(state: OwnTurn, required_first: str | None = None):
    """Shortest legal sequence gusting the target and ending ready to attack.

    Any Pokemon initially in hand must also be Benched by the attack
    deadline. A None result means the represented endpoint is unreachable.
    """
    queue = deque([(state, ())])
    visited = {state}
    while queue:
        current, line = queue.popleft()
        if current.gusted and current.active_ready and not current.hand_ready:
            return line
        for label, successor in legal_actions(current):
            if not line and required_first and not label.startswith(required_first):
                continue
            if successor not in visited:
                visited.add(successor)
                queue.append((successor, line + (label,)))
    return None
