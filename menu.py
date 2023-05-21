import sqlite3
import os

def clear():
    os.system('cls' if os.name=='nt' else 'clear')

class Menu:
    def __init__(self, options):
        self.options = options

    def display(self):
        print("Menu:")
        for index, option in enumerate(self.options, start=1):
            print(f"[{index}] {option}")
        
    def get_user_choice(self):
        while True:
            try:
                choice = int(input("Enter your choice: "))
                if 1 <= choice <= len(self.options):
                    return choice
                else:
                    print("Invalid choice. Please try again.")
            except ValueError:
                print("Invalid input. Please enter a number.")

    def login(self):
        clear()
        username = input("Enter your username: ")
        password = input("Enter your password: ")

        # Connect to the SQLite database
        conn = sqlite3.connect("fitnessplus.db")
        cursor = conn.cursor()

        # Execute a query to check if the username and password combination exists
        cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
        result = cursor.fetchone()

        if result:
            print("Login successful! You can proceed.")
        else:
            print("Invalid username or password. Please try again.")

        conn.close()