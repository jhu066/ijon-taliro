from __future__ import annotations

import itertools
import json
import logging
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


class Line(typing.TypedDict):
    x: float
    y: float
    dead: bool
    start: bool


def _parse_line(line: str) -> Line:
    data = json.loads(line)

    return Line(
        x=float(data["x"]),
        y=float(data["y"]),
        dead=data["dead"] == 1,
        start=data["start"] == 1,
    )


def _convert_joystick(angle: float) -> Command:
    if angle < 90:
        return "0,0"

    if 90 <= angle < 180:
        return "0,1"

    if 180 <= angle < 270:
        return "1,0"

    return "1,1"


def smbc(bin_path: pathlib.Path, world: int) -> models.Blackbox[Line, list[str]]:
    @models.blackbox(step_size=1.0)
    def model(sample: models.Blackbox.Inputs) -> staliro.Result[models.Trace[Line], list[str]]:
        commands = [_convert_joystick(state["joystick"]) for state in sample.times.values()]
        lines = "\n".join(commands) + "\n"

        with tempfile.NamedTemporaryFile("w", suffix=".seed") as input_file:
            input_file.write(lines)
            input_file.seek(0)

            cwd = pathlib.Path("data")
            proc = subprocess.run(
                args=f"{bin_path} {world} trace",
                stdin=input_file,
                stdout=subprocess.PIPE,
                encoding="utf-8",
                shell=True,
                cwd=cwd.resolve(),
            )

            if proc.returncode != 0:
                raise RuntimeError()

            output = list(proc.stdout.splitlines())
            positions = [
                _parse_line(line) for line in output if line.startswith("{")
            ]

        return staliro.Result(models.Trace(times=list(sample.times), states=positions), commands)

    return model


def req(goal: int) -> staliro.Specification[Line, float, None]:
    inner = rtamt.parse_dense(f"always (x < {goal})", {"x": 0, "y": 1})

    @staliro.specification()
    def spec(trace: staliro.Trace[Line]) -> staliro.Result[float, None]:
        transformed = staliro.Trace(
            times=list(trace.times),
            states=[[line["x"], line["y"]] for line in trace.states]
        )

        return inner.evaluate(transformed)

    return spec


def _print_min(runs: list[staliro.Run]):
    evals = itertools.chain.from_iterable(run.evaluations for run in runs)
    eval = min(evals, key=lambda e: e.cost)
    pprint.pprint(eval.extra.trace.elements)


def _save_results(runs: list[staliro.Run], path: pathlib.Path):
    if path.suffix != ".pickle":
        path = path.with_suffix(f"{path.suffix}.pickle")

    with path.open("wb") as file:
        pickle.dump(runs, file)


def _ensure_binary(dir_path: str | pathlib.Path) -> pathlib.Path:
    logger = logging.getLogger("test.binary")
    logger.addHandler(logging.NullHandler())

    if not isinstance(dir_path, pathlib.Path):
        dir_path = pathlib.Path(dir_path)

    if dir_path.exists() and not dir_path.is_dir():
        raise RuntimeError(f"path {dir_path} already exists and is not a directory")

    src_path = pathlib.Path("ijon-data/SuperMarioBros-C").resolve()
    dir_path = dir_path.resolve()
    bin_path = dir_path / "smbc"

    if bin_path.exists() and not bin_path.is_file():
        raise RuntimeError(f"path {bin_path} already exists and is not a file")

    logger.debug("Configuring SBMC build")
    res = subprocess.run(
        args=f"cmake -S {src_path} -B {dir_path} -Wno-dev",
        stdout=subprocess.PIPE,
        encoding="utf-8",
        shell=True,
    )

    for line in res.stdout.splitlines():
        logger.debug("\x1b[33;20m" + line + "\x1b[0m")

    logger.debug("Building SMBC binary")
    res = subprocess.run(
        args=f"cmake --build {dir_path}",
        stdout=subprocess.PIPE,
        encoding="utf-8",
        shell=True,
    )

    for line in res.stdout.splitlines():
        logger.debug("\x1b[33;20m" + line + "\x1b[0m")
    
    return bin_path


@click.command()
@click.option("-c", "--control-points", type=int, default=100)
@click.option("-f", "--frames", type=int, default=1000)
@click.option("-b", "--budget", type=int, default=400)
@click.option("-o", "--output", default=None, type=click.Path(dir_okay=False, writable=True, path_type=pathlib.Path))
@click.option("-w", "--world", default=0, type=click.IntRange(min=0, max=36))
@click.option("-v", "--verbose", is_flag=True)
def main(
    control_points: int,
    frames: int,
    budget: int,
    output: pathlib.Path | None,
    world: int,
    verbose: bool,
):
    if verbose:
        logging.basicConfig(level=logging.DEBUG)
        logging.getLogger("staliro").setLevel(logging.ERROR)

    bin_path = _ensure_binary("build")
    opts = staliro.TestOptions(
        tspan=(0, frames),
        iterations=budget,
        signals={
            "joystick": staliro.SignalInput(control_points=[(0, 360)]*control_points),
        }
    )
    opt = optimizers.DualAnnealing()
    runs = staliro.test(smbc(bin_path, world), req(WIN_POSITIONS[world]), opt, opts)

    if output:
        _save_results(runs, output)
    else:
        _print_min(runs)


if __name__ == "__main__":
    main()
