
# Email Notifier

The **Email Notifier** is a notifier component of the **OpsFlow Framework**.  
It sends notifications via SMTP and integrates seamlessly into the OpsFlow notification pipeline.

## Features

- Send notifications via SMTP
- Supports plain SMTP, STARTTLS, and SSL
- Simple configuration via **YAML** or **Python**
- Built on OpsFlow's `NotifierConfig` system

## Configuration

The notifier can be configured either declaratively (YAML) or programmatically (Python).

Internally, recipients are always normalized to a list of email addresses.  
For convenience, a single recipient can be provided as a string.

### Configuration Options

| Field       | Type           | Description                                      | Default     |
|------------|----------------|--------------------------------------------------|-------------|
| `server`   | `str`          | SMTP server address                              | `localhost` |
| `port`     | `int`          | SMTP server port (1–65535)                       | `25`        |
| `sender`   | `str`          | Email sender address                             | —           |
| `recipient`| `str \| list[str]`          | One or more email recipients                           | —           |
| `security` | `none \| starttls \| ssl` | SMTP transport security mode         | `none`      |
| `user`     | `str \| None`  | SMTP username                                    | `None`      |
| `password` | `str \| None`  | SMTP password                                    | `None`      |

### YAML Configuration

Single recipient:

```yaml
notifier:
  name: email
  server: smtp.example.com
  port: 587
  sender: opsflow@example.com
  recipient: admin@example.com
  security: starttls
  user: smtp-user
  password: secret
```

Multiple recipients:

```yaml
notifier:
  type: email
  server: smtp.example.com
  port: 587
  sender: opsflow@example.com
  recipient:
    - admin@example.com
    - ops@example.com
  security: starttls
```

### Python Configuration
```python
from opsflow.notifiers.email import EmailNotifierConfig, SmtpSecurity

config = EmailNotifierConfig(
    server="smtp.example.com",
    port=587,
    sender="opsflow@example.com",
     recipient=[
        "admin@example.com",
        "ops@example.com",
    ],
    security=SmtpSecurity.STARTTLS,
    user="smtp-user",
    password="secret",
)
```

## Notes

-   Authentication is optional and only required if `user` is set.
-   For `SSL`, ensure the correct port (e.g. 465) is used.
- Recipients are always handled internally as a list.
-   The notifier relies on the OpsFlow runtime for execution and lifecycle management.

## License

Part of the **OpsFlow** project.