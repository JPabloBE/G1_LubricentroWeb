"""
Management command para cierre automático de periodos.

Uso:
    python manage.py auto_close_period --type monthly --year 2026 --month 3

Puede ser llamado por cron del servidor, por ejemplo:
    0 1 1 * * cd /path/to/project && python manage.py auto_close_period --type monthly
"""
import calendar
from datetime import date

from django.core.management.base import BaseCommand, CommandError
from django.db import connection


class Command(BaseCommand):
    help = "Ejecuta un cierre de periodo automático (mensual)."

    def add_arguments(self, parser):
        parser.add_argument("--type", default="monthly", choices=["monthly"], help="Tipo de cierre")
        parser.add_argument("--year", type=int, help="Año del periodo (default: mes actual)")
        parser.add_argument("--month", type=int, help="Mes del periodo (default: mes anterior)")
        parser.add_argument("--force", action="store_true", help="Ignorar sesiones abiertas")
        parser.add_argument("--notes", default="", help="Notas del cierre automático")

    def handle(self, *args, **options):
        today = date.today()
        closure_type = options["type"]

        if closure_type == "monthly":
            # Por defecto cierra el mes anterior
            if options["year"] and options["month"]:
                year, month = options["year"], options["month"]
            else:
                first_day = today.replace(day=1)
                prev_month = first_day.replace(day=1)
                import datetime
                prev = first_day - datetime.timedelta(days=1)
                year, month = prev.year, prev.month

            last_day = calendar.monthrange(year, month)[1]
            period_start = date(year, month, 1)
            period_end = date(year, month, last_day)
            folio = f"CM-{year}-{month:02d}"

        # Verificar si ya existe
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT closure_id FROM public.period_closures WHERE folio = %s LIMIT 1", [folio]
            )
            if cursor.fetchone():
                self.stdout.write(self.style.WARNING(f"Ya existe un cierre con folio {folio}. Omitiendo."))
                return

        # Verificar sesiones abiertas
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT COUNT(*) FROM django_app.cash_sessions
                WHERE opened_at::date >= %s AND opened_at::date <= %s AND status = 'open'
                """,
                [period_start, period_end],
            )
            open_count = cursor.fetchone()[0]

        if open_count and not options["force"]:
            raise CommandError(
                f"Hay {open_count} sesión(es) abiertas en el periodo {folio}. "
                "Use --force para cerrar de igual manera."
            )

        # Aggregar
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    COUNT(DISTINCT cs.cash_session_id),
                    COUNT(cm.cash_movement_id),
                    COALESCE(SUM(CASE WHEN cm.amount > 0 THEN cm.amount ELSE 0 END), 0),
                    COALESCE(SUM(CASE WHEN cm.amount < 0 THEN ABS(cm.amount) ELSE 0 END), 0),
                    COALESCE(SUM(CASE WHEN cm.movement_type = 'sale'       THEN cm.amount ELSE 0 END), 0),
                    COALESCE(SUM(CASE WHEN cm.movement_type = 'payment'    THEN cm.amount ELSE 0 END), 0),
                    COALESCE(SUM(CASE WHEN cm.movement_type = 'withdrawal' THEN cm.amount ELSE 0 END), 0),
                    COALESCE(SUM(CASE WHEN cm.movement_type = 'refund'     THEN cm.amount ELSE 0 END), 0),
                    COALESCE(SUM(CASE WHEN cm.movement_type = 'adjustment' THEN cm.amount ELSE 0 END), 0),
                    COALESCE(SUM(cc.difference), 0)
                FROM django_app.cash_sessions cs
                LEFT JOIN django_app.cash_movements cm ON cm.cash_session_id = cs.cash_session_id
                LEFT JOIN django_app.cash_closings cc  ON cc.cash_session_id = cs.cash_session_id
                WHERE cs.opened_at::date >= %s AND cs.opened_at::date <= %s
                """,
                [period_start, period_end],
            )
            row = cursor.fetchone()
            total_income = float(row[2] or 0)
            total_expenses = float(row[3] or 0)

            notes = options["notes"] or f"Cierre automático {folio}."
            cursor.execute(
                """
                INSERT INTO public.period_closures
                  (closure_type, period_start, period_end, folio, status,
                   total_income, total_expenses, total_net,
                   total_sessions, total_movements, cash_discrepancies,
                   sales_total, payment_total, withdrawal_total, refund_total, adjustment_total,
                   notes, closed_at, created_at, updated_at)
                VALUES
                  (%s, %s, %s, %s, 'closed',
                   %s, %s, %s,
                   %s, %s, %s,
                   %s, %s, %s, %s, %s,
                   %s, now(), now(), now())
                RETURNING closure_id
                """,
                [
                    closure_type, period_start, period_end, folio,
                    str(row[2] or 0), str(row[3] or 0), str(total_income - total_expenses),
                    int(row[0] or 0), int(row[1] or 0), str(row[9] or 0),
                    str(row[4] or 0), str(row[5] or 0), str(row[6] or 0),
                    str(row[7] or 0), str(row[8] or 0),
                    notes,
                ],
            )
            closure_id = str(cursor.fetchone()[0])
            cursor.execute(
                """
                INSERT INTO public.period_closure_audit (closure_id, action, performed_at, notes)
                VALUES (%s, 'created', now(), %s)
                """,
                [closure_id, f"Cierre automático ejecutado via management command."],
            )

        self.stdout.write(self.style.SUCCESS(f"Cierre {folio} creado exitosamente (ID: {closure_id})."))
