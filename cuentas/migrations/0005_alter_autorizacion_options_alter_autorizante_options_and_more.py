# Generated by Django 4.1.5 on 2024-06-15 00:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cuentas', '0004_rename_habilitar_solicitud_estado'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='autorizacion',
            options={'verbose_name': 'autorizacion', 'verbose_name_plural': 'Autorizaciones'},
        ),
        migrations.AlterModelOptions(
            name='autorizante',
            options={'verbose_name': 'autorizante', 'verbose_name_plural': 'Autorizantes'},
        ),
        migrations.AlterModelOptions(
            name='cuenta',
            options={'verbose_name': 'cuenta', 'verbose_name_plural': 'Cuentas'},
        ),
        migrations.AlterModelOptions(
            name='solicitud',
            options={'verbose_name': 'solicitud', 'verbose_name_plural': 'Solicitudes'},
        ),
        migrations.CreateModel(
            name='MovimientoCuenta',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('descripcion', models.CharField(blank=True, max_length=255, null=True)),
                ('importe', models.FloatField(default=0.0)),
                ('cuenta', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='cuentas.cuenta')),
            ],
            options={
                'verbose_name': 'movimiento',
                'verbose_name_plural': 'Movimientos de cuenta',
            },
        ),
    ]
