# signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Solicitud, Autorizante, Autorizacion

@receiver(post_save, sender=Solicitud)
def crear_autorizaciones(sender, instance, created, **kwargs):
    if created:
        importe = instance.importe
        autorizantes_niveles = []

        if importe <= 1_000_000:
            # Obtener los autorizantes de nivel 1
            autorizantes_niveles.append(Autorizante.objects.filter(nivel=1))
        elif importe <= 5_000_000:
            # Obtener los autorizantes de nivel 1 y nivel 2
            autorizantes_niveles.append(Autorizante.objects.filter(nivel=1))
            autorizantes_niveles.append(Autorizante.objects.filter(nivel=2))
        else:
            # Obtener los autorizantes de nivel 1, nivel 2 y nivel 3
            autorizantes_niveles.append(Autorizante.objects.filter(nivel=1))
            autorizantes_niveles.append(Autorizante.objects.filter(nivel=2))
            autorizantes_niveles.append(Autorizante.objects.filter(nivel=3))

        # Crear autorizaciones para cada autorizante en los niveles correspondientes
        for autorizantes in autorizantes_niveles:
            for autorizante in autorizantes:
                Autorizacion.objects.create(solicitud=instance, autorizante=autorizante)