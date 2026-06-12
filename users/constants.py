class PaymentMethod:
    CASH = "cash"
    BANK_TRANSFER = "bank_transfer"

    CHOICES = [
        (CASH, "Наличные"),
        (BANK_TRANSFER, "Перевод"),
    ]
