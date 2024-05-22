import curses
import time


def main(stdscr):
    # Specify the key you want to count. 
    # For example, ord('a') for the 'a' key. 
    # Use curses.KEY_* for special keys like F1, Arrow keys etc.

    # Set up the screen
    curses.curs_set(0)  # Hide the cursor
    stdscr.nodelay(1)  # Don't block on getch()
    stdscr.clear()     # Clear the screen

    count = 0
    total = 0
    last_time = time.time()
    diffs = []

    while True:
        # Display the count
        stdscr.clear()
        if total == 0:
            stdscr.addstr(2, 5, f"Press any key to start counting.")
        else:
            stdscr.addstr(2, 5, f"Repeats {count / total * 100:.2f}% times.")
        stdscr.refresh()

        # Get the key pressed
        key = stdscr.getch()

        # Check if the key is the one we're counting
        if key != -1:
            diff = time.time() - last_time
            last_time = time.time()
            if diff < 0.1:
                count += 1
            total += 1

        # if esc, reset
        if key == 27:
            count = 0
            total = 0
            
# Run the curses application
curses.wrapper(main)

