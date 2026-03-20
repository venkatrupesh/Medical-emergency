import sqlite3
import hashlib

def verify_login(username, password):
    """Verify if login credentials are correct"""
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    conn = sqlite3.connect('emergency_reports.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password_hash))
    user = cursor.fetchone()
    conn.close()
    
    if user:
        print(f"✅ Login successful for user: {username}")
        print(f"User ID: {user[0]}")
        print(f"Email: {user[2]}")
        return True
    else:
        print(f"❌ Invalid credentials for user: {username}")
        print(f"Password hash: {password_hash}")
        return False

def reset_password(username, new_password):
    """Reset password for a user"""
    password_hash = hashlib.sha256(new_password.encode()).hexdigest()
    
    conn = sqlite3.connect('emergency_reports.db')
    cursor = conn.cursor()
    
    cursor.execute('UPDATE users SET password = ? WHERE username = ?', (password_hash, username))
    
    if cursor.rowcount > 0:
        conn.commit()
        print(f"✅ Password reset successful for user: {username}")
        print(f"New password hash: {password_hash}")
    else:
        print(f"❌ User not found: {username}")
    
    conn.close()

def list_all_users():
    """List all users in database"""
    conn = sqlite3.connect('emergency_reports.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, username, email FROM users')
    users = cursor.fetchall()
    conn.close()
    
    print("\n📋 All Users in Database:")
    print("-" * 50)
    for user in users:
        print(f"ID: {user[0]} | Username: {user[1]} | Email: {user[2]}")
    print("-" * 50)

# Main menu
if __name__ == '__main__':
    print("=" * 50)
    print("TrainCare Connect - User Management Utility")
    print("=" * 50)
    
    list_all_users()
    
    print("\nOptions:")
    print("1. Verify Login")
    print("2. Reset Password")
    print("3. Exit")
    
    choice = input("\nEnter choice (1-3): ")
    
    if choice == '1':
        username = input("Enter username: ")
        password = input("Enter password: ")
        verify_login(username, password)
    elif choice == '2':
        username = input("Enter username: ")
        new_password = input("Enter new password: ")
        reset_password(username, new_password)
    else:
        print("Exiting...")
