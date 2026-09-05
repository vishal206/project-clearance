"""Fare computation helpers for the FareDesk agent portal."""

FREE_BAGGAGE_ALLOWANCE_KG = 20
BAGGAGE_RATE_PER_KG = 8.50


def calculate_total_fare(base_fare, tax_rate, baggage_kg, pax):
    """Return the total payable fare for a booking.

    base_fare  -- per-passenger fare in the quote currency
    tax_rate   -- decimal rate, e.g. 0.12 for 12%
    baggage_kg -- checked baggage weight per passenger
    pax        -- number of passengers on the booking
    """
    taxed = base_fare + (base_fare * tax_rate)

    baggage_charge = 0.0
    if baggage_kg > FREE_BAGGAGE_ALLOWANCE_KG:
        excess = baggage_kg - FREE_BAGGAGE_ALLOWANCE_KG
        baggage_charge = excess * BAGGAGE_RATE_PER_KG

    per_pax = taxed + baggage_charge
    total = per_pax * pax

    return round(total, 2)
