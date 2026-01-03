from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.conf import settings
import dns.resolver
import smtplib
import socket


def is_valid_email_format(email: str) -> bool:
    try:
        validate_email(email)
        return True
    except ValidationError:
        return False


def email_exists(email: str, timeout: int = 10) -> bool:
    """
    Heuristically check whether an email address exists by looking up MX records
    and attempting an SMTP RCPT TO command.

    Returns True if any MX server accepts the recipient, False otherwise.

    Note: this can produce false negatives (many servers block RCPT checks)
    and may require network access. Use cautiously in production.
    """
    try:
        domain = email.split('@', 1)[1]
    except IndexError:
        return False

    try:
        answers = dns.resolver.resolve(domain, 'MX', lifetime=timeout)
    except Exception:
        return False

    mx_hosts = sorted([(r.preference, str(r.exchange).rstrip('.')) for r in answers], key=lambda x: x[0])

    from_address = getattr(settings, 'DEFAULT_FROM_EMAIL', 'validator@localhost')

    for _, mx in mx_hosts:
        server = None
        try:
            # connect directly to the MX host on port 25 with a timeout
            server = smtplib.SMTP(mx, 25, timeout=timeout)
            server.set_debuglevel(0)
            server.ehlo()
            # Some servers require MAIL FROM before RCPT TO
            server.mail(from_address)
            code, resp = server.rcpt(email)
            if code in (250, 251):
                try:
                    server.quit()
                except Exception:
                    pass
                return True
        except BrokenPipeError:
            # remote server closed connection unexpectedly; try next MX
            continue
        except (smtplib.SMTPServerDisconnected, smtplib.SMTPConnectError, socket.timeout, smtplib.SMTPRecipientsRefused, OSError, Exception):
            # try next MX on any failure
            continue
        finally:
            if server:
                try:
                    server.close()
                except Exception:
                    pass

    return False
