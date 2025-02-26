import pygame

# game board
COLUMNS, ROWS = 10, 18
CELL_SIZE = 40
BOARD_WIDTH, BOARD_HEIGHT = COLUMNS * CELL_SIZE, ROWS * CELL_SIZE
PADDING = 20

# shape_colours
RED = '#e51b20'
ORANGE = '#f07e13'
YELLOW = '#f1e60d'
GREEN = '#65b32e'
BLUE = '#6cc6d9'
DARKBLUE = '#00008b'
PURPLE = '#7b217f'

# shapes
BLOCK_POSITIONS = {
    'I': {'shape': [(0, 0), (0, -1), (0, 1), (0, 2)], 'colour': BLUE},
    'J': {'shape': [(0, 0), (0, -1), (0, 1), (-1, 1)], 'colour': DARKBLUE},
    'L': {'shape': [(0, 0), (0, -1), (0, 1), (1, 1)], 'colour': ORANGE},
    'O': {'shape': [(0, 0), (0, -1), (1, 0), (1, -1)], 'colour': YELLOW},
    'S': {'shape': [(0, 0), (-1, 0), (0, -1), (1, -1)], 'colour': GREEN},
    'T': {'shape': [(0, 0), (-1, 0), (1, 0), (0, -1)], 'colour': PURPLE},
    'Z': {'shape': [(0, 0), (1, 0), (0, -1), (-1, -1)], 'colour': RED}
    }
BLOCK_OFFSET = pygame.Vector2(COLUMNS // 2, -1)

# shapes_movement
V_START_SPEED = 400
H_START_SPEED = 200
ROTATE_WAIT_TIME = 200

# score
SCORE_DATA = {1: 50, 2: 100, 3: 500, 4: 1000}

# side bar
BAR_WIDTH = 200
BAR_HEIGHT_FRACTION = 0.7
SCORE_HEIGHT_FRACTION = 1 - BAR_HEIGHT_FRACTION

# window parameters
WINDOW_WIDTH = PADDING * 3 + BAR_WIDTH + BOARD_WIDTH
WINDOW_HEIGHT = PADDING * 2 + BOARD_HEIGHT
BG_COLOUR = (50, 50, 50)

# frame rate per second
FPS = 50