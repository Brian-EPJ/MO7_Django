# Alke Wallet — Módulo 7: Desarrollo Web con Django

Billetera digital para gestionar clientes, cuentas y transacciones, construida con Django (ORM, migraciones, vistas basadas en clases y apps preinstaladas).

## Arquitectura

```
alke_wallet/         Configuración del proyecto (settings.py, urls.py)
gestion/             App principal
  models.py          Cliente, Cuenta (1-1 con Cliente, M2M con Etiqueta), Etiqueta, Transaccion (N-1 con Cuenta)
  forms.py           ClienteForm, CuentaForm, TransaccionForm, RegistroForm, LoginForm
  views.py           CRUD con vistas basadas en clases + registro + reportes
  consultas.py       Consultas personalizadas (filter / exclude / annotate / raw() / cursor)
  admin.py           Modelos registrados en django.contrib.admin
  templates/         base.html, listados, formularios, confirmaciones, reportes, registration/
  static/gestion/    CSS y JS (django.contrib.staticfiles)
  migrations/        Historial versionado del esquema
  tests.py           Pruebas unitarias y de integración (22)
```

### Modelo de datos
| Relación | Implementación |
|---|---|
| Uno a Uno | `Cuenta.cliente` → `Cliente` |
| Muchos a Uno | `Transaccion.cuenta` → `Cuenta` |
| Muchos a Muchos | `Cuenta.etiquetas` ↔ `Etiqueta` |

### Reglas de negocio
- El saldo de una cuenta solo cambia mediante transacciones (dentro de `transaction.atomic()` con `select_for_update()`).
- Depósito suma; retiro y transferencia restan y se rechazan si el saldo es insuficiente.
- El monto debe ser mayor a 0.

## Base de datos
- **Desarrollo (por defecto):** SQLite, sin configuración (`db.sqlite3`).
- **Producción:** PostgreSQL con `psycopg2`. Define en `.env`: `DB_ENGINE=postgres`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT` (ver `.env.example`).

## Ejecutar localmente
```bash
python -m venv venv
venv\Scripts\activate          # Windows  (Linux/Mac: source venv/bin/activate)
pip install -r requirements.txt
cp .env.example .env           # opcional en desarrollo
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```
- App: http://127.0.0.1:8000/clientes/ (pide login) · Registro: `/registro/` · Admin: `/admin/`

## Rutas principales
`/clientes/` · `/cuentas/` · `/cuentas/<pk>/` · `/transacciones/` · `/transacciones/nueva/` · `/reportes/` · `/registro/` · `/accounts/login/`

## Consultas personalizadas (`gestion/consultas.py`)
| Función | Técnica |
|---|---|
| `resumen_cuentas()` | `annotate` + `Sum(filter=Q(...))` + `Count` |
| `clientes_con_telefono()` / `clientes_sin_telefono()` | `exclude` / `filter` con `Q` |
| `cuentas_sin_movimientos()` | `annotate` + `filter` sobre el agregado |
| `cuentas_con_saldo_mayor_a(minimo)` | SQL con `raw()` parametrizado |
| `totales_por_tipo()` | SQL con `connection.cursor()` |

Se visualizan en `/reportes/`.

## Seguridad
Formularios con `{% csrf_token %}`, vistas protegidas con `LoginRequiredMixin`, consultas SQL parametrizadas, secretos en variables de entorno (`.env` está en `.gitignore`).

## Pruebas
```bash
python manage.py test
```
Resultado: **22 pruebas, OK** (modelos y relaciones, consultas personalizadas, CRUD, autenticación/registro, lógica de saldos y reportes).

## Flujo Git sugerido
`main` (estable) · `feature/modelos` · `feature/crud`.
