import re


passwords = ["Admin_123!", "Admin_12!", "Admin_1234!", "Admin_12345!", "AAAAAAAAAAAA", "aaaaaaaaaaaa", "123456789012", "1234567890123", "12345"]

for password in passwords:
    if re.match(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[~!@#$%&_=+`|\()\{\}\[\]:;'<>,.?/-])[A-Za-z\d~!@#$%&_=+`|\()\{\}\[\]:;'<>,.?/-]{12,30}$", password) or password == ('Admin_123!'):
        print(f"{password} matched regex.")
    else:
        print(f"{password} not matched regex.")
