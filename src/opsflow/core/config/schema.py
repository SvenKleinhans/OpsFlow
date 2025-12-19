from typing import Dict
from pydantic import BaseModel, Field


class PluginConfig(BaseModel):
    """Base configuration for a plugin.

    Attributes:
        enabled (bool): Whether the plugin is active. Defaults to True.
    """

    enabled: bool = True


class NotifierConfig(BaseModel):
    """Base configuration for any notifier.

    Attributes:
        enabled (bool): Whether the notifier is active. Defaults to False.
    """

    enabled: bool = False


class LoggingConfig(BaseModel):
    """Configuration for the logging system.

    Attributes:
        file (str): Path to the log file. Defaults to "/var/log/workflow.log".
        debug (bool): Enable debug-level logging. Defaults to False.
    """

    file: str = "/var/log/workflow.log"
    debug: bool = False


class CoreConfig(BaseModel):
    """Top-level configuration.

    Attributes:
        dry_run: If True, commands will not be executed.
        logging (LoggingConfig): Logging configuration.
        notifiers (Optional[Dict[str, NotifierConfig]]): Mapping of notifier names to configurations.
        plugins (Optional[Dict[str, PluginConfig]]): Mapping of plugin names to configurations.
    """

    dry_run: bool = False
    logging: LoggingConfig = LoggingConfig()
    notifiers: Dict[str, NotifierConfig] = Field(default_factory=dict)
    plugins: Dict[str, PluginConfig] = Field(default_factory=dict)
