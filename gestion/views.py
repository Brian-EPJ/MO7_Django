from django.shortcuts import redirect
from django.contrib import messages
from django.db import transaction
from django.contrib.auth.mixins import LoginRequiredMixin
from decimal import Decimal, InvalidOperation
from django.views.generic import TemplateView, ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy
from .models import Cliente, Cuenta, Transaccion
from . import consultas
from .forms import ClienteForm, CuentaForm, TransaccionForm, RegistroForm

class ClienteListView(LoginRequiredMixin, ListView):
    model = Cliente
    template_name = 'gestion/cliente_list.html'
    context_object_name = 'clientes'
    
class ClienteCreateView(LoginRequiredMixin, CreateView):
    model = Cliente
    form_class = ClienteForm
    template_name = 'gestion/cliente_form.html'
    success_url = reverse_lazy('cliente_list')
    
class ClienteUpdateView(LoginRequiredMixin, UpdateView):
    model = Cliente
    form_class =  ClienteForm
    template_name = 'gestion/cliente_form.html'
    success_url = reverse_lazy('cliente_list')
    
class ClienteDeleteView(LoginRequiredMixin, DeleteView):
    model = Cliente
    template_name = 'gestion/cliente_confirm_delete.html'
    success_url = reverse_lazy('cliente_list')


class RegistroView(CreateView):
    form_class = RegistroForm
    template_name = 'registration/register.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        messages.success(self.request, 'Cuenta de usuario creada. Ya puedes iniciar sesion.')
        return super().form_valid(form)


class CuentaListView(LoginRequiredMixin, ListView):
    model = Cuenta
    template_name = 'gestion/cuenta_list.html'
    context_object_name = 'cuentas'

    def get_queryset(self):
        return Cuenta.objects.select_related('cliente').prefetch_related('etiquetas')


class CuentaDetailView(LoginRequiredMixin, DetailView):
    model = Cuenta
    template_name = 'gestion/cuenta_detail.html'
    context_object_name = 'cuenta'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['transacciones'] = self.object.transacciones.order_by('-fecha')
        return context


class CuentaCreateView(LoginRequiredMixin, CreateView):
    model = Cuenta
    form_class = CuentaForm
    template_name = 'gestion/cuenta_form.html'
    success_url = reverse_lazy('cuenta_list')


class CuentaUpdateView(LoginRequiredMixin, UpdateView):
    model = Cuenta
    form_class = CuentaForm
    template_name = 'gestion/cuenta_form.html'
    success_url = reverse_lazy('cuenta_list')


class CuentaDeleteView(LoginRequiredMixin, DeleteView):
    model = Cuenta
    template_name = 'gestion/cuenta_confirm_delete.html'
    success_url = reverse_lazy('cuenta_list')


class TransaccionListView(LoginRequiredMixin, ListView):
    model = Transaccion
    template_name = 'gestion/transaccion_list.html'
    context_object_name = 'transacciones'

    def get_queryset(self):
        return Transaccion.objects.select_related('cuenta__cliente').order_by('-fecha')


class TransaccionCreateView(LoginRequiredMixin, CreateView):
    model = Transaccion
    form_class = TransaccionForm
    template_name = 'gestion/transaccion_form.html'
    success_url = reverse_lazy('transaccion_list')

    def get_initial(self):
        initial = super().get_initial()
        if self.request.GET.get('cuenta'):
            initial['cuenta'] = self.request.GET['cuenta']
        return initial

    def form_valid(self, form):
        tipo = form.cleaned_data['tipo']
        monto = form.cleaned_data['monto']
        with transaction.atomic():
            cuenta = Cuenta.objects.select_for_update().get(pk=form.cleaned_data['cuenta'].pk)
            if tipo == 'DEPOSITO':
                cuenta.saldo += monto
            else:
                if cuenta.saldo < monto:
                    form.add_error('monto', 'Saldo insuficiente en la cuenta.')
                    return self.form_invalid(form)
                cuenta.saldo -= monto
            cuenta.save(update_fields=['saldo'])
            self.object = form.save()
        messages.success(self.request, 'Transaccion registrada.')
        return redirect(self.get_success_url())


class ReporteView(LoginRequiredMixin, TemplateView):
    template_name = 'gestion/reportes.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            minimo = Decimal(self.request.GET.get('saldo_minimo', '0'))
        except InvalidOperation:
            minimo = Decimal('0')
        context.update({
            'saldo_minimo': minimo,
            'resumen': consultas.resumen_cuentas(),
            'cuentas_saldo': consultas.cuentas_con_saldo_mayor_a(minimo),
            'sin_movimientos': consultas.cuentas_sin_movimientos(),
            'sin_telefono': consultas.clientes_sin_telefono(),
            'totales_tipo': consultas.totales_por_tipo(),
        })
        return context
