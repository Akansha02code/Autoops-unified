"""
Currency Conversion - converts an extracted price to INR, since that's
the base currency your policy thresholds are written in.

Uses static approximate rates for the MVP (documented as a known
simplification - a production version would call a live FX API).

Usage: import convert_to_inr(amount, currency_code) from elsewhere.
"""

# Approximate rates as of late 2026 - update periodically, or replace
# with a live FX API call (e.g. exchangerate-api.com) in a later phase.
FX_TO_INR = {
    "INR": 1.0,
    "USD": 95.95,
    "EUR": 90.0,
    "GBP": 105.0,
}


def convert_to_inr(amount, currency_code: str):
    """
    Returns (converted_amount_in_inr, rate_used, note_string).
    Defaults to treating unrecognized/missing currency as INR
    (rate 1.0) so nothing silently breaks, but flags this in the note.
    """
    if amount is None:
        return None, None, None

    code = (currency_code or "INR").upper()
    rate = FX_TO_INR.get(code)

    if rate is None:
        # Unrecognized currency code - don't guess, flag it instead
        return amount, 1.0, f"Unrecognized currency '{code}' - treated as INR, please verify manually"

    converted = round(amount * rate, 2)
    if code == "INR":
        note = None
    else:
        note = f"Converted from {amount:,.2f} {code} to INR {converted:,.2f} (rate: 1 {code} = {rate} INR)"

    return converted, rate, note