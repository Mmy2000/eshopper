# Generated by Django 4.2.10 on 2024-04-28 23:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0016_alter_product_discount'),
    ]

    operations = [
        migrations.CreateModel(
            name='Coupon',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=50, unique=True)),
                ('discount', models.FloatField()),
                ('expiration_date', models.DateField()),
                ('is_expired', models.BooleanField(default=False)),
            ],
        ),
    ]
