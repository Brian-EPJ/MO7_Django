from django.urls import path
from .views import (
    ClienteListView,
    ClienteCreateView,
    ClienteUpdateView,
    ClienteDeleteView,
    RegistroView,
    CuentaListView,
    CuentaDetailView,
    CuentaCreateView,
    CuentaUpdateView,
    CuentaDeleteView,
    TransaccionListView,
    TransaccionCreateView,
    ReporteView,
)

urlpatterns = [
    path('clientes/', ClienteListView.as_view(), name='cliente_list'),
    path('clientes/nuevo/', ClienteCreateView.as_view(), name='cliente_create'),
    path('clientes/<int:pk>/editar/', ClienteUpdateView.as_view(), name='cliente_update'),
    path('clientes/<int:pk>/eliminar/', ClienteDeleteView.as_view(), name='cliente_delete'),
    path('registro/', RegistroView.as_view(), name='registro'),
    path('cuentas/', CuentaListView.as_view(), name='cuenta_list'),
    path('cuentas/nueva/', CuentaCreateView.as_view(), name='cuenta_create'),
    path('cuentas/<int:pk>/', CuentaDetailView.as_view(), name='cuenta_detail'),
    path('cuentas/<int:pk>/editar/', CuentaUpdateView.as_view(), name='cuenta_update'),
    path('cuentas/<int:pk>/eliminar/', CuentaDeleteView.as_view(), name='cuenta_delete'),
    path('transacciones/', TransaccionListView.as_view(), name='transaccion_list'),
    path('transacciones/nueva/', TransaccionCreateView.as_view(), name='transaccion_create'),
    path('reportes/', ReporteView.as_view(), name='reportes'),
]
