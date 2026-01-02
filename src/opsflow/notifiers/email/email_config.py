from typing import List
from enum import Enum

from pydantic import field_validator

from opsflow.core.config import NotifierConfig


class SmtpSecurity(str, Enum):
    """Defines the SMTP transport security mode."""

    NONE = "none"
    STARTTLS = "starttls"
    SSL = "ssl"


class EmailNotifierConfig(NotifierConfig):
    """Configuration for the EmailNotifier.

    Attributes:
        server (str): SMTP server address. Defaults to "localhost".
        port (int): SMTP server port. Defaults to 25.
        sender (str): Email sender address.
        recipient (str | List[str]): Email recipient address.
    """

    server: str = "localhost"
    port: int = 25
    sender: str
    recipient: str | List[str]
    security: SmtpSecurity = SmtpSecurity.NONE
    password: str | None = None
    user: str | None = None

    @classmethod
    @field_validator("port")
    def validate_port(cls, v: int) -> int:
        if v <= 0 or v > 65535:
            raise ValueError("Port must be between 1 and 65535")
        return v

    @classmethod
    @field_validator("recipient", mode="before")
    def normalize_recipient(cls, v: str | List[str]):
        if isinstance(v, str):
            return [v]
        return v
