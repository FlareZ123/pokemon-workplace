from __future__ import annotations

from datetime import date
from pathlib import Path

from tools.release_legality import audit_30th_celebration, release_status


def main() -> None:
    resources = Path("resources")

    waiting = audit_30th_celebration(resources, as_of=date(2026, 9, 29))
    legal = audit_30th_celebration(resources, as_of=date(2026, 9, 30))
    audit = audit_30th_celebration(resources, as_of=date(2026, 10, 7))

    assert release_status("me55", as_of=date(2026, 9, 29))[0] == "waiting_period"
    assert release_status("me55c", as_of=date(2026, 9, 29))[0] == "waiting_period"
    assert waiting["all_fallback_prints_ordinary_release_eligible"] is False

    assert release_status("me55", as_of=date(2026, 9, 30))[0] == "ordinary_release_eligible"
    assert release_status("me55c", as_of=date(2026, 9, 30))[0] == "ordinary_release_eligible"
    assert legal["all_fallback_prints_ordinary_release_eligible"] is True

    assert audit["fallback_print_count"] == 191
    assert audit["fallback_by_set"] == {"me55": 161, "me55c": 30}
    assert audit["anchor"]["ordinary_legal_date"] == "2026-09-30"
    assert audit["all_fallback_prints_ordinary_release_eligible"] is True

    candidate_ids = {
        row["id"] for row in audit["exact_prior_fingerprint_candidates"]
    }
    assert audit["exact_prior_fingerprint_candidate_count"] == 5
    assert audit["exact_prior_fingerprint_candidates_by_set"] == {
        "me55": 2,
        "me55c": 3,
    }
    assert candidate_ids == {
        "me55-126",
        "me55-127",
        "me55c-101",
        "me55c-50",
        "me55c-203",
    }

    print("release legality regression passed")


if __name__ == "__main__":
    main()
