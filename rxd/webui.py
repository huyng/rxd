#!/usr/bin/env python
import logging
import time
import sys
import os.path as pth
import os
import json
import shutil
import multiprocessing as mp
import threading
import toml

from argparse import ArgumentParser
from flask import cli
from flask import Flask
from flask import make_response
from flask import request
from flask import render_template
from flask import send_file
from flask import send_from_directory
from gunicorn.app.base import BaseApplication
from pprint import pprint

frontend_path = pth.join(
    pth.split(
        pth.split(
            pth.abspath(__file__))[0])[0], "frontend")

app = Flask(__name__)
# static_folder=pth.join(frontend_path, "dist"),
# static_url_path="")


basedir = os.path.abspath(os.curdir)


def print_banner(args):
    print("")
    print("\x1b[32m================\x1b[0m")
    print("\x1b[32m-    rxd       -\x1b[0m")
    print("\x1b[32m================\x1b[0m")
    print("")
    print(f"\x1b[32mStarting server at http://{args.host}:{args.port}\x1b[0m")
    print("")


@app.route("/")
def index_page():
    return "Hello World"

@app.post("/ping")
def webhook():
    content = request.json
    return json.dumps(content)


# Supervisor App
class Manager(threading.Thread):
    def __init__(self, config):
        self.config = config
        threading.Thread.__init__(self)

    def run(self):

        pprint(self.config)

        while True:
            time.sleep(5)
            t = time.time()
            print(f"In thread t={t}")


# Gunicorn app
class Application(BaseApplication):

    def __init__(self, app, options=None):
        self.options = options or {}
        self.application = app
        super().__init__()

    def load_config(self):
        config = {}
        for key, value in self.options.items():
            if key in self.cfg.settings:
                if value is not None:
                    config[key] = value

        for key, value in config.items():
            self.cfg.set(key.lower(), value)

    def load(self):
        return self.application


def main():
    p = ArgumentParser()
    p.add_argument("-H", "--host", default="localhost",
                   help="Host address to bind server to (default: 127.0.0.1)")
    p.add_argument("-p", "--port", default=5000,
                   help="Host port to bind server to (default: 9999)")
    p.add_argument("-c", "--config")

    cmdln_args = p.parse_args()

    # parse config
    with open(cmdln_args.config) as fh:
        manager_config = toml.loads(fh.read())

    # start suepervisor
    manager_thread = Manager(manager_config)
    manager_thread.daemon = True
    manager_thread.start()

    # start webserver
    print_banner(cmdln_args)
    options = {
        'bind': '%s:%s' % (cmdln_args.host, cmdln_args.port),
        'workers': 1,
        'timeout': 120,
    }
    Application(app, options).run()


if __name__ == '__main__':
    main()
