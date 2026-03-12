import datetime
import logging
from datetime import date

from django.db import connection

logger = logging.getLogger(__name__)


def run_monthly_auto_close():
    """
    Ejecuta el cierre del mes anterior.
    Idempotente: si el cierre ya existe, lo omite sin error.
    Reutiliza los helpers de views.py para no duplicar lógica.
    """
    from .views import _aggregate_period, _insert_audit, _open_sessions_in_period, _period_dates

    today = date.today()
    first = today.replace(day=1)
    prev = first - datetime.timedelta(days=1)
    year, month = prev.year, prev.month

    period_start, period_end = _period_dates(year, month)
    folio = f"CM-{year}-{month:02d}"

    # Verificar si ya existe
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT closure_id FROM public.period_closures WHERE folio = %s LIMIT 1",
            [folio],
        )
        if cursor.fetchone():
            logger.info("[AutoClose] %s ya existe. Omitiendo.", folio)
            return

    # Advertir sobre sesiones abiertas (pero proceder igual)
    open_sessions = _open_sessions_in_period(period_start, period_end)
    if open_sessions:
        logger.warning(
            "[AutoClose] %s: %d sesión(es) aún abiertas — se cierra de todas formas.",
            folio,
            len(open_sessions),
        )

    agg = _aggregate_period(period_start, period_end)

    with connection.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO public.period_closures
              (closure_type, period_start, period_end, folio, status,
               total_income, total_expenses, total_net,
               total_sessions, total_movements, cash_discrepancies,
               sales_total, payment_total, withdrawal_total, refund_total, adjustment_total,
               notes, closed_at, created_at, updated_at)
            VALUES ('monthly', %s, %s, %s, 'closed',
                    %s, %s, %s,
                    %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, now(), now(), now())
            RETURNING closure_id
            """,
            [
                period_start, period_end, folio,
                str(agg["total_income"]), str(agg["total_expenses"]), str(agg["total_net"]),
                agg["total_sessions"], agg["total_movements"], str(agg["cash_discrepancies"]),
                str(agg["sales_total"]), str(agg["payment_total"]),
                str(agg["withdrawal_total"]), str(agg["refund_total"]),
                str(agg["adjustment_total"]),
                f"Cierre automático {folio}.",
            ],
        )
        closure_id = str(cursor.fetchone()[0])

    _insert_audit(closure_id, "created", "system", f"Cierre automático mensual {folio}.")
    logger.info("[AutoClose] %s creado exitosamente (ID: %s).", folio, closure_id)


def start_scheduler():
    from apscheduler.schedulers.background import BackgroundScheduler
    from apscheduler.triggers.cron import CronTrigger

    scheduler = BackgroundScheduler(timezone="America/Costa_Rica")
    scheduler.add_job(
        run_monthly_auto_close,
        CronTrigger(day=1, hour=1, minute=0),
        id="monthly_period_close",
        replace_existing=True,
        misfire_grace_time=3600,  # ejecuta hasta 1h después si el server estaba apagado
    )
    scheduler.start()
    logger.info(
        "[AutoClose] Scheduler iniciado — cierre automático el día 1 de cada mes a la 01:00 AM (CR)."
    )
