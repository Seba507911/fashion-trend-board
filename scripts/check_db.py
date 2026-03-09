"""DB 현황 체크."""
import sqlite3

conn = sqlite3.connect("backend/db/ftib.db")
c = conn.cursor()

c.execute("""
    SELECT brand_id, COUNT(*),
        SUM(CASE WHEN description IS NOT NULL AND description != '' THEN 1 ELSE 0 END),
        SUM(CASE WHEN fit_info IS NOT NULL AND fit_info != '' THEN 1 ELSE 0 END),
        SUM(CASE WHEN sizes IS NOT NULL AND sizes != '[]' THEN 1 ELSE 0 END)
    FROM products GROUP BY brand_id
""")

print(f"{'Brand':12} | {'Total':>5} | {'w/Desc':>6} | {'w/Fit':>5} | {'w/Size':>6}")
print("-" * 52)
for row in c.fetchall():
    print(f"{row[0]:12} | {row[1]:5} | {row[2]:6} | {row[3]:5} | {row[4]:6}")

print()
c.execute("SELECT COUNT(*) FROM products")
print(f"Total products: {c.fetchone()[0]}")

conn.close()
