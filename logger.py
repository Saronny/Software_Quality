import os
from datetime import datetime
from typing import Optional
import textwrap

import re # For checking if string is suspicious

import rsa
import binascii

class logger:
    _instance = None
    public_key, private_key = None, None
    latest_log: int = 0

    def __new__(self):
        if not self._instance:
            self._instance = super().__new__(self)
        return self._instance
    
    def __init__(self):
        # Create the logs folder and file
        if not os.path.exists("logs"):
            os.mkdir("logs")
        
        if not os.path.exists("logs/log.txt"):
            now = datetime.now()
            current_time = now.strftime("%Y-%m-%d %H:%M:%S")
            with open("logs/log.txt", "w") as f:
                f.write(f"CREATED LOG FILE at {current_time}\n")

        # Set latest log
        with open("logs/log.txt", "r") as f:
            last_line: str = f.readlines()[-1]
            firstchars: str = last_line.split(",")[0]
            if firstchars.isdigit():
                self.latest_log = int(firstchars)

        # Get/generate RSA key
        if os.path.exists("./public.pem") and os.path.exists("./private.pem"):
            with open("./public.pem", 'rb') as f:
                self.public_key = rsa.PublicKey.load_pkcs1(f.read())
            with open("./private.pem", 'rb') as f:
                self.private_key = rsa.PrivateKey.load_pkcs1(f.read())
            
        else:
            self.public_key, self.private_key = rsa.newkeys(512)
            with open("./public.pem", 'wb') as f:
                f.write(self.public_key.save_pkcs1())
            with open("./private.pem", 'wb') as f:
                f.write(self.private_key.save_pkcs1())
                print("Keys generated")

    def is_suspicious(self, message: str) -> bool:
        # Check if the message is suspicious
        # Suspicious messages are messages that contain a lot of non-alphanumeric characters
        # This is to prevent SQL injection and other attacks
        # If the message is suspicious, log it and return True
        # If the message is not suspicious, return False
        sql_injection_pattern = re.compile(r"['\"].*? OR .*?['\"]", re.IGNORECASE)
        escape_character_pattern = re.compile(r"\\[0-7]{1,3}")

        if re.search(sql_injection_pattern, message) or re.search(escape_character_pattern, message):
            return True
        else:
            return False

    def __encrypt(self, message: Optional[str]) -> str:
        if message is None:
            return None
        message: str = message.encode('utf-8') # Encode to bytes

        # Split into chunks to avoid an overflow error with large messages
        max_chunk_size: int = 53
        chunks: list[str | any] = [message[i:i+max_chunk_size] for i in range(0, len(message), max_chunk_size)]

        # Encrypt each chunk and join them together
        encrypted_chunks: list[bytes] = [rsa.encrypt(chunk, self.public_key) for chunk in chunks]
        encrypted_message: bytes = b''.join(encrypted_chunks)
        return binascii.hexlify(encrypted_message).decode() # Hexlify to make it store as hex string
    
    def __decrypt(self, message: Optional[str]) -> str:
        if message is None:
            return None
        try:
            # Unhexlify to convert the hex string back to bytes
            message = binascii.unhexlify(message)
            
            # Split into chunks to avoid an overflow error with large messages (64 should be the chunk size for 512 bit keys)
            max_chunk_size = 64  
            chunks = [message[i:i+max_chunk_size] for i in range(0, len(message), max_chunk_size)]

            # Decrypt each chunk and join them together
            decrypted_chunks = [rsa.decrypt(chunk, self.private_key) for chunk in chunks]
            # Join the decrypted chunks together and decode them to get the original message
            decrypted_message = b''.join(decrypted_chunks).decode('utf-8')

        except (ValueError, rsa.DecryptionError):
            # If the message is not a hex string or the decryption fails, return the original message
            decrypted_message = message

        return decrypted_message

    def log(self, Username: Optional[str] = None, Description: Optional[str] = None, Additional: Optional[str] = None, Suspicious: bool = False) -> None:
        """Usage:
        All field are set to null or false. 
        Change field using, for example, log(Username=username, Description="example"). This will set the username and description, Suspicious flag is set to false, the remaining fields remain null"""
        self.latest_log = self.latest_log + 1
        date = datetime.now().strftime("%d-%m-%Y")
        time = datetime.now().strftime("%H:%M:%S")
        # with open("logs/log.txt", "a") as f:
        #     f.write(f"{self.latest_log},{self.__encrypt(Username)},{self.__encrypt(Description)},{self.__encrypt(Additional)},{Suspicious}\n")
        with open("logs/log.txt", "a") as f:
            f.write(f"{self.latest_log},{date},{time},{self.__encrypt(Username)},{self.__encrypt(Description)},{self.__encrypt(Additional)},{Suspicious}\n")

    def display_logs(self):
        """Provides a clear and organized way to display the log entries stored in the log file"""
        # field_widths = [7, 22, 32, 34, 12]
        # header = ['ID', 'Username', 'Description', 'Additional', 'Suspicious']
        field_widths = [7, 12, 10, 22, 32, 34, 12]
        header = ['ID', 'Date', 'Time', 'Username', 'Description', 'Additional', 'Suspicious']

        # Print out header
        print('+-' + '-+-'.join('-' * (width - 2) for width in field_widths) + '-+')
        print('|' + '|'.join(name.center(width) for name, width in zip(header, field_widths)) + '|')
        print('+-' + '-+-'.join('-' * (width - 2) for width in field_widths) + '-+')

        # Iterate through log entries
        with open('logs/log.txt', 'r') as f:
            for line in f:
                # Filter out the first line
                if line.startswith('CREATED LOG FILE'):
                    continue

                # Get the values from the line
                log_id, date, time, enc_username, enc_description, enc_additional, suspicious = line.strip().split(',')
                # Decrypt the values
                username: str = self.__decrypt(enc_username) or ''
                description: str = self.__decrypt(enc_description) or ''
                additional: str = self.__decrypt(enc_additional) or ''

                # Wrap each field to fit the column width
                row: list[str] = [str(log_id), date, time, username, description, additional, suspicious]
                try:
                    wrapped_row: list[list[str]] = [textwrap.wrap(value, width-2) for value, width in zip(row, field_widths)] # zip to iterate through each field and its width
                except TypeError:
                    # If the value is not a string, just use the original value (the wrong key was probably used to decrypt)
                    wrapped_row: list[list[str]] = [[value] for value in row]

                # Get the maximum number of lines in this row
                max_lines: int = max(len(cell) for cell in wrapped_row)
                
                # Make sure each cell in the row has the same number of lines
                for cell in wrapped_row:
                    cell += [''] * (max_lines - len(cell))
                
                # Print out each line of the row
                for i in range(max_lines):
                    try:
                        print('|' + '|'.join(cell[i].center(width) for cell, width in zip(wrapped_row, field_widths)) + '|')
                    except TypeError:
                        # If the value is not a string, just use the original value (the wrong key was probably used to decrypt)
                        print('|' + '|'.join(str(cell[i]).center(width) for cell, width in zip(wrapped_row, field_widths)) + '|')
                
                # Print out the row separator
                print('+-' + '-+-'.join('-' * (width - 2) for width in field_widths) + '-+')

# # dummy log entries
# logger.log(Username="User1", Description="Logged into the system", Additional=None, Suspicious=False)

# logger.log(Username="User2", Description="Tried to access a restricted page", Additional="IP: 123.456.789.012", Suspicious=True)

# long_description = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec tincidunt, nibh nec convallis aliquam, turpis orci viverra metus, a dictum ipsum magna a sem. Mauris ac mauris a purus malesuada consectetur. Nulla facilisi. Etiam dignissim diam eget mi."
# logger.log(Username="User3", Description=long_description, Additional=None, Suspicious=False)

# logger.log(Username="User4", Description="Submitted a form", Additional="Form ID: 1234", Suspicious=False)

# logger.log(Username="User5", Description="Logged out", Additional=None, Suspicious=False)

# logger.display_logs()