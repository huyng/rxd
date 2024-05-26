import click
from .app_manager import AppManager, Application

@click.group(name='app')
def app_cmd_group():
    """Manage applications on serving computers"""
    pass


@app_cmd_group.command()
@click.argument('name')
@click.argument('repo')
def add(name, repo):
    print(f"adding {name} {repo}")
    app = Application(name, repo)
    if app.exists():
        print(f"Application with name '{app.name}' already exists")
    else:
        app.save()


@app_cmd_group.command()
@click.argument('name')
@click.argument('repo')
def add(name, repo):
    print(f"adding {name} {repo}")
    app = Application(name, repo)
    if app.exists():
        print(f"Application with name '{app.name}' already exists")
    else:
        app.save()

@app_cmd_group.command()
@click.argument('name')
def fetch(name):
    app = Application.load(name)
    if not app.exists():
        print(f"Application with name '{app.name}' does not exists")
    else:
        app.fetch()



@app_cmd_group.command()
@click.argument('name')
def build(name):
    app = Application.load(name)
    if not app.exists():
        print(f"Application with name '{app.name}' does not exists")
    else:
        app.build()

@app_cmd_group.command()
@click.argument('name')
def daemonize(name):
    app = Application.load(name)
    if not app.exists():
        print(f"Application with name '{app.name}' does not exists")
    else:
        app.daemonize()


@app_cmd_group.command()
@click.argument('name')
def run(name):
    app = Application.load(name)
    if not app.exists():
        print(f"Application with name '{app.name}' does not exists")
    else:
        app.run()


@app_cmd_group.command()
def list():
    am = AppManager()
    for app in am.list():
        print(f"{app.name} {app.repo}")



if __name__ == '__main__':
    app_cmd_group()
