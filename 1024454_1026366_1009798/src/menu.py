import random
import shutil
import sqlite3
import os
from datetime import date
import string
import re
import time
import zipfile
from logger import logger

# Passwords
import getpass # For passwords on linux
import msvcrt # for passwords on windows

# Hashing/encryption
import bcrypt # for hashing passwords
import rsa # for encryption

# database creation
conn = sqlite3.connect('fitnessplus.db')
cursor = conn.cursor()
public_key, private_key = None, None # generate public and private keys for encryption

# Creation of keys
if os.path.exists("./public.pem") and os.path.exists("./private.pem"):
    with open("./public.pem", 'rb') as f:
        public_key = rsa.PublicKey.load_pkcs1(f.read())
    with open("./private.pem", 'rb') as f:
        private_key = rsa.PrivateKey.load_pkcs1(f.read())
    
else:
    public_key, private_key = rsa.newkeys(512)
    with open("./public.pem", 'wb') as f:
        f.write(public_key.save_pkcs1())
    with open("./private.pem", 'wb') as f:
        f.write(private_key.save_pkcs1())

log = logger()

def clear():
    os.system('cls' if os.name=='nt' else 'clear')

def get_password_windows(prompt='Password: '):
    print(prompt, end='', flush=True)
    password = ''
    while True:
        ch = msvcrt.getch()
        if ch == b'\r':  # Carriage return is pressed, finish input
            msvcrt.putch(b'\n')  # Echo a newline
            return password
        elif ch == b'\x08':  # Backspace is pressed, remove last character
            if len(password) > 0:
                password = password[:-1]
                msvcrt.putch(b'\x08')  # Echo backspace
                msvcrt.putch(b' ')  # Echo space
                msvcrt.putch(b'\x08')  # Echo backspace
            else:
                continue
        elif ch == b'\xe0':  # Arrow key is pressed, read next byte
            ch = msvcrt.getch()
            if ch in [b'H', b'P']:  # Up or down arrow key
                continue
            else:  # Left or right arrow key
                continue
        else:
            password += ch.decode()  # Add character to password
            msvcrt.putch(b'*')  # Echo * for each character

