import click
import json
from flask import Flask, request
from pprint import pprint

app = Flask(__name__)


@app.route('/', methods=['GET'])
def index():
    return "+OK"


@app.route('/receive_github_webhook', methods=['POST'])
def github_webhook_endpoint():
    print("github webhook recieved")
    pprint(request.json)
    return json.dumps(request.json)


@app.route('/receive_rxd', methods=['POST'])
def rxd_webhook_endpoint():
    from .messages import RXDRepoUpdatedEvent
    from .codex import Cipher
    cipher = Cipher(key="")
    print("rxd webhook recieved")
    pprint(request.json)
    data = request.json
    if data is None:
        return "+FAIL"

    message_enc = data['payload']
    message = cipher.decrypt(message_enc)
    event = RXDRepoUpdatedEvent.model_validate_json(message)

    print(event)

    return "+OK"

# ----------------
# Argument parsing
# ----------------


@click.group(name='responder')
def responder_cmd_group():
    """Web server to monitor for events"""
    pass


@responder_cmd_group.command()
def run():
    app.run(host='0.0.0.0', port=30475)


if __name__ == '__main__':
    responder_cmd_group()
