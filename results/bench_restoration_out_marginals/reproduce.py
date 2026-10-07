from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from bench_restoration_out_marginals import build_result


def main() -> None:
    r = build_result()
    z = r["states"]["zero_slack"]
    o = r["states"]["one_slack"]
    m = r["single_copy_marginals"]
    assert z["live_unlockers"] == 2 and z["live_remover_outs"] == 0
    assert o["live_unlockers"] == 4 and o["live_remover_outs"] == 2
    assert z["unlock_probability_fraction"] == "37/156"
    assert o["unlock_probability_fraction"] == "3903/9139"
    assert z["joint_unlock_plus_entrant_fraction"] == "245/2812"
    assert o["joint_unlock_plus_entrant_fraction"] == "13175/82251"
    assert m["zero_slack_add_remover_pp"] == 0.0
    assert abs(m["zero_slack_add_direct_pp"] - 10.037112010796222) < 1e-12
    assert abs(m["one_slack_add_direct_pp"] - m["one_slack_add_remover_pp"]) < 1e-12
    print("bench_restoration_out_marginals regression passed")


if __name__ == "__main__":
    main()
