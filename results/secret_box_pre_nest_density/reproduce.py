"""SFT: 60-card Nest Ball copy-density sequencing marginals."""
from __future__ import annotations

from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/"tools"))

from secret_box_pre_nest_density import scan_nest_density


def main():
    rows=scan_nest_density()
    assert len(rows)==8
    for r in rows:
        assert r.box_first<=r.choose_order<=r.clairvoyant_upper
        assert 0<=r.advantage<=r.advantage_hand_mass
        print(
            f"D={r.disposable_copies:2d} I={r.nest_ball_copies} "
            f"Box-first={100*float(r.box_first):.8f}% "
            f"Choice={100*float(r.choose_order):.8f}% "
            f"Gain={100*float(r.advantage):.10f} pp "
            f"Gap={100*float(r.clairvoyant_upper-r.choose_order):.10f} pp "
            f"improved hand states={r.advantage_state_count} "
            f"improved hand mass={100*float(r.advantage_hand_mass):.10f}%"
        )
        if (r.disposable_copies,r.nest_ball_copies)==(20,1):
            assert r.advantage==0
    print("ALL TESTS PASSED")


if __name__=="__main__":
    main()
