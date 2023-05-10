import curses
from menu import Menu


def main():
    login_menu = Menu([("Username", None), ("Password", None)], curses.initscr(), "Login Menu")

    m = Menu([("Login", login_menu), ("Register", None)], curses.initscr(), "Main Menu")
    m.run()


if __name__ == "__main__":
    main()
