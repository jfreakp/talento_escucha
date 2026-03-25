from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tickets', '0010_agencia_provincia_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='ticket',
            name='motivo_rechazo',
            field=models.TextField(blank=True, help_text='Razón registrada cuando el ticket es rechazado o cancelado', null=True, verbose_name='Motivo de Rechazo'),
        ),
    ]