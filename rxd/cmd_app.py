import click
from .app_manager import Manager, Application


@click.group(name='app')
def app_cmd_group():
    """Manage applications on serving computers"""
    pass


@app_cmd_group.command()
@click.argument('name')
@click.argument('repo')
@click.option('-d', '--dname',
              required=False, type=str,
              help="Use a different folder than the default .deploy")
def add(name, repo, dname=None):
    """
    Add app to with <name> and <repo> to rxd
    """
    print(f"adding {name} {repo} deploy_name={dname}")
    app = Application(name, repo, deploy_name=dname)
    if app.exists():
        print(f"Application with name '{app.name}' already exists")
    else:
        app.save()


@app_cmd_group.command()
@click.argument('name')
def fetch(name):
    """
    Pull latest commit from app's repository
    """
    app = Application.load(name)
    if not app.exists():
        print(f"Application with name '{app.name}' does not exists")
    else:
        app.fetch()


@app_cmd_group.command()
@click.argument('name')
def build(name):
    """
    Build app by cd-ing into app workspace and running .deploy/build
    """
    app = Application.load(name)
    if not app.exists():
        print(f"Application with name '{app.name}' does not exists")
    else:
        app.build()


@app_cmd_group.command()
@click.argument('name')
def install(name):
    """
    Install a systemd service file to call .deploy/run upon system
    startup
    """
    app = Application.load(name)
    if not app.exists():
        print(f"Application with name '{app.name}' does not exists")
    else:
        app.daemonize()


@app_cmd_group.command()
@click.argument('name')
def run(name):
    """
    CD into app workspace and run it using .deploy/run
    """
    app = Application.load(name)
    if not app.exists():
        print(f"Application with name '{app.name}' does not exists")
    else:
        app.run()


@app_cmd_group.command()
def list():
    """
    List all apps currently installed
    """
    from tabulate import tabulate
    am = Manager()
    table = []
    for app in am.list():
        status = app.status()
        # currently installed in systemd
        if status:
            table.append([app.name,
                          app.repo,
                          app.deploy_name,
                          status['is_running'],
                          status['state'],
                          status['pid'],
                          status['memory_mb']
                          ])
        else:
            table.append([app.name,
                          app.repo,
                          app.deploy_name,
                          None,
                          None,
                          None,
                          None])
    print(tabulate(table, headers=['Name',
                                   'Repo',
                                   'Deploy Target',
                                   'Running',
                                   'State',
                                   'PID',
                                   'Mem MB'],
                   tablefmt='mixed_outline'))


@app_cmd_group.command()
@click.argument('name')
def status(name):
    """
    Get App's daemon status
    """
    app = Application.load(name)
    if not app.exists():
        print(f"Application with name '{app.name}' does not exists")
        return
    app.status(output=True)


@app_cmd_group.command()
@click.argument('name')
def stop(name):
    """
    Stop App's daemon
    """
    app = Application.load(name)
    if not app.exists():
        print(f"Application with name '{app.name}' does not exists")
        return

    app.stop()


@app_cmd_group.command()
@click.argument('name')
def start(name):
    """
    Start App's daemon
    """
    app = Application.load(name)
    if not app.exists():
        print(f"Application with name '{app.name}' does not exists")
        return

    app.start()


@app_cmd_group.command()
@click.argument('name')
def remove(name):
    """
    Start App's daemon
    """
    app = Application.load(name)
    if not app.exists():
        print(f"Application with name '{app.name}' does not exists")
        return

    app.remove()


@app_cmd_group.command()
@click.argument('name')
def enable(name):
    """
    Enable App's daemon
    """
    app = Application.load(name)
    if not app.exists():
        print(f"Application with name '{app.name}' does not exists")
        return

    app.enable()


@app_cmd_group.command()
@click.argument('name')
def disable(name):
    """
    Disable App's daemon
    """
    app = Application.load(name)
    if not app.exists():
        print(f"Application with name '{app.name}' does not exists")
        return
    app.disable()


@app_cmd_group.command()
@click.argument('name')
def restart(name):
    """
    Restart App's daemon
    """
    app = Application.load(name)
    if not app.exists():
        print(f"Application with name '{app.name}' does not exists")
        return
    app.restart()


@app_cmd_group.command()
@click.argument('name')
@click.option('-f', '--follow',
              is_flag=True,
              show_default=True,
              default=False)
def logs(name, follow=False):
    """
    Get App's daemon's log
    """
    app = Application.load(name)
    if not app.exists():
        print(f"Application with name '{app.name}' does not exists")
        return

    app.logs(follow)


if __name__ == '__main__':
    app_cmd_group()
