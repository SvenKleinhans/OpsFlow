import pytest
from email.message import EmailMessage

from opsflow.notifiers.email import (
    EmailNotifier,
    EmailNotifierConfig,
    SmtpSecurity,
)

EMAIL_MODULE = "opsflow.notifiers.email.email"


class DummySMTP:
    def __init__(self, server, port):
        self.server = server
        self.port = port
        self.started_tls = False
        self.logged_in = None
        self.sent: list[EmailMessage] = []
        self.closed = False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def starttls(self):
        self.started_tls = True

    def login(self, user, password):
        self.logged_in = (user, password)

    def send_message(self, msg: EmailMessage):
        self.sent.append(msg)

    def quit(self):
        self.closed = True


@pytest.fixture
def smtp(monkeypatch):
    smtp = DummySMTP("smtp.example", 25)
    monkeypatch.setattr(
        f"{EMAIL_MODULE}.SMTP",
        lambda *a, **k: smtp,
    )
    monkeypatch.setattr(
        f"{EMAIL_MODULE}.SMTP_SSL",
        lambda *a, **k: smtp,
    )
    return smtp


@pytest.fixture
def base_cfg():
    cfg = EmailNotifierConfig(
        enabled=True,
        sender="from@test",
        recipient="to@test",
    )
    return EmailNotifierConfig.model_validate(cfg)


@pytest.fixture
def notifier(base_cfg, logger):
    return EmailNotifier(base_cfg, logger)


def test_disabled_config_does_nothing(notifier, smtp):
    notifier.config.enabled = False

    notifier.notify("sub", "msg")

    assert smtp.sent == []


def test_plain_smtp(notifier, smtp):
    notifier.notify("Hello", "Body")

    assert len(smtp.sent) == 1
    msg = smtp.sent[0]
    assert msg["Subject"] == "Hello"
    assert msg["From"] == "from@test"
    assert "to@test" == msg["To"]
    assert smtp.started_tls is False
    assert smtp.logged_in is None
    assert smtp.closed is True


def test_starttls_and_login(notifier, smtp):
    notifier.config.security = SmtpSecurity.STARTTLS
    notifier.config.user = "user"
    notifier.config.password = "pw"

    notifier.notify("sub", "msg")

    assert smtp.started_tls is True
    assert smtp.logged_in == ("user", "pw")


def test_ssl(notifier, smtp):
    notifier.config.security = SmtpSecurity.SSL

    notifier.notify("ssl", "msg")

    assert len(smtp.sent) == 1
