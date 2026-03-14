-- ============================================================
-- Bitácora de movimientos de inventario
-- Schema: django_app
-- Referencia FK: public.products (search_path: django_app,public)
-- ============================================================

CREATE TABLE IF NOT EXISTS django_app.product_movements (
    movement_id      UUID          PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id       UUID          NOT NULL
                                   REFERENCES public.products(product_id)
                                   ON DELETE RESTRICT,
    movement_type    TEXT          NOT NULL
                                   CHECK (movement_type IN (
                                     'sale',
                                     'work_order',
                                     'work_order_refund',
                                     'manual_adjustment',
                                     'purchase',
                                     'deactivation'
                                   )),
    qty_before       NUMERIC(12,2) NOT NULL,
    qty_change       NUMERIC(12,2) NOT NULL,  -- positivo = entrada, negativo = salida
    qty_after        NUMERIC(12,2) NOT NULL,
    reason           TEXT,
    reference_id     UUID,           -- cash_movement_id o work_order_product_id
    reference_type   TEXT,           -- 'cash_movement' | 'work_order_product' | NULL
    performed_by     UUID,           -- user id (nullable para operaciones de sistema)
    created_at       TIMESTAMPTZ   NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_product_movements_product_at
  ON django_app.product_movements (product_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_product_movements_type
  ON django_app.product_movements (movement_type);
