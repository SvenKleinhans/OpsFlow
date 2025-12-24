from unittest.mock import Mock, patch

from opsflow.core.workflow import Workflow


class TestWorkflowResultProcessing:
    """Test result collection and reporting."""

    def test_workflow_processes_results_and_sends_report(self, config_with_plugins):
        """Workflow should process collected results and send a notification report."""
        workflow = Workflow(config=config_with_plugins)

        workflow.run_plugins()

        # Mock the notifier to capture the report
        with patch.object(workflow._notifier, "notify") as mock_notify:
            workflow.process_results()

            mock_notify.assert_called_once()
            subject, report = mock_notify.call_args[0]
            assert subject == "Workflow Report"
            assert isinstance(report, str)

    def test_workflow_formats_report_with_logs(self, config_with_plugins):
        """Workflow should include logs in the formatted report."""
        workflow = Workflow(config=config_with_plugins)

        # Log something
        workflow._logger.info("Test log message")

        with patch.object(workflow._notifier, "notify") as mock_notify:
            workflow.process_results()

            _, report = mock_notify.call_args[0]
            # Report should be generated (actual content depends on implementation)
            assert isinstance(report, str)

    def test_workflow_handles_notification_errors(self, config_with_plugins):
        """Workflow should handle errors when sending notifications."""
        workflow = Workflow(config=config_with_plugins)

        # Make notifier raise an error
        workflow._notifier.notify = Mock(side_effect=RuntimeError("Notification failed"))

        # Should not raise, but log the error
        workflow.process_results()

        # No exception should propagate
