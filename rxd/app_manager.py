import sys
import os
import subprocess as sp
import json
import typing as t
import textwrap
import getpass
from pathlib import Path

HOME = '~/.rxd'
HOME = Path(HOME).expanduser().resolve()
APP_DIR = Path(HOME, "apps")
WORKSPACE_DIR = Path('~/workspace').expanduser().resolve()


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


class AppManager:
    def __init__(self):
        pass

    def list(self):
        return [Application.load(app_file.split(".json")[0])
                for app_file in os.listdir(APP_DIR)]

    def add(self, name, repo):
        app = Application(name, repo)
        app.save()

    def delete(self, name):
        return Application.load(name).delete()

    def fetch(self, name):
        app = Application.load(name)
        app.fetch()


class Application:
    def __init__(self, name,
                 repo=None) -> None:
        self.name = name
        self.repo = repo

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
                "repo": self.repo
            }, fh)

    def delete(self):
        os.remove(self.metadata_path)

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
                                   repo=data['repo'])
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

    def build(self):
        if repo_path := self.repo_path:
            with Chdir(repo_path):
                sp.check_call("/usr/bin/bash .deploy/build", shell=True)

    def run(self):
        if repo_path := self.repo_path:
            with Chdir(repo_path):
                sp.check_call("/usr/bin/bash .deploy/run", shell=True)

    def daemonize(self):
        screen_name = self.name
        python_path = sys.executable
        user = getpass.getuser()
        systemd_service_file = \
            f"""
            [Unit]
            Description=rxd
            After=network.target
            StartLimitIntervalSec=30
            StartLimitBurst=5

            [Service]
            Type=simple
            User={user}
            ExecStart={python_path} -m rxd.cmd app run {self.name}
            Restart=always
            RestartSec=5

            [Install]
            WantedBy=default.target
            """
        systemd_service_file = textwrap.dedent(systemd_service_file)
        systemd_service_install_path = Path(
            f'/etc/systemd/system/{self.systemd_service_name}')
        print(f'Writing {self.systemd_services_definition_path}')
        with open(self.systemd_services_definition_path, "w") as fh:
            fh.write(systemd_service_file)

        if Path('/etc/systemd/system').exists():
            if not systemd_service_install_path.exists():

                print("Moving %s -> %s" %
                      (self.systemd_services_definition_path,
                       systemd_service_install_path))
                print("We need sudo permissions to do so")
                sp.check_call(
                    ["sudo", "mv",
                     self.systemd_services_definition_path,
                     systemd_service_install_path])
                sp.check_call(["sudo", "systemctl",
                               "daemon-reload"])
        else:
            print("Systemd does not exist")

    def status(self, output=False):
        if not Path('/etc/systemd/system').exists():
            return None

        lines = sp.check_output(["systemctl",
                                 "show",
                                 "--no-pager",
                                 self.systemd_service_name])
        lines = lines.decode("utf-8").split("\n")
        status_data = {}
        for line in lines:
            kv = line.strip().split("=", 1)
            if len(kv) == 2:
                key, value = kv
                status_data[key] = value

        status = dict(
            is_running=status_data.get('ActiveState') == 'active',
            pid=status_data.get('MainPID'),
            user=status_data.get('User'),
            memory_mb=status_data.get('MemoryCurrent'),
            state=status_data.get('UnitFileState')
        )
        if output:
            print(json.dumps(status, indent=4))
        return status

    def start(self):
        sp.check_call(["sudo",
                       "systemctl",
                       "start",
                       self.systemd_service_name])

    def stop(self):
        sp.check_call(["sudo",
                       "systemctl",
                       "stop",
                       self.systemd_service_name])

    def restart(self):
        sp.check_call(["sudo",
                       "systemctl",
                       "restart",
                       self.systemd_service_name])
        pass

    def enable(self):
        sp.check_call(["sudo",
                       "systemctl",
                       "enable",
                       self.systemd_service_name])

    def disable(self):
        sp.check_call(["sudo",
                       "systemctl",
                       "disable",
                       self.systemd_service_name])

    def log(self, follow=False):
        if follow:
            sp.check_call(["journalctl",
                           "-f",
                           "-u",
                           self.systemd_service_name])
        else:
            sp.check_call(["journalctl",
                           "-u",
                           self.systemd_service_name])

    def __repr__(self):
        return "Application(name=%s, repo=%s)" % (self.name, self.repo)
