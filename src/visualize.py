import itertools
import pathlib
import pickle
import subprocess
import tempfile

import click
import staliro

import main


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


@click.group("visualize")
def visualize():
    pass


@visualize.command("traces")
@click.argument("FILE", type=click.Path(exists=True, dir_okay=False, path_type=pathlib.Path))
def traces(file: pathlib.Path):
    with file.open("rb") as pickle_file:
        runs = pickle.load(pickle_file)

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
@click.argument("FILE", type=click.Path(exists=True, dir_okay=False, path_type=pathlib.Path))
def play(file: pathlib.Path):
    with file.open("rb") as data:
        runs = pickle.load(data)

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
