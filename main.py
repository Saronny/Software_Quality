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
            (id text PRIMARY KEY, firstname text, lastname text, age integer, gender text, weight real, 
            street_name text, house_number text, zip_code text, city text,
            email text, phone text, registration_date text)''')

con.commit()


def main():
    login = False# login status
    application = True  # application status

    while application == True:  # application loop
        while login == False:    # login loop
            menu = Menu(["Login", "Exit"])
            menu.display()
            choice = menu.get_user_choice()
            if choice == 1:    # login
                role = menu.login()
            elif choice == 2:   # exit
                print("Goodbye!")
                application = False 
                break
            if role != None:   # login successful
                login = True
                break
            else:  # login failed 
                continue

        while login == True:  # main menu loop
            if role[1] == 1:
                menu = Menu(["Check the list of users and their roles.", 
                "Define and add a new trainer to the system.", 
                "Modify or update an existing trainer’s account and profile.",
                "Delete an existing trainer’s account.",
                "Reset an existing trainer’s password.",
                "Define and add a new admin to the system.",
                "Modify or update an existing admin’s account and profile.",
                "Delete an existing admin’s account.",
                "Reset an existing admin’s password.",
                "Make a backup of the system or restore a backup.",
                "See the logs file of the system.",
                "Add a new member to the system.",
                "Modify or update the information of a member in the system.",
                "Delete a member's record from the database.",
                "Search and retrieve the information of a member.", 
                "Logout."])
                menu.display()
                menu.super_admin(role)
            elif role[1] == 2:
                menu = Menu(["Update your own password.",
                "Check the list of users and their roles", 
                "Define and add a new trainer to the system.", 
                "Modify or update an existing trainer’s account and profile.",
                "Delete an existing trainer’s account.",
                "Reset an existing trainer’s password.",
                "Define and add a new admin to the system.",
                "Make a backup of the system or restore a backup.",
                "See the logs file of the system.",
                "Add a new member to the system.",
                "Modify or update the information of a member in the system.",
                "Delete a member's record from the database",
                "Search and retrieve the information of a member.",
                "Logout"])
                menu.display()
                menu.system_admin(role)
            elif role[1] == 3:
                menu = Menu(["Update your own password.",
                "Add a new member to the system.",
                "Modify or update the information of a member in the system.",
                "Search and retrieve the information of a member.", 
                "Logout"])
                menu.display()
                menu.trainer(role)
            else:
                print("Logged out!")
                login = False
                break
    exit()



if __name__ == "__main__":
    main()


