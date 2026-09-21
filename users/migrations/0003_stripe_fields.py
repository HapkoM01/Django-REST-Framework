from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_payment'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='status',
            field=models.CharField(
                choices=[('pending', 'Ожидает оплаты'), ('paid', 'Оплачен'), ('canceled', 'Отменён')],
                default='pending',
                max_length=20,
                verbose_name='Статус',
            ),
        ),
        migrations.AddField(
            model_name='payment',
            name='stripe_product_id',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='payment',
            name='stripe_price_id',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='payment',
            name='stripe_session_id',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='payment',
            name='payment_link',
            field=models.URLField(blank=True, null=True, verbose_name='Ссылка на оплату'),
        ),
        migrations.AlterField(
            model_name='payment',
            name='payment_method',
            field=models.CharField(
                choices=[('cash', 'Наличные'), ('transfer', 'Перевод на счёт'), ('stripe', 'Stripe')],
                max_length=20,
                verbose_name='Способ оплаты',
            ),
        ),
    ]
