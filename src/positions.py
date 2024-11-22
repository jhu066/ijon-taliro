import pathlib

import click


@click.command()
@click.option("-p", "--path", type=click.Path(exists=True, file_okay=False))
def positions(path: pathlib.Path):
    build_dir = path / "build"

    if not build_dir.exists():
        raise RuntimeError()

    smbc = build_dir / "smbc"

    if not smbc.exists():
        raise RuntimeError()




if __name__ == "__main__":
    positions()
