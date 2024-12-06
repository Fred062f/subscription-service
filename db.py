import sqlite3
from datetime import date
import os
from dotenv import load_dotenv

load_dotenv()
DATABASE = os.getenv("DATABASE")

def init_db():
    """Initializes the Subscription database and populates it with sample data."""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS subscriptions (
        subscription_id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER,
        start_date DATE,
        end_date DATE NOT NULL,
        rental_location VARCHAR(255) NOT NULL,
        price_per_month DECIMAL(10, 2) NOT NULL,
        agreed_km INTEGER NOT NULL,
        actual_km INTEGER NOT NULL,
        vehicle_id INTEGER NOT NULL,
        down_payment DECIMAL(10, 2)
    )
    """)

    '''subscription_data = [
        (1, "2024-01-01", "2024-06-01", "Copenhagen", 1200.00, 10000, 9000, 1, 500.00),
        (2, "2024-02-15", "2024-08-15", "Aarhus", 1000.00, 8000, 7500, 2, 400.00),
        (3, "2024-03-10", "2024-09-10", "Kolding", 1100.00, 9000, 8500, 3, 450.00)
    ]

    cursor.executemany("""
        INSERT INTO subscriptions (
            customer_id, start_date, end_date, rental_location, price_per_month,
            agreed_km, actual_km, vehicle_id, down_payment
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, subscription_data)'''

    conn.commit()
    conn.close()
    print("Database initialized and sample data added.")

if __name__ == "__main__":
    init_db()
