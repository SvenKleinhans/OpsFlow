import logging
from typing import List, Optional, Dict
from opsflow.core.models import Context

from .gitlab_config import Hook


def execute_hooks(
    ctx: Context,
    hooks: Optional[List[Hook]] = None,
    logger: Optional[logging.Logger] = None,
    env: Optional[Dict[str, str]] = None,
) -> bool:
    """Executes a list of shell command hooks.

    Args:
        ctx (Context): OpsFlow plugin context to run commands and collect results.
        hooks (Optional[List[Hook]]): List of hook objects to execute. Defaults to None.
        logger (Optional[logging.Logger]): Logger instance for logging steps. Defaults to None.
        env Optional[Dict[str, str]]: Environment variables. Defaults to None.

    Returns:
        bool: True if all hooks succeeded or errors were allowed to continue,
              False if a hook failed and halted execution.
    """
    if not hooks:
        return True

    for hook in hooks:
        if logger:
            logger.info("Running hook: %s → %s", hook.name, hook.cmd)

        result = ctx.cmd.run_as_result(hook.cmd.split(), hook.name, env=env)

        if result:
            ctx.add_result(result)
            if logger:
                logger.error("Hook %s failed: %s", hook.name, result.message)

            if not hook.allow_failure:
                if logger:
                    logger.warning(
                        "Stopping hook execution due to failure in: %s", hook.name
                    )
                return False

    return True
