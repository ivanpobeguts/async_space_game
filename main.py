import time
import curses
import asyncio
import random

from utils import read_rocket_frames

ROCKET_FRAMES = read_rocket_frames('graphics')


def draw_frame(canvas, start_row, start_column, text, negative=False):
    """Draw multiline text fragment on canvas.
     Erase text instead of drawing if negative=True is specified."""

    rows_number, columns_number = canvas.getmaxyx()

    for row, line in enumerate(text.splitlines(), round(start_row)):
        if row < 0:
            continue

        if row >= rows_number:
            break

        for column, symbol in enumerate(line, round(start_column)):
            if column < 0:
                continue

            if column >= columns_number:
                break

            if symbol == ' ':
                continue

            # Check that current position it is not in a lower right corner of the window
            # Curses will raise exception in that case. Don`t ask why…
            # https://docs.python.org/3/library/curses.html#curses.window.addch
            if row == rows_number - 1 and column == columns_number - 1:
                continue

            symbol = symbol if not negative else ' '
            canvas.addch(row, column, symbol)


async def blink(canvas, row, column, symbol='*'):
    delay = random.randint(0, 10)
    while True:
        canvas.addstr(row, column, symbol, curses.A_DIM)
        for i in range(delay):
            await asyncio.sleep(0)
        for i in range(20):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol)
        for i in range(3):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol, curses.A_BOLD)
        for i in range(5):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol)
        for i in range(3):
            await asyncio.sleep(0)


async def animate_spaceship(canvas, start_row, start_column):
    while True:
        for frame in ROCKET_FRAMES:
            draw_frame(canvas, start_row, start_column, frame)
            await asyncio.sleep(0)
            draw_frame(canvas, start_row, start_column, frame, negative=True)


async def fire(canvas, start_row, start_column, rows_speed=-0.3, columns_speed=0):
    """Display animation of gun shot. Direction and speed can be specified."""

    row, column = start_row, start_column

    canvas.addstr(round(row), round(column), '*')
    await asyncio.sleep(0)

    canvas.addstr(round(row), round(column), 'O')
    await asyncio.sleep(0)
    canvas.addstr(round(row), round(column), ' ')

    row += rows_speed
    column += columns_speed

    symbol = '-' if columns_speed else '|'

    rows, columns = canvas.getmaxyx()
    max_row, max_column = rows - 1, columns - 1

    curses.beep()

    while 0 < row < max_row and 0 < column < max_column:
        canvas.addstr(round(row), round(column), symbol)
        await asyncio.sleep(0)
        canvas.addstr(round(row), round(column), ' ')
        row += rows_speed
    column += columns_speed


def draw(canvas):
    # row, column = (5, 20)
    TIC_TIMEOUT = 0.1
    coroutines = []
    max_row, max_col = canvas.getmaxyx()
    limit = random.randint(10, 100)
    coroutines.append(fire(canvas, max_row / 2, max_col / 2))
    coroutines.append(animate_spaceship(canvas, max_row / 2, max_col / 2 - 2))
    for i in range(limit):
        column = random.randint(1, max_col - 1)
        row = random.randint(1, max_row - 1)
        symbol = random.choice('+*.:')
        coroutines.append(blink(canvas, row, column, symbol))
    while True:
        curses.curs_set(False)
        canvas.border()
        for coroutine in coroutines:
            try:
                coroutine.send(None)
            except StopIteration:
                coroutines.remove(coroutine)
            if len(coroutines) == 0:
                break
        canvas.refresh()
        time.sleep(TIC_TIMEOUT)


if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw)
