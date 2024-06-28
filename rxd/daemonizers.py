import json
import sys
import getpass
import textwrap
import subprocess as sp
from pathlib import Path


def run(cmdline: list, ignore_errors=False):
    try:
        print("Running %s" % " ".join(cmdline))
        sp.check_call(cmdline)
    except sp.CalledProcessError:
        if not ignore_errors:
            raise


class Systemd:
    def __init__(self):
        pass

    @classmethod
    def is_available(cls):
        return Path('/etc/systemd/system').exists()

    @classmethod
    def install(cls, app):
        pass

    @classmethod
    def remove(cls, app):
        service_name = app.systemd_service_name
        install_path = Path(f'/etc/systemd/system/{service_name}')
        cls.stop(app)
        cls.disable(app)
        if install_path.exists():
            print("Removing %s" % install_path)
            run(["sudo", "rm", str(install_path)])

    @classmethod
    def start(cls, app):
        run(["sudo", "systemctl", "start",
             app.systemd_service_name],
            ignore_errors=True)

    @classmethod
    def stop(cls, app):
        run(["sudo", "systemctl", "stop",
             app.systemd_service_name],
            ignore_errors=True)

    @classmethod
    def restart(cls, app):
        run(["sudo", "systemctl", "restart",
            app.systemd_service_name], ignore_errors=True)
        pass

    @classmethod
    def enable(cls, app):
        run(["sudo", "systemctl", "enable",
            app.systemd_service_name], ignore_errors=True)

    @classmethod
    def disable(cls, app):
        run(["sudo", "systemctl", "disable",
            app.systemd_service_name], ignore_errors=True)

    @classmethod
    def logs(cls, app, follow):
        if follow:
            run(["journalctl", "-f", "-u", app.systemd_service_name],
                ignore_errors=True)
        else:
            run(["journalctl", "-e", "-u", app.systemd_service_name],
                ignore_errors=True)

    @classmethod
    def daemonize(cls, app):
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
            ExecStart={python_path} -m rxd.cmd app run {app.name}
            Restart=always
            RestartSec=5

            [Install]
            WantedBy=default.target
            """
        systemd_service_file = textwrap.dedent(systemd_service_file)
        systemd_service_install_path = Path(
            f'/etc/systemd/system/{app.systemd_service_name}')
        print(f'Writing {app.systemd_services_definition_path}')
        with open(app.systemd_services_definition_path, "w") as fh:
            fh.write(systemd_service_file)

        if Path('/etc/systemd/system').exists():
            if not systemd_service_install_path.exists():
                print("Moving %s -> %s" %
                      (app.systemd_services_definition_path,
                       systemd_service_install_path))
                print("We need sudo permissions to do so")
                sp.check_call(
                    ["sudo", "mv",
                     app.systemd_services_definition_path,
                     systemd_service_install_path])
                sp.check_call(["sudo", "systemctl",
                               "daemon-reload"])
        else:
            print("Systemd does not exist")

    @classmethod
    def status(cls, app, output):
        if not Path('/etc/systemd/system').exists():
            return None

        lines = sp.check_output(["systemctl",
                                 "show",
                                 "--no-pager",
                                 app.systemd_service_name])
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
