#!/usr/bin/env python3
import curses
import random
import time

BOARD_W = 10
BOARD_H = 20

PIECES = {
    'I': [[(0,0),(1,0),(2,0),(3,0)], [(0,0),(0,1),(0,2),(0,3)]],
    'O': [[(0,0),(1,0),(0,1),(1,1)]],
    'T': [[(0,0),(1,0),(2,0),(1,1)], [(0,0),(0,1),(1,1),(0,2)], [(1,0),(0,1),(1,1),(2,1)], [(1,0),(0,1),(1,1),(1,2)]],
    'S': [[(1,0),(2,0),(0,1),(1,1)], [(0,0),(0,1),(1,1),(1,2)]],
    'Z': [[(0,0),(1,0),(1,1),(2,1)], [(1,0),(0,1),(1,1),(0,2)]],
    'J': [[(0,0),(0,1),(1,1),(2,1)], [(0,0),(1,0),(0,1),(0,2)], [(0,0),(1,0),(2,0),(2,1)], [(1,0),(1,1),(0,2),(1,2)]],
    'L': [[(2,0),(0,1),(1,1),(2,1)], [(0,0),(0,1),(0,2),(1,2)], [(0,0),(1,0),(2,0),(0,1)], [(0,0),(1,0),(1,1),(1,2)]],
}

COLORS = {'I':1, 'O':2, 'T':3, 'S':4, 'Z':5, 'J':6, 'L':7}

