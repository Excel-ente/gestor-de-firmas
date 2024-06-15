from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator


class Cliente(models.Model):
    codigo = models.CharField(verbose_name="documento", unique=True, max_length=200, null=False, blank=False)
    nombre = models.CharField(max_length=200, null=False, blank=False)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    habilitar = models.BooleanField(default=True)
    comentarios = models.TextField(blank=True,null=True)

    def __str__(self):
        return self.nombre

class Cuenta(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='cuentas')
    nombre = models.CharField(max_length=200, null=False, blank=False)

    def calcular_saldo_actual(self):
        movimientos = self.movimientocuenta_set.all()
        saldo_actual = sum(movimiento.importe for movimiento in movimientos)
        return saldo_actual

    def __str__(self):
        saldo_actual = self.calcular_saldo_actual()
        return f"{self.nombre} - {self.cliente.nombre} (Saldo: ${saldo_actual:,.2f})"

    class Meta:
        verbose_name = 'cuenta'
        verbose_name_plural ='Cuentas' 

class MovimientoCuenta(models.Model):
    cuenta = models.ForeignKey(Cuenta, on_delete=models.CASCADE,null=True)
    descripcion = models.CharField(max_length=255,null=True,blank=True)
    importe = models.FloatField(default=0.0)

    def __str__(self):
        return f"{self.cuenta.cliente} - {self.importe:,.2f}"

    class Meta:
        verbose_name = 'movimiento'
        verbose_name_plural ='Movimientos de cuenta' 

class Solicitud(models.Model):
    fecha = models.DateTimeField(default=timezone.now)
    solicitante = models.ForeignKey(Cliente, on_delete=models.CASCADE, null=False, blank=False)
    cuenta = models.ForeignKey(Cuenta, on_delete=models.CASCADE, null=False, blank=False)
    importe = models.FloatField(validators=[MinValueValidator(0.0)], blank=False, null=False)
    estado = models.BooleanField(default=False)
    comentarios = models.TextField(blank=True)

    def __str__(self):
        #if self.estado:
        return f"Solicitud de {self.solicitante.nombre} por {self.importe}"
    
    class Meta:
        verbose_name = 'solicitud'
        verbose_name_plural ='Solicitudes' 

class Autorizante(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=False)
    nivel = models.IntegerField(choices=[(1, 'Nivel 1'), (2, 'Nivel 2'), (3, 'Nivel 3')], default=1)

    def __str__(self):
        return f"{self.usuario.username} - Nivel {self.nivel}"

    
    class Meta:
        verbose_name = 'autorizante'
        verbose_name_plural ='Autorizantes' 

class Autorizacion(models.Model):
    solicitud = models.ForeignKey(Solicitud, on_delete=models.CASCADE, related_name='autorizaciones')
    autorizante = models.ForeignKey(Autorizante, on_delete=models.CASCADE)
    fecha = models.DateTimeField(default=timezone.now)


    aprobado = models.BooleanField(default=False)
    aprobado_por  =models.ForeignKey(User,on_delete=models.CASCADE,blank=True,null=True)
    aprobado_el = models.DateTimeField(blank=True,null=True)
    comentarios = models.TextField(blank=True)

    def __str__(self):
        return f"Autorización de {self.autorizante.usuario.username} para {self.solicitud}"

    
    class Meta:
        verbose_name = 'autorizacion'
        verbose_name_plural ='Autorizaciones' 

        