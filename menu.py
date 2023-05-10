import curses


class Menu:
    def __init__(self, items, stdscreen, title):
        self.current_row_idx = None
        self.title = title
        self.window = stdscreen.subwin(0, 0)
        self.window.keypad(1)
        self.items = items
        self.items.append(('exit', 'exit'))

    def display_menu(self):
        self.window.clear()
        self.window.border(0)
        self.window.addstr(2, 2, self.title)
        if self.title == "Main Menu":
            self.window.addstr(4, 2, 'Use arrow keys to navigate')
            self.window.addstr(5, 2, 'Press Enter to select an option')

        # Display menu items
        for index, item in enumerate(self.items):
            if index == self.current_row_idx:
                mode = curses.A_REVERSE
            else:
                mode = curses.A_NORMAL

            msg = '%d. %s' % (index, item[0])
            self.window.addstr(6 + index, 4, msg, mode)

        self.window.refresh()

    def run(self):
        self.current_row_idx = 0

        # Loop until user selects a menu item
        while True:
            self.display_menu()
            key = self.window.getch()

            if key in [curses.KEY_ENTER, ord('\n')]:
                if self.current_row_idx == len(self.items) - 1:
                    break
                else:
                    self.items[self.current_row_idx][1].run()

            elif key == curses.KEY_UP:
                self.current_row_idx = (self.current_row_idx - 1) % len(self.items)

            elif key == curses.KEY_DOWN:
                self.current_row_idx = (self.current_row_idx + 1) % len(self.items)

    def get_input(self):
        curses.echo()
        user_input = self.window.getstr(7, 2, 60)
        curses.noecho()
        return user_input




