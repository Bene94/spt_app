import sqlite3
import bcrypt

def create_users_table():
    with sqlite3.connect('users.db') as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS users
                        (username TEXT PRIMARY KEY,
                        password TEXT NOT NULL,
                        tokens_used INTEGER DEFAULT 0,
                        max_tokens INTEGER DEFAULT 100);''')  # Assuming 100 as the default max tokens

def print_user_base():
    with sqlite3.connect('users.db') as conn:
        cursor = conn.execute('SELECT username, tokens_used, max_tokens FROM users')
        for row in cursor:
            print(f"Username: {row[0]}, Tokens Used: {row[1]}, Max Tokens: {row[2]}")
            
def adjust_max_tokens(username, new_max):
    with sqlite3.connect('users.db') as conn:
        conn.execute('UPDATE users SET max_tokens = ? WHERE username = ?', (new_max, username))
        print(f"Updated max tokens for user '{username}' to {new_max}")

def get_token_info(username):
    with sqlite3.connect('users.db') as conn:
        cursor = conn.execute('SELECT tokens_used, max_tokens FROM users WHERE username = ?', (username,))
        data = cursor.fetchone()
    return data if data else (0, 0)  # Return (0, 0) if no data found

def update_token_usage(username, tokens_used):
    with sqlite3.connect('users.db') as conn:
        conn.execute('UPDATE users SET tokens_used = tokens_used + ? WHERE username = ?', (tokens_used, username))

def add_user(username, password):
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    conn = sqlite3.connect('users.db')
    conn.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed))
    conn.commit()
    conn.close()

def verify_user(username, password):
    conn = sqlite3.connect('users.db')
    cursor = conn.execute('SELECT password FROM users WHERE username = ?', (username,))
    data = cursor.fetchone()
    conn.close()
    if data and bcrypt.checkpw(password.encode('utf-8'), data[0]):
        return True
    return False

def add_user(username, password):
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    with sqlite3.connect('users.db') as conn:
        try:
            conn.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed))
            print(f"User '{username}' added successfully.")
        except sqlite3.IntegrityError:
            print(f"User '{username}' already exists.")

def main():
    create_users_table()

    while True:
        print("\nOptions:")
        print("1. Add user")
        print("2. Print user base")
        print("3. Adjust max tokens for a user")
        print("4. Exit")
        choice = input("Enter option: ")

        if choice == '1':
            username = input("Enter username to add: ")
            password = input("Enter password for the user: ")
            add_user(username, password)
        elif choice == '2':
            print_user_base()
        elif choice == '3':
            username = input("Enter username: ")
            new_max = int(input("Enter new max tokens: "))
            adjust_max_tokens(username, new_max)
        elif choice == '4':
            break
        else:
            print("Invalid option. Please try again.")

if __name__ == "__main__":
    main()