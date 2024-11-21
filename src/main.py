import pathlib
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


@models.blackbox(step_size=1.0)
def smbc(sample: models.Blackbox.Inputs) -> models.Trace[list[float]]:
    with tempfile.TemporaryFile("w") as input_file:
        input_file.writelines(
            _convert_joystick(state["joystick"]) for state in sample.times.values()
        )

        cwd = pathlib.Path("utils")
        proc = subprocess.run(
            args="./smbc 0 trace",
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

    return models.Trace(times=list(sample.times), states=positions)


@click.command()
@click.option("-f", "--frames", type=int, default=100)
@click.option("-b", "--budget", type=int, default=400)
def main(frames: int, budget: int):
    req = rtamt.parse_dense("always (x < 100)", {"x": 0, "y": 1})
    opts = staliro.TestOptions(
        tspan=(0, frames),
        iterations=budget,
        signals={"joystick": staliro.SignalInput(control_points=[(0, 360)]*frames)}
    )
    opt = optimizers.UniformRandom()
    runs = staliro.test(smbc, req, opt, opts)
    run = runs[0]
    eval = min(run.evaluations, key=lambda e: e.cost)

    pprint.pprint(eval.extra.trace.elements)


if __name__ == "__main__":
    main()
