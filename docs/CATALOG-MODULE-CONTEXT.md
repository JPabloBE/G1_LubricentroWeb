# AI Context — Módulo Catálogo (Categorías + Productos)

## Objetivo
Implementar un CRUD de **Categorías** y **Productos** conectado a **Supabase/Postgres** (tablas existentes), visible y utilizable **solo por admin** desde el dashboard. El front **no debe tener datos hardcoded**: todo se obtiene vía API.

---

## DB (Supabase) — estructura real

### `public.categories`
- **PK real:** `category_id uuid`
- Campos:
  - `name text not null` (único)
  - `description text`
  - `created_at timestamptz not null`
  - `updated_at timestamptz not null`
- Problemas reales encontrados:
  - PK NO es `id` (es `category_id`)
  - `created_at/updated_at` son NOT NULL → si la DB no rellena defaults, el backend debe setearlos

### `public.products`
- **PK:** `product_id uuid`
- **FK:** `category_id uuid` → debe referenciar `categories.category_id` (no `id`)
- Campos:
  - `sku text` (unique, opcional)
  - `name text not null`
  - `description text`
  - `unit_price numeric(12,2) not null default 0`
  - `cost numeric(12,2) not null default 0`
  - `stock_qty numeric(12,2) not null default 0`
  - `is_active boolean not null default true`
  - `created_at timestamptz not null`
  - `updated_at timestamptz not null`
  - `image_url text` (nullable) → imagen por URL para el producto

---

## Backend (Django + DRF) — decisiones clave

### Modelos
- Las tablas ya existen en Supabase → **`managed = False`** en modelos.
- Mapeo correcto de PKs:
  - `Category.category_id` (`db_column="category_id"`)
  - `Product.product_id` (`db_column="product_id"`)
- Relación:
  - `Product.category`:
    - `ForeignKey(Category, to_field="category_id", db_column="category_id", on_delete=SET_NULL)`

### Serializers
- Para evitar violaciones `NOT NULL` en `created_at/updated_at`:
  - En `create()` setear:
    - `created_at = timezone.now()`
    - `updated_at = timezone.now()`
  - En `update()` setear:
    - `updated_at = timezone.now()`
- `ProductSerializer` expone:
  - `category_id` (write) y `category_name` (read)
  - `image_url` (write/read)
  - PK: `product_id`

### Endpoints
- Categorías:
  - `GET/POST  /api/catalog/categories/`
  - `GET/PUT/DELETE /api/catalog/categories/<uuid>/`
- Productos:
  - `GET/POST  /api/catalog/products/`
  - `GET/PUT/DELETE /api/catalog/products/<uuid>/`

### Permisos
- CRUD desde dashboard solo admin:
  - `IsAdminOrReadOnly` en DRF (mutaciones solo admin)
  - En el front, validar admin con `GET /api/auth/me/`

---

## Front (Bootstrap + JS fetch) — decisiones clave

### Pantallas
- `dashboard_categories.html`: CRUD de categorías
- `dashboard_products.html`: CRUD de productos

### Reglas UI / Data (sin hardcode)
- Toda data viene del backend (API)
- Respuesta API puede ser:
  - `[...]` (lista) o
  - `{ "results": [...] }` (paginación DRF)
  → el JS normaliza con `normalizeList()`

### Categorías (Front)
- Tabla renderiza `name/description/created_at`
- Edit/Delete usan `category_id` (no `id`)

### Productos (Front)
- Tabla renderiza:
  - miniatura con `image_url` + fallback (`onerror`)
  - `name`, `sku`, `category_name`, `unit_price`, `stock_qty`, `is_active`
- Form incluye:
  - dropdown de categorías cargado desde `/api/catalog/categories/`
  - input `imageUrl` para `image_url`

---

## Debug checklist (errores comunes)

- `column "id" does not exist`:
  - Estás usando PK incorrecta → usar `category_id/product_id`
- `null value violates not-null constraint (created_at/updated_at)`:
  - DB no tiene defaults o Django manda null → setear timestamps en serializer
- Front “no muestra nada”:
  - el JS está leyendo `id` en vez de `category_id/product_id`
  - la API devuelve `{results:[]}` y el JS esperaba `[]` → normalizar respuesta
  - revisar consola: `RAW ... response`
