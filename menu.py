import random
import shutil
import sqlite3
import os
from datetime import date
import string
import re
import time
import zipfile
import bcrypt # for hashing passwords
import getpass
import rsa # for encryption

# database creation
conn = sqlite3.connect('fitnessplus.db')
cursor = conn.cursor()
(public_key, private_key) = rsa.newkeys(512) # generate public and private keys for encryption

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
                    # if self.options[choice - 1] == "Exit": 
                    #     self.Exit()
                    return choice
                else:
                    print("Invalid choice. Please try again.")
            except ValueError:
                print("Invalid input. Please enter a number.")

    def login(self):
        clear()
        login_attempts = 0
        while login_attempts < 3:
            username_input = input("Enter your username: ")
            if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_'\.]{7,11}$", username_input):
                print("Invalid username. Please try again.")
                login_attempts += 1
                continue

            password = getpass.getpass("Enter your password: ")
            # Check if password matches the regex or is superadmin password (kinda iffy but it works)
            if re.match(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[~!@#$%&_=+`|\()\{\}\[\]:;'<>,.?/-])[A-Za-z\d~!@#$%&_=+`|\()\{\}\[\]:;'<>,.?/-]{12,30}$", password):
                pass
            elif username_input == 'super_admin' and password == 'Admin_123!':
                pass
            else:
                print("Invalid password.")
                login_attempts += 1
                continue

            # Execute a query to retrieve all users from the database
            cursor.execute("SELECT * FROM users")
            users = cursor.fetchall()

            # Look for matching user
            
            for user in users:
            # Check if the entered password matches the hashed password in the database
                if username_input == 'super_admin' and password == ('Admin_123!'):
                    return [user[0], user[6]]
                decrypted_username = rsa.decrypt(user[0], private_key).decode('utf8')

                if decrypted_username == username_input:
                    hashed_password = user[1].encode('utf-8')
                    
                    try:
                        if bcrypt.checkpw(password.encode('utf-8'), hashed_password):
                            return [user[0], user[6]]
                    except ValueError:
                        print("Invalid username or password.")
                        login_attempts += 1
                    else:
                        print("Invalid username or password.")
                        login_attempts += 1
            else:
                print("Invalid username or password.")
                login_attempts += 1

        print("You have been blocked for 1 minute due to excessive login attempts.")
        time.sleep(60)  # Delay for 1 minute
        return None
        
    def super_admin(self, role):
        choice = self.get_user_choice()
        
        actions = {
            1: self.check_users,
            2: self.add_trainer,
            3: self.update_trainer,
            4: self.delete_trainer,
            5: self.reset_trainer_password,
            6: self.add_admin,
            7: self.update_admin,
            8: self.delete_admin,
            9: self.reset_admin_password,
            10: self.backup_or_restore,
            11: self.see_logs,
            12: self.add_member,
            13: self.update_member,
            14: self.delete_member,
            15: self.search_member,
            16: lambda: self.logout(role)
        }
        
        if choice in actions:
            actions[choice]()
        else:
            print("Invalid choice.")


    def system_admin(self, role):
        choice = self.get_user_choice()

        actions = {
            1: lambda: self.update_own_password(role[0]),
            2: self.check_users,
            3: self.add_trainer,
            4: self.update_trainer,
            5: self.delete_trainer,
            6: self.see_logs,
            7: self.backup_or_restore,
            8: self.add_member,
            9: self.update_member,
            10: self.delete_member,
            11: self.search_member,
            12: lambda: self.logout(role)
        }

        if choice in actions:
            actions[choice]()
        else:
            print("Invalid choice.")

    def trainer(self, role):
        choice = self.get_user_choice()

        actions = {
            1: lambda: self.update_own_password(role[0]),
            2: self.add_member,
            3: self.update_member,
            4: self.search_member,
            5: lambda: self.logout(role)
        }

        if choice in actions:
            actions[choice]()
        else:
            print("Invalid choice.")

    def check_username_unique(self, username):
        cursor.execute("SELECT 1 FROM users WHERE username = ?", (username,))
        if cursor.rowcount:
            return True
        else:
            return False

    def get_validated_username(self, prompt):
        while True:
            username = input(prompt)
            if len(username) < 8 or len(username) > 12:
                print("Username must be between 8 and 12 characters.")
            elif not re.match("^[a-zA-Z_][a-zA-Z0-9_'\.]*$", username):
                print("Username must start with a letter or underscore and can contain letters (a-z), numbers (0-9), underscores (_), apostrophes ('), and periods (.)")
            elif not self.check_username_unique(username):
                print("Username already exists. Please choose another.")
            else:
                return username

    def get_validated_password(self, prompt):
        while True:
            password = getpass.getpass(prompt)
            password_confirm = getpass.getpass("Confirm password: ")

            if password != password_confirm:
                print("Passwords do not match. Please try again.")
            else:
                if len(password) < 12 or len(password) > 30:
                    print("Password must be between 12 and 30 characters.")
                elif not re.match("^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[~!@#$%&\_\-+=`|\()\{\}\[\]:;'<>,.?/]).+$", password):
                    print("Password must contain at least one lowercase letter, one uppercase letter, one digit, and one special character.")
                else:
                    return password

    def get_validated_email(self, prompt):
        while True:
            email = input(prompt)
            if not re.match("^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", email):
                print("Invalid email address. Please enter a valid email.")
            else:
                return email
    
    def get_validated_name(self, prompt):
        while True:
            name = input(prompt)
            if not name or re.match("^[a-zA-Z-' ]+$", name):
                return name
            print("Invalid name. It should contain only letters, spaces, hyphens, and apostrophes.")
    
    def get_validated_age(self, prompt):
        while True:
            age = input(prompt)
            if not age or (age.isdigit() and 0 <= int(age) <= 150):
                return age
            print("Invalid age. It should be a number between 0 and 150.")

    def get_validated_gender(self, prompt):
        while True:
            gender = input(prompt)
            if gender:
                gender = gender.lower()
                if gender in ['man', 'm']:
                    return 'M'
                if gender in ['female', 'f']:
                    return 'F'
            print("Invalid gender. It should be either 'man', 'female', 'm' or 'f'.")

    def get_validated_weight(self, prompt):
        while True:
            weight = input(prompt)
            if not weight or (weight.isdigit() and 25 <= int(weight) <= 1000):
                return weight
            print("Invalid weight. It should be a number between 25 and 1000.")
    
    def get_city_choice(self):
        cities = ["Amsterdam", "Rotterdam", "The Hague", "Utrecht", "Eindhoven", 
                "Tilburg", "Groningen", "Almere", "Breda", "Nijmegen"]
        while True:
            print("\nChoose a city from the following list:")
            for i, city in enumerate(cities, 1):
                print(f"{i}. {city}")
            choice = input("\nEnter your choice (1-10): ")
            if choice.isdigit() and 1 <= int(choice) <= 10:
                return cities[int(choice) - 1]
            else:
                print("Invalid choice. Please try again.")

    def get_validated_zip_code(self, prompt):
        while True:
            zip_code = input(prompt)
            if not zip_code or re.match("^\d{4}[a-zA-Z]{2}$", zip_code):
                return zip_code
            print("Invalid zip code. It should be in the format DDDDXX.")
    
    def get_validated_street_or_house(self, prompt):
        while True:
            user_input = input(prompt)
            if re.match("^[a-zA-Z0-9- ]+$", user_input):
                return user_input
            else:
                if 'street' in prompt.lower():
                    print("Invalid street name. It should contain only letters, numbers, and hyphens.")
                elif 'house' in prompt.lower():
                    print("Invalid house number. It should contain only letters, numbers, and hyphens.")

    def get_validated_phone(self, prompt):
        while True:
            phone = input(prompt)
            if not phone or re.match("^\d{8}$", phone):
                return phone
            print("Invalid phone number. It should contain exactly 8 digits.")
            
    def update_own_password(self, username):
        clear()
        
        old_password = getpass.getpass("Enter your old password: ")
        
        # Fetch the hashed password from the database
        cursor.execute("SELECT password FROM users WHERE username = ?", (username,))
        stored_hashed_password = cursor.fetchone()[0]

        # Check if the old password matches the hashed password stored in the database
        if bcrypt.checkpw(old_password.encode('utf-8'), stored_hashed_password):
            while True:
                new_password = self.get_validated_password("Enter your new password: ")

                hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())

                # Execute a query to update the password
                cursor.execute("UPDATE users SET password = ? WHERE username = ?", (hashed_password, username))
                conn.commit()

                self.show_message("Your password has been updated.")
                break
            return
        else:
            self.show_message("Invalid password. Please try again.")
            return

    def check_users(self):
        clear()
        # Execute a query to get all users and their roles
        cursor.execute("SELECT username, firstname, lastname, role FROM users")
        users = cursor.fetchall()

        # Print each user's username and role
        for user in users:
            print(f"Username: {user[0]}, Firstname: {user[1]}, Lastname: {user[2]}, Role: {user[3]}")
            self.return_to_main_menu()
            return

    def add_trainer(self):
        while True:
            username = self.get_validated_username("Enter username for new trainer: ").encode('utf-8')
            password = self.get_validated_password("Enter password for new trainer: ")
            firstname = self.get_validated_name("Enter first name for new trainer: ")
            lastname = self.get_validated_name("Enter last name for new trainer: ")
            email = self.get_validated_email("Enter email for new trainer: ").encode('utf-8')
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            registration_date = date.today()

            #Encrypt sensitive data
            username = rsa.encrypt(username, public_key)
            email = rsa.encrypt(email, public_key)

            # Execute a query to insert the new trainer into the users table
            cursor.execute(
                "INSERT INTO users (username, password, firstname, lastname, email, registration_date, role) VALUES (?, ?, ?, ?, ?, ?, 3)",
                (username, hashed_password, firstname, lastname, email, registration_date)
            )
            conn.commit()
            self.show_message("New trainer added successfully.")
            break
        return

    def update_trainer(self):
        clear()
        username = input("Enter the username of the trainer to be updated: ")

        # Check if user exists and is a trainer
        cursor.execute("SELECT * FROM users WHERE username = ? AND role = 3", (username,))
        user = cursor.fetchone()
        if user is None:
            self.show_message("No trainer found with that username.")
            return

        print("Enter the new values (leave blank to keep the old value):")

        new_password = self.get_validated_password("Enter new password: ")
        new_firstname = self.get_validated_name("Enter new first name: ")
        new_lastname = self.get_validated_name("Enter new last name: ")
        new_email = self.get_validated_email("Enter new email: ")
        
        # Use the new values if provided, otherwise keep the old ones
        hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()) if new_password else user[1]
        new_firstname = new_firstname if new_firstname else user[2]
        new_lastname = new_lastname if new_lastname else user[3]
        new_email = new_email if new_email else user[4]

        cursor.execute(
            "UPDATE users SET password = ?, firstname = ?, lastname = ?, email = ? WHERE username = ?",
            (hashed_password, new_firstname, new_lastname, new_email, username)
        )
        conn.commit()
        self.show_message("Trainer profile updated successfully.")
        return

    def delete_trainer(self):
        clear()
        username = input("Enter the username of the trainer to be deleted: ")

        # Check if user exists and is a trainer
        cursor.execute("SELECT * FROM users WHERE username = ? AND role = 3", (username,))
        user = cursor.fetchone()
        if user is None:
            self.show_message("No trainer found with that username.")
            return

        # Ask for confirmation before deleting
        confirm = input(f"Are you sure you want to delete trainer {username}? (y/n): ")
        if confirm.lower() != 'y':
            self.show_message("Delete operation cancelled.")
            return

        # Delete the user
        cursor.execute("DELETE FROM users WHERE username = ?", (username,))
        conn.commit()
        self.show_message("Trainer account deleted successfully.")
        return

    def reset_trainer_password(self):
        clear()
        username = input("Enter the username of the trainer to reset password: ")

        # Check if user exists and is a trainer
        cursor.execute("SELECT * FROM users WHERE username = ? AND role = 3", (username,))
        user = cursor.fetchone()
        if user is None:
            self.show_message("No trainer found with that username.")
            return

        # Generate a random temporary password
        temp_password = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(8))
        hashed_password = bcrypt.hashpw(temp_password.encode('utf-8'), bcrypt.gensalt())

        # Update the user's password
        cursor.execute(
            "UPDATE users SET password = ? WHERE username = ?",
            (hashed_password, username)
        )
        conn.commit()

        self.show_message(f"Password for trainer {username} has been reset. The new temporary password is {temp_password}.")
        return

    def add_admin(self):
        while True:
            username = self.get_validated_username("Enter username for new admin: ").encode('utf-8')
            password = self.get_validated_password("Enter password for new admin: ")
            firstname = self.get_validated_name("Enter first name for new admin: ")
            lastname = self.get_validated_name("Enter last name for new admin: ")
            email = self.get_validated_email("Enter email for new admin: ").encode('utf-8')
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            registration_date = date.today()

            #Encrypt sensitive data
            username = rsa.encrypt(username, public_key)
            email = rsa.encrypt(email, public_key)

            # Execute a query to insert the new admin into the users table
            cursor.execute(
                "INSERT INTO users (username, password, firstname, lastname, email, registration_date, role) VALUES (?, ?, ?, ?, ?, ?, 2)",
                (username, hashed_password, firstname, lastname, email, registration_date)
            )
            conn.commit()
            self.show_message(f"New admin {username} has been added to the system.")
            break
        return

    def update_admin(self):
        clear()
        username = input("Enter the username of the admin to be updated: ")

        # Check if user exists and is an admin
        cursor.execute("SELECT * FROM users WHERE username = ? AND (role = 2 OR role = 1)", (username,))
        user = cursor.fetchone()
        if user is None:
            self.show_message("No admin found with that username.")
            return

        print("Enter the new values (leave blank to keep the old value):")

        new_password = self.get_validated_password("Enter new password: ")
        new_firstname = self.get_validated_name("Enter new first name: ")
        new_lastname = self.get_validated_name("Enter new last name: ")
        new_email = self.get_validated_email("Enter new email: ")
        
        # Use the new values if provided, otherwise keep the old ones
        hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()) if new_password else user[1]
        new_firstname = new_firstname if new_firstname else user[2]
        new_lastname = new_lastname if new_lastname else user[3]
        new_email = new_email if new_email else user[4]

        cursor.execute(
            "UPDATE users SET password = ?, firstname = ?, lastname = ?, email = ? WHERE username = ?",
            (hashed_password, new_firstname, new_lastname, new_email, username)
        )
        conn.commit()
        self.show_message("Admin profile updated successfully.")
        return

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

                self.show_message(f"Admin {username}'s account has been deleted.")
                return
            else:
                self.show_message("Delete operation cancelled.")
                return
        else:
            self.show_message("No admin found with that username.")
            return
        
    def reset_admin_password(self):
        clear()
        username = input("Enter the username of the admin to reset password: ")

        # Check if user exists and is a admin
        cursor.execute("SELECT * FROM users WHERE username = ? AND r(role = 1 OR role 2)", (username,))
        user = cursor.fetchone()
        if user is None:
            self.show_message("No admin found with that username.")
            return

        # Generate a random temporary password
        temp_password = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(8))
        hashed_password = bcrypt.hashpw(temp_password.encode('utf-8'), bcrypt.gensalt())

        # Update the user's password
        cursor.execute(
            "UPDATE users SET password = ? WHERE username = ?",
            (hashed_password, username)
        )
        conn.commit()

        self.show_message(f"Password for admin {username} has been reset. The new temporary password is {temp_password}.")

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
        backup_file = f"fitnessplus_backup_{date.today().strftime('%d%m%Y')}.db"
        backup_zip = f"Backups/fitnessplus_backup_{date.today().strftime('%d%m%Y')}.zip"
        
        # Create a new directory if it doesn't exist
        if not os.path.exists('Backups'):
            os.makedirs('Backups')

        # Copy the db to the backup file
        shutil.copy2('fitnessplus.db', backup_file)

        # Create a zip file
        with zipfile.ZipFile(backup_zip, 'w') as zipf:
            zipf.write(backup_file)
        
        # Remove the .db backup file after zipping it
        os.remove(backup_file)
        
        self.show_message(f'Database has been backed up to {backup_zip}.')
        return

    def restore_database(self):
        clear()
        backup_file = input("Enter the filename of the backup to restore: ")

        # Adjust to look in the 'Backups' directory
        backup_zip = f"Backups/{backup_file}"

        if not os.path.isfile(backup_zip):
            self.show_message("Backup file not found.")
            return
        
        # Extract the database file from the zip
        with zipfile.ZipFile(backup_zip, 'r') as zipf:
            zipf.extractall()

        # Extracted file will have the same name as original .db file, copy it to original location
        extracted_db_file = f"fitnessplus_backup_{backup_file.split('_')[2].split('.')[0]}.db"
        shutil.copy2(extracted_db_file, 'fitnessplus.db')
        
        # Remove the extracted .db file after copying it
        os.remove(extracted_db_file)
        
        self.show_message('Database has been restored from backup.')

    def add_member(self):
        clear()
        firstname = self.get_validated_name("Enter first name for new member: ")
        lastname = self.get_validated_name("Enter last name for new member: ")
        age = self.get_validated_age("Enter age for new member: ")
        gender = self.get_validated_gender("Enter gender for new member (M/F): ")
        weight = self.get_validated_weight("Enter weight for new member (kg): ")
        street_name = self.get_validated_street_or_house("Enter the street name: ").encode('utf8')
        house_number = self.get_validated_street_or_house("Enter the house number: ").encode('utf8')
        zip_code = self.get_validated_zip_code("Enter the zip code (DDDDXX): ").encode('utf8')
        city = self.get_city_choice().encode('utf8')
        email = self.get_validated_email("Enter the email address: ").encode('utf8')
        phone = ("+31-6-" + self.get_validated_phone("Enter the phone number (DDDDDDDD): 06-")).encode('utf8')

        #encrypt all sensitive data
        street_name = rsa.encrypt(street_name, public_key)
        house_number = rsa.encrypt(house_number, public_key)
        zip_code = rsa.encrypt(zip_code, public_key)
        city = rsa.encrypt(city, public_key)
        email = rsa.encrypt(email, public_key)
        phone = rsa.encrypt(phone, public_key)

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

        self.show_message(f"Member {firstname} {lastname} with ID {member_id} has been added to the system.")
        return

    def update_member(self):
        clear()
        member_id = input("Enter the member's ID you would like to update: ")

        # Check if the member ID exists
        cursor.execute("SELECT * FROM members WHERE id = ?", (member_id,))
        member = cursor.fetchone()
        if not member:
            self.show_message("No member found with this ID.")
            return

        print("Leave the field empty if you don't want to update the information.")
        firstname = self.get_validated_name("Enter first name for new member: ")
        lastname = self.get_validated_name("Enter last name for new member: ")
        age = self.get_validated_age("Enter age for new member: ")
        gender = self.get_validated_gender("Enter gender for new member (M/F): ")
        weight = self.get_validated_weight("Enter weight for new member (kg): ")
        street_name = self.get_validated_street_or_house("Enter the street name: ").encode('utf8')
        house_number = self.get_validated_street_or_house("Enter the house number: ").encode('utf8')
        zip_code = self.get_validated_zip_code("Enter the zip code (DDDDXX): ").encode('utf8')
        city = self.get_city_choice().encode('utf8')
        email = self.get_validated_email("Enter the email address: ").encode('utf8')
        phone = ("+31-6-" + self.get_validated_phone("Enter the phone number (DDDDDDDD): 06-")).encode('utf8')

        #encrypt all sensitive data
        street_name = rsa.encrypt(street_name, public_key)
        house_number = rsa.encrypt(house_number, public_key)
        zip_code = rsa.encrypt(zip_code, public_key)
        city = rsa.encrypt(city, public_key)
        email = rsa.encrypt(email, public_key)
        phone = rsa.encrypt(phone, public_key)

        # Update the member information
        cursor.execute('''UPDATE members SET firstname = ?, lastname = ?, age = ?, gender = ?, weight = ?, 
                        street_name = ?, house_number = ?, zip_code = ?, city = ?, email = ?, phone = ?
                        WHERE id = ?''', 
                    (firstname or member[1], lastname or member[2], age or member[3], gender or member[4], 
                        weight or member[5], street_name or member[6], house_number or member[7], 
                        zip_code or member[8], city or member[9], email or member[10], phone or member[11], member_id))
        conn.commit()
        self.show_message("Member information updated.")
        return

    def delete_member(self):
        clear()
        member_id = input("Enter the member's ID you would like to delete: ")

        # Check if the member ID exists
        cursor.execute("SELECT * FROM members WHERE id = ?", (member_id,))
        member = cursor.fetchone()
        if not member:
            self.show_message("No member found with this ID.")
            return

        confirmation = input("Are you sure you want to delete this member's record? (yes/no): ")
        if confirmation.lower() == "yes":
            # Delete the member record
            cursor.execute("DELETE FROM members WHERE id = ?", (member_id,))
            conn.commit()
            self.show_message("Member record deleted.")
        else:
            self.show_message("Delete operation cancelled.")
        return


    def search_member(self):
        clear()
        search_key = input("Enter search key: ")

        # Fetch all members
        cursor.execute("SELECT * FROM members")
        members = cursor.fetchall()

        matching_members = []

        for member in members:
            # Decrypt the sensitive fields
            decrypted_street_name = rsa.decrypt(member[6], private_key)
            decrypted_house_number = rsa.decrypt(member[7], private_key)
            decrypted_zip_code = rsa.decrypt(member[8], private_key)
            decrypted_city = rsa.decrypt(member[9], private_key)
            decrypted_email = rsa.decrypt(member[10], private_key)
            decrypted_phone = rsa.decrypt(member[11], private_key)

            #Decode bytes to string
            decrypted_street_name = decrypted_street_name.decode('utf8')
            decrypted_house_number = decrypted_house_number.decode('utf8')
            decrypted_zip_code = decrypted_zip_code.decode('utf8')
            decrypted_city = decrypted_city.decode('utf8')
            decrypted_email = decrypted_email.decode('utf8')
            decrypted_phone = decrypted_phone.decode('utf8')

            # Check if the decrypted fields match the search key
            if search_key.lower() in member[0].lower() or search_key.lower() in member[1].lower() or search_key.lower() in member[2].lower() or search_key.lower() in decrypted_street_name.lower() or search_key.lower() in decrypted_house_number.lower() or search_key.lower() in decrypted_zip_code.lower() or search_key.lower() in decrypted_city.lower() or search_key.lower() in decrypted_email.lower() or search_key.lower() in decrypted_phone.lower():
                matching_members.append(member)

        if matching_members:
            print("Matching members found:")
            for member in matching_members:
                print(member)
            self.return_to_main_menu()
            return
        else:
            self.show_message("No matching members found.")
            return

    def show_message(self, message):   # function to show a message and return to main menu
        print(message + " returning to main menu...")
        time.sleep(2)


    def see_logs(self):
        pass

    def return_to_main_menu(self):  # function to return to main menu after an action is completed
        while True:
            try:
                user_input = int(input("Press 1 to return to the main menu: "))
                if user_input == 1:
                    clear()
                    break
            except ValueError:
                print("Invalid input. Please enter a number.")
        return
    
    def logout(self, role): # function to logout and return to main menu
        role[1] = None # set role to None
        clear()
        return  # return to main menu
        
    def Exit(self):
        exit()
