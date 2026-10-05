"""Consultas personalizadas de Alke Wallet: ORM (filter/exclude/annotate), raw() y cursores."""
from decimal import Decimal

from django.db import connection
from django.db.models import Count, Q, Sum, Value
from django.db.models.functions import Coalesce

from .models import Cliente, Cuenta

CERO = Value(Decimal('0'))


def resumen_cuentas():
    """ORM + annotate: depositos, egresos y cantidad de movimientos por cuenta."""
    return (
        Cuenta.objects.select_related('cliente')
        .annotate(
            total_depositos=Coalesce(
                Sum('transacciones__monto', filter=Q(transacciones__tipo='DEPOSITO')), CERO),
            total_egresos=Coalesce(
                Sum('transacciones__monto', filter=Q(transacciones__tipo__in=['RETIRO', 'TRANSFERENCIA'])), CERO),
            num_transacciones=Count('transacciones'),
        )
        .order_by('-saldo')
    )


def clientes_con_telefono():
    """ORM + exclude: clientes que si registraron telefono."""
    return Cliente.objects.exclude(Q(telefono__isnull=True) | Q(telefono=''))


def clientes_sin_telefono():
    """ORM + filter con Q."""
    return Cliente.objects.filter(Q(telefono__isnull=True) | Q(telefono=''))


def cuentas_sin_movimientos():
    """ORM + annotate + filter sobre el agregado."""
    return Cuenta.objects.select_related('cliente').annotate(n=Count('transacciones')).filter(n=0)


def cuentas_con_saldo_mayor_a(minimo):
    """SQL personalizado con raw(); el valor va parametrizado (evita SQL injection)."""
    sql = """
        SELECT c.id, c.numero_cuenta, c.saldo, cl.nombre AS cliente_nombre
        FROM gestion_cuenta c
        INNER JOIN gestion_cliente cl ON cl.id = c.cliente_id
        WHERE c.saldo > %s
        ORDER BY c.saldo DESC
    """
    return list(Cuenta.objects.raw(sql, [minimo]))


def totales_por_tipo():
    """SQL directo con cursor: cantidad y monto total por tipo de transaccion."""
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT tipo, COUNT(*), COALESCE(SUM(monto), 0) "
            "FROM gestion_transaccion GROUP BY tipo ORDER BY tipo"
        )
        return [{'tipo': t, 'cantidad': c, 'total': m} for t, c, m in cursor.fetchall()]
