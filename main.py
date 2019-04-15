import time
import curses
import asyncio
import random
# test comment

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
    row, column = (5, 20)
    TIC_TIMEOUT = 0.1
    coroutines = []
    max_row, max_col = canvas.getmaxyx()
    limit = random.randint(10, 100)
    coroutines.append(fire(canvas, max_row / 2, max_col / 2))
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