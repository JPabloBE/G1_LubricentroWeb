# LubricentroWeb

Sistema web para un lubricentro: gestión de clientes, vehículos, citas, órdenes de trabajo, catálogo de productos/servicios y caja.

## Stack

- **Backend**: Django 5 + Django REST Framework + JWT (simplejwt)
- **Frontend**: HTML/CSS/JS vanilla + Bootstrap 5.3.3 + Bootstrap Icons 1.11.3 (sin framework JS)
- **Base de datos**: PostgreSQL en Supabase — schema `django_app`, search_path `django_app,public`
- **Auth**: JWT con `Authorization: Bearer <token>`

## Estructura

```
backend/
  config/           # settings.py, urls.py
  apps/
    authentication/ # Usuarios staff/admin — JWT login
    customers/      # Clientes — auth separada
    catalog/        # Productos y categorías
    services/       # Servicios del lubricentro
    vehicles/       # Vehículos de clientes
    appointments/   # Citas
    work_orders/    # Órdenes de trabajo
    cash_register/  # Módulo de caja (sesiones, movimientos, cierres)
frontend/
  admin/            # Panel administrador (HTML/JS)
  client/           # Portal cliente (HTML/JS)
sql/                # Scripts SQL de referencia (tablas en Supabase)
```

## Autenticación — dos flujos distintos

| Actor | App | Endpoint base |
|-------|-----|---------------|
| Staff / Admin | `apps.authentication` | `api/auth/` |
| Clientes | `apps.customers` | `api/` |

No mezclar los dos sistemas de auth.

## Reglas críticas

- **No crear ni borrar tablas en Supabase.** Todos los modelos usan `managed = False`. No cambiar ese flag ni correr `migrate`.
- **No romper funcionalidad existente.** Cambios deben ser aditivos o compatibles hacia atrás.
- **No subir secretos.** Credenciales solo en `backend/.env` y `.mcp.json` (ambos en `.gitignore`).
- **Contraseña Supabase**: no se puede cambiar vía MCP ni SQL (requiere superusuario). Ignorar ese paso — el `.env` no está en git y no es un riesgo.
- **managed=False + DRF FKs**: declarar FKs explícitas con `PrimaryKeyRelatedField(source=...)` para evitar errores de null.
- Después de `save()` sobre un objeto con `prefetch_related`, re-fetch para invalidar caché: `obj = Model.objects.prefetch_related(...).get(pk=obj.pk)`.
- **Esquemas en SQL raw**: todas las tablas de dominio (`work_orders`, `customers`, `vehicles`, `appointments`, `services`, `products`) están en schema `public`. Solo `auth_users` está en `django_app`. Usar siempre `public.tabla` y `django_app.auth_users` explícitamente.
- **Nombre de cliente**: `customers.full_name` (campo único de texto). No tiene `first_name` ni `last_name`.
- **authorization_status** en `work_orders`: valores válidos son `pending`, `approved`, `rejected` (el constraint de la DB rechaza `authorized`).

## Comandos de desarrollo

```bash
source venv/bin/activate
cd backend && python manage.py runserver   # → http://127.0.0.1:8000
python manage.py check
```

## URLs de la API

- `api/auth/` — login, refresh, me, logout (staff)
- `api/catalog/`, `api/services/`, `api/customers/`, `api/vehicles/`
- `api/appointments/` — citas; `POST {id}/confirm/` crea OT y retorna `work_order_id`
- `api/work-orders/` — OTs; `GET /dashboard_metrics/` retorna KPIs del dashboard; `GET /report/` acepta `date_from`, `date_to`, `status`, `mechanic_id`, `export=excel`
- `api/cash/sessions/` — sesiones; `/active/`, `/{id}/close/`, `/{id}/force-close/`, `/{id}/intermediate-check/`, `/work-orders-summary/`
- `api/cash/movements/` — movimientos (`movement_type: "sale"` para venta rápida)

## CORS habilitado para

`localhost:3000`, `localhost:5500`, `localhost:5501`

## Páginas admin destacadas

| Página | Contenido |
|--------|-----------|
| `dashboard_catalog.html` | Tabs: Productos · Servicios · Categorías. Historial unificado (changelog + movimientos de stock) en offcanvas. |
| `dashboard_staff_users.html` | Tabs: Staff/Admin · Clientes · Reporte. Gestiona ambos tipos de usuario y genera reporte exportable a Excel. |
| `dashboard_inventory_report.html` | Reporte de inventario con filtros y exportación Excel. |
| `dashboard_work_orders_report.html` | Reporte de OTs con filtros por fecha, estado y técnico. Exportación Excel vía backend (openpyxl). |
| `dashboard_appointment_report.html` | Reporte de citas con filtros por fecha, estado y servicio. Exportación Excel vía backend (openpyxl). |

## Convenciones frontend (admin)

- **Acciones en tabla**: botón `[ ✏ Editar ] [ ⋮ ]` — primario para editar, kebab dropdown para secundarias/destructivas.
- **Dropdown en tablas**: añadir `.table-responsive:has(.dropdown-menu.show) { overflow: visible !important; }` para que el menú no quede cortado.
- **Tabs**: usar `data-bs-toggle="tab"` con `shown.bs.tab` para carga lazy del contenido.
- **JS en páginas admin**: poner TODA la lógica ejecutable (Bootstrap inits, addEventListener) dentro de una función `setup()` llamada al final — evita crashes silenciosos si algún elemento aún no existe.
- **Sidebar**: el ítem "Usuarios" apunta a `dashboard_staff_users.html` (unifica staff + clientes). No agregar entradas separadas para cada uno.
- **Navegación cross-page (admin)**: pasar `?highlight=<id>` — resalta la fila Y llama `openDetail(id)` para abrir el modal automáticamente. Usar `CSS.escape()` al seleccionar el elemento.
- **Navegación cross-page (cliente)**: pasar `?open=<id>` en `work_orders.html` — expande el collapse de esa OT automáticamente.
- **CSS sobre Bootstrap**: usar `!important` en `@keyframes` para override de `table-hover`.

## Auth cliente

- Token: `CustomerJWTAuthentication` con `token_type: "customer"` (payload custom, NO simplejwt).
- Almacenado como `customer_access_token` en localStorage. Expira en 12h.
- Si un endpoint cliente da **403**: el token expiró o es inválido → cerrar sesión y volver a entrar en el portal cliente.
- **No mezclar** con el token admin (`access_token` / simplejwt).
