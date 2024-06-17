from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone

from cuentas.forms import DashboardForm
from .models import Autorizacion, Cliente, MovimientoCuenta, Solicitud,Cuenta
from django.contrib import messages
from django.db import transaction
from django.db.models import Sum,Count
from django.contrib.admin.sites import site
from django import forms
from datetime import timedelta
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse 
from django.http import HttpResponse

def mostrar_hora_actual(request):
    hora_actual = timezone.now()
    return HttpResponse(f"La hora actual es: {hora_actual}")

def cargar_cuentas(request):
    cliente_id = request.GET.get('cliente')
    cuentas = Cuenta.objects.filter(cliente_id=cliente_id).order_by('nombre')
    cuentas_list = [{'id': cuenta.id, 'nombre': cuenta.nombre, 'saldo': cuenta.calcular_saldo_actual()} for cuenta in cuentas]
    return JsonResponse(cuentas_list, safe=False)

def Autorizacion_solicitud(request, id_autorizacion):
    try:
        # Iniciar una transacción para asegurar que todas las operaciones se completen o se reviertan en caso de error
        with transaction.atomic():
            autorizacion = get_object_or_404(Autorizacion.objects.select_related('solicitud'), id=id_autorizacion)

            if not autorizacion.aprobado:
                autorizacion.aprobado = True
                autorizacion.aprobado_por = request.user
                autorizacion.aprobado_el = timezone.now()
                autorizacion.save()

                autorizaciones_pendientes = Autorizacion.objects.filter(solicitud=autorizacion.solicitud, aprobado=False).count()

                if autorizaciones_pendientes == 0:


                    solicitud = autorizacion.solicitud
                    solicitud.estado = True
                    solicitud.save()
                    

                    # Crear un movimiento de cuenta
                    importe = - 1 * solicitud.importe
                    movimiento = MovimientoCuenta.objects.create(
                        cuenta=solicitud.cuenta,
                        descripcion=f'Solicitud de extracción de {solicitud.solicitante.nombre} por {solicitud.importe:,.2f}.',
                        importe=importe
                    )
                    movimiento.save()

                messages.success(request, "El pago se confirmó correctamente.")
            else:
                messages.warning(request, "El pago ya estaba confirmado.")

    except Exception as e:
        messages.error(request, f"Ha ocurrido un error al confirmar el pago: {str(e)}")

    return redirect('admin:cuentas_autorizacion_changelist')



@login_required(login_url='/admin/login/')
def dashboard(request):

    today = timezone.now().date()
    
    # Inicializar el formulario con las fechas por defecto
    initial_data = {
        'start_date': today,
        'end_date': today,
    }
    
    form = DashboardForm(request.GET or None, initial=initial_data)
    start_date = form['start_date'].value() or today
    end_date = form['end_date'].value() or today
    cliente = form['cliente'].value()

    solicitudes = Solicitud.objects.all()
    if cliente:
        solicitudes = solicitudes.filter(solicitante_id=cliente)
    if start_date:
        solicitudes = solicitudes.filter(fecha__date__gte=start_date)
    if end_date:
        solicitudes = solicitudes.filter(fecha__date__lte=end_date)

    total_solicitado = solicitudes.aggregate(total=Sum('importe'))['total'] or 0
    total_pendiente = solicitudes.filter(autorizaciones__aprobado=False).aggregate(total=Sum('importe'))['total'] or 0

    firmantes_data = []
    for nivel in range(1, 4):
        firmantes_data.append(
            solicitudes.filter(autorizaciones__autorizante__nivel=nivel, autorizaciones__aprobado=False).distinct().count()
        )

    # Obtener los IDs únicos de los solicitantes y luego sus nombres
    solicitantes_ids = solicitudes.values_list('solicitante_id', flat=True).distinct()
    solicitantes = Cliente.objects.filter(id__in=solicitantes_ids)
    
    chart1_data = {
        'labels': [solicitante.nombre for solicitante in solicitantes],
        'data': [solicitudes.filter(solicitante=solicitante).aggregate(total=Sum('importe'))['total'] for solicitante in solicitantes]
    }

    # Obtener firmas pendientes por usuario
    firmas_pendientes = Autorizacion.objects.filter(aprobado=False).values('autorizante__usuario__username').annotate(total=Count('id')).order_by('-total')

    # Datos para el gráfico de los últimos 30 días
    today = timezone.now().date()
    last_30_days = [today - timedelta(days=i) for i in range(30)]
    chart2_labels = [day.strftime('%Y-%m-%d') for day in last_30_days]
    chart2_data = [solicitudes.filter(fecha__date=day).aggregate(total=Sum('importe'))['total'] or 0 for day in last_30_days]

    context = {
        'form': form,
        'total_solicitado': total_solicitado,
        'total_pendiente': total_pendiente,
        'firmantes_data': firmantes_data,
        'chart1_data': chart1_data,
        'firmas_pendientes': firmas_pendientes,
        'chart2_data': {
            'labels': chart2_labels,
            'data': chart2_data
        },
        'title': 'Dashboard',
        'available_apps': site.get_app_list(request),
    }
    return render(request, 'admin/dashboard.html', context)



