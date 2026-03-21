"""
Helpers para movimientos de stock de inventario.

Dos funciones principales:
- log_stock_movement(): solo inserta el registro de movimiento.
  Úsala cuando el stock ya fue actualizado por el caller (ej: work_orders/views.py).
  DEBE llamarse dentro de transaction.atomic().

- apply_stock_change(): hace todo: lock FOR UPDATE, valida, actualiza stock y loguea.
  Úsala cuando el caller NO tiene ya un lock (ej: cash_register, ajustes manuales).
"""
from decimal import Decimal

from django.db import connection, transaction


def log_stock_movement(
    product_id,
    qty_before: Decimal,
    qty_change: Decimal,
    qty_after: Decimal,
    movement_type: str,
    performed_by=None,
    reason: str = None,
    reference_id=None,
    reference_type: str = None,
) -> None:
    """
    Inserta un registro en product_movements.
    NO actualiza el stock — asume que el caller ya lo hizo.
    Debe llamarse dentro de un bloque transaction.atomic().
    """
    with connection.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO django_app.product_movements
              (product_id, movement_type, qty_before, qty_change, qty_after,
               reason, reference_id, reference_type, performed_by)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            [
                str(product_id),
                movement_type,
                str(qty_before),
                str(qty_change),
                str(qty_after),
                reason,
                str(reference_id) if reference_id else None,
                reference_type,
                str(performed_by) if performed_by else None,
            ],
        )


def apply_stock_change(
    product_id,
    qty_change: Decimal,
    movement_type: str,
    performed_by=None,
    reason: str = None,
    reference_id=None,
    reference_type: str = None,
) -> Decimal:
    """
    Atómicamente: bloquea el producto (FOR UPDATE), valida, actualiza stock y loguea.
    Úsala cuando el caller no tiene ya un lock sobre el producto.

    qty_change debe estar en la unidad base del producto.

    Retorna qty_after (Decimal).
    Lanza ValueError en caso de producto inactivo o stock insuficiente.
    """
    with transaction.atomic():
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT stock_qty, is_active FROM public.products WHERE product_id = %s FOR UPDATE",
                [str(product_id)],
            )
            row = cursor.fetchone()
            if not row:
                raise ValueError("Producto no encontrado.")

            qty_before = Decimal(str(row[0] or 0))
            is_active = row[1]

            if not is_active and movement_type != "deactivation":
                raise ValueError("Producto inactivo. No se pueden registrar movimientos.")

            qty_after = qty_before + qty_change

            if qty_after < 0:
                raise ValueError(f"Stock insuficiente. Disponible: {qty_before}")

            cursor.execute(
                "UPDATE public.products SET stock_qty = %s, updated_at = now() WHERE product_id = %s",
                [str(qty_after), str(product_id)],
            )

            cursor.execute(
                """
                INSERT INTO django_app.product_movements
                  (product_id, movement_type, qty_before, qty_change, qty_after,
                   reason, reference_id, reference_type, performed_by)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                [
                    str(product_id),
                    movement_type,
                    str(qty_before),
                    str(qty_change),
                    str(qty_after),
                    reason,
                    str(reference_id) if reference_id else None,
                    reference_type,
                    str(performed_by) if performed_by else None,
                ],
            )

    return qty_after
