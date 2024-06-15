from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin

from cuentas.forms import SolicitudForm
from .models import Cliente, Cuenta, Solicitud, Autorizante, Autorizacion,MovimientoCuenta
from django.urls import reverse
from django.utils.html import format_html
from django.utils import timezone
from django.contrib import messages

# Inline
class MovimientoCuentaInline(admin.TabularInline):
    model = MovimientoCuenta
    extra = 0
    can_delete=False
    readonly_fields = ('descripcion','total',)
    exclude = ('importe',)
    
    def total(self,obj):
        return f'{obj.importe:,.2f}'

    def has_add_permission(self, request, obj=None):
        return False  # Desactivar la capacidad de añadir nuevas ventas desde el admin de Cliente

    def has_change_permission(self, request, obj=None):
        return False  # Desactivar la capacidad de editar ventas desde el admin de Cliente

    def has_delete_permission(self, request, obj=None):
        return False  # Desactivar la capacidad de eliminar ventas desde el admin de Cliente


# Define resources for import/export functionality
class ClienteResource(resources.ModelResource):
    class Meta:
        model = Cliente


class CuentaResource(resources.ModelResource):
    class Meta:
        model = Cuenta

class SolicitudResource(resources.ModelResource):
    class Meta:
        model = Solicitud


class AutorizanteResource(resources.ModelResource):
    class Meta:
        model = Autorizante


class AutorizacionResource(resources.ModelResource):
    class Meta:
        model = Autorizacion


# Admin configurations
@admin.register(Cliente)
class ClienteAdmin(ImportExportModelAdmin):
    resource_class = ClienteResource
    list_display = ('codigo', 'nombre', 'telefono', 'habilitar')
    list_filter = ('habilitar',)
    search_fields = ('codigo', 'nombre')


@admin.register(Cuenta)
class CuentaAdmin(ImportExportModelAdmin):
    resource_class = CuentaResource
    list_display = ('cliente', 'nombre', 'saldo_actual')
    list_filter = ('cliente',)
    search_fields = ('nombre', 'cliente__nombre')
    inlines = [MovimientoCuentaInline,]

    def saldo_actual(self, obj):
        return f'$ {obj.calcular_saldo_actual():,.2f}'


@admin.register(Solicitud)
class SolicitudAdmin(ImportExportModelAdmin):
    resource_class = SolicitudResource
    list_display = ('fecha', 'solicitante', 'cuenta', 'importe_solicitado', 'saldo_cuenta', 'estado', 'verificacion_saldo')
    exclude = ('fecha','estado',)
    form = SolicitudForm
    list_filter = ('estado', 'fecha', 'solicitante', 'cuenta')
    search_fields = ('solicitante__nombre', 'cuenta__nombre')
    date_hierarchy = 'fecha'
    change_form_template = 'admin/solicitud_change_form.html'

    def importe_solicitado(self, obj):
        return f'$ {obj.importe:,.2f}'

    def saldo_cuenta(self, obj):
        return f'$ {obj.cuenta.calcular_saldo_actual():,.2f}'

    def verificacion_saldo(self, obj):
        saldo_actual = obj.cuenta.calcular_saldo_actual()
        if saldo_actual >= obj.importe:
            return format_html('<span style="color: green;">&#x2705;</span>')
        else:
            return format_html('<span style="color: red;">&#x274C;</span>')


@admin.register(Autorizante)
class AutorizanteAdmin(ImportExportModelAdmin):
    resource_class = AutorizanteResource
    list_display = ('usuario', 'nivel')
    list_filter = ('nivel',)
    search_fields = ('usuario__username', 'usuario__email')



def aprobar_solicitudes(modeladmin, request, queryset):
    aprobadas = 0
    for autorizacion in queryset:
        if not autorizacion.aprobado:
            autorizacion.aprobado = True
            autorizacion.aprobado_por = request.user
            autorizacion.aprobado_el = timezone.now()
            autorizacion.save()
            aprobadas += 1
            
            # Verificar si todas las autorizaciones de la solicitud están aprobadas
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


    messages.success(request, f"{aprobadas} autorizaciones han sido aprobadas.")

aprobar_solicitudes.short_description = "Aprobar solicitudes seleccionadas"


@admin.register(Autorizacion)
class AutorizacionAdmin(ImportExportModelAdmin):
    resource_class = AutorizacionResource
    list_display = ('fecha', 'solicitud', 'autorizante', 'total', 'Estado',)
    readonly_fields = ('fecha','aprobado','aprobado_por','aprobado_el',)
    list_filter = ('aprobado','autorizante')
    search_fields = ('solicitud__solicitante__nombre', 'autorizante__usuario__username')
    date_hierarchy = 'fecha'
    actions = [aprobar_solicitudes]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(aprobado=False).distinct()

 
    def total(self,obj):
        return f'$ {obj.solicitud.importe:,.2f}'
    
    def Estado(self, obj):
        if obj.aprobado == False:
            return format_html('<a class="btn btn-danger" href="{}">Autorizar Solicitud', reverse('Autorizacion_solicitud', args=[obj.id]))
        else:
            aprobado_el_formateado = obj.aprobado_el.strftime("%d/%m - %H:%M")
            return f'Autorizó {obj.aprobado_por} el {aprobado_el_formateado}'

