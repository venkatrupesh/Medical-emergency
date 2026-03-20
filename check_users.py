import sqlite3

conn = sqlite3.connect('emergency_reports.db')
cursor = conn.cursor()

cursor.execute('SELECT id, username, email, password FROM users')
users = cursor.fetchall()

print('Users in database:')
for user in users:
    print(f'ID: {user[0]}, Username: {user[1]}, Email: {user[2]}, Password Hash: {user[3][:30]}...')

conn.close()
