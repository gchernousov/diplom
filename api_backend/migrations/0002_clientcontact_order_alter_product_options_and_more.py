# Generated by Django 4.1.4 on 2023-01-15 14:39

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api_backend', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ClientContact',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('city', models.CharField(max_length=48, verbose_name='Город')),
                ('street', models.CharField(max_length=48, verbose_name='Улица')),
                ('house', models.CharField(max_length=12, verbose_name='Номер дома')),
                ('building', models.CharField(blank=True, max_length=12, verbose_name='Корпус/Строение')),
                ('apartment', models.CharField(blank=True, max_length=12, verbose_name='Квартира')),
                ('phone', models.CharField(max_length=24, verbose_name='Телефон')),
            ],
            options={
                'verbose_name': 'Контакты пользователя',
                'verbose_name_plural': 'Контакты пользователей',
            },
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(choices=[('basket', 'Корзина'), ('new', 'Новый'), ('confirmed', 'Обработан'), ('sent', 'На доставке'), ('delivered', 'Доставлен'), ('canceled', 'Отменен')], max_length=9, verbose_name='Статус заказа')),
                ('contact', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='api_backend.clientcontact', verbose_name='Контакт')),
            ],
        ),
        migrations.AlterModelOptions(
            name='product',
            options={'ordering': ('-name',), 'verbose_name': 'Товар', 'verbose_name_plural': 'Товары'},
        ),
        migrations.AlterField(
            model_name='usermodel',
            name='company',
            field=models.CharField(blank=True, max_length=48, verbose_name='Компания'),
        ),
        migrations.AlterField(
            model_name='usermodel',
            name='first_name',
            field=models.CharField(blank=True, max_length=48, verbose_name='Имя'),
        ),
        migrations.AlterField(
            model_name='usermodel',
            name='last_name',
            field=models.CharField(blank=True, max_length=48, verbose_name='Фамилия'),
        ),
        migrations.AlterField(
            model_name='usermodel',
            name='position',
            field=models.CharField(blank=True, max_length=48, verbose_name='Должность'),
        ),
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField(verbose_name='Количество')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ordered_items', to='api_backend.order', verbose_name='Номер заказа')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ordered_items', to='api_backend.product', verbose_name='Товар')),
            ],
        ),
        migrations.AddField(
            model_name='order',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='orders', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь'),
        ),
        migrations.AddField(
            model_name='clientcontact',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='contacts', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь'),
        ),
    ]
