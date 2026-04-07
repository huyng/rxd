# rxd

A CLI tool for managing application deployments on Linux servers using systemd.

## Overview

`rxd` manages the lifecycle of server applications — fetching code from Git repositories, building, running, and operating them as systemd services.

Each app needs a `.deploy` directory in its repo with two bash scripts:
- `.deploy/build` — installs dependencies, compiles, etc.
- `.deploy/run` — starts the application

## Installation

```bash
pip install rxd
```

## Quick Start

```bash
# Initialize rxd (one-time)
rxd setup --workspace ~/workspace

# Register an app
rxd app add myapp https://github.com/user/myapp.git

# Fetch code, build, and install as a service
rxd app fetch myapp
rxd app build myapp
rxd app install myapp

# Start the service
rxd app start myapp

# Monitor
rxd app list
rxd app logs myapp -f
```

## Commands

### Setup

```
rxd setup [--workspace PATH]    Initialize rxd config and workspace directory
rxd info                        Show current config
```

### App Management

```
rxd app add <name> <repo> [-d DEPLOY_NAME]   Register an app from a Git repo
rxd app fetch <name>                          Clone or pull latest code
rxd app build <name>                          Run .deploy/build script
rxd app run <name>                            Run .deploy/run interactively
rxd app remove <name>                         Remove app, workspace, and service
rxd app list                                  List all apps with status
```

### Service Management

```
rxd app install <name>      Create and install systemd service
rxd app start <name>        Start service
rxd app stop <name>         Stop service
rxd app restart <name>      Restart service
rxd app enable <name>       Enable auto-start on boot
rxd app disable <name>      Disable auto-start
rxd app status <name>       Show service status
rxd app logs <name> [-f]    View logs (use -f to follow)
```

## Deploy Scripts

Your repository needs a `.deploy` directory with executable bash scripts. Example:

**`.deploy/build`**
```bash
#!/usr/bin/env bash
set -e
test -d venv || python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**`.deploy/run`**
```bash
#!/usr/bin/env bash
source venv/bin/activate
gunicorn app:app
```

### Multiple Deploy Targets

You can have multiple deploy configurations in one repo (e.g., staging vs production) using the `-d` flag:

```bash
rxd app add myapp-staging https://github.com/user/myapp.git -d .deploy-staging
rxd app add myapp-prod    https://github.com/user/myapp.git -d .deploy-prod
```

## Configuration

rxd stores its config in `~/.rxd/`:

```
~/.rxd/
├── config.json          # Workspace path
└── apps/
    └── myapp.json       # Per-app metadata
```

**`~/.rxd/config.json`**
```json
{
  "workspace": "/home/user/workspace"
}
```

Apps are checked out to `{workspace}/{app_name}/{repo_name}/`.

## Requirements

- Python 3.8+
- Git
- systemd (for service management)
- sudo access (for systemd operations)
