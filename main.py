from menu import Menu
import sqlite3

# database creation
con = sqlite3.connect('fitnessplus.db')
cur = con.cursor()

# role 1 = super admin, 2 = system admin, 3 = trainer
cur.execute('''CREATE TABLE IF NOT EXISTS users 
            (username text PRIMARY KEY, password text, firstname text, lastname text, email text, registration_date text, role number)''')

cur.execute('''INSERT OR IGNORE INTO users VALUES
            ('super_admin', 'Admin_123!', :null, :null, :null, :null, 1)''', 
            {"null": None})

cur.execute('''CREATE TABLE IF NOT EXISTS members 
            (id integer PRIMARY KEY, firstname text, lastname text, address text, email text, phone integer)''')

con.commit()

def main():
    menu = Menu(["Login"])
    menu.display()
    choice = menu.get_user_choice()
    if choice == 1:
        menu.login()
    else:
        print("Invalid choice.")


if __name__ == "__main__":
    main()


