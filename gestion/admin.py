from django.contrib import admin
from .models import Cliente, Etiqueta, Transaccion, Cuenta

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = (
        'nombre',
        'email',
        'telefono',
        'fecha_registro'
    )
    
    search_fields = (
        'nombre',
        'email',
        'telefono'
    )
    
@admin.register(Etiqueta)
class EtiquetaAdmin(admin.ModelAdmin):
    list_display = (
        'nombre',
    )
    
    search_fields = (
        'nombre',
    )
    
@admin.register(Cuenta)
class CuentaAdmin(admin.ModelAdmin):
    list_display = (
        'cliente',
        'numero_cuenta',
        'saldo',
        'fecha_creacion'
    )
    
    search_fields = (
        'cliente__nombre',
        'numero_cuenta'
    )
    
@admin.register(Transaccion)
class TransaccionAdmin(admin.ModelAdmin):
    list_display = (
        'cuenta',
        'tipo',
        'monto',
        'fecha',
        'descripcion'
    )
    
    search_fields = (
        'cuenta__numero_cuenta',
        'tipo',
        'descripcion'
    )