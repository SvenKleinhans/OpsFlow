import yaml
from pydantic import BaseModel
from pathlib import Path

from opsflow.core.config import (
    CoreConfig,
    LoggingConfig,
    PluginConfig,
    NotifierConfig,
)

from opsflow.plugins.rclone import (
    RClonePluginConfig,
    RCloneTask,
    RCloneAction,
)
from opsflow.notifiers.email import EmailNotifierConfig, SmtpSecurity


def create_yaml(model: BaseModel, name: str) -> None:
    """Create a YAML file from a Pydantic model.

    Args:
        model (BaseModel): The Pydantic model instance to serialize.
        name (str): The output file name.
    """
    Path(name).parent.mkdir(parents=True, exist_ok=True)
    with open(name, "w", encoding="utf-8") as f:
        yaml.safe_dump(model.model_dump(mode="json"), f, sort_keys=False)


def main():
    core_example = CoreConfig(
        logging=LoggingConfig(),
        plugins={"example_plugin": PluginConfig()},
        notifiers={"example_notifier": NotifierConfig()},
        dry_run=False,
    )
    create_yaml(core_example, "examples/core_config.yaml")

    email_example = EmailNotifierConfig(
        enabled=True,
        server="smtp.example.com",
        port=587,
        security=SmtpSecurity.STARTTLS,
        sender="opsflow@exampel.com",
        password="securepassword",
        user="opsflow_user",
        recipient="example@example.com",
    )
    create_yaml(email_example, "examples/email_notifier.yaml")

    rclone_example = RClonePluginConfig(
        tasks=[
            RCloneTask(
                name="sync_docs",
                description="Sync documents to backup location",
                action=RCloneAction.SYNC,
                src="/data/docs",
                dest="/backup/docs",
            )
        ]
    )
    create_yaml(rclone_example, "examples/rclone_plugin.yaml")


if __name__ == "__main__":
    main()
