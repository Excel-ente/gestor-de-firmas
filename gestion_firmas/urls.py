from django.contrib import admin
from django.urls import path
from cuentas.views import Autorizacion_solicitud,dashboard,cargar_cuentas,mostrar_hora_actual
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('Autorizacion_solicitud/<int:id_autorizacion>/', Autorizacion_solicitud, name='Autorizacion_solicitud'),
    path('dashboard/',dashboard,name='dashboard'),
    path('ajax/cargar-cuentas/', cargar_cuentas, name='cargar_cuentas'),
    path('', RedirectView.as_view(url='/dashboard/')),
    path('hora-actual/', mostrar_hora_actual, name='mostrar_hora_actual'),
]
