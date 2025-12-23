# OpsFlow

OpsFlow is a modular automation framework for orchestrating operational tasks, monitoring systems, and delivering results across multiple notification channels. It provides a small, well-typed core and a plugin-based extension model so you can implement checks, integrations and delivery channels independently and compose them into flexible operational workflows.

# Features

- **Modular plugin architecture** — implement checks, probes, and operational tasks as standalone plugins that OpsFlow discovers and executes.
- **Pluggable notifiers** — deliver plugin results and operational messages through interchangeable notifier implementations (e.g. chat systems, email, webhooks).
- **System-specific managers** — SystemManager implementations are bound to a concrete system type (e.g. Linux, Windows) and encapsulate system discovery and system-level operations.
- **Package-specific managers** — PackageManager implementations target a specific package ecosystem (e.g. APT) and provide a structured interface for interacting with system packages or components.
- **Extensible architecture** — plugins, notifiers, system managers and package managers follow consistent base abstractions and can be added or replaced without touching the core.
- **Flexible configuration** — all configurations are implemented as **Pydantic models**, including inherited configurations (e.g., PluginConfig), enabling automatic validation and type safety.
- **Parallel execution of plugins** — plugins can be executed concurrently to improve workflow performance.
- **Lightweight, OOP-first core** — a minimal core with clearly defined base classes, designed for testable and maintainable object-oriented extensions.

# Dependencies

OpsFlow requires Python 3.13 or higher. The core dependencies are:

- `pydantic` — for configuration models and validation
- `PyYAML` — for YAML-based workflow configuration

# Concepts & Terminology

OpsFlow is built around a small set of core concepts that can be combined to model operational workflows.

## Plugin
A Plugin encapsulates a single operational task, check, or integration.  
Plugins are executed by OpsFlow and return structured results that can be consumed by notifiers or further processing.

Examples:
- system health checks
- resource usage probes
- custom automation steps

## SystemManager
A SystemManager encapsulates operating system–level lifecycle and maintenance tasks for a specific platform.  
It is always bound to a concrete OS or system type and focuses on high-level system state and update management.

Typical responsibilities include:
- determining whether a system reboot is required
- checking for the availability of a new stable operating system release
- performing operating system updates
- optionally executing **pre-update** and **post-update** hooks for custom actions before or after updates

SystemManager implementations are intentionally narrow in scope and do not replace plugins; instead, they provide a consistent interface for OS-specific maintenance operations.

## PackageManager
A PackageManager encapsulates package-level maintenance tasks for a specific package ecosystem.  
It is always tied to a concrete package manager implementation (e.g. APT) and focuses exclusively on update and upgrade operations.

Typical responsibilities include:
- checking whether package updates are available
- performing package upgrades on a system

PackageManager implementations are intentionally limited in scope and are used to complement system-level maintenance provided by the SystemManager.

## Notifier
A Notifier is responsible for delivering the aggregated execution results of an OpsFlow run.  
It receives a summary of all plugin and manager results as well as collected logs and forwards them to an external channel.

Typical responsibilities include:
- sending a summarized execution report
- forwarding logs and diagnostic information

Notifiers do not perform filtering or routing; they always receive the complete result set of a run and decide only how it is delivered.

# Quick Start

## Installation

```
pip install opsflow
```

## Configuration

OpsFlow is configured via YAML. See `examples/example_config.yaml` for a complete working setup.

Key points:
-   `dry_run`: execute without making changes
-   `logging`: debug mode and log file
-   `plugins`: enable and configure plugins
-   `notifiers`: enable and configure notifiers

> Refer to the `examples/` folder for a ready-to-run configuration.

## Running OpsFlow

OpsFlow can be run via the workflow API:

```python
from opsflow.core.workflow import Workflow

wf = Workflow(config_path="examples/example_config.yaml")
wf.run_all()
```

## Registering Plugins and Notifiers
Plugins and notifiers must be registered before they can be used. There are two options:

### 1. Manual registration

```python
from opsflow.core.plugin import PluginRegistry 
from opsflow.core.notifier import NotifierRegistry

# Plugin class and its corresponding config class
PluginRegistry.register_class(ExamplePlugin, ExamplePluginConfig)

# Notifier class and its corresponding config class
NotifierRegistry.register_class(ExampleNotifier, ExampleNotifierConfig)
```

**Notes:**
- `ExamplePlugin` and `ExampleNotifier` are **Python classes** implementing the OpsFlow plugin and notifier interfaces.
- Each implementation should have a corresponding configuration class (e.g. `ExamplePluginConfig`) for YAML or programmatic configuration.

### 2. Automatic registration via ModuleLoader / decorators

OpsFlow can automatically discover and register plugins and notifiers using decorators and the `Workflow` class.

**Usage in a workflow:**

```python
from opsflow.core.workflow import Workflow

wf = Workflow(plugin_dir="plugins/", notifier_dir="notifiers/")
wf.run_all() 
```
**How it works:**

- `Workflow` loads classes in the specified directories decorated with `@PluginRegistry.register(...)` (or the equivalent notifier decorator).
- Enabled plugins and notifiers are executed according to the configuration, with results and logs passed to all notifiers.
    
> See the `examples/` folder for complete working examples, including workflows with SystemManager and PackageManager.

# Built-in Implementations

## Plugins

- `rclone` — automates file syncs using Rclone

## Notifiers

- `email` — sends notifications via email
    
## SystemManagers

- `debian` — manages Debian-specific system tasks
- `ubuntu` — manages Ubuntu-specific system tasks
    
## PackageManagers

- `apt` — manages package updates and upgrades for APT-based systems

# Contributing

Contributions are welcome! To contribute:
1. Fork the repository.
2. Create a feature branch and add tests.
3. Submit a merge request.

# License

This project is licensed under the MIT License. See the [LICENSE](./LICENSE) file for details.