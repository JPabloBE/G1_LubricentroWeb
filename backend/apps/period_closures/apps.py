import os
import sys

from django.apps import AppConfig


class PeriodClosuresConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.period_closures"
    verbose_name = "Cierres de Periodo"

    def ready(self):
        # Solo iniciar el scheduler cuando Django corre como servidor web.
        # Evitar arranque en: migrate, shell, tests, y el proceso padre del StatReloader.
        is_runserver = "runserver" in sys.argv
        is_gunicorn = sys.argv and "gunicorn" in sys.argv[0]

        if not (is_runserver or is_gunicorn):
            return

        # Con StatReloader, Django lanza DOS procesos:
        #   padre (watcher): RUN_MAIN no está seteado
        #   hijo  (worker):  RUN_MAIN = 'true'
        # Solo iniciamos en el hijo para no duplicar el scheduler.
        if is_runserver and os.environ.get("RUN_MAIN") != "true":
            return

        from .scheduler import start_scheduler
        start_scheduler()
