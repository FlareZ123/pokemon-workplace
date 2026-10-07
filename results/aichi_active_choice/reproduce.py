"""Reproduce the Aichi starting-Active policy comparison."""

from aichi_active_choice import ANY_ROUTE_ENDPOINTS, simulate_active_choice


def main() -> None:
    trials = 100_000
    result = simulate_active_choice(trials, seed=20261007)

    print(f"trials={trials}")
    for endpoint in ANY_ROUTE_ENDPOINTS:
        default = result.default_successes.get(endpoint, 0)
        bunnelby = result.bunnelby_first_successes.get(endpoint, 0)
        oracle = result.oracle_successes.get(endpoint, 0)
        oracle_gain = result.oracle_gains.get(endpoint, 0)
        b_gain = result.bunnelby_first_gains.get(endpoint, 0)
        b_loss = result.bunnelby_first_losses.get(endpoint, 0)

        assert oracle == default
        assert oracle_gain == 0
        assert bunnelby == default
        assert b_gain == 0
        assert b_loss == 0

        print(
            endpoint,
            f"default={default / trials:.8f}",
            f"bunnelby_first={bunnelby / trials:.8f}",
            f"oracle={oracle / trials:.8f}",
            f"b_gain={b_gain}",
            f"b_loss={b_loss}",
            f"oracle_gain={oracle_gain}",
        )


if __name__ == "__main__":
    main()
