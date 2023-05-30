import random
import shutil
import sqlite3
import os
from datetime import date
import string

# database creation
conn = sqlite3.connect('fitnessplus.db')
cursor = conn.cursor()

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

        # Execute a query to check if the username and password combination exists
        cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
        user = cursor.fetchone()
        if user:
            return (user[0], user[6])
        else:
            print("Invalid username or password.")
            return None
        
    def super_admin(self, username):
        choice = self.get_user_choice()
        if choice == 1:
            self.check_users()
        elif choice == 2:
            self.add_trainer()
        elif choice == 3:
            self.update_trainer()
        elif choice == 4:
            self.delete_trainer()
        elif choice == 5:
            self.reset_trainer_password()
        elif choice == 6:
            self.add_admin()
        elif choice == 7:
            self.update_admin()
        elif choice == 8:
            self.delete_admin()
        elif choice == 9:
            self.reset_admin_password()
        elif choice == 10:
            self.backup_or_restore()
        elif choice == 11:
            self.see_logs()
        elif choice == 12:
            self.add_member()
        elif choice == 13:
            self.update_member()
        elif choice == 14:
            self.delete_member()
        elif choice == 15:
            self.search_member()

    def system_admin(self, username):
        choice = self.get_user_choice()
        if choice == 1:
            self.update_own_password(username)
        elif choice == 2:
            self.check_users()
        elif choice == 3:
            self.add_trainer()
        elif choice == 4:
            self.update_trainer()
        elif choice == 5:
            self.delete_trainer()
        elif choice == 6:
            self.see_logs()
        elif choice == 7:
            self.backup_or_restore()
        elif choice == 8:
            self.add_member()
        elif choice == 9:
            self.update_member()
        elif choice == 10:
            self.delete_member()
        elif choice == 11:
            self.search_member()

    def trainer(self, username):
        choice = self.get_user_choice()
        if choice == 1:
            self.update_own_password(username)
        elif choice == 2:
            self.add_member()
        elif choice == 3:
            self.update_member()
        elif choice == 4:
            self.search_member()
    
    def update_own_password(self, username):
        clear()
        print("Hello, " + username + "!")
        old_password = input("Enter your old password: ")

        # Execute a query to check if the username and old password combination exists
        cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, old_password))
        user = cursor.fetchone()

        if user:
            new_password = input("Enter your new password: ")

            # Execute a query to update the password
            cursor.execute("UPDATE users SET password = ? WHERE username = ?", (new_password, username))
            conn.commit()

            print("Your password has been updated.")
        else:
            print("Invalid password. Please try again.")

    def check_users(self):
        clear()
        # Execute a query to get all users and their roles
        cursor.execute("SELECT username, firstname, lastname, role FROM users")
        users = cursor.fetchall()

        # Print each user's username and role
        for user in users:
            print(f"Username: {user[0]}, Firstname: {user[1]}, Lastname: {user[2]}, Role: {user[3]}")

    def add_trainer(self):
        clear()
        username = input("Enter username for new trainer: ")
        password = input("Enter password for new trainer: ")
        firstname = input("Enter first name for new trainer: ")
        lastname = input("Enter last name for new trainer: ")
        email = input("Enter email for new trainer: ")
        registration_date = date.today()

        # Execute a query to insert the new trainer into the users table
        cursor.execute(
            "INSERT INTO users (username, password, firstname, lastname, email, registration_date, role) VALUES (?, ?, ?, ?, ?, ?, 3)",
            (username, password, firstname, lastname, email, registration_date)
        )
        conn.commit()
        print("New trainer added successfully.")

    def update_trainer(self):
        clear()
        username = input("Enter the username of the trainer to be updated: ")

        # Check if user exists and is a trainer
        cursor.execute("SELECT * FROM users WHERE username = ? AND role = 3", (username,))
        user = cursor.fetchone()
        if user is None:
            print("No trainer found with that username.")
            return

        print("Enter the new values (leave blank to keep the old value):")

        new_password = input("Enter new password: ")
        new_firstname = input("Enter new first name: ")
        new_lastname = input("Enter new last name: ")
        new_email = input("Enter new email: ")
        
        # Use the new values if provided, otherwise keep the old ones
        new_password = new_password if new_password else user[1]
        new_firstname = new_firstname if new_firstname else user[2]
        new_lastname = new_lastname if new_lastname else user[3]
        new_email = new_email if new_email else user[4]

        cursor.execute(
            "UPDATE users SET password = ?, firstname = ?, lastname = ?, email = ? WHERE username = ?",
            (new_password, new_firstname, new_lastname, new_email, username)
        )
        conn.commit()
        print("Trainer profile updated successfully.")

    def delete_trainer(self):
        clear()
        username = input("Enter the username of the trainer to be deleted: ")

        # Check if user exists and is a trainer
        cursor.execute("SELECT * FROM users WHERE username = ? AND role = 3", (username,))
        user = cursor.fetchone()
        if user is None:
            print("No trainer found with that username.")
            return

        # Ask for confirmation before deleting
        confirm = input(f"Are you sure you want to delete trainer {username}? (y/n): ")
        if confirm.lower() != 'y':
            print("Operation cancelled.")
            return

        # Delete the user
        cursor.execute("DELETE FROM users WHERE username = ?", (username,))
        conn.commit()
        print("Trainer account deleted successfully.")

    def reset_trainer_password(self):
        clear()
        username = input("Enter the username of the trainer to reset password: ")

        # Check if user exists and is a trainer
        cursor.execute("SELECT * FROM users WHERE username = ? AND role = 3", (username,))
        user = cursor.fetchone()
        if user is None:
            print("No trainer found with that username.")
            return

        # Generate a random temporary password
        temp_password = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(8))

        # Update the user's password
        cursor.execute(
            "UPDATE users SET password = ? WHERE username = ?",
            (temp_password, username)
        )
        conn.commit()

        print(f"Password for trainer {username} has been reset. The new temporary password is {temp_password}.")

    def add_admin(self):
        clear()
        username = input("Enter username: ")
        password = input("Enter password: ")
        firstname = input("Enter first name: ")
        lastname = input("Enter last name: ")
        email = input("Enter email: ")
        registration_date = date.today()

        # Execute a query to insert the new admin into the users table
        cursor.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?)", 
                    (username, password, firstname, lastname, email, registration_date, 2))
        conn.commit()

        print(f"New admin {username} has been added to the system.")

    def update_admin(self):
        clear()
        username = input("Enter the username of the admin to be updated: ")

        # Check if user exists and is an admin
        cursor.execute("SELECT * FROM users WHERE username = ? AND (role = 2 OR role = 1)", (username,))
        user = cursor.fetchone()
        if user is None:
            print("No admin found with that username.")
            return

        print("Enter the new values (leave blank to keep the old value):")

        new_password = input("Enter new password: ")
        new_firstname = input("Enter new first name: ")
        new_lastname = input("Enter new last name: ")
        new_email = input("Enter new email: ")
        
        # Use the new values if provided, otherwise keep the old ones
        new_password = new_password if new_password else user[1]
        new_firstname = new_firstname if new_firstname else user[2]
        new_lastname = new_lastname if new_lastname else user[3]
        new_email = new_email if new_email else user[4]

        cursor.execute(
            "UPDATE users SET password = ?, firstname = ?, lastname = ?, email = ? WHERE username = ?",
            (new_password, new_firstname, new_lastname, new_email, username)
        )
        conn.commit()
        print("Admin profile updated successfully.")

    def delete_admin(self):
        username = input("Enter the username of the admin you want to delete: ")

        # Execute a query to check if the username exists and is an admin
        cursor.execute("SELECT * FROM users WHERE username = ? AND role = ?", (username, 2))
        user = cursor.fetchone()

        if user:
            confirmation = input(f"Are you sure you want to delete admin {username}? (yes/no): ")
            if confirmation.lower() == 'yes':
                # Execute a query to delete the user's account
                cursor.execute("DELETE FROM users WHERE username = ? AND (role = 1 OR role 2)", (username,))
                conn.commit()

                print(f"Admin {username}'s account has been deleted.")
            else:
                print("Delete operation cancelled.")
        else:
            print("No admin found with that username.")
    
    def reset_admin_password(self):
        clear()
        username = input("Enter the username of the admin to reset password: ")

        # Check if user exists and is a admin
        cursor.execute("SELECT * FROM users WHERE username = ? AND r(role = 1 OR role 2)", (username,))
        user = cursor.fetchone()
        if user is None:
            print("No admin found with that username.")
            return

        # Generate a random temporary password
        temp_password = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(8))

        # Update the user's password
        cursor.execute(
            "UPDATE users SET password = ? WHERE username = ?",
            (temp_password, username)
        )
        conn.commit()

        print(f"Password for admin {username} has been reset. The new temporary password is {temp_password}.")

    def backup_or_restore(self):
        clear()
        Menu(["Backup database", "Restore database"]).display()
        choice = self.get_user_choice()
        if choice == 1:
            self.backup_database()
        elif choice == 2:
            self.restore_database()

    def backup_database(self):
        clear()
        backup_file = f'fitnessplus_backup_{date.today().strftime("%d-%m%-Y%")}.db'
        shutil.copy2('fitnessplus.db', backup_file)
        print(f'Database has been backed up to {backup_file}.')

    def restore_database(self):
        clear()
        backup_file = input("Enter the filename of the backup to restore: ")
        if not os.path.isfile(backup_file):
            print("Backup file does not exist.")
            return

        shutil.copy2(backup_file, 'fitnessplus.db')
        print('Database has been restored from backup.')

    def add_member(self):
        clear()
        firstname = input("Enter the first name: ")
        lastname = input("Enter the last name: ")
        age = input("Enter the age: ")
        gender = input("Enter the gender: ")
        weight = input("Enter the weight (kg): ")
        street_name = input("Enter the street name: ")
        house_number = input("Enter the house number: ")
        zip_code = input("Enter the zip code (DDDDXX): ")
        city = input("Enter the city: ")
        email = input("Enter the email: ")
        phone = "+31-6-" + input("Enter the phone number (DDDDDDDD): ")

        # Get current year for ID generation
        today = date.today()
        current_year = today.strftime("%Y")[2:]

        # Generate random member ID
        member_id = str(current_year) + ''.join(random.choices(string.digits, k=7))

        # Calculate the checksum
        checksum = sum(int(digit) for digit in member_id) % 10

        # Append checksum to member ID
        member_id += str(checksum)

        registration_date = date.today()

        with sqlite3.connect('fitnessplus.db') as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO members (id, firstname, lastname, age, gender, weight, street_name, house_number, zip_code, city, email, phone, registration_date) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                        (member_id, firstname, lastname, age, gender, weight, street_name, house_number, zip_code, city, email, phone, registration_date))
            conn.commit()

        print(f"Member {firstname} {lastname} with ID {member_id} has been added to the system.")

    def update_member(self):
        clear()
        member_id = input("Enter the member's ID you would like to update: ")

        # Check if the member ID exists
        cursor.execute("SELECT * FROM members WHERE id = ?", (member_id,))
        member = cursor.fetchone()
        if not member:
            print("No member found with this ID.")
            return

        print("Leave the field empty if you don't want to update the information.")
        firstname = input("Enter the new first name: ")
        lastname = input("Enter the new last name: ")
        age = input("Enter the new age: ")
        gender = input("Enter the new gender: ")
        weight = input("Enter the new weight: ")
        street_name = input("Enter the new street name: ")
        house_number = input("Enter the new house number: ")
        zip_code = input("Enter the new zip code (DDDDXX): ")
        city = input("Enter the new city: ")
        email = input("Enter the new email: ")
        phone = input("Enter the new phone number (DDDDDDDD): ")

        # Update the member information
        cursor.execute('''UPDATE members SET firstname = ?, lastname = ?, age = ?, gender = ?, weight = ?, 
                        street_name = ?, house_number = ?, zip_code = ?, city = ?, email = ?, phone = ?
                        WHERE id = ?''', 
                    (firstname or member[1], lastname or member[2], age or member[3], gender or member[4], 
                        weight or member[5], street_name or member[6], house_number or member[7], 
                        zip_code or member[8], city or member[9], email or member[10], phone or member[11], member_id))
        conn.commit()
        print("Member information has been updated.")

    def delete_member(self):
        clear()
        member_id = input("Enter the member's ID you would like to delete: ")

        # Check if the member ID exists
        cursor.execute("SELECT * FROM members WHERE id = ?", (member_id,))
        member = cursor.fetchone()
        if not member:
            print("No member found with this ID.")
            return

        confirmation = input("Are you sure you want to delete this member's record? (yes/no): ")
        if confirmation.lower() == "yes":
            # Delete the member record
            cursor.execute("DELETE FROM members WHERE id = ?", (member_id,))
            conn.commit()
            print("Member record has been deleted.")
        else:
            print("Operation cancelled.")

    def search_member(self):
        clear()
        search_key = input("Enter search key: ")
        search_key = "%" + search_key + "%"  # Add wildcards to the search key for pattern matching

        # Concatenate the address fields
        address_fields = "street_name || ' ' || house_number || ' ' || zip_code || ' ' || city"

        # Execute a query to find members that match the search key
        cursor.execute(f"SELECT * FROM members WHERE id LIKE ? OR firstname LIKE ? OR lastname LIKE ? OR ({address_fields}) LIKE ? OR email LIKE ? OR phone LIKE ?", 
                    (search_key, search_key, search_key, search_key, search_key, search_key))

        members = cursor.fetchall()

        if members:
            print("Matching members found:")
            for member in members:
                print(member)
        else:
            print("No matching members found.")

    def see_logs(self):
        pass