"""Redundancy sensitivity of T2 Beheeyem+TAE packet and alternative Basic-line certificates."""

from __future__ import annotations

import json
from reproduce import continuation_access


def main() -> None:
    rows = []
    for elgyem in (3, 4):
        for anchor in (1, 2, 3, 4):
            for eligible in (True, False):
                candidates = []
                for vip in range(5):
                    for nest in range(5 - vip):
                        poffin = 4 - vip - nest
                        *_, both = continuation_access(
                            vip, nest, poffin, elgyem=elgyem,
                            anchor=anchor, anchor_poffin_eligible=eligible
                        )
                        candidates.append((vip, nest, poffin, both))
                best = max(candidates, key=lambda row: row[-1])
                expected = (
                    (0, 0, 4) if eligible else
                    ((3, 0, 1) if elgyem == 3 else (4, 0, 0))
                )
                assert best[:3] == expected
                rows.append({
                    "elgyem": elgyem,
                    "anchor": anchor,
                    "anchor_poffin_eligible": eligible,
                    "best_vip": best[0],
                    "best_nest": best[1],
                    "best_poffin": best[2],
                    "best_union_percent": round(100 * float(best[-1]), 6),
                })
    assert len(rows) == 16
    assert rows[-1]["best_union_percent"] == 1.344844
    assert rows[-2]["best_union_percent"] == 1.438726
    print(json.dumps({"fixed_item_slots":4, "rows":rows},indent=2))


if __name__ == "__main__":
    main()
