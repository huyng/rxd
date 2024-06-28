import click
import os
import json
from pathlib import Path
from .cmd_app import app_cmd_group

HOME = Path('~/.rxd').expanduser().resolve()
CONFIG_PATH = HOME.joinpath("config.json")


@click.group(name="rxd")
def main():
    pass


@main.command()
@click.option("-w", "--workspace",
              required=False,
              type=str,
              default=Path('~/workspace').expanduser().resolve(),
              help="Path to directory where your apps will be stored")
def setup(workspace):

    # create home directory
    if not HOME.exists():
        print(f"Making directory: {HOME}")
        os.makedirs(HOME)

    # write config file to point to workspace
    if not CONFIG_PATH.exists():
        with open(CONFIG_PATH, "w") as fh:
            print(f"Saving config: {CONFIG_PATH}")
            json.dump({"workspace": workspace}, fh, indent=4)

    # create workspace
    workspace_path = Path(workspace)
    if not workspace_path.exists():
        print(f"Making directory: {workspace_path}")
        workspace_path.mkdir()


@main.command()
def info():
    print(f"Home: {HOME}")
    print(f"Config file: {CONFIG_PATH}")
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH) as fh:
            config = json.load(fh)
        workspace = Path(config['workspace'])\
            .expanduser()\
            .resolve()
        print(f"Workspace: {workspace}")


main.add_command(app_cmd_group)

if __name__ == "__main__":
    main()
