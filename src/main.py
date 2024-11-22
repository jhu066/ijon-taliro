from __future__ import annotations

import itertools
import pathlib
import pickle
import pprint
import subprocess
import tempfile
import typing

import click
import staliro
import staliro.models as models
import staliro.optimizers as optimizers
import staliro.specifications.rtamt as rtamt

Command: typing.TypeAlias = typing.Literal["0,0", "0,1", "1,0", "1,1"]
WIN_POSITIONS: typing.Final[dict[int, int]] = {
    0: 3149, # World 1-1
    1: 160,  # World 1-2
    2: 257,  # World 1-3
    3: 416,  # World 1-4
    4: 226,  # World 2-1
}


def _parse_position(line: str) -> list[float]:
    return list(map(float, line.split(",")))


def _convert_joystick(angle: float) -> Command:
    if angle < 90:
        return "0,0"

    if 90 <= angle < 180:
        return "0,1"

    if 180 <= angle < 270:
        return "1,0"

    return "1,1"


def smbc(world: int) -> models.Blackbox[list[float], list[str]]:
    @models.blackbox(step_size=1.0)
    def model(sample: models.Blackbox.Inputs) -> staliro.Result[models.Trace[list[float]], list[str]]:
        with tempfile.NamedTemporaryFile("w", suffix=".seed", delete=False) as input_file:
            commands = [_convert_joystick(state["joystick"]) for state in sample.times.values()]
            lines = "\n".join(commands) + "\n"
            input_file.write(lines)
            input_file.seek(0)

            cwd = pathlib.Path("utils")
            proc = subprocess.run(
                args=f"./smbc {world} trace",
                stdin=input_file,
                stdout=subprocess.PIPE,
                encoding="utf-8",
                shell=True,
                cwd=cwd.resolve(),
            )

            if proc.returncode != 0:
                raise RuntimeError()

            positions = [
                _parse_position(line) for line in proc.stdout.splitlines() if "," in line
            ]

        return staliro.Result(models.Trace(times=list(sample.times), states=positions), commands)

    return model


def _print_min(runs: list[staliro.Run]):
    evals = itertools.chain.from_iterable(run.evaluations for run in runs)
    eval = min(evals, key=lambda e: e.cost)
    pprint.pprint(eval.extra.trace.elements)


def _save_results(runs: list[staliro.Run], path: pathlib.Path):
    if path.suffix != ".pickle":
        path = path.with_suffix(f"{path.suffix}.pickle")

    with path.open("wb") as file:
        pickle.dump(runs, file)


@click.command()
@click.option("-c", "--control-points", type=int, default=100)
@click.option("-f", "--frames", type=int, default=1000)
@click.option("-b", "--budget", type=int, default=400)
@click.option("-o", "--output", default=None, type=click.Path(dir_okay=False, writable=True, path_type=pathlib.Path))
@click.option("-w", "--world", default=0, type=click.IntRange(min=0, max=36))
def main(control_points: int, frames: int, budget: int, output: pathlib.Path | None, world: int):
    goal = WIN_POSITIONS[world]
    req = rtamt.parse_dense(f"always (x < {goal})", {"x": 0, "y": 1})
    opts = staliro.TestOptions(
        tspan=(0, frames),
        iterations=budget,
        signals={
            "joystick": staliro.SignalInput(control_points=[(0, 360)]*control_points),
        }
    )
    opt = optimizers.DualAnnealing()
    runs = staliro.test(smbc(world), req, opt, opts)

    if output:
        _save_results(runs, output)
    else:
        _print_min(runs)


if __name__ == "__main__":
    main()
