"""Exact Nest Ball role-ablation validation."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))
from bench_trigger_paid_replay import analyze_paid_replay

def test_roles(o: int) -> None:
    common = dict(other_basics=o, nest_balls=4)
    none = analyze_paid_replay(other_basics=o, nest_balls=0)
    stock = analyze_paid_replay(**common, allow_backup_nest=False,
                                allow_target_nest=False)
    backup = analyze_paid_replay(**common, allow_backup_nest=True,
                                 allow_target_nest=False)
    replay = analyze_paid_replay(**common, allow_backup_nest=False,
                                 allow_target_nest=True)
    full = analyze_paid_replay(**common)
    assert none <= stock <= min(backup, replay) <= full
    assert full == backup + replay - stock
    for name, p in (("no Nest", none), ("discard stock", stock),
                    ("with backup", backup), ("with replay", replay),
                    ("with both", full)):
        print("O", o, name, f"{100*float(p):.6f}%")
    print("Role increments, pp:",
          *(f"{100*float(x):.6f}" for x in
            (stock-none, backup-stock, replay-stock, full-none)))

if __name__ == "__main__":
    for count in (1, 3, 5):
        test_roles(count)
    print("PASS: exact partition across three Nest Ball roles")
