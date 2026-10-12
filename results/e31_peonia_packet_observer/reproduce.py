"""Execute the Peonia packet choice/observer physical regression."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from e31_peonia_packet_observer import run


def main() -> None:
    metrics = run()
    assert metrics["posterior_jirachi_at_slot2"] == 1.0
    assert metrics["posterior_greedy_at_slot0"] == 0.5
    for key, value in metrics.items():
        print(f"{key}={value:.12g}")
    print("Peonia packet selection + pending observer integration passed")


if __name__ == "__main__":
    main()
