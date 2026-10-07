from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from supporter_play_event_corpus import supporter_play_sensitive_rows, summarize_sensitive_rows
from supporter_play_event_history import SupporterExecutionState, SupporterIdentity, play_supporter_from_hand, played_supporter_from_hand


def main() -> None:
    summary = summarize_sensitive_rows(supporter_play_sensitive_rows(ROOT / "resources"))
    assert summary["print_rows"] == 62
    assert summary["categories"] == {"history_gate": 28, "play_lock": 8, "play_reaction": 26}
    card = SupporterIdentity("copy-1", "Team Rocket's Ariana")
    state = play_supporter_from_hand(SupporterExecutionState(), card)
    assert state is not None
    assert played_supporter_from_hand(state, name_contains="Team Rocket")
    print("supporter_play_event_history regression: PASS")
    print(summary)


if __name__ == "__main__":
    main()
