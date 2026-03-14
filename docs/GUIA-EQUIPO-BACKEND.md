# 🚀 Guía Rápida - Setup del Backend

## ⚡ Configuración Inicial (Solo la primera vez)

### 1️⃣ Verificar que tienes Python instalado

Abre PowerShell o CMD y ejecuta:
```powershell
python --version
```

Deberías ver algo como: `Python 3.10.x` o superior

❌ **Si no está instalado:**
- Descargar de: https://www.python.org/downloads/
- ✅ Durante la instalación: Marcar **"Add Python to PATH"**

---

### 2️⃣ Clonar el repositorio

```powershell
git clone <URL-DEL-REPO>
cd G1_LubricentroWeb
```

---

### 3️⃣ Configurar el Backend

```powershell
# Ir a la carpeta backend
cd backend

# Crear entorno virtual
source venv/bin/activate

# Activar entorno virtual
venv\Scripts\activate
```

Deberías ver `(venv)` al inicio de tu terminal:
```
(venv) PS C:\...\backend>
```

---

### 4️⃣ Instalar dependencias

```powershell
# Actualizar pip
python -m pip install --upgrade pip

# Instalar todo lo necesario
pip install -r requirements.txt
```

Esto tomará 1-2 minutos. Verás que se instalan Django, REST Framework, etc.

---

### 5️⃣ Configurar variables de entorno

```powershell
# Copiar el archivo de ejemplo
copy .env.example .env
```

**⚠️ IMPORTANTE:** Pedir al líder del equipo el archivo `.env` real con las credenciales de Supabase.

Si ya te lo compartieron, reemplaza el archivo `.env` con el que te dieron.

---

### 6️⃣ Verificar que todo funciona

```powershell
# Probar la conexión a la base de datos
python test_connection.py
```

Deberías ver:
```
✅ Conexión exitosa a Supabase!
PostgreSQL version: ...
📋 Tablas disponibles:
  - customers
  - vehicles
  - ...
```

---

## 🏃‍♂️ Uso Diario (Cada vez que trabajes)

### Iniciar el servidor backend

```powershell
# 1. Ir a la carpeta backend
cd backend

# 2. Activar entorno virtual
venv\Scripts\activate

# 3. Iniciar servidor
python manage.py runserver
```

Verás algo como:
```
Starting development server at http://127.0.0.1:8000/
Quit the server with CTRL-BREAK.
```

✅ **El backend está corriendo!** Déjalo así mientras trabajas.

**Acceder al Admin:** http://localhost:8000/admin

---

### Para detener el servidor

Presiona `Ctrl + C` en la terminal

---

### Para desactivar el entorno virtual

```powershell
deactivate
```

---

## 🔧 Comandos Útiles

### Si alguien actualiza el código

```powershell
# Actualizar desde GitHub
git pull

# Activar venv
venv\Scripts\activate

# Instalar nuevas dependencias (si hay)
pip install -r requirements.txt

# Aplicar nuevas migraciones (si hay)
python manage.py migrate
```

---

### Verificar configuración

```powershell
python manage.py check
```

Si todo está bien, verás:
```
System check identified no issues (0 silenced).
```

---

## ❓ Solución de Problemas

### Error: "python no se reconoce como comando"
- Python no está instalado o no está en PATH
- Reinstalar Python y marcar "Add to PATH"

### Error: "No module named 'django'"
- El entorno virtual no está activado
- Ejecutar: `venv\Scripts\activate`
- Instalar dependencias: `pip install -r requirements.txt`

### Error: "Permission denied" al activar venv (Windows)
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```
Luego intentar activar de nuevo: `venv\Scripts\activate`

### Error de conexión a base de datos
- Verificar que el archivo `.env` tiene las credenciales correctas
- Pedir el `.env` actualizado al líder del equipo

### El servidor no se detiene con Ctrl+C
- Intentar: `Ctrl + Break`
- O cerrar la terminal directamente

---

## 📁 Estructura del Proyecto

```
G1_LubricentroWeb/
├── backend/              ← Aquí trabajas
│   ├── venv/            ← Entorno virtual (NO tocar)
│   ├── config/          ← Configuración Django
│   ├── apps/            ← Aplicaciones (modelos, vistas, etc)
│   ├── manage.py        ← Comandos Django
│   ├── requirements.txt ← Dependencias
│   ├── .env            ← Credenciales (NO SUBIR A GIT)
│   └── .env.example    ← Plantilla de credenciales
└── frontend/            ← Para el equipo de frontend
```

---

## ⚠️ Reglas Importantes

### ✅ HACER:
- Activar el venv antes de trabajar
- Hacer `git pull` antes de empezar
- Pedir el archivo `.env` al líder

### ❌ NO HACER:
- ❌ **NUNCA** subir el archivo `.env` a GitHub
- ❌ **NUNCA** modificar `venv/` manualmente
- ❌ **NUNCA** borrar `venv/` sin avisar (tendrás que reinstalar todo)
- ❌ **NUNCA** compartir credenciales públicamente

---

## 🆘 Contacto

Si tienes problemas:
1. Revisar esta guía de nuevo
2. Buscar el error en Google
3. Preguntar en el grupo de WhatsApp/Discord
4. Contactar al líder del equipo

---

## ✅ Checklist de Primera Vez

- [ ] Python instalado
- [ ] Repositorio clonado
- [ ] Entorno virtual creado (`venv/`)
- [ ] Entorno virtual activado (ves `(venv)`)
- [ ] Dependencias instaladas (`pip install -r requirements.txt`)
- [ ] Archivo `.env` configurado
- [ ] Conexión probada (`python test_connection.py`)
- [ ] Servidor corriendo (`python manage.py runserver`)
- [ ] Admin accesible (http://localhost:8000/admin)

---

**¡Listo para desarrollar!** 🎉