def new_piece():
    kind = random.choice(list(PIECES.keys()))
    return {'kind': kind, 'rot': 0, 'x': BOARD_W//2 - 2, 'y': 0}

def get_cells(piece):
    cells = PIECES[piece['kind']][piece['rot'] % len(PIECES[piece['kind']])]
    return [(piece['x'] + dx, piece['y'] + dy) for dx, dy in cells]

def valid(board, piece):
    for x, y in get_cells(piece):
        if x < 0 or x >= BOARD_W or y >= BOARD_H:
            return False
        if y >= 0 and board[y][x]:
            return False
    return True

def place(board, piece):
    color = COLORS[piece['kind']]
    for x, y in get_cells(piece):
        if 0 <= y < BOARD_H:
            board[y][x] = color

def clear_lines(board):
    full = [i for i, row in enumerate(board) if all(row)]
    for i in full:
        del board[i]
        board.insert(0, [0]*BOARD_W)
    return len(full)

def draw(stdscr, board, piece, next_piece, score, level, lines, game_over, paused):
    stdscr.erase()
    h, w = stdscr.getmaxyx()

    ox = max(0, w//2 - BOARD_W - 12)
    oy = max(0, h//2 - BOARD_H//2 - 1)

    # Border
    for y in range(BOARD_H + 2):
        stdscr.addstr(oy + y, ox, '|', curses.color_pair(8))
        stdscr.addstr(oy + y, ox + BOARD_W*2 + 1, '|', curses.color_pair(8))
    stdscr.addstr(oy, ox, '+' + '-'*BOARD_W*2 + '+', curses.color_pair(8))
    stdscr.addstr(oy + BOARD_H + 1, ox, '+' + '-'*BOARD_W*2 + '+', curses.color_pair(8))

    # Board cells
    for y in range(BOARD_H):
        for x in range(BOARD_W):
            c = board[y][x]
            ch = '[]' if c else '  '
            try:
                stdscr.addstr(oy + 1 + y, ox + 1 + x*2, ch, curses.color_pair(c) | curses.A_BOLD if c else curses.color_pair(0))
            except curses.error:
                pass

    # Current piece
    if not game_over and not paused:
        color = COLORS[piece['kind']]
        for x, y in get_cells(piece):
            if 0 <= y < BOARD_H:
                try:
                    stdscr.addstr(oy + 1 + y, ox + 1 + x*2, '[]', curses.color_pair(color) | curses.A_BOLD)
                except curses.error:
                    pass

    # Ghost piece
    if not game_over and not paused:
        ghost = dict(piece)
        while valid(board, {**ghost, 'y': ghost['y']+1}):
            ghost['y'] += 1
        for x, y in get_cells(ghost):
            if 0 <= y < BOARD_H and board[y][x] == 0:
                try:
                    stdscr.addstr(oy + 1 + y, ox + 1 + x*2, '..', curses.color_pair(8))
                except curses.error:
                    pass

    # Sidebar
    sx = ox + BOARD_W*2 + 4
    try:
        stdscr.addstr(oy + 1,  sx, '┌─────────────┐', curses.color_pair(8))
        stdscr.addstr(oy + 2,  sx, '│   TETRIS    │', curses.color_pair(8) | curses.A_BOLD)
        stdscr.addstr(oy + 3,  sx, '└─────────────┘', curses.color_pair(8))
        stdscr.addstr(oy + 5,  sx, f'  Score', curses.color_pair(8))
        stdscr.addstr(oy + 6,  sx, f'  {score:<11}', curses.color_pair(2) | curses.A_BOLD)
        stdscr.addstr(oy + 8,  sx, f'  Level', curses.color_pair(8))
        stdscr.addstr(oy + 9,  sx, f'  {level:<11}', curses.color_pair(3) | curses.A_BOLD)
        stdscr.addstr(oy + 11, sx, f'  Lines', curses.color_pair(8))
        stdscr.addstr(oy + 12, sx, f'  {lines:<11}', curses.color_pair(1) | curses.A_BOLD)

        stdscr.addstr(oy + 14, sx, '  Next:', curses.color_pair(8))
        # Draw next piece preview
        np_cells = PIECES[next_piece['kind']][0]
        nc = COLORS[next_piece['kind']]
        for dx, dy in np_cells:
            try:
                stdscr.addstr(oy + 16 + dy, sx + 2 + dx*2, '[]', curses.color_pair(nc) | curses.A_BOLD)
            except curses.error:
                pass

        stdscr.addstr(oy + 20, sx, '  Controls:', curses.color_pair(8))
        stdscr.addstr(oy + 21, sx, '  ←→  move', curses.color_pair(8))
        stdscr.addstr(oy + 22, sx, '  ↑   rotate', curses.color_pair(8))
        stdscr.addstr(oy + 23, sx, '  ↓   soft drop', curses.color_pair(8))
        stdscr.addstr(oy + 24, sx, '  SPC hard drop', curses.color_pair(8))
        stdscr.addstr(oy + 25, sx, '  P   pause', curses.color_pair(8))
        stdscr.addstr(oy + 26, sx, '  Q   quit', curses.color_pair(8))
    except curses.error:
        pass

    if paused:
        msg = '  PAUSED  '
        try:
            stdscr.addstr(oy + BOARD_H//2, ox + BOARD_W - len(msg)//2, msg, curses.color_pair(2) | curses.A_BOLD | curses.A_REVERSE)
        except curses.error:
            pass

    if game_over:
        msgs = ['GAME OVER', f'Score: {score}', 'R - restart', 'Q - quit']
        for i, m in enumerate(msgs):
            try:
                stdscr.addstr(oy + BOARD_H//2 - 1 + i, ox + BOARD_W - len(m)//2 + 1, m,
                              curses.color_pair(5) | curses.A_BOLD | curses.A_REVERSE)
            except curses.error:
                pass

    stdscr.refresh()

def init_colors():
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_CYAN,    -1)  # I
    curses.init_pair(2, curses.COLOR_YELLOW,  -1)  # O
    curses.init_pair(3, curses.COLOR_MAGENTA, -1)  # T
    curses.init_pair(4, curses.COLOR_GREEN,   -1)  # S
    curses.init_pair(5, curses.COLOR_RED,     -1)  # Z
    curses.init_pair(6, curses.COLOR_BLUE,    -1)  # J
    curses.init_pair(7, curses.COLOR_WHITE,   -1)  # L
    curses.init_pair(8, curses.COLOR_WHITE,   -1)  # UI

SCORES = {0:0, 1:100, 2:300, 3:500, 4:800}

def main(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.keypad(True)
    init_colors()

    def start_game():
        board = [[0]*BOARD_W for _ in range(BOARD_H)]
        piece = new_piece()
        nxt = new_piece()
        return board, piece, nxt, 0, 1, 0, False, False

    board, piece, nxt, score, level, lines, game_over, paused = start_game()
    drop_interval = 0.5
    last_drop = time.time()

    while True:
        now = time.time()
        key = stdscr.getch()

        if key == ord('q') or key == ord('Q'):
            break

        if game_over:
            if key == ord('r') or key == ord('R'):
                board, piece, nxt, score, level, lines, game_over, paused = start_game()
                drop_interval = 0.5
                last_drop = time.time()
        else:
            if key == ord('p') or key == ord('P'):
                paused = not paused
                if not paused:
                    last_drop = time.time()

            if not paused:
                moved = dict(piece)
                if key == curses.KEY_LEFT:
                    moved['x'] -= 1
                    if valid(board, moved): piece = moved
                elif key == curses.KEY_RIGHT:
                    moved['x'] += 1
                    if valid(board, moved): piece = moved
                elif key == curses.KEY_UP:
                    moved['rot'] = (piece['rot'] + 1) % len(PIECES[piece['kind']])
                    if valid(board, moved): piece = moved
                elif key == curses.KEY_DOWN:
                    moved['y'] += 1
                    if valid(board, moved):
                        piece = moved
                        last_drop = now
                elif key == ord(' '):
                    while valid(board, {**piece, 'y': piece['y']+1}):
                        piece['y'] += 1
                    place(board, piece)
                    cleared = clear_lines(board)
                    lines += cleared
                    score += SCORES[cleared] * level
                    level = lines // 10 + 1
                    drop_interval = max(0.05, 0.5 - (level-1)*0.04)
                    piece = nxt
                    nxt = new_piece()
                    if not valid(board, piece):
                        game_over = True
                    last_drop = now

                # Gravity
                if not game_over and now - last_drop >= drop_interval:
                    down = {**piece, 'y': piece['y']+1}
                    if valid(board, down):
                        piece = down
                    else:
                        place(board, piece)
                        cleared = clear_lines(board)
                        lines += cleared
                        score += SCORES[cleared] * level
                        level = lines // 10 + 1
                        drop_interval = max(0.05, 0.5 - (level-1)*0.04)
                        piece = nxt
                        nxt = new_piece()
                        if not valid(board, piece):
                            game_over = True
                    last_drop = now

        draw(stdscr, board, piece, nxt, score, level, lines, game_over, paused)
        time.sleep(0.016)

if __name__ == '__main__':
    curses.wrapper(main)
