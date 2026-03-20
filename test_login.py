import sqlite3
import hashlib

# Test password "123456"
test_password = "123456"
password_hash = hashlib.sha256(test_password.encode()).hexdigest()

print(f"Testing with password: {test_password}")
print(f"Password hash: {password_hash}")
print()

conn = sqlite3.connect('emergency_reports.db')
cursor = conn.cursor()

cursor.execute('SELECT id, username, email, password FROM users')
users = cursor.fetchall()

print("Login Test Results:")
print("-" * 60)

for user in users:
    if user[3] == password_hash:
        print(f"✅ Username: {user[1]} | Email: {user[2]} | Password: 123456")
    else:
        print(f"❌ Username: {user[1]} | Email: {user[2]} | Different password")

conn.close()

print("\n💡 If your account shows '✅', use password: 123456")
print("💡 If your account shows '❌', the password was changed")
