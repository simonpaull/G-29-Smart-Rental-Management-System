import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Room',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('roomnumber', models.CharField(max_length=10)),
                ('roomtype', models.CharField(max_length=50)),
                ('size', models.DecimalField(decimal_places=2, max_digits=6)),
                ('price', models.DecimalField(decimal_places=2, max_digits=8)),
                ('availability', models.BooleanField(default=True)),
                ('description', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Tenant',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20)),
                ('gender', models.CharField(choices=[('male', 'Male'), ('female', 'Female')], max_length=10)),
                ('contactnumber', models.CharField(max_length=15)),
                ('email', models.EmailField(max_length=254)),
                ('ic', models.CharField(max_length=20)),
                ('moveindate', models.DateField()),
                ('moveoutdate', models.DateField(blank=True, null=True)),
                ('room', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.room')),
            ],
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone_number', models.CharField(blank=True, max_length=15)),
                ('role', models.CharField(choices=[('admin', 'Admin'), ('tenant', 'Tenant')], default='tenant', max_length=10)),
                ('address', models.TextField(blank=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
