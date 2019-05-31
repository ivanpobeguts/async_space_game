import time
import curses
import asyncio
import random

from utils import read_rocket_frames
from curses_tools import *

ROCKET_FRAMES = read_rocket_frames('graphics/rocket')
TRASH_FRAMES = read_rocket_frames('graphics/trash')
BORDER_WIDTH = 1
TIC_TIMEOUT = 0.1
STARS_AMOUNT = random.randint(10, 100)
COROUTINES = []


async def blink(canvas, row, column, offset_tics, symbol='*'):
    """Change 'star' intensity"""

    while True:
        canvas.addstr(row, column, symbol, curses.A_DIM)
        for i in range(offset_tics):
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
            new_column = column + columns_direction
            if BORDER_WIDTH <= new_row <= max_row - row_size - BORDER_WIDTH:
                row = new_row
            if BORDER_WIDTH <= new_column <= max_col - col_size - BORDER_WIDTH:
                column = new_column
            draw_frame(canvas, round(row), round(column), frame)
            await asyncio.sleep(0)
            draw_frame(canvas, round(row), round(column), frame, negative=True)


async def fly_garbage(canvas, column, garbage_frame, speed=0.5):
    """Animate garbage, flying from top to bottom.
     Сolumn position will stay same, as specified on start."""

    rows_number, columns_number = canvas.getmaxyx()

    column = max(column, 0)
    column = min(column, columns_number - 1)

    row = 0

    while row < rows_number:
        draw_frame(canvas, row, column, garbage_frame)
        await asyncio.sleep(0)
        draw_frame(canvas, row, column, garbage_frame, negative=True)
        row += speed


async def fill_orbit_with_garbage(canvas):
    while True:
        rows_number, columns_number = canvas.getmaxyx()
        frame_num = random.randint(1, len(TRASH_FRAMES) - 1)
        garbage_coroutine = fly_garbage(canvas, random.randint(1, columns_number - 1), TRASH_FRAMES[frame_num])
        COROUTINES.append(garbage_coroutine)
        for i in range(20):
            await asyncio.sleep(0)


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

    max_row, max_col = canvas.getmaxyx()
    canvas.nodelay(True)

    COROUTINES.append(fire(canvas, max_row // 2, max_col // 2))
    COROUTINES.append(animate_spaceship(canvas, max_row // 2, max_col // 2 - 2, max_row, max_col))
    COROUTINES.append(fill_orbit_with_garbage(canvas))
    for i in range(STARS_AMOUNT):
        column = random.randint(1, max_col - 1)
        row = random.randint(1, max_row - 1)
        symbol = random.choice('+*.:')
        COROUTINES.append(blink(canvas, row, column, random.randint(0, 10), symbol))

    while COROUTINES:
        curses.curs_set(False)
        canvas.border()
        for coroutine in COROUTINES:
            try:
                coroutine.send(None)
            except StopIteration:
                COROUTINES.remove(coroutine)
            if len(COROUTINES) == 0:
                break
        canvas.refresh()
        time.sleep(TIC_TIMEOUT)


def main():
    curses.update_lines_cols()
    curses.wrapper(draw)


if __name__ == '__main__':
    main()
