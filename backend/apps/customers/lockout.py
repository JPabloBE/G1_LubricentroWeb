from datetime import datetime, timezone

from django.db import connection

MAX_ATTEMPTS = 5
LOCKOUT_SECONDS = 15 * 60  # 15 minutos


def get_lockout_status(email):
    """Returns (is_locked, remaining_minutes)."""
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT locked_until FROM public.customers WHERE email ILIKE %s AND is_active = true",
            [email],
        )
        row = cursor.fetchone()

    if not row or row[0] is None:
        return False, 0

    locked_until = row[0]
    if locked_until.tzinfo is None:
        locked_until = locked_until.replace(tzinfo=timezone.utc)

    now = datetime.now(timezone.utc)
    if now >= locked_until:
        return False, 0

    remaining = int((locked_until - now).total_seconds() / 60) + 1
    return True, remaining


def record_failure(email):
    """
    Increment failure counter. On 5th failure (or if a previous lock expired),
    set a new lockout. Uses original row values in CASE — both SET expressions
    evaluate against the pre-UPDATE state.
    """
    with connection.cursor() as cursor:
        cursor.execute(
            """
            UPDATE public.customers
            SET
                failed_login_attempts = CASE
                    WHEN locked_until IS NOT NULL AND locked_until <= now()
                    THEN 1
                    ELSE failed_login_attempts + 1
                END,
                locked_until = CASE
                    WHEN locked_until IS NOT NULL AND locked_until <= now()
                    THEN NULL
                    WHEN failed_login_attempts + 1 >= %s
                    THEN now() + (%s * interval '1 second')
                    ELSE NULL
                END,
                updated_at = now()
            WHERE email ILIKE %s AND is_active = true
            """,
            [MAX_ATTEMPTS, LOCKOUT_SECONDS, email],
        )


def clear_failures(email):
    with connection.cursor() as cursor:
        cursor.execute(
            """
            UPDATE public.customers
            SET failed_login_attempts = 0, locked_until = NULL, updated_at = now()
            WHERE email ILIKE %s AND is_active = true
            """,
            [email],
        )
