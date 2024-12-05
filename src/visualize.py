import itertools
import pathlib
import pickle
import subprocess
import tempfile
import typing

import click
import staliro
import staliro.tests as tests

import main

Runs: typing.TypeAlias = typing.List[
    staliro.Run[typing.Any, float, tests.ModelSpecExtra[main.Line, typing.List[str], None]]
]


def _create_svg_path(name: str, trace: staliro.Trace[main.Line]):
    color = "#f8bf00"
    alpha = "0.2"
    data = [
        (state["x"], state["y"])
        for state in trace.states if state["x"] != 0 and state["y"] != 0
    ]
    path_data = " ".join(f"L{x + 8} {y + 16}" for x, y in data)
    path_element = (
        f'<path fill="none" stroke="{color}" stroke-opacity="{alpha}" '
        f'stroke-width="3" d="M40 176{path_data}">'
        f'<title>{name}</title></path>'
    )

    return path_element


def _load_runs(file: pathlib.Path) -> Runs:
    if file.suffix != ".pickle":
        file = file.with_suffix(f"{file.suffix}.pickle")

    if not file.exists():
        raise ValueError(f"File {file} does not exist")

    with file.open("rb") as pickle_file:
        runs = pickle.load(pickle_file)

    if not isinstance(runs, list):
        raise TypeError()

    if not all(isinstance(run, staliro.Run) for run in runs):
        raise TypeError()

    return runs


@click.group("visualize")
def visualize():
    pass


@visualize.command("traces")
@click.argument("FILE", type=click.Path(dir_okay=False, path_type=pathlib.Path))
def traces(file: pathlib.Path):
    runs = _load_runs(file)
    paths_list = [
        _create_svg_path(f"{n}.trace", e.extra.trace)
        for n, e in enumerate(itertools.chain.from_iterable(run.evaluations for run in runs))
    ]

    svg_path = pathlib.Path("data/mario-1-1.svg")

    # Read the SVG file
    with svg_path.open("r") as svg_file:
        svg = svg_file.read()

    # replace placeholder in SVG and write to file
    content = svg.replace("{{PATHS}}", "\n".join(paths_list))

    with open("mario-1-1.svg", "w") as output_file:
        output_file.write(content)


@visualize.command("play")
@click.argument("FILE", type=click.Path(dir_okay=False, path_type=pathlib.Path))
def play(file: pathlib.Path):
    runs = _load_runs(file)
    evals = [e for r in runs for e in r.evaluations]
    eval = min(evals, key=lambda e: e.cost)
    smbc = main._ensure_binary("build")
    data_dir = pathlib.Path("data")

    with tempfile.TemporaryFile("w") as input:
        input.write("\n".join(eval.extra.model) + "\n")
        input.seek(0)
        subprocess.run(args=f"{smbc} 0 video", stdin=input, cwd=data_dir, shell=True)


if __name__ == "__main__":
    visualize()
