import stripe
from django.conf import settings

stripe.api_key = settings.STRIPE_API_KEY


class StripeService:
    """Сервис для работы с платежами через Stripe"""

    @staticmethod
    def create_product(name: str, description: str = ""):
        """Создаёт продукт в Stripe"""
        return stripe.Product.create(name=name, description=description)

    @staticmethod
    def create_price(product_id: str, amount: int, currency: str = "rub"):
        """
        Создаёт цену для продукта.
        amount — в копейках! (1000 руб = 100000 копеек)
        """
        return stripe.Price.create(
            product=product_id,
            unit_amount=amount,
            currency=currency,
        )

    @staticmethod
    def create_checkout_session(price_id: str, success_url: str, cancel_url: str):
        """
        Создаёт сессию оплаты и возвращает URL для перехода.
        """
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price": price_id,
                    "quantity": 1,
                }
            ],
            mode="payment",
            success_url=success_url,
            cancel_url=cancel_url,
        )
        return session
