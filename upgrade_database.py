import sqlite3

print("=== Upgrading Database Schema ===\n")

conn = sqlite3.connect('emergency_reports.db')
cursor = conn.cursor()

# Check if columns already exist
cursor.execute('PRAGMA table_info(emergency_reports)')
columns = [col[1] for col in cursor.fetchall()]

print("Current columns:", columns)

# Add new columns if they don't exist
new_columns = [
    ('nearest_station_code', 'TEXT'),
    ('nearest_station_name', 'TEXT'),
    ('assigned_station_code', 'TEXT'),
    ('assigned_station_name', 'TEXT'),
    ('assigned_by_admin', 'TEXT'),
    ('assigned_at', 'DATETIME')
]

for col_name, col_type in new_columns:
    if col_name not in columns:
        try:
            cursor.execute(f'ALTER TABLE emergency_reports ADD COLUMN {col_name} {col_type}')
            print(f"✓ Added column: {col_name} ({col_type})")
        except Exception as e:
            print(f"✗ Error adding {col_name}: {e}")
    else:
        print(f"  Column {col_name} already exists")

conn.commit()
conn.close()

print("\n=== Database upgrade complete! ===")
