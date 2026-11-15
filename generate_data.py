"""Create a reproducible, clearly labelled six-month synthetic sales dataset."""
from __future__ import annotations

import random
from datetime import date, timedelta
from pathlib import Path

import pandas as pd


AS_OF_DATE = date(2026, 11, 15)
START_DATE = AS_OF_DATE - timedelta(days=182)


def main() -> None:
    rng = random.Random(20261115)
    products = [
        ("P001", "Wireless Earbuds", "Electronics", 2499, 1450),
        ("P002", "Bluetooth Speaker", "Electronics", 3299, 2050),
        ("P003", "Phone Case", "Accessories", 599, 180),
        ("P004", "USB-C Charger", "Accessories", 999, 420),
        ("P005", "Running Shoes", "Fashion", 3999, 2300),
        ("P006", "Cotton T-Shirt", "Fashion", 899, 390),
        ("P007", "Desk Lamp", "Home", 1599, 820),
        ("P008", "Water Bottle", "Home", 749, 260),
        ("P009", "Face Moisturizer", "Beauty", 699, 280),
        ("P010", "Hair Care Set", "Beauty", 1299, 590),
    ]
    regions = {
        "North": ["Delhi", "Jaipur", "Chandigarh"],
        "South": ["Bengaluru", "Chennai", "Hyderabad"],
        "East": ["Kolkata", "Bhubaneswar", "Patna"],
        "West": ["Mumbai", "Pune", "Ahmedabad"],
        "Central": ["Bhopal", "Indore", "Nagpur"],
    }
    channels = ["Website", "Mobile app", "Marketplace"]
    payments = ["UPI", "Credit card", "Debit card", "Wallet", "Cash on delivery", "Net banking"]
    statuses = ["Delivered", "In transit", "Processing"]
    customer_segments = {
        customer_id: rng.choices(["New", "Returning", "VIP"], weights=[0.38, 0.50, 0.12])[0]
        for customer_id in range(1, 601)
    }
    rows = []

    # One row represents one synthetic order. Uniform sampling covers every day
    # in the recent six-month demonstration window.
    for i in range(1, 1801):
        product_id, name, category, list_price, cost = rng.choice(products)
        if i == 1:
            order_date = START_DATE
        elif i == 2:
            order_date = AS_OF_DATE
        else:
            order_date = START_DATE + timedelta(days=rng.randrange((AS_OF_DATE - START_DATE).days + 1))
        quantity = rng.choices([1, 2, 3, 4], weights=[0.64, 0.25, 0.08, 0.03])[0]
        discount = rng.choices([0, 5, 10, 15, 20, 25], weights=[0.34, 0.12, 0.25, 0.16, 0.10, 0.03])[0]
        region = rng.choice(list(regions))
        shipping_days = rng.randint(1, 8)
        status = rng.choices(statuses, weights=[0.82, 0.12, 0.06])[0]
        customer_id = rng.randrange(1, 601)
        rows.append({
            "order_id": f"ORD-{i:05d}",
            "order_date": order_date.isoformat(),
            "customer_id": f"CUS-{customer_id:04d}",
            "customer_segment": customer_segments[customer_id],
            "product_id": product_id,
            "product_name": name,
            "category": category,
            "region": region,
            "city": rng.choice(regions[region]),
            "sales_channel": rng.choices(channels, weights=[0.32, 0.46, 0.22])[0],
            "payment_method": rng.choices(payments, weights=[0.35, 0.22, 0.13, 0.12, 0.12, 0.06])[0],
            "fulfillment_status": status,
            "quantity": quantity,
            "list_unit_price": list_price,
            "discount_pct": discount,
            "unit_price": round(list_price * (1 - discount / 100), 2),
            "unit_cost": cost,
            "shipping_days": shipping_days,
        })

    output = Path(__file__).parent / "data" / "ecommerce_sales_synthetic.csv"
    output.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).sort_values("order_date").to_csv(output, index=False)
    print(f"Wrote {len(rows)} synthetic orders ({START_DATE} to {AS_OF_DATE}) to {output}")


if __name__ == "__main__":
    main()
