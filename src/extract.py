import pathlib
import pickle

import click


@click.command()
@click.option("-i", "--inputs-dir", type=click.Path(exists=False, file_okay=False, writable=True, path_type=pathlib.Path), default=pathlib.Path("inputs"))
@click.option("-o", "--outputs-dir", type=click.Path(exists=False, file_okay=False, writable=True, path_type=pathlib.Path), default=pathlib.Path("outputs"))
@click.argument("runs_file", type=click.Path(exists=True, dir_okay=False, path_type=pathlib.Path))
def extract(inputs_dir: pathlib.Path, outputs_dir: pathlib.Path, runs_path: pathlib.Path):
    if not inputs_dir.exists():
        inputs_dir.mkdir()

    if not outputs_dir.exists():
        outputs_dir.mkdir()

    with runs_path.open("rb") as runs_file:
        runs = pickle.load(runs_file)

    for run in runs:
        for n, evaluation in enumerate(run.evaluations):
            input_path = inputs_dir / f"{n}.test"
            output_path = outputs_dir / f"{n}.trace"
            output_trace = [
                f"{pose[0]},{pose[1]}"
                for pose in evaluation.extra.trace.elements.values()
            ]

            with input_path.open("wt") as input_file:
                input_file.write(f"{evaluation.extra.model}\n")

            with output_path.open("wt") as output_file:
                output_file.write("\n".join(output_trace))


if __name__ == "__main__":
    extract()
