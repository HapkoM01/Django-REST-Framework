"""Сервисные функции для работы со Stripe."""
import stripe
from django.conf import settings

stripe.api_key = settings.STRIPE_SECRET_KEY


class StripeError(Exception):
    """Обёртка над ошибками Stripe."""

    def __init__(self, message, original=None):
        super().__init__(message)
        self.original = original


def create_stripe_product(name: str, description: str = '') -> dict:
    """Создаёт продукт в Stripe. Возвращает dict с id."""
    try:
        product = stripe.Product.create(
            name=name,
            description=description or name,
        )
        return {'id': product.id, 'name': product.name}
    except stripe.error.StripeError as e:
        raise StripeError(str(e.user_message or e), original=e) from e


def create_stripe_price(product_id: str, amount_rub: float, currency: str = 'rub') -> dict:
    """
    Создаёт цену в Stripe.
    amount_rub — сумма в рублях; в Stripe передаём копейки (amount * 100).
    """
    try:
        unit_amount = int(round(float(amount_rub) * 100))
        price = stripe.Price.create(
            product=product_id,
            unit_amount=unit_amount,
            currency=currency,
        )
        return {'id': price.id, 'unit_amount': price.unit_amount, 'currency': price.currency}
    except stripe.error.StripeError as e:
        raise StripeError(str(e.user_message or e), original=e) from e


def create_stripe_checkout_session(
    price_id: str,
    success_url: str,
    cancel_url: str,
    customer_email: str = None,
) -> dict:
    """Создаёт Checkout Session и возвращает id + url."""
    try:
        params = {
            'mode': 'payment',
            'line_items': [{'price': price_id, 'quantity': 1}],
            'success_url': success_url,
            'cancel_url': cancel_url,
        }
        if customer_email:
            params['customer_email'] = customer_email

        session = stripe.checkout.Session.create(**params)
        return {
            'id': session.id,
            'url': session.url,
            'payment_status': session.payment_status,
            'status': session.status,
        }
    except stripe.error.StripeError as e:
        raise StripeError(str(e.user_message or e), original=e) from e


def retrieve_stripe_session(session_id: str) -> dict:
    """Получает данные сессии по id (проверка статуса)."""
    try:
        session = stripe.checkout.Session.retrieve(session_id)
        return {
            'id': session.id,
            'payment_status': session.payment_status,
            'status': session.status,
            'url': session.url,
            'amount_total': session.amount_total,
            'currency': session.currency,
        }
    except stripe.error.StripeError as e:
        raise StripeError(str(e.user_message or e), original=e) from e
