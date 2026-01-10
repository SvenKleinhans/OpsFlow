# GitLab Plugin for OpsFlow

> ⚠️ **Prerequisite:** You should have a basic understanding of [OpsFlow](https://github.com/SvenKleinhans/OpsFlow), including how to register and configure plugins.

## Overview

The GitLab plugin extends OpsFlow to manage **GitLab Omnibus instances**. It provides two main features:

1. **Backups**  
   - Backup GitLab repositories and databases from the internal GitLab backup directory (default: `/var/opt/gitlab/backups`).
   - Backup GitLab **Omnibus configuration** from `/etc/gitlab` using `gitlab-ctl backup-etc`.
   - Optionally run pre- and post-backup hooks.
   - Store all artifacts in a unified backup directory.

2. **Updates**  
   - Update GitLab to the latest package version (minor/patch updates only).
   - Optionally restart GitLab after updates.
   - Run pre- and post-update hooks.
   - Automatically perform a backup before applying updates if enabled.

This plugin is designed to be **modular and extensible**, while keeping the core functionality compact.

---

## Configuration

The plugin is configured via a **Python class** or YAML. The configuration controls:

- GitLab edition (EE or CE)
- Backup behavior
- Update behavior
- Hooks to execute during backup or update
- Backup directories and options

---

### Python Configuration Example

```python
from pathlib import Path
from opsflow.plugins.gitlab import GitLabConfig, GitLabEdition, Hook, GitLabBackupConfig

config = GitLabConfig(
    edition=GitLabEdition.CE,
    run_backup=True,
    run_update=True,
    backup_before_update=True,
    auto_restart=True,
    backup_config=GitLabBackupConfig(
        backup_target_dir=Path("/opt/opsflow/gitlab-backups"),
        gitlab_source_backup_dir=Path("/var/opt/gitlab/backups"),
        gitlab_backup_options={"STRATEGY": "copy"},
        pre_backup_hooks=[
            Hook(name="stop_custom_service", cmd="systemctl stop myservice"),
        ],
        post_backup_hooks=[
            Hook(name="upload_to_s3", cmd="/usr/local/bin/upload.sh"),
        ],
    ),
    pre_update_hooks=[
        Hook(name="pre_update_check", cmd="/usr/local/bin/check.sh"),
    ],
    post_update_hooks=[
        Hook(name="notify_team", cmd="/usr/local/bin/notify.sh"),
    ],
)
```

### YAML configuration example 

```yaml
plugins:
  gitlab:
    enabled: true
    edition: ce
    run_backup: true
    run_update: true
    backup_before_update: true
    auto_restart: true

    backup_config:
      backup_target_dir: /opt/opsflow/gitlab-backups
      gitlab_source_backup_dir: /var/opt/gitlab/backups
      gitlab_backup_options:
        STRATEGY: copy
      pre_backup_hooks:
        - name: stop_custom_service
          cmd: systemctl stop myservice
      post_backup_hooks:
        - name: upload_to_s3
          cmd: /usr/local/bin/upload.sh

    pre_update_hooks:
      - name: pre_update_check
        cmd: /usr/local/bin/check.sh

    post_update_hooks:
      - name: notify_team
        cmd: /usr/local/bin/notify.sh
```

## Notes

- **Backup Paths:**  
  All final backup artifacts are stored in `backup_target_dir`. Repositories and DB backups are copied from GitLab's internal backup directory (`gitlab_source_backup_dir`) to this unified location.  
  **Default:** `/var/opt/gitlab/backups`.  
  ⚠️ If the GitLab internal backup path has been changed in GitLab's configuration, you must update `gitlab_source_backup_dir` in the plugin configuration accordingly.

- **Backup Options:**  
  The `gitlab_backup_options` dictionary allows passing additional parameters to `gitlab-backup create`. By default, `STRATEGY` is set to `"copy"` if not specified.

- **Hooks:**  
  Hooks are simple shell commands executed at the specified workflow step. If a hook fails and `allow_failure=False`, the workflow stops.
  During hook execution, the environment variable `OPSFLOW_GITLAB_BACKUP_DIR` is automatically set. It points to the backup target directory where backups are copied to.
  The directory is composed of
  `backup_target_dir` (e.g. `/opt/opsflow/gitlab-backups`)
  plus the current date and time (e.g. `YYYY-MM-DD_HHMMSS`).

- **Update Restrictions:**  
  Major GitLab upgrades are **not supported automatically**. If a major upgrade is detected, the plugin will log a **warning** indicating that manual intervention is required and the update will **not** proceed automatically. Only minor or patch upgrades are applied automatically.

- **OpsFlow Integration:**  
  The plugin leverages OpsFlow's `CommandRunner` and `Result` objects for executing commands and reporting status.

## License

Part of the **OpsFlow** project.