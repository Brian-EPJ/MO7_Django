from decimal import Decimal

from django.contrib.auth.models import User
from django.db import IntegrityError, transaction
from django.test import TestCase
from django.urls import reverse

from . import consultas
from .models import Cliente, Cuenta, Etiqueta, Transaccion


class DatosBase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user('tester', password='clave-test-123')
        cls.ana = Cliente.objects.create(nombre='Ana García', email='ana@example.com', telefono='123456789')
        cls.luis = Cliente.objects.create(nombre='Luis Pérez', email='luis@example.com')
        cls.cuenta_ana = Cuenta.objects.create(cliente=cls.ana, numero_cuenta='001', saldo=Decimal('800'))
        cls.cuenta_luis = Cuenta.objects.create(cliente=cls.luis, numero_cuenta='002', saldo=Decimal('50'))
        Transaccion.objects.create(cuenta=cls.cuenta_ana, tipo='DEPOSITO', monto=Decimal('1000'))
        Transaccion.objects.create(cuenta=cls.cuenta_ana, tipo='RETIRO', monto=Decimal('200'))

    def setUp(self):
        self.client.login(username='tester', password='clave-test-123')


class ModelosTests(DatosBase):
    def test_email_unico(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            Cliente.objects.create(nombre='Otra', email='ana@example.com')

    def test_cuenta_uno_a_uno(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            Cuenta.objects.create(cliente=self.ana, numero_cuenta='999')

    def test_etiquetas_muchos_a_muchos(self):
        vip = Etiqueta.objects.create(nombre='VIP')
        self.cuenta_ana.etiquetas.add(vip)
        self.assertEqual(list(vip.cuenta.all()), [self.cuenta_ana])

    def test_str(self):
        self.assertEqual(str(self.ana), 'Ana García')


class ConsultasTests(DatosBase):
    def test_resumen_cuentas_annotate(self):
        c = consultas.resumen_cuentas().get(pk=self.cuenta_ana.pk)
        self.assertEqual(c.total_depositos, Decimal('1000'))
        self.assertEqual(c.total_egresos, Decimal('200'))
        self.assertEqual(c.num_transacciones, 2)

    def test_cuentas_sin_movimientos(self):
        self.assertEqual(list(consultas.cuentas_sin_movimientos()), [self.cuenta_luis])

    def test_clientes_con_y_sin_telefono(self):
        self.assertEqual(list(consultas.clientes_con_telefono()), [self.ana])
        self.assertEqual(list(consultas.clientes_sin_telefono()), [self.luis])

    def test_raw_saldo_mayor_a(self):
        res = consultas.cuentas_con_saldo_mayor_a(Decimal('100'))
        self.assertEqual([c.numero_cuenta for c in res], ['001'])
        self.assertEqual(res[0].cliente_nombre, 'Ana García')

    def test_cursor_totales_por_tipo(self):
        totales = {t['tipo']: t for t in consultas.totales_por_tipo()}
        self.assertEqual(totales['DEPOSITO']['cantidad'], 1)
        self.assertEqual(Decimal(str(totales['RETIRO']['total'])), Decimal('200'))


class CrudClienteTests(DatosBase):
    def test_requiere_login(self):
        self.client.logout()
        r = self.client.get(reverse('cliente_list'))
        self.assertEqual(r.status_code, 302)
        self.assertIn('/accounts/login/', r.url)

    def test_listar(self):
        self.assertContains(self.client.get(reverse('cliente_list')), 'Ana García')

    def test_crear(self):
        r = self.client.post(reverse('cliente_create'), {'nombre': 'Eva', 'email': 'eva@example.com'})
        self.assertRedirects(r, reverse('cliente_list'))
        self.assertTrue(Cliente.objects.filter(email='eva@example.com').exists())

    def test_actualizar(self):
        self.client.post(reverse('cliente_update', args=[self.luis.pk]),
                         {'nombre': 'Luis P.', 'email': 'luis@example.com', 'telefono': '987'})
        self.luis.refresh_from_db()
        self.assertEqual(self.luis.telefono, '987')

    def test_eliminar(self):
        self.client.post(reverse('cliente_delete', args=[self.luis.pk]))
        self.assertFalse(Cliente.objects.filter(pk=self.luis.pk).exists())


class CuentasYTransaccionesTests(DatosBase):
    def test_crear_cuenta(self):
        eva = Cliente.objects.create(nombre='Eva', email='eva@example.com')
        r = self.client.post(reverse('cuenta_create'), {'cliente': eva.pk, 'numero_cuenta': '003'})
        self.assertRedirects(r, reverse('cuenta_list'))
        self.assertEqual(Cuenta.objects.get(numero_cuenta='003').saldo, 0)

    def test_deposito_aumenta_saldo(self):
        self.client.post(reverse('transaccion_create'), {'cuenta': self.cuenta_luis.pk, 'tipo': 'DEPOSITO', 'monto': '100'})
        self.cuenta_luis.refresh_from_db()
        self.assertEqual(self.cuenta_luis.saldo, Decimal('150'))

    def test_retiro_disminuye_saldo(self):
        self.client.post(reverse('transaccion_create'), {'cuenta': self.cuenta_luis.pk, 'tipo': 'RETIRO', 'monto': '30'})
        self.cuenta_luis.refresh_from_db()
        self.assertEqual(self.cuenta_luis.saldo, Decimal('20'))

    def test_retiro_con_saldo_insuficiente_se_rechaza(self):
        r = self.client.post(reverse('transaccion_create'), {'cuenta': self.cuenta_luis.pk, 'tipo': 'RETIRO', 'monto': '500'})
        self.assertContains(r, 'Saldo insuficiente')
        self.cuenta_luis.refresh_from_db()
        self.assertEqual(self.cuenta_luis.saldo, Decimal('50'))
        self.assertEqual(self.cuenta_luis.transacciones.count(), 0)

    def test_monto_debe_ser_positivo(self):
        r = self.client.post(reverse('transaccion_create'), {'cuenta': self.cuenta_luis.pk, 'tipo': 'DEPOSITO', 'monto': '-5'})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(self.cuenta_luis.transacciones.count(), 0)

    def test_detalle_y_listados(self):
        for name, args in [('cuenta_list', []), ('cuenta_detail', [self.cuenta_ana.pk]),
                           ('transaccion_list', []), ('reportes', [])]:
            self.assertEqual(self.client.get(reverse(name, args=args)).status_code, 200, name)


class AutenticacionTests(TestCase):
    def test_registro_crea_usuario(self):
        r = self.client.post(reverse('registro'), {'username': 'nuevo', 'password1': 'Clave-Segura-9731', 'password2': 'Clave-Segura-9731'})
        self.assertRedirects(r, reverse('login'))
        self.assertTrue(User.objects.filter(username='nuevo').exists())

    def test_login_y_logout(self):
        User.objects.create_user('u', password='clave-test-123')
        r = self.client.post(reverse('login'), {'username': 'u', 'password': 'clave-test-123'})
        self.assertRedirects(r, reverse('cliente_list'), fetch_redirect_response=False)
        r = self.client.post(reverse('logout'))
        self.assertRedirects(r, reverse('login'))
