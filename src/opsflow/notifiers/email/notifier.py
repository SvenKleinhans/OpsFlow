from email.message import EmailMessage
from smtplib import SMTP, SMTP_SSL

from opsflow.core.notifier import Notifier

from .config import EmailNotifierConfig, SmtpSecurity


class EmailNotifier(Notifier[EmailNotifierConfig]):
    """Notifier implementation that sends emails via SMTP."""

    name = "email"

    def notify(self, subject: str, message: str) -> None:
        """Sends an email notification.

        Args:
            subject (str): Email subject.
            message (str): Email body text.

        Raises:
            SMTPException: If sending the email fails.
        """
        if self.config is None or not self.config.enabled:
            return

        msg = EmailMessage()
        msg["From"] = self.config.sender
        msg["To"] = self.config.recipient
        msg["Subject"] = subject
        msg.set_content(message)

        if self.config.security is SmtpSecurity.SSL:
            smtp_cls = SMTP_SSL
        else:
            smtp_cls = SMTP

        with smtp_cls(self.config.server, self.config.port) as server:
            if self.config.security is SmtpSecurity.STARTTLS:
                server.starttls()

            if self.config.user and self.config.password:
                server.login(self.config.user, self.config.password)

            server.send_message(msg)

            server.quit()
