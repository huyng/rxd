import click
import os
from pathlib import Path
# from .cmd_responder import responder_cmd_group
from .cmd_app import app_cmd_group

HOME = Path('~/.rxd').expanduser().resolve()


@click.group(name="rxd")
def main():
    pass


@main.command()
@click.option("-u", "--url", required=True, type=str)
@click.option("-a", "--app", required=True, type=str)
def trigger(address: str, app: str):
    import requests
    from .codex import Cipher
    from .messages import RXDRepoUpdatedEvent
    cipher = Cipher(key="")
    message = RXDRepoUpdatedEvent(app_name=app).model_dump_json()
    message_encoded = cipher.encrypt(message).decode('utf-8')
    requests.post(address, json={'payload': message_encoded})


# @main.command()
# @click.option("-w", "--workspace",
#               required=False,
#               type=str,
#               default="workspace",
#               help="Path to workspace directory where your apps will be stored")
# def setup(workspace):

@main.command()
def setup():
    if not HOME.exists():
        print(f"Making {HOME}")
        os.makedirs(HOME)


main.add_command(app_cmd_group)
# main.add_command(responder_cmd_group)

if __name__ == "__main__":
    main()
