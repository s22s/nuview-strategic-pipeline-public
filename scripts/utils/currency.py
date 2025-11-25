import logging

EXCHANGE_RATES = {
    "EUR": 1.09, "GBP": 1.30, "BRL": 0.18, "INR": 0.012,
    "CNY": 0.14, "JPY": 0.0067, "CAD": 0.74, "AUD": 0.66
}


def to_usd(amount, currency="USD"):
    if not amount:
        return 0
    try:
        clean = float(str(amount).replace(',', '').replace('$', ''))
        return int(clean * EXCHANGE_RATES.get(currency.upper(), 1))
    except Exception as e:
        if isinstance(e, (KeyboardInterrupt, SystemExit)):
            raise
        logging.exception("Failed to convert %s %s to USD: %s", amount, currency, e)
        return 0
