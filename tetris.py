import pygame
import sys
import random

# NES-like + new colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
CYAN = (88, 248, 252)
BLUE = (0, 88, 248)
ORANGE = (252, 152, 56)
YELLOW = (252, 224, 168)
GREEN = (0, 168, 0)
PURPLE = (216, 0, 204)
RED = (228, 0, 88)
GREY = (200, 200, 200)
DARK_GREY = (50, 50, 50)

# Tetrimino shapes
TETROMINOS = {
    'I': [[1, 1, 1, 1]],
    'O': [[1, 1], [1, 1]],
    'T': [[0,1,0],[1,1,1]],
    'S': [[0,1,1],[1,1,0]],
    'Z': [[1,1,0],[0,1,1]],
    'J': [[1,0,0],[1,1,1]],
    'L': [[0,0,1],[1,1,1]]
}

# Map piece to color
COLORS = {
    'I': CYAN,
    'O': YELLOW,
    'T': PURPLE,
    'S': GREEN,
    'Z': RED,
    'J': BLUE,
    'L': ORANGE
}

# Grid size
CELL = 30  # bigger cells
COLS = 10
ROWS = 20
SIDE_WIDTH = 200
BORDER = 5
WIDTH = COLS * CELL + SIDE_WIDTH + BORDER*2
HEIGHT = ROWS * CELL + BORDER*2

# Init
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
font = pygame.font.SysFont("Times New Roman", 24)

# Empty grid
grid = [[None for _ in range(COLS)] for _ in range(ROWS)]

# Current and next piece
def new_piece():
    kind = random.choice(list(TETROMINOS.keys()))
    shape = TETROMINOS[kind]
    color = COLORS[kind]
    return {'shape': shape, 'x': COLS//2-2, 'y': 0, 'color': color, 'kind': kind}

piece = new_piece()
next_piece = new_piece()

fall_time = 0
fall_speed = 500  # ms
score = 0

def rotate(shape):
    return [ [shape[y][x] for y in range(len(shape))][::-1] for x in range(len(shape[0])) ]

def valid(posx, posy, shape):
    for y, row in enumerate(shape):
        for x, cell in enumerate(row):
            if cell:
                if x + posx < 0 or x + posx >= COLS or y + posy >= ROWS:
                    return False
                if y + posy >= 0 and grid[y + posy][x + posx]:
                    return False
    return True

def lock(piece):
    for y, row in enumerate(piece['shape']):
        for x, cell in enumerate(row):
            if cell and y + piece['y'] >= 0:
                grid[y + piece['y']][x + piece['x']] = piece['color']

def clear_lines():
    global grid, score
    lines = 0
    new_grid = []
    for row in grid:
        if all(cell is not None for cell in row):
            lines += 1
        else:
            new_grid.append(row)
    for _ in range(lines):
        new_grid.insert(0, [None for _ in range(COLS)])
    grid = new_grid
    score += lines * 100

# Draw block with border
def draw_block(px, py, color):
    for dy in range(CELL):
        for dx in range(CELL):
            screen.set_at((px+dx, py+dy), color)
    # draw block border (black outline)
    for i in range(CELL):
        screen.set_at((px+i, py), BLACK)
        screen.set_at((px+i, py+CELL-1), BLACK)
        screen.set_at((px, py+i), BLACK)
        screen.set_at((px+CELL-1, py+i), BLACK)

# Game loop
while True:
    dt = clock.tick(60)
    fall_time += dt

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # Controls
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        if valid(piece['x']-1, piece['y'], piece['shape']):
            piece['x'] -= 1
    if keys[pygame.K_RIGHT]:
        if valid(piece['x']+1, piece['y'], piece['shape']):
            piece['x'] += 1
    if keys[pygame.K_DOWN]:
        if valid(piece['x'], piece['y']+1, piece['shape']):
            piece['y'] += 1
            fall_time = 0
    if keys[pygame.K_UP]:
        r = rotate(piece['shape'])
        if valid(piece['x'], piece['y'], r):
            piece['shape'] = r

    # Piece falling
    if fall_time > fall_speed:
        fall_time = 0
        if valid(piece['x'], piece['y']+1, piece['shape']):
            piece['y'] += 1
        else:
            lock(piece)
            clear_lines()
            piece = next_piece
            next_piece = new_piece()
            if not valid(piece['x'], piece['y'], piece['shape']):
                pygame.quit()
                sys.exit()

    # Draw
    screen.fill(GREY)

    # Draw dark grey playfield
    pygame.draw.rect(screen, DARK_GREY, (BORDER, BORDER, COLS*CELL, ROWS*CELL))

    # Draw grid
    for y in range(ROWS):
        for x in range(COLS):
            if grid[y][x]:
                draw_block(BORDER+x*CELL, BORDER+y*CELL, grid[y][x])

    # Draw current piece
    for y, row in enumerate(piece['shape']):
        for x, cell in enumerate(row):
            if cell:
                draw_block(BORDER+(piece['x']+x)*CELL, BORDER+(piece['y']+y)*CELL, piece['color'])

    # Draw next piece preview
    np_shape = next_piece['shape']
    np_color = next_piece['color']
    np_x = COLS*CELL + BORDER + 30
    np_y = 80
    for y, row in enumerate(np_shape):
        for x, cell in enumerate(row):
            if cell:
                draw_block(np_x + x*CELL, np_y + y*CELL, np_color)

    # Draw score
    score_text = font.render(f"Score: {score}", True, BLACK)
    screen.blit(score_text, (COLS*CELL + BORDER + 20, 20))

    # Draw border around playfield
    pygame.draw.rect(screen, BLACK, (BORDER-2, BORDER-2, COLS*CELL+4, ROWS*CELL+4), 4)

    pygame.display.flip()
