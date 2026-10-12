"""Cross-check for one-draw Quick Ball option model."""
from quick_ball_pre_draw_option import opening_option_probability

if __name__ == "__main__":
    r = opening_option_probability(60, 6, other_starters=10, attacker_starter_copies=1, critical_nonstarter=4, rescue_nonstarter=2, quick_ball_copies=4, disposable_nonstarter=12)
    assert abs(r.wait_joint - 0.1775536858681557) < 1e-12
    print(r)
