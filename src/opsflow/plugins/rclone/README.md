# RClone Plugin

An OpsFlow plugin for executing **RClone** tasks (`sync`, `copy`, `move`) in parallel.  
It integrates cloud storage operations seamlessly into OpsFlow workflows using declarative configuration.

> **Note**  
> This plugin builds on concepts defined in the OpsFlow **core framework** (plugin registration, workflow context, configuration loading).  
> These concepts are **not repeated here** and are assumed to be known.

## Features

-   **Multiple Actions**: `sync`, `copy`, and `move`
-   **Parallel Execution**: Concurrent task execution via `ThreadPoolExecutor`
-   **Configuration-Driven**: Configure via **Python** or **YAML**
-   **Dry-Run Support**: Automatically appends `--dry-run` when `context.dry_run=True`
-   **Structured Results**: Task results are aggregated in the workflow context
-   **Detailed Logging**: Full stdout/stderr capture per task

## Installation

The plugin is part of the OpsFlow ecosystem:

```bash
pip install opsflow[rclone]
``` 

### Requirements

-   Python 3.10+
-   OpsFlow core framework

**Note:**
The rclone binary is shipped with the plugin and does not need to be installed
or managed separately.

## Configuration

### Python Configuration

```python
from opsflow.plugins.rclone import (
    RClonePluginConfig,
    RCloneTask,
    RCloneAction,
    RCloneOptions,
)

config = RClonePluginConfig(
    name="RClone",
    max_workers=4,
    config_file="/path/to/.rclone.conf",
    tasks=[
        RCloneTask(
            name="sync_backup",
            description="Sync local folder to cloud storage",
            action=RCloneAction.SYNC,
            src="local_remote:source/path",
            dest="cloud_remote:dest/path",
            options=RCloneOptions(
                options={ "--exclude": "*.tmp", "--delete-excluded": True,
                }
            ),
        ),
        RCloneTask(
            name="copy_archive",
            action=RCloneAction.COPY,
            src="source_remote:files",
            dest="archive_remote:backup",
        ),
    ],
)
``` 

### YAML Configuration

```yaml
plugins:
    name: rclone
    max_workers: 4
    config_file: /path/to/.rclone.conf
    tasks:
      - name: sync_backup
        description: Sync local folder to cloud storage
        action: sync
        src: local_remote:source/path
        dest: cloud_remote:dest/path
        options:
          --exclude: "*.tmp"
          --delete-excluded: true

      - name: copy_archive
        action: copy
        src: source_remote:files
        dest: archive_remote:backup
```

## Configuration Reference

### RClonePluginConfig

| Field | Type | Description |
|--|--|--|
| `name` | `str` | Plugin name (default: `RClone`) |
| `max_workers` | `int` | Maximum number of parallel tasks (default: `4`) |
| `config_file` | `str | None` | Path to rclone config file |
| `tasks` | `list[RCloneTask]` | Tasks executed by the plugin |

### RCloneTask

| Field | Type | Description |
|--|--|--|
| `name` | `str` | Unique task identifier |
| `description` | `str | None` | Optional description |
| `action` | `RCloneAction` | `SYNC`, `COPY`, or `MOVE` |
| `src` | `str` | Source (`remote:path`) |
| `dest` | `str` | Destination (`remote:path`) |
| `options` | `RCloneOptions | None` | Additional rclone flags |

## RClone Options

RClone options are passed **as raw command-line flags**.
-   Flags **with values** → string
-   Flags **without values** → `true`

See [rclone Documentation](https://rclone.org/commands/rclone/) for all commands.

### Example

```yaml
options:
  --dry-run: true
  --exclude: "*.log"
  --transfers: "8"
``` 

Results in:

```bash
rclone copy ... --dry-run --exclude "*.log" --transfers 8
``` 

## License

Part of the **OpsFlow** project.