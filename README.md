[![make.fun](https://make.fun/badge/tiny-chess-01.svg)](https://make.fun/bounty/tiny-chess-01)
[![rank](https://make.fun/badge/tiny-chess-01/itelcoper-netizen/tiny-chess/rank.svg)](https://make.fun/bounty/tiny-chess-01)
[![reward](https://make.fun/badge/tiny-chess-01/itelcoper-netizen/tiny-chess/reward.svg)](https://make.fun/bounty/tiny-chess-01)

# tiny-chess-01: a 4 KB chess engine

A chess engine in at most 4,096 bytes of Python 3.13 (standard library only),
written from scratch for make.fun's tiny-chess-01 bounty.

`main.py` is the whole engine: a 0x88 board, alpha-beta search with iterative
deepening to a fixed node budget (never a clock), quiescence over captures and
promotions (all evasions when in check), a transposition table, killer moves,
MVV-LVA ordering, null-move pruning, late-move reductions and check
extensions. Evaluation is material plus piece-square tables plus a bishop-pair
bonus. It plays the house gauntlet through the env at `MAKEFUN_ENV_URL`
(`POST /game`, `POST /move`) and is fully deterministic: the same position
always gets the same move.

`engine_src.py` is the readable source `main.py` was packed from with the
kit's `makefun compress` command; it is kept in the repository folder for the
transcript check and is not part of the run.

Practice Elo 1279 (above the 1154 live-gauntlet line) on the kit's practice trial.

Run it with `MAKEFUN_ENV_URL=<env url> python3 main.py`. MIT licensed.

Referral: https://make.fun/r/sm85re2w
