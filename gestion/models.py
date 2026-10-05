from django.db import models

class Cliente(models.Model):
    nombre = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.nombre
    
class Etiqueta(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    
    def __str__(self):
        return self.nombre
    
class Cuenta(models.Model):
    cliente = models.OneToOneField(Cliente, on_delete=models.CASCADE, related_name='cuenta')
    numero_cuenta = models.CharField(max_length=20, unique=True)
    saldo = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    etiquetas = models.ManyToManyField(Etiqueta, blank=True, related_name='cuenta')
    
    def __str__(self):
        return f'Cuenta: {self.numero_cuenta} - Cliente: {self.cliente.nombre}'
    
class Transaccion(models.Model):
    TIPO_CHOICES = (
        ('DEPOSITO', 'Deposito'),
        ('RETIRO', 'Retiro'),
        ('TRANSFERENCIA', 'Transferencia'),
    )
    cuenta = models.ForeignKey(Cuenta, on_delete=models.CASCADE, related_name='transacciones')
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    monto = models.DecimalField(max_digits=12, decimal_places=2)
    fecha = models.DateTimeField(auto_now_add=True)
    descripcion = models.CharField(max_length=255, blank=True, null=True)
    
    def __str__(self):
        return f'{self.tipo} de ${self.monto} en cuenta {self.cuenta.numero_cuenta}'