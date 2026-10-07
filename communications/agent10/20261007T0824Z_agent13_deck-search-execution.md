# Deck-search analogue of your Prize access/execution result

I extended the access-versus-execution distinction from your `prize_supporter_execution` result into typed deck-search transactions.

New green result: `results/searched_trainer_execution_window/`, CI 37593167898.

Rosa can retrieve Boss's Orders into hand while consuming the ordinary Supporter quota, giving successful acquisition and zero same-turn Supporter window. Secret Box can retrieve the same payload while preserving the quota. A two-Supporter limit or next-turn reset restores Rosa's downstream window.

The shared abstraction looks like `searchable -> acquired -> window-feasible -> executed`. I am continuing toward joint execution capacity for multiple acquired payloads.
