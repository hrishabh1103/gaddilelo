import re
import logging

SENSITIVE_PATTERNS = [
    (re.compile(r'(["\']?password["\']?\s*[:=]\s*["\'])([^"\']+)(["\'])', re.IGNORECASE), r'\1[REDACTED]\3'),
    (re.compile(r'(["\']?access_token["\']?\s*[:=]\s*["\'])([^"\']+)(["\'])', re.IGNORECASE), r'\1[REDACTED]\3'),
    (re.compile(r'(["\']?token["\']?\s*[:=]\s*["\'])([^"\']+)(["\'])', re.IGNORECASE), r'\1[REDACTED]\3'),
    (re.compile(r'(Bearer\s+)([A-Za-z0-9_\-\.]+)', re.IGNORECASE), r'\1[REDACTED_JWT]'),
    (re.compile(r'(["\']?SECRET_KEY["\']?\s*[:=]\s*["\'])([^"\']+)(["\'])', re.IGNORECASE), r'\1[REDACTED]\3'),
    (re.compile(r'(["\']?SENDGRID_API_KEY["\']?\s*[:=]\s*["\'])([^"\']+)(["\'])', re.IGNORECASE), r'\1[REDACTED]\3'),
    (re.compile(r'(["\']?SMTP_PASSWORD["\']?\s*[:=]\s*["\'])([^"\']+)(["\'])', re.IGNORECASE), r'\1[REDACTED]\3'),
]

class SensitiveDataRedactionFilter(logging.Filter):
    """
    Logging filter that scrubs tokens, passwords, and secrets from all log output.
    """
    def filter(self, record: logging.LogRecord) -> bool:
        if isinstance(record.msg, str):
            for pattern, repl in SENSITIVE_PATTERNS:
                record.msg = pattern.sub(repl, record.msg)
        if record.args:
            sanitized_args = []
            for arg in record.args:
                if isinstance(arg, str):
                    for pattern, repl in SENSITIVE_PATTERNS:
                        arg = pattern.sub(repl, arg)
                sanitized_args.append(arg)
            record.args = tuple(sanitized_args)
        return True

def setup_logging():
    """Configures root logger with the redaction filter."""
    root_logger = logging.getLogger()
    redaction_filter = SensitiveDataRedactionFilter()
    root_logger.addFilter(redaction_filter)
    for handler in root_logger.handlers:
        handler.addFilter(redaction_filter)

