import sqlite3

conn = sqlite3.connect('emergency_reports.db')
cursor = conn.cursor()

print("=== Emergency Reports Table Schema ===")
cursor.execute('PRAGMA table_info(emergency_reports)')
columns = cursor.fetchall()
for col in columns:
    print(f"  {col[1]} ({col[2]})")

conn.close()
