import os
import subprocess as sp
import json
import typing as t
from pathlib import Path
from .daemonizers import Systemd


HOME = Path('~/.rxd').expanduser().resolve()
CONFIG_PATH = HOME.joinpath("config.json")
APP_DIR = Path(HOME, "apps")


# Set workspace directory
WORKSPACE_DIR = Path('~/workspace').expanduser().resolve()
if CONFIG_PATH.exists():
    with open(CONFIG_PATH) as fh:
        config = json.load(fh)
        WORKSPACE_DIR = Path(config["workspace"]).expanduser().resolve()


class Chdir:

    def __init__(self, directory):
        self.directory = directory
        self.oldcwd = None

    def __enter__(self):
        print("changing directory to %s" % self.directory)
        self.oldcwd = Path(os.curdir).resolve()
        os.chdir(self.directory)

    def __exit__(self, type, value, traceback):

        if self.oldcwd is not None:
            print("changing directory back to %s" % self.oldcwd)
            os.chdir(self.oldcwd)
            self.oldcwd = None


class Manager:
    def __init__(self):
        pass

    def list(self):
        return [Application.load(app_file.split(".json")[0])
                for app_file in os.listdir(APP_DIR)]

    def add(self, name, repo):
        app = Application(name, repo)
        app.save()

    def remove(self, name):
        return Application.load(name).remove()

    def fetch(self, name):
        app = Application.load(name)
        app.fetch()


class Application:
    def __init__(self, name, repo=None, deploy_name=None) -> None:
        self.name = name
        self.repo = repo
        self.deploy_name = ".deploy" if not deploy_name else deploy_name

    @property
    def repo_name(self) -> t.Union[str, None]:
        if self.repo:
            return str(Path(self.repo).stem)
        return None

    @property
    def repo_path(self) -> t.Union[Path, None]:
        if self.repo and self.repo_name:
            return self.workspace_container_path\
                       .joinpath(self.repo_name)\
                       .resolve()
        return None

    @property
    def metadata_path(self) -> Path:
        return Path(HOME, "apps", "%s.json" % self.name).resolve()

    @property
    def workspace_container_path(self) -> Path:
        return Path(WORKSPACE_DIR, self.name).resolve()

    @property
    def systemd_services_definition_path(self) -> Path:
        return self.workspace_container_path.joinpath("app.service").resolve()

    @property
    def systemd_service_name(self):
        return f"rxd-app-{self.name}.service"

    def save(self):
        self.setup_metadata()
        path = self.metadata_path
        with open(path, "w") as fh:
            json.dump({
                "name": self.name,
                "repo": self.repo,
                "deploy_name": self.deploy_name
            }, fh)

    def setup_metadata(self):
        if not self.metadata_path.parent.exists():
            os.makedirs(self.metadata_path.parent)

    def setup_workspace(self):
        if not self.workspace_container_path.exists():
            os.makedirs(self.workspace_container_path)

    def exists(self):
        return self.metadata_path.exists()

    @classmethod
    def load(cls, name):
        metadata_path = Path(HOME,
                             "apps",
                             "%s.json" % name).resolve()

        if metadata_path.exists():
            with open(metadata_path, "r") as fh:
                data = json.load(fh)
                return Application(name=data['name'],
                                   repo=data['repo'],
                                   deploy_name=data.get('deploy_name'))
        else:
            return Application(name=name)

    def fetch(self):
        self.setup_workspace()

        # if no repo
        if self.workspace_container_path.exists() \
                and self.repo_path \
                and not self.repo_path.exists():
            with Chdir(self.workspace_container_path):
                sp.check_call("git clone --depth 1 %s" % self.repo,
                              shell=True)

        # if repo exists
        elif self.workspace_container_path.exists()\
                and self.repo_path \
                and self.repo_path.exists():
            with Chdir(self.repo_path):
                sp.check_call("git pull origin main",
                              shell=True)

    def remove(self):
        if workspace_path := self.workspace_container_path:
            answer = input("Are you sure you want to remove '%s' [y/n] ?: "
                           % workspace_path)
            if answer.strip().lower() == 'y':
                Systemd.remove(self)

                # remove app's workspace folder
                if workspace_path.exists():
                    print("Removing %s" % workspace_path)
                    import shutil
                    shutil.rmtree(workspace_path)

                # remove app's metadata file
                if metadata_path := self.metadata_path:
                    if self.metadata_path.exists():
                        print("Removing %s" % metadata_path)
                        metadata_path.unlink()

    def build(self):
        if repo_path := self.repo_path:
            if not repo_path.exists():
                print(f"{repo_path} does not exist, please run "
                      f"'rxd app fetch {self.name}'")
                return
            with Chdir(repo_path):
                sp.check_call(["/usr/bin/bash", f"{self.deploy_name}/build"],
                              shell=True)

    def run(self):
        if repo_path := self.repo_path:
            if not repo_path.exists():
                print(f"{repo_path} does not exist, please run "
                      f"'rxd app fetch {self.name}'")
                return
            with Chdir(repo_path):
                sp.check_call(["/usr/bin/bash", f"{self.deploy_name}/run"],
                              shell=True)

    def daemonize(self):
        Systemd.daemonize(self)

    def status(self, output=False):
        return Systemd.status(self, output=output)

    def start(self):
        Systemd.start(self)

    def stop(self):
        Systemd.stop(self)

    def restart(self):
        Systemd.restart(self)

    def enable(self):
        Systemd.enable(self)

    def disable(self):
        Systemd.disable(self)

    def logs(self, follow=False):
        Systemd.logs(self, follow=follow)

    def __repr__(self):
        return "Application(name=%s, repo=%s)" % (self.name, self.repo)
