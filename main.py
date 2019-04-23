import time
import curses
import asyncio
import random

from utils import read_rocket_frames
from curses_tools import *

ROCKET_FRAMES = read_rocket_frames('graphics')
BORDER_WIDTH = 1


async def blink(canvas, row, column, symbol='*'):
    """Change 'star' intensity"""

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


async def animate_spaceship(canvas, row, column, max_row, max_col):
    """Animate spaceship according to the user input"""

    row_size, col_size = get_frame_size(ROCKET_FRAMES[0])

    while True:
        for frame in ROCKET_FRAMES:
            rows_direction, columns_direction, _ = read_controls(canvas)
            new_row = row + rows_direction
            new_column = column + 2 * columns_direction
            if BORDER_WIDTH <= new_row <= max_row - row_size - BORDER_WIDTH:
                row = new_row
            if BORDER_WIDTH <= new_column <= max_col - col_size + 1 - BORDER_WIDTH:
                column = new_column
            draw_frame(canvas, row, column, frame)
            await asyncio.sleep(0)
            draw_frame(canvas, row, column, frame, negative=True)


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
    """Start main loop for coroutines and draw all graphics"""

    TIC_TIMEOUT = 0.1
    coroutines = []
    max_row, max_col = canvas.getmaxyx()
    limit = random.randint(10, 100)
    canvas.nodelay(True)

    coroutines.append(fire(canvas, max_row / 2, max_col / 2))
    coroutines.append(animate_spaceship(canvas, max_row / 2, max_col / 2 - 2, max_row, max_col))
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