class Menu:
    def __init__(self, options, current_user):
        self.options = options
        self.current_user = current_user

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
                log.log(Description="Unsuccesful login", Additional="Invalid username: " + username_input, Suspicious=False)
                login_attempts += 1
                continue
            if log.is_suspicious(username_input): # Should never trigger since we filtered out invalid usernames
                log.log(Description="Malicious username", Additional="Username: " + username_input, Suspicious=True)

            password = get_password_windows("Enter your password: ") if os.name == 'nt' else getpass.getpass("Enter your password: ")
            # Check if password matches the regex or is superadmin password (kinda iffy but it works)
            if self.check_null_bytes(password):
                log.log(Username="login attempt", Description="Malicious input", Additional="Null byte on login password", Suspicious=True)
                print("Suspicious activity detected. Please contact the administrator.")
                exit()
            
            if re.match(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[~!@#$%&_=+`|\()\{\}\[\]:;'<>,.?/-])[A-Za-z\d~!@#$%&_=+`|\()\{\}\[\]:;'<>,.?/-]{12,30}$", password):
                pass
            elif username_input == 'super_admin' and password == 'Admin_123!':
                pass
            else:
                print("Invalid password.")
                log.log(Description="Unsuccesful login", Additional="Entered invalid password for username: " + username_input, Suspicious=False)
                login_attempts += 1
                continue

            # Execute a query to retrieve all users from the database
            cursor.execute("SELECT * FROM users")
            users = cursor.fetchall()

            # Look for matching user
            
            for user in users:
            # Check if the entered password matches the hashed password in the database
                decrypted_username = rsa.decrypt(user[0], private_key).decode('utf8')
                
                if username_input == 'super_admin' and password == ('Admin_123!'):
                    self.current_user = decrypted_username
                    log.log(Username=self.current_user, Description="Logged in", Suspicious=False)
                    return [decrypted_username, user[6]]

                if decrypted_username == username_input:
                    hashed_password = user[1]
                    
                    try:
                        if bcrypt.checkpw(password.encode('utf-8'), hashed_password):
                            self.current_user = username_input
                            log.log(Username=self.current_user, Description="Logged in", Suspicious=False)
                            return [user[0], user[6]]
                    except ValueError:
                        print("Invalid username or password.")
                        log.log(Description="Unsuccesful login", Additional="Entered invalid username or password", Suspicious=False)
                        login_attempts += 1
                    else:
                        print("Invalid username or password.")
                        log.log(Description="Unsuccesful login", Additional="Entered invalid username or password", Suspicious=False)
                        login_attempts += 1
            else:
                print("Invalid username or password.")
                log.log(Description="Unsuccesful login", Additional="Entered invalid username or password", Suspicious=False)
                login_attempts += 1

        print("You have been blocked for 1 minute due to excessive login attempts.")
        log.log(Description="Unsuccesful login", Additional="Multiple usernames and passwords are tried in a row", Suspicious=True)
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
            6: self.reset_trainer_password,
            7: self.see_logs,
            8: self.backup_or_restore,
            9: self.add_member,
            10: self.update_member,
            11: self.delete_member,
            12: self.search_member,
            13: lambda: self.logout(role)
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
        cursor.execute("SELECT username FROM users")
        rows = cursor.fetchall()
        for row in rows:
            decrypted_username = rsa.decrypt(row[0], private_key).decode('utf8')
            if decrypted_username == username:
                return False
        return True

    def get_validated_username(self, prompt):
        while True:
            username = input(prompt)
            if self.check_null_bytes(username):
                log.log(Username=self.current_user, Description="Malicious input", Additional="On username input", Suspicious=True)
                print("Suspicious activity detected. Please contact the administrator.")
                exit()
            if log.is_suspicious(username):
                log.log(Username=self.current_user, Description="Malicious input", Additional="On username input", Suspicious=True)
                print("Suspicious activity detected. Please contact the administrator.")
                exit()
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
            password = get_password_windows("Enter your password: ") if os.name == 'nt' else getpass.getpass("Enter your password: ")
            if self.check_null_bytes(password):
                log.log(Username=self.current_user, Description="Malicious input", Additional="On password input", Suspicious=True)
                print("Suspicious activity detected. Please contact the administrator.")
                exit()
            if log.is_suspicious(password):
                log.log(Username=self.current_user, Description="Malicious input", Additional="On password input", Suspicious=True)
                print("Suspicious activity detected. Please contact the administrator.")
                exit()
            password_confirm = get_password_windows("Enter your password to confirm: ") if os.name == 'nt' else getpass.getpass("Enter your password to confirm: ")
            if log.is_suspicious(password):
                log.log(Username=self.current_user, Description="Malicious input", Additional="On password input validation", Suspicious=True)
                print("Suspicious activity detected. Please contact the administrator.")
                exit()

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
            if self.check_null_bytes(email):
                log.log(Username=self.current_user, Description="Malicious input", Additional="On email input", Suspicious=True)
                print("Suspicious activity detected. Please contact the administrator.")
                exit()
            if log.is_suspicious(email):
                log.log(Username=self.current_user, Description="Malicious input", Additional="On email input", Suspicious=True)
                print("Suspicious activity detected. Please contact the administrator.")
                exit()
            if not re.match("^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", email):
                print("Invalid email address. Please enter a valid email.")
            else:
                return email
    
    def get_validated_name(self, prompt):
        while True:
            name = input(prompt)
            if self.check_null_bytes(name):
                log.log(Username=self.current_user, Description="Malicious input", Additional="On name input", Suspicious=True)
                print("Suspicious activity detected. Please contact the administrator.")
                exit()
            if log.is_suspicious(name):
                log.log(Username=self.current_user, Description="Malicious input", Additional="On name input", Suspicious=True)
                print("Suspicious activity detected. Please contact the administrator.")
                exit()
            if not name or re.match("^[a-zA-Z-' ]+$", name):
                return name
            print("Invalid name. It should contain only letters, spaces, hyphens, and apostrophes.")
    
    def get_validated_age(self, prompt):
        while True:
            age = input(prompt)
            if self.check_null_bytes(age):
                log.log(Username=self.current_user, Description="Malicious input", Additional="On age input", Suspicious=True)
                print("Suspicious activity detected. Please contact the administrator.")
                exit()
            if log.is_suspicious(age):
                log.log(Username=self.current_user, Description="Malicious input", Additional="On age input", Suspicious=True)
                print("Suspicious activity detected. Please contact the administrator.")
                exit()
            if not age or (age.isdigit() and 0 <= int(age) <= 150):
                return age
            print("Invalid age. It should be a number between 0 and 150.")

    def get_validated_gender(self, prompt):
        while True:
            gender = input(prompt)
            if self.check_null_bytes(gender):
                log.log(Username=self.current_user, Description="Malicious input", Additional="On gender input", Suspicious=True)
                print("Suspicious activity detected. Please contact the administrator.")
                exit()
            if log.is_suspicious(gender):
                log.log(Username=self.current_user, Description="Malicious input", Additional="On gender input", Suspicious=True)
                print("Suspicious activity detected. Please contact the administrator.")
                exit()
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
            if self.check_null_bytes(weight):
                log.log(Username=self.current_user, Description="Malicious input", Additional="On weight input", Suspicious=True)
                print("Suspicious activity detected. Please contact the administrator.")
                exit()
            if log.is_suspicious(weight):
                log.log(Username=self.current_user, Description="Malicious input", Additional="On weight input", Suspicious=True)
                print("Suspicious activity detected. Please contact the administrator.")
                exit()
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
            if log.is_suspicious(choice):
                log.log(Username=self.current_user, Description="Malicious input", Additional="On city input", Suspicious=True)
                print("Suspicious activity detected. Please contact the administrator.")
                exit()
            if self.check_null_bytes(choice): 
                log.log(Username=self.current_user, Description="Malicious input", Additional="On city input", Suspicious=True)
                print("Suspicious activity detected. Please contact the administrator.")
                exit()   
            if choice.isdigit() and 1 <= int(choice) <= 10:
                return cities[int(choice) - 1]
            else:
                print("Invalid choice. Please try again.")

    def get_validated_zip_code(self, prompt):
        while True:
            zip_code = input(prompt)
            if log.is_suspicious(zip_code):
                log.log(Username=self.current_user, Description="Malicious input", Additional="On zip code input", Suspicious=True)
                print("Suspicious activity detected. Please contact the administrator.")
                exit()
                
            if self.check_null_bytes(zip_code):
                log.log(Username=self.current_user, Description="Malicious input", Additional="On zip code input", Suspicious=True)
                print("Suspicious activity detected. Please contact the administrator.")
                exit()    

            if not zip_code or re.match("^\d{4}[a-zA-Z]{2}$", zip_code):
                return zip_code
            print("Invalid zip code. It should be in the format DDDDXX.")
    
    def get_validated_street_or_house(self, prompt):
        while True:
            user_input = input(prompt)
            if log.is_suspicious(user_input):
                log.log(Username=self.current_user, Description="Malicious input", Additional="On street or house number input", Suspicious=True)
                print("Suspicious activity detected. Please contact the administrator.")
                exit()
                
            if self.check_null_bytes(user_input):
                log.log(Username=self.current_user, Description="Malicious input", Additional="On street or house number input", Suspicious=True)
                print("Suspicious activity detected. Please contact the administrator.")
                exit()    

            if re.match("^[a-zA-Z0-9- .]+$", user_input):
                return user_input
            else:
                if 'street' in prompt.lower():
                    print("Invalid street name. It should contain only letters, numbers, and hyphens.")
                elif 'house' in prompt.lower():
                    print("Invalid house number. It should contain only letters, numbers, and hyphens.")

    def get_validated_phone(self, prompt):
        while True:
            phone = input(prompt)
            if log.is_suspicious(phone):
                log.log(Username=self.current_user, Description="Malicious input", Additional="On phone number input", Suspicious=True)
                print("Suspicious activity detected. Please contact the administrator.")
                exit()
                
            if self.check_null_bytes(phone):
                log.log(Username=self.current_user, Description="Malicious input", Additional="On phone number input", Suspicious=True)
                print("Suspicious activity detected. Please contact the administrator.")
                exit()    

            if not phone or re.match("^\d{8}$", phone):
                return phone
            print("Invalid phone number. It should contain exactly 8 digits.")
            
    def update_own_password(self, username):
        clear()
        
        old_password = get_password_windows("Enter your old password: ") if os.name == 'nt' else getpass.getpass("Enter your old password: ")
        if log.is_suspicious(old_password):
                log.log(Username=self.current_user, Description="Malicious input", Additional="On password updating", Suspicious=True)
                print("Suspicious activity detected. Please contact the administrator.")
                exit()
                
        if self.check_null_bytes(old_password):
            log.log(Username=self.current_user, Description="Malicious input", Additional="On password updating", Suspicious=True)
            print("Suspicious activity detected. Please contact the administrator.")
            exit()        

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

                log.log(Username=self.current_user, Description="Updated own password", Suspicious=False)
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
            username = rsa.decrypt(user[0], private_key).decode('utf-8')
            print(f"Username: {username}, Firstname: {user[1]}, Lastname: {user[2]}, Role: {user[3]}")

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
            try:
                cursor.execute(
                    "INSERT INTO users (username, password, firstname, lastname, email, registration_date, role) VALUES (?, ?, ?, ?, ?, ?, 3)",
                    (username, hashed_password, firstname, lastname, email, registration_date)
                )
                conn.commit()
                self.show_message("New trainer added successfully.")
                log.log(Username=self.current_user, Description="Added new trainer", Additional="Username: " + rsa.decrypt(username, private_key).decode('utf-8'))
            except Exception as e:
                print("Failed to insert new trainer: ", e)
                log.log(Username=self.current_user, Description="Failed to add new trainer", Additional=e)
            break
        return

    def update_trainer(self):
        clear()
        username = input("Enter the username of the trainer to be updated: ")
        if log.is_suspicious(username):
            log.log(Username=self.current_user, Description="Malicious input", Additional="On trainer update", Suspicious=True)
            print("Suspicious activity detected. Please contact the administrator.")
            exit()
        if self.check_null_bytes(username):
            log.log(Username=self.current_user, Description="Malicious input", Additional="On trainer update", Suspicious=True)
            print("Suspicious activity detected. Please contact the administrator.")
            exit()       

        # Get all trainers
        cursor.execute("SELECT * FROM users WHERE role = 3")
        trainers = cursor.fetchall()
        
        for trainer in trainers:
            # Decrypt the username
            decrypted_username = rsa.decrypt(trainer[0], private_key).decode('utf8')
            
            # If the decrypted username matches the input username, update the trainer
            if decrypted_username == username:
                
                options = [ "password", "firstname", "lastname", "email", "return to main menu" ]
                for i, option in enumerate(options):
                    print(f"[{i + 1}] {option}")
                    
                try: 
                    choice = int(input("Enter your choice: "))
                    match choice: 
                        case 1:
                            clear() 
                            new_password = self.get_validated_password("Enter new password: ")
                            cursor.execute( "UPDATE users SET password = ? WHERE username = ?", (bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()), trainer[0]))
                            log.log(Username=self.current_user, Description="Updated trainers password", Additional="Trainer: " + decrypted_username)
                        case 2:
                            new_firstname = self.get_validated_name("Enter new first name: ")
                            cursor.execute( "UPDATE users SET firstname = ? WHERE username = ?", (new_firstname, trainer[0]))
                            log.log(Username=self.current_user, Description="Updated trainers first name", Additional="Trainer: " + decrypted_username)
                        case 3:
                            new_lastname = self.get_validated_name("Enter new last name: ")
                            cursor.execute( "UPDATE users SET lastname = ? WHERE username = ?", (new_lastname, trainer[0]))
                            log.log(Username=self.current_user, Description="Updated trainers last name", Additional="Trainer: " + decrypted_username)
                        case 4:
                            new_email = rsa.encrypt(self.get_validated_email("Enter new email: ").encode('utf-8'), public_key)
                            cursor.execute( "UPDATE users SET email = ? WHERE username = ?", (new_email, trainer[0]))
                            log.log(Username=self.current_user, Description="Updated trainers email", Additional="Trainer: " + decrypted_username)
                        case 5:
                            self.show_message("")
                            return
                except ValueError:
                    self.show_message("Invalid choice.")
                    log.log(Username=self.current_user, Description="Failed to update trainer", Additional="Invalid choice", Suspicious=True)
                    return
                conn.commit()
                self.show_message("Trainer profile updated successfully.")
                return            
                                        
        self.show_message("No trainer found with that username.")
        return

    def delete_trainer(self):
        clear()
        username = input("Enter the username of the trainer to be deleted: ")
        if log.is_suspicious(username):
            log.log(Username=self.current_user, Description="Malicious input", Additional="On trainer update", Suspicious=True)
            print("Suspicious activity detected. Please contact the administrator.")
            exit()
        if self.check_null_bytes(username):
            log.log(Username=self.current_user, Description="Malicious input", Additional="On trainer update", Suspicious=True)
            print("Suspicious activity detected. Please contact the administrator.")
            exit()    

        # Get all trainers
        cursor.execute("SELECT * FROM users WHERE role = 3")
        trainers = cursor.fetchall()

        for trainer in trainers:
            # Decrypt the username
            decrypted_username = rsa.decrypt(trainer[0], private_key).decode('utf8')

            # If the decrypted username matches the input username, delete the trainer
            if decrypted_username == username:
                # Ask for confirmation before deleting
                confirm = input(f"Are you sure you want to delete trainer {username}? (y/n): ")
                if confirm.lower() != 'y':
                    self.show_message("Delete operation cancelled.")
                    return

                # Delete the user
                cursor.execute("DELETE FROM users WHERE username = ?", (trainer[0],))
                conn.commit()
                self.show_message("Trainer account deleted successfully.")
                log.log(Username=self.current_user, Description="Deleted trainer", Additional="Trainer: " + decrypted_username)
                return

        self.show_message("No trainer found with that username.")
        return

    def reset_trainer_password(self):
        clear()
        username = input("Enter the username of the trainer to reset password: ")
        if log.is_suspicious(username):
            log.log(Username=self.current_user, Description="Malicious input", Additional="On trainer update", Suspicious=True)
            print("Suspicious activity detected. Please contact the administrator.")
            exit()
            
        if self.check_null_bytes(username):
            log.log(Username=self.current_user, Description="Malicious input", Additional="On trainer update", Suspicious=True)
            print("Suspicious activity detected. Please contact the administrator.")
            exit()    

        # Get all trainers
        cursor.execute("SELECT * FROM users WHERE role = 3")
        trainers = cursor.fetchall()

        for trainer in trainers:
            # Decrypt the username
            decrypted_username = rsa.decrypt(trainer[0], private_key).decode('utf8')

            # If the decrypted username matches the input username, reset the trainer's password
            if decrypted_username == username:
                # Generate a random temporary password
                temp_password = self.generate_temp_password()
                hashed_password = bcrypt.hashpw(temp_password.encode('utf-8'), bcrypt.gensalt())

                # Update the user's password
                cursor.execute(
                    "UPDATE users SET password = ? WHERE username = ?",
                    (hashed_password, trainer[0])
                )
                conn.commit()

                log.log(Username=self.current_user, Description="Reset trainers password", Additional="Trainer: " + decrypted_username + ". New password: " + temp_password)
                self.show_message(f"Password for trainer {decrypted_username} has been reset. The new temporary password is {temp_password}.")
                return

        self.show_message("No trainer found with that username.")
        return

    def add_admin(self):
        while True:
            username = self.get_validated_username("Enter username for new admin: ")
            password = self.get_validated_password("Enter password for new admin: ")
            firstname = self.get_validated_name("Enter first name for new admin: ")
            lastname = self.get_validated_name("Enter last name for new admin: ")
            email = self.get_validated_email("Enter email for new admin: ").encode('utf-8')
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            registration_date = date.today()

            #Encrypt sensitive data
            encrypted_username = rsa.encrypt(username.encode('utf-8'), public_key)
            email = rsa.encrypt(email, public_key)

            # Execute a query to insert the new admin into the users table
            cursor.execute(
                "INSERT INTO users (username, password, firstname, lastname, email, registration_date, role) VALUES (?, ?, ?, ?, ?, ?, 2)",
                (encrypted_username, hashed_password, firstname, lastname, email, registration_date)
            )
            conn.commit()
            log.log(Username=self.current_user, Description="Added new admin", Additional="Admin: " + username)
            self.show_message(f"New admin {username} has been added to the system.")
            break
        return

    def update_admin(self):
        clear()
        username = input("Enter the username of the admin to be updated: ")
        if log.is_suspicious(username):
            log.log(Username=self.current_user, Description="Malicious input", Additional="On admin update", Suspicious=True)
            print("Suspicious activity detected. Please contact the administrator.")
            exit()
        if self.check_null_bytes(username):
            log.log(Username=self.current_user, Description="Malicious input", Additional="On admin input", Suspicious=True)
            print("Suspicious activity detected. Please contact the administrator.")
            exit()    

        # Get all admins
        cursor.execute("SELECT * FROM users WHERE role = 2 OR role = 1")
        admins = cursor.fetchall()
        for admin in admins:
            # Decrypt the username
            decrypted_username = rsa.decrypt(admin[0], private_key).decode('utf8')

            # If the decrypted username matches the input username, update the admin's data
            if decrypted_username == username:
                
                options = ["Username", "Password", "First name", "Last name", "Email", "Return to main menu"]
                for i in range(len(options)):
                    print(f"[{i + 1}] Update {options[i]}")
                try:
                    choice = int(input("\nEnter your choice you want to edit: "))
                    match choice:
                        case 1:
                            clear()
                            new_username = rsa.encrypt(self.get_validated_username("Enter new username: ").encode('utf-8'), public_key) # Encrypt the username
                            cursor.execute("UPDATE users SET username = ? WHERE username = ?", (new_username, admin[0]))
                            log.log(Username=self.current_user, Description="Updated admin username", Additional="Admin: " + decrypted_username + ". New username: " + rsa.decrypt(new_username, private_key).decode('utf8'))
                        case 2: 
                            clear()
                            new_password = self.get_validated_password("Enter new password: ")  # hash the password
                            cursor.execute("UPDATE users SET password = ? WHERE username = ?", (bcrypt.hashpw(new_password.encode("utf-8"), bcrypt.gensalt()), admin[0]))
                            log.log(Username=self.current_user, Description="Updated admin password", Additional="Admin: " + decrypted_username)
                        case 3:
                            clear()
                            new_firstname = self.get_validated_name("Enter new first name: ")    
                            cursor.execute("UPDATE users SET firstname = ? WHERE username = ?", (new_firstname, admin[0]))
                            log.log(Username=self.current_user, Description="Updated admin first name", Additional="Admin: " + decrypted_username + ". New first name: " + new_firstname)
                        case 4:
                            clear()
                            new_lastname = self.get_validated_name("Enter new last name: ")
                            cursor.execute("UPDATE users SET lastname = ? WHERE username = ?", (new_lastname, admin[0]))
                            log.log(Username=self.current_user, Description="Updated admin last name", Additional="Admin: " + decrypted_username + ". New last name: " + new_lastname)
                        case 5:
                            clear()
                            new_email = rsa.encrypt(self.get_validated_email("Enter new email: ").encode('utf-8'), public_key) # Encrypt the email
                            cursor.execute("UPDATE users SET email = ? WHERE username = ?", (new_email, admin[0]))
                            log.log(Username=self.current_user, Description="Updated admin email", Additional="Admin: " + decrypted_username + ". New email: " + rsa.decrypt(new_email, private_key).decode('utf8'))
                        case 6:
                            clear()
                            self.show_message("")
                            return
                        
                    conn.commit()
                    self.show_message("Admin profile updated successfully.")
                    return
                
                except ValueError:
                    self.show_message("Invalid choice. Please try again.")
                    return   

        self.show_message("No admin found with that username.")
        return

    def delete_admin(self):
        clear()
        username = input("Enter the username of the admin to be deleted: ")
        if log.is_suspicious(username):
            log.log(Username=self.current_user, Description="Malicious input", Additional="On admin delete", Suspicious=True)
            print("Suspicious activity detected. Please contact the administrator.")
            exit()
            
        if self.check_null_bytes(username):
            log.log(Username=self.current_user, Description="Malicious input", Additional="On admin delete", Suspicious=True)
            print("Suspicious activity detected. Please contact the administrator.")
            exit()    

        # Get all admins
        cursor.execute("SELECT * FROM users WHERE role = 1 OR role = 2")
        admins = cursor.fetchall()

        for admin in admins:
            # Decrypt the username
            decrypted_username = rsa.decrypt(admin[0], private_key).decode('utf8')

            # If the decrypted username matches the input username, delete the admin
            if decrypted_username == username:
                confirmation = input(f"Are you sure you want to delete admin {username}? (yes/no): ")
                if confirmation.lower() == 'yes':
                    # Execute a query to delete the user's account
                    cursor.execute("DELETE FROM users WHERE username = ?", (admin[0],))
                    conn.commit()
                    log.log(Username=self.current_user, Description="Deleted admin", Additional="Admin: " + decrypted_username)
                    self.show_message(f"Admin {username}'s account has been deleted.")
                    return

        self.show_message("No admin found with that username.")
        return
        
    def reset_admin_password(self):
        clear()
        username = input("Enter the username of the admin to reset password: ")
        if log.is_suspicious(username):
            log.log(Username=self.current_user, Description="Malicious input", Additional="On admin password reset", Suspicious=True)
            print("Suspicious activity detected. Please contact the administrator.")
            exit()
            
        if self.check_null_bytes(username):
            log.log(Username=self.current_user, Description="Malicious input", Additional="On admin password reset", Suspicious=True)
            print("Suspicious activity detected. Please contact the administrator.")
            exit()    

        # Get all admins
        cursor.execute("SELECT * FROM users WHERE role = 1 OR role = 2")
        admins = cursor.fetchall()

        for admin in admins:
            # Decrypt the username
            decrypted_username = rsa.decrypt(admin[0], private_key).decode('utf8')

            # If the decrypted username matches the input username, reset the admin's password
            if decrypted_username == username:
                # Generate a random temporary password
                temp_password = self.generate_temp_password()
                hashed_password = bcrypt.hashpw(temp_password.encode('utf-8'), bcrypt.gensalt())

                # Update the user's password
                cursor.execute(
                    "UPDATE users SET password = ? WHERE username = ?",
                    (hashed_password, admin[0])
                )
                conn.commit()
                log.log(Username=self.current_user, Description="Reset admin password", Additional="Admin: " + decrypted_username)
                self.show_message(f"Password for admin {username} has been reset. The new temporary password is {temp_password}.")
                return

        self.show_message("No admin found with that username.")
        return

    def backup_or_restore(self):
        clear()
        Menu(["Backup database", "Restore database"], self.current_user).display()
        choice = self.get_user_choice()
        if choice == 1:
            self.backup_database()
        elif choice == 2:
            self.restore_database()

    def backup_database(self):
        clear()
        version = 1
        backup_zip = f"Backups/fitnessplus_backup_{date.today().strftime('%d%m%Y')}_{version}.zip"
        
        # Create a new directory if it doesn't exist
        if not os.path.exists('Backups'):
            os.makedirs('Backups')

        # If backup with the same date already exists, increment version number
        while os.path.exists(backup_zip):
            version += 1
            backup_zip = f"Backups/fitnessplus_backup_{date.today().strftime('%d%m%Y')}_{version}.zip"

        # Create a zip file
        with zipfile.ZipFile(backup_zip, 'w') as zipf:
            zipf.write('fitnessplus.db')
            zipf.write('private.pem')
            zipf.write('public.pem')
            zipf.write('logs/log.txt')
        
        log.log(Username=self.current_user, Description="Backed up system")
        self.show_message(f'Database and keys have been backed up to {backup_zip}.')
        return

    def restore_database(self):
        clear()
        backup_file = input("Enter the filename of the backup to restore: ")
        if log.is_suspicious(backup_file):
            log.log(Username=self.current_user, Description="Malicious input", Additional="On backup entry", Suspicious=True)
            print("Suspicious activity detected. Please contact the administrator.")
            exit()

        # Adjust to look in the 'Backups' directory
        backup_zip = f"Backups/{backup_file}"

        if not os.path.isfile(backup_zip):
            self.show_message("Backup file not found.")
            return
        
        # Extract the database file and the pem files from the zip
        with zipfile.ZipFile(backup_zip, 'r') as zipf:
            zipf.extractall()
        
        log.log(Username=self.current_user, Description="Restored system from backup")
        self.show_message('Database, keys and logs have been restored from backup.')
        return

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
        
        log.log(Username=self.current_user, Description="Added new member", Additional="Member ID: " + member_id)
        self.show_message(f"Member {firstname} {lastname} with ID {member_id} has been added to the system.")
        return

    def update_member(self):
        clear()
        member_id = input("Enter the member's ID you would like to update: ")
        if log.is_suspicious(member_id):
            log.log(Username=self.current_user, Description="Malicious input", Additional="On member update", Suspicious=True)
            print("Suspicious activity detected. Please contact the administrator.")
            exit()
            
        if self.check_null_bytes(member_id):
            log.log(Username=self.current_user, Description="Malicious input", Additional="On member update", Suspicious=True)
            print("Suspicious activity detected. Please contact the administrator.")
            exit()    

        # Check if the member ID exists
        cursor.execute("SELECT * FROM members WHERE id = ?", (member_id,))
        member = cursor.fetchone()
        if not member:
            self.show_message("No member found with this ID.")
            return
        
        options = ["first name", "last name", "age", "gender", "weight", "street name", "house number", "zip code", "city", "email", "phone"]
        for i, option in enumerate(options):
            print(f"[{i+1}] Update {option}")
        try:
            choice = int(input("Enter your choice: "))
            match choice:
                case 1:
                    clear()
                    new_value = self.get_validated_name("Enter new first name: ")
                    cursor.execute("UPDATE members SET firstname = ? WHERE id = ?", (new_value, member_id))
                    log.log(Username=self.current_user, Description="Updated members first name", Additional="Member ID: " + member_id + ", New first name: " + new_value)
                case 2:
                    clear()
                    new_value = self.get_validated_name("Enter new last name: ")
                    cursor.execute("UPDATE members SET lastname = ? WHERE id = ?", (new_value, member_id))
                    log.log(Username=self.current_user, Description="Updated members last name", Additional="Member ID: " + member_id + ", New last name: " + new_value)
                case 3:
                    clear()
                    new_value = self.get_validated_age("Enter new age: ")
                    cursor.execute("UPDATE members SET age = ? WHERE id = ?", (new_value, member_id))
                    log.log(Username=self.current_user, Description="Updated members age", Additional="Member ID: " + member_id + ", New age: " + new_value)
                case 4:
                    clear()
                    new_value = self.get_validated_gender("Enter new gender (M/F): ")
                    cursor.execute("UPDATE member SET gender = ? WHERE id = ?", (new_value, member_id))
                    log.log(Username=self.current_user, Description="Updated member gender", Additional="Member ID: " + member_id + ", new gender: " + new_value)
                case 5:
                    clear()
                    new_value = self.get_validated_weight("Enter new weight (kg): ")
                    cursor.execute("UPDATE members SET weight = ? WHERE id = ?", (new_value, member_id))
                    log.log(Username=self.current_user, Description="Updated members weight", Additional="Member ID: " + member_id + ", New weight: " + new_value)
                case 6:
                    clear()
                    new_value = self.get_validated_street_or_house("Enter new street name: ").encode('utf8')
                    cursor.execute("UPDATE members SET street_name = ? WHERE id = ?", (rsa.encrypt(new_value, public_key), member_id))
                    log.log(Username=self.current_user, Description="Updated members street name", Additional="Member ID: " + member_id + ", New street name: " + new_value)
                case 7:
                    clear()
                    new_value = self.get_validated_street_or_house("Enter new house number: ").encode('utf8')
                    cursor.execute("UPDATE members SET house_number = ? WHERE id = ?", (rsa.encrypt(new_value, public_key), member_id))
                    log.log(Username=self.current_user, Description="Updated members house number", Additional="Member ID: " + member_id + ", New house number: " + new_value)
                case 8:
                    clear()
                    new_value = self.get_validated_zip_code("Enter new zip code (DDDDXX): ").encode('utf8')
                    cursor.execute("UPDATE members SET zip_code = ? WHERE id = ?", (rsa.encrypt(new_value, public_key), member_id))
                    log.log(Username=self.current_user, Description="Updated members zip code", Additional="Member ID: " + member_id + ", New zip code: " + new_value)
                case 9:
                    clear()
                    new_value = self.get_city_choice().encode('utf8')
                    cursor.execute("UPDATE members SET city = ? WHERE id = ?", (rsa.encrypt(new_value, public_key), member_id))
                    log.log(Username=self.current_user, Description="Updated members city", Additional="Member ID: " + member_id + ", New city: " + new_value)
                case 10:
                    clear()
                    new_value = self.get_validated_email("Enter new email address: ").encode('utf8')
                    cursor.execute("UPDATE members SET email = ? WHERE id = ?", (rsa.encrypt(new_value, public_key), member_id))
                    log.log(Username=self.current_user, Description="Updated members email", Additional="Member ID: " + member_id + ", New email: " + new_value)
                case 11:
                    clear() 
                    new_value = ("+31-6-" + self.get_validated_phone("Enter new phone number (DDDDDDDD): 06-")).encode('utf8')
                    cursor.execute("UPDATE members SET phone = ? WHERE id = ?", (rsa.encrypt(new_value, public_key), member_id))
                    log.log(Username=self.current_user, Description="Updated members phone number", Additional="Member ID: " + member_id + ", New phone number: " + new_value)
                case 12:
                    clear()
                    self.show_message("")
                    return
        except ValueError:
            self.show_message("Invalid input. Please try again.")
            return            
                                                        
        conn.commit()
        self.show_message("Member information updated.")
        return

    def delete_member(self):
        clear()
        member_id = input("Enter the member's ID you would like to delete: ")
        if log.is_suspicious(member_id):
            log.log(Username=self.current_user, Description="Malicious input", Additional="On member deletion", Suspicious=True)
            print("Suspicious activity detected. Please contact the administrator.")
            exit()

        if self.check_null_bytes(member_id):
            log.log(Username=self.current_user, Description="Malicious input", Additional="On member deletion", Suspicious=True)
            print("Suspicious activity detected. Please contact the administrator.")
            exit()
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
            log.log(Username=self.current_user, Description="Deleted member", Additional="Member ID: " + member_id)
            self.show_message("Member record deleted.")
        else:
            self.show_message("Delete operation cancelled.")
        return


    def search_member(self):
        clear()
        search_key = input("Enter search key: ")
        if log.is_suspicious(search_key):
            log.log(Username=self.current_user, Description="Malicious input", Additional="On member search", Suspicious=True)
            print("Suspicious activity detected. Please contact the administrator.")
            exit()
            
        if self.check_null_bytes(search_key):
            log.log(Username=self.current_user, Description="Malicious input", Additional="On member search", Suspicious=True)
            print("Suspicious activity detected. Please contact the administrator.")
            exit()    

        # Fetch all members
        cursor.execute("SELECT * FROM members")
        members = cursor.fetchall()

        matching_members: list[tuple] = []

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
                decrypted_member: tuple = (member[0], member[1], member[2], member[3], member[4], member[5], decrypted_street_name, decrypted_house_number, decrypted_zip_code, decrypted_city, decrypted_email, decrypted_phone, member[12])
                matching_members.append(decrypted_member)

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
        log.log(Username=self.current_user, Description="Viewed logs")
        log.display_logs()
        self.return_to_main_menu()

    def generate_temp_password(self):
        # Generate a random length for the password between 12 and 30
        length = random.randint(12, 30)

        # All possible characters for the password
        all_characters = string.ascii_letters + string.digits + "~!@#$%&_-+=`|\(){}[]:;'<>,.?/"

        # Create a list of character sets
        character_sets = [string.ascii_lowercase, string.ascii_uppercase, string.digits, "~!@#$%&_-+=`|\(){}[]:;'<>,.?/"]

        # Generate at least one character from each character set
        password_characters = [random.choice(char_set) for char_set in character_sets]

        # Fill the rest of the password length with random characters from all possible characters
        for i in range(length - len(character_sets)):
            password_characters.append(random.choice(all_characters))

        # Shuffle the characters so that the characters from each character set aren't at the start of the password
        random.shuffle(password_characters)

        # Convert the list of characters into a string and return it
        return ''.join(password_characters)

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
        log.log(Username=self.current_user, Description="Logged out")
        self.current_user = None
        clear()
        return  # return to main menu
    
    def check_null_bytes(self, input: str) -> str:  # function to check for null bytes
        if r'\x00' in input:
            return True
        elif "%00" in input:
            return True
        elif None == input:
            return True
        elif input is None:
            return True
        else: 
            return False
        
    def Exit(self):
        exit()
