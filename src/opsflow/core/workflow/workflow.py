import sys
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import current_thread

from opsflow.core.utils.report_formatter import ReportFormatter

from ..config.loader import ConfigLoader
from ..config.schema import CoreConfig
from ..models.context import Context
from ..models.result import Result, ResultCollector, Severity
from ..notifier.composite import CompositeNotifier
from ..notifier.factory import NotifierFactory
from ..plugin.base import Plugin
from ..plugin.factory import PluginFactory
from ..system.base import SystemManager
from ..utils.command_runner import CommandRunner
from ..utils.logger_setup import setup_logger
from ..utils.module_loader import ModuleLoader


class Workflow:
    """Orchestrator for executing system updates, plugins, and reporting results.

    If no `SystemManager` is provided, the workflow can still run plugins and send reports.
    """

    def __init__(
        self,
        system_manager: SystemManager | None = None,
        config: CoreConfig | None = None,
        config_path: str | None = None,
        plugin_dir: str | None = None,
        notifier_dir: str | None = None,
    ):
        """Initialize the workflow orchestrator.

        This will load plugins and notifiers from specified directories, configure logging,
        initialize the optional system manager, result collector, and instantiate all plugins and notifiers.

        Args:
            system_manager (Optional[SystemManager]): The system manager instance for system operations. Can be None.
            config (Optional[CoreConfig]): Preloaded configuration object.
            config_path (Optional[str]): Path to a configuration file (used if `config` is None).
            plugin_dir (Optional[str]): Directory containing plugin modules.
            notifier_dir (Optional[str]): Directory containing notifier modules.
        """
        # Load and validate core configuration (from object or config file)
        self._config = config or self._load_config(config_path)

        # Initialize logging early so all subsystems (plugins, command runner, etc.)
        # can rely on a fully configured logger
        self._logger, self._memory_handler = setup_logger(self._config.logging)
        self._logger.debug("Logger initialized")

        # Configure CommandRunner as a process-wide service
        # (uses framework logging and dry-run settings)
        CommandRunner.configure(
            dry_run=self._config.dry_run,
            logger=self._logger,
        )

        # Create shared result collector used across the workflow
        self._result_collector = ResultCollector()

        # Build execution context passed to all runtime components
        self._ctx = Context(
            result_collector=self._result_collector,
            dry_run=self._config.dry_run,
        )

        # Attach framework-managed runtime dependencies to the system manager
        # before it is used by the workflow
        if system_manager:
            system_manager._attach_runtime(self._logger, self._ctx)
            self._system_manager = system_manager
        else:
            self._system_manager = None
            self._logger.info("No system manager provided, skipping system updates")

        # Load modules safely
        self._load_modules(
            plugin_dir,
            step="module_load:plugins",
            success_msg="Plugins loaded from directory: %s",
            error_msg="Failed loading plugins from %s",
        )

        self._load_modules(
            notifier_dir,
            step="module_load:notifiers",
            success_msg="Notifiers loaded from directory: %s",
            error_msg="Failed loading notifiers from %s",
        )

        # Build notifiers and plugins
        self._notifier: CompositeNotifier = self._build_notifier()
        self._plugins: list[Plugin] = self._build_plugins()
        self._logger.debug("Workflow initialized with %d plugins", len(self._plugins))

    def run_system_update(self) -> None:
        """Execute the system update via the system manager and collect the results.

        If no system manager is set, this method logs and skips the update.
        """
        if not self._system_manager:
            return

        self._logger.info("Starting system update...")
        try:
            self._logger.debug("Calling system_manager.update()")
            self._system_manager.update()

            self._logger.debug("Checking if reboot is required")
            self._system_manager.check_reboot_required()

            self._logger.debug("Checking for major OS release")
            self._system_manager.check_new_stable_available()

        except Exception as e:
            self._logger.exception("System update failed")
            self._result_collector.add(
                Result(step="system_update", severity=Severity.ERROR, message=str(e))
            )

        self._logger.debug("System update completed")

    def run_plugins(self, parallel: bool = False, max_workers: int = 4) -> None:
        """Execute all instantiated plugins and collect their results.

        Args:
            parallel (bool): If True, run plugins in parallel threads.
            max_workers (int): Maximum number of threads when running in parallel.
        """
        self._logger.info(
            "Running %d plugins (parallel=%s)...", len(self._plugins), parallel
        )
        if not parallel:
            for plugin in self._plugins:
                self._run_single_plugin(plugin)
            return

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(self._run_single_plugin, p): p for p in self._plugins
            }
            for _ in as_completed(futures):
                # _run_single_plugin handles exceptions and results
                self._logger.debug(
                    "Plugin future completed in thread %s", current_thread().name
                )

    def process_results(self) -> None:
        """Format all collected results and send a report via the notifier."""
        self._logger.debug("Processing results for report")
        reporter = ReportFormatter(results=self._result_collector.all_results())
        logs = self._memory_handler.get_value()
        report = reporter.format_report(logs=logs)
        try:
            self._notifier.notify("Workflow Report", report)
            self._logger.info("Report sent successfully.")
        except Exception as e:
            self._logger.error("Failed to send report: %s", e)

    def run_all(self) -> None:
        """Run the full workflow: system update, plugin execution, and result processing."""
        self._logger.info("Starting full workflow run")
        self.run_system_update()
        self.run_plugins()
        self.process_results()
        self._logger.info("Workflow run finished")

    def _run_single_plugin(self, plugin: Plugin) -> None:
        """Execute a single plugin, handling setup, run, teardown, and result collection.

        Args:
            plugin (Plugin): The plugin instance to execute.
        """
        thread = current_thread().name
        name = plugin.name

        self._logger.debug("[%s] Plugin %s setup started", thread, name)
        if not self._safe_call(
            plugin.setup, step="setup", plugin=plugin, severity=Severity.ERROR
        ):
            return

        self._logger.debug("[%s] Plugin %s run started", thread, name)
        self._safe_call(plugin.run, step="run", plugin=plugin, severity=Severity.ERROR)

        self._logger.debug("[%s] Plugin %s teardown started", thread, name)
        self._safe_call(
            plugin.teardown, step="teardown", plugin=plugin, severity=Severity.WARNING
        )

    def _safe_call(
        self,
        func: Callable[[], None],
        step: str,
        plugin: Plugin,
        severity: Severity,
    ) -> bool:
        """Safely call a plugin method, catching exceptions and logging results.

        Args:
            func (Callable[[], None]): The plugin method to call.
            step (str): The step identifier (e.g., "setup", "run", "
            plugin (Plugin): The plugin instance.
            severity (Severity): Severity level for logging errors.

        Returns:
            bool: True if the call succeeded, False if an exception occurred.
        """
        try:
            func()
            return True
        except Exception as e:
            self._logger.exception(
                "[%s] %s failed for plugin %s",
                current_thread().name,
                step,
                plugin.name,
            )
            self._result_collector.add(
                Result(
                    step=f"plugin:{step}:{plugin.name}",
                    severity=severity,
                    message=str(e),
                )
            )
            return False

    @staticmethod
    def _load_config(config_path: str | None) -> CoreConfig:
        """Load the configuration from the specified file or command-line argument.

        Args:
            config_path (Optional[str]): Path to the configuration file.

        Returns:
            CoreConfig: The loaded configuration object.
        """
        path = config_path or (sys.argv[1] if len(sys.argv) > 1 else "config.yaml")
        return ConfigLoader.load(path)

    def _load_modules(self, directory, step, success_msg, error_msg) -> None:
        """Load modules from a specified directory with error handling.

        Args:
            directory (str): Directory path to load modules from.
            step (str): Identifier for the loading step.
            success_msg (str): Message to log on successful loading.
            error_msg (str): Message to log on loading failure.
        """
        if not directory:
            return
        try:
            ModuleLoader.load_from_directory(directory)
            self._logger.debug(success_msg, directory)
        except Exception as e:
            self._logger.exception(error_msg, directory)
            self._result_collector.add(
                Result(
                    step=step,
                    severity=Severity.ERROR,
                    message=str(e),
                )
            )

    def _build_notifier(self) -> CompositeNotifier:
        """Instantiate a CompositeNotifier containing all registered notifiers.

        Returns:
            CompositeNotifier: Aggregated notifier for sending reports.
        """
        self._logger.debug("Building notifiers")
        factory = NotifierFactory(config=self._config, logger=self._logger)
        composite = CompositeNotifier()
        for notifier in factory.create_all():
            composite.add_notifier(notifier)
            self._logger.debug("Notifier added: %s", type(notifier).__name__)
        return composite

    def _build_plugins(self) -> list[Plugin]:
        """Instantiate all enabled plugins with a shared execution context.

        Returns:
            List[Plugin]: List of plugin instances ready for execution.
        """
        self._logger.debug("Building plugins")
        ctx = Context(
            result_collector=self._result_collector, dry_run=self._config.dry_run
        )
        factory = PluginFactory(config=self._config, ctx=ctx, logger=self._logger)
        plugins = list(factory.create_all())
        self._logger.debug("Total plugins instantiated: %d", len(plugins))
        return plugins
