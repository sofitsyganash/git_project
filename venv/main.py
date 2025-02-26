import pygame
import sys
from random import choice
from pygame.image import load
from os import path
from settings import *


class Tetris:
    def __init__(self):
        # general
        pygame.init()
        pygame.display.set_caption('Tetris')
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.clock = pygame.time.Clock()

        # next shapes
        self.next_shapes = [choice(list(BLOCK_POSITIONS.keys())) for shape in range(3)]

        # components (game_board, preview, score)
        self.board = GameBoard(self.get_next_shape, self.update_score)
        self.score = Score()
        self.preview = Preview()

    def update_score(self, lines, score, level):
        self.score.lines = lines
        self.score.score = score
        self.score.level = level

    def get_next_shape(self):
        next_shape = self.next_shapes.pop(0)
        self.next_shapes.append(choice(list(BLOCK_POSITIONS.keys())))
        return next_shape

    def run(self):

        # main game loop
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            # display main surface
            self.display_surface.fill((BG_COLOUR))

            # display components (game_board, preview, score)
            self.board.run()
            self.score.run()
            self.preview.run(self.next_shapes)

            # frames update
            pygame.display.update()
            self.clock.tick(FPS)


class GameBoard:
    def __init__(self, get_next_shape, update_score):
        # general
        self.surface = pygame.Surface((BOARD_WIDTH, BOARD_HEIGHT))
        self.display_surface = pygame.display.get_surface()
        self.rect = self.surface.get_rect(topleft=(PADDING, PADDING))
        self.sprites = pygame.sprite.Group()
        self.update_score = update_score

        # shapes
        self.get_next_shape = get_next_shape
        self.field_data = [[0 for x in range(COLUMNS)] for y in range(ROWS)]
        self.shape = Shapes(
            choice(list(BLOCK_POSITIONS.keys())),
            self.sprites,
            self.create_new_shape,
            self.field_data)

        # timer
        self.down_speed = V_START_SPEED
        self.down_speed_faster = self.down_speed * 0.3
        self.down_pressed = False
        self.timers = {
            'vertical move': Timer(V_START_SPEED, True, self.move_down),
            'horizontal move': Timer(H_START_SPEED),
            'rotate': Timer(ROTATE_WAIT_TIME)
        }
        self.timers['vertical move'].activate()

        # score
        self.current_level = 1
        self.current_score = 0
        self.current_lines = 0

    def check_game_over(self):
        for block in self.shape.blocks:
            if block.pos.y <= 0:
                sys.exit()

    def calculate_score(self, num_lines):
        self.current_lines += num_lines
        self.current_score += SCORE_DATA[num_lines] * self.current_level

        # every 10 lines += level
        if self.current_lines / 10 > self.current_level:
            self.current_level += 1
            self.timers['vertical move'].duration *= 0.7
        self.update_score(self.current_lines, self.current_score, self.current_level)

    def create_new_shape(self):
        self.check_game_over()
        self.check_finished_rows()
        self.shape = Shapes(self.get_next_shape(),
                            self.sprites,
                            self.create_new_shape,
                            self.field_data)

    def timer_update(self):
        for timer in self.timers.values():
            timer.update()

    def move_down(self):
        self.shape.move_down()

    def render(self):
        for i in range(ROWS):
            for j in range(COLUMNS):
                pygame.draw.rect(self.surface, (80, 80, 80), (j * CELL_SIZE, i * CELL_SIZE,
                                                              CELL_SIZE, CELL_SIZE), 1)

    def input(self):
        keys = pygame.key.get_pressed()

        # checking horizontal movement
        if not self.timers['horizontal move'].active:
            if keys[pygame.K_LEFT]:
                self.shape.move_horizontal(-1)
                self.timers['horizontal move'].activate()
            if keys[pygame.K_RIGHT]:
                self.shape.move_horizontal(1)
                self.timers['horizontal move'].activate()

        # check for rotation
        if not self.timers['rotate'].active:
            if keys[pygame.K_UP]:
                self.shape.rotate()
                self.timers['rotate'].activate()

        # down speedup
        if not self.down_pressed and keys[pygame.K_DOWN]:
            self.down_pressed = True
            self.timers['vertical move'].duration = self.down_speed_faster

        if self.down_pressed and not keys[pygame.K_DOWN]:
            self.down_pressed = False
            self.timers['vertical move'].duration = self.down_speed

    def check_finished_rows(self):
        # get the full row indexes
        delete_rows = []
        for i, row in enumerate(self.field_data):
            if all(row):
                delete_rows.append(i)

        if delete_rows:

            for delete_row in delete_rows:

                # delete full rows
                for block in self.field_data[delete_row]:
                    block.kill()

                # move down blocks
                for row in self.field_data:
                    for block in row:
                        if block and block.pos.y < delete_row:
                            block.pos.y += 1

            # rebuild the field_data
            self.field_data = [[0 for x in range(COLUMNS)] for y in range(ROWS)]

            for block in self.sprites:
                self.field_data[int(block.pos.y)][int(block.pos.x)] = block

            # update score
            self.calculate_score(len(delete_rows))

    def run(self):
        # update
        self.input()
        self.timer_update()
        self.sprites.update()

        # drawing
        self.surface.fill('black')
        self.sprites.draw(self.surface)

        self.render()
        self.display_surface.blit(self.surface, (PADDING, PADDING))
        pygame.draw.rect(self.display_surface, (150, 150, 150), self.rect, 2, 2)


class Score:
    def __init__(self):
        # general
        self.surface = pygame.Surface((BAR_WIDTH, BOARD_HEIGHT * SCORE_HEIGHT_FRACTION - PADDING))
        self.display_surface = pygame.display.get_surface()
        self.rect = self.surface.get_rect(bottomright=(WINDOW_WIDTH - PADDING, WINDOW_HEIGHT - PADDING))

        # font
        self.font = pygame.font.Font(None, 30)

        # increment
        self.increment_height = self.surface.get_height() / 3

        # data
        self.score = 0
        self.level = 1
        self.lines = 0

    def display_text(self, pos, text):
        text_surface = self.font.render(f'{text[0]}: {text[1]}', True, 'white')
        text_rect = text_surface.get_rect(center=pos)
        self.surface.blit(text_surface, text_rect)

    def run(self):
        self.surface.fill('black')
        for i, text in enumerate([('Score', self.score), ('Level', self.level), ('Lines', self.lines)]):
            x = self.surface.get_width() / 2
            y = self.increment_height / 2 + i * self.increment_height
            self.display_text((x, y), text)

        self.display_surface.blit(self.surface, self.rect)
        pygame.draw.rect(self.display_surface, (150, 150, 150), self.rect, 2, 2)


class Preview:
    def __init__(self):
        # general
        self.surface = pygame.Surface((BAR_WIDTH, BOARD_HEIGHT * BAR_HEIGHT_FRACTION))
        self.display_surface = pygame.display.get_surface()
        self.rect = self.surface.get_rect(topright=(WINDOW_WIDTH - PADDING, PADDING))

        # shapes
        self.shape_surfaces = {shape: self.load_image(f'{shape}.png').convert_alpha() for shape in
                               BLOCK_POSITIONS.keys()}

        # image position data
        self.increment_height = self.surface.get_height() / 3

    def load_image(self, name):
        fullname = path.join('images', name)
        image = pygame.image.load(fullname)
        return image

    def display_shapes(self, shapes):
        for i, shape in enumerate(shapes):
            shape_surface = self.shape_surfaces[shape]
            x = self.surface.get_width() / 2
            y = self.increment_height / 2 + i * self.increment_height
            rect = shape_surface.get_rect(center=(x, y))
            self.surface.blit(shape_surface, rect)

    def run(self, next_shapes):
        self.surface.fill('black')
        self.display_shapes(next_shapes)
        self.display_surface.blit(self.surface, self.rect)
        pygame.draw.rect(self.display_surface, (150, 150, 150), self.rect, 2, 2)


class Shapes:
    def __init__(self, shape, group, create_new_shape, field_data):
        # set up
        self.shape = shape
        self.block_positions = BLOCK_POSITIONS[shape]['shape']
        self.colour = BLOCK_POSITIONS[shape]['colour']
        self.create_new_shape = create_new_shape
        self.field_data = field_data

        # create shape
        self.blocks = [Block(group, pos, self.colour) for pos in self.block_positions]

    # collisions
    def next_move_horizontal_collide(self, blocks, n):
        collision_list = [block.horizontal_collide(int(block.pos.x + n), self.field_data) for block in self.blocks]
        return True if any(collision_list) else False

    def next_move_vertical_collide(self, blocks, n):
        collision_list = [block.vertical_collide(int(block.pos.y + n), self.field_data) for block in self.blocks]
        return True if any(collision_list) else False

    def move_down(self):
        if not self.next_move_vertical_collide(self.blocks, 1):
            for block in self.blocks:
                block.pos.y += 1
        else:
            for block in self.blocks:
                self.field_data[int(block.pos.y)][int(block.pos.x)] = block
            self.create_new_shape()

    def move_horizontal(self, n):
        if not self.next_move_horizontal_collide(self.blocks, n):
            for block in self.blocks:
                block.pos.x += n

    def rotate(self):
        if self.shape != 'O':
            # center
            center_pos = self.blocks[0].pos

            # new block positions
            new_block_positions = [block.rotate(center_pos) for block in self.blocks]

            # collision check
            for pos in new_block_positions:
                # horizontal
                if pos.x < 0 or pos.x >= COLUMNS:
                    return

                # vertical
                if pos.y >= ROWS:
                    return

                # with other shapes
                if self.field_data[int(pos.y)][int(pos.x)]:
                    return

            # set new positions
            for i, block in enumerate(self.blocks):
                block.pos = new_block_positions[i]


class Block(pygame.sprite.Sprite):
    def __init__(self, group, pos, colour):
        # general
        super().__init__(group)
        self.image = pygame.Surface((CELL_SIZE, CELL_SIZE))
        self.image.fill(colour)

        # position
        self.pos = pygame.Vector2(pos) + BLOCK_OFFSET
        x = self.pos.x * CELL_SIZE
        y = self.pos.y * CELL_SIZE
        self.rect = self.image.get_rect(topleft=(x, y))

    def rotate(self, center_pos):
        return center_pos + (self.pos - center_pos).rotate(90)

    def horizontal_collide(self, x, field_data):
        if not 0 <= x <= COLUMNS - 1:
            return True

        if field_data[int(self.pos.y)][x]:
            return True

    def vertical_collide(self, y, field_data):
        if y >= ROWS:
            return True

        if y >= 0 and field_data[y][int(self.pos.x)]:
            return True

    def update(self):
        # self.pos -> rect
        self.rect.topleft = self.pos * CELL_SIZE


class Timer:
    def __init__(self, duration, repeated=False, func=None):
        self.duration = duration
        self.repeated = repeated
        self.func = func

        self.start_time = 0
        self.active = False

    def activate(self):
        self.active = True
        self.start_time = pygame.time.get_ticks()

    def deactivate(self):
        self.active = False
        self.start_time = 0

    def update(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.start_time >= self.duration and self.active:
            # call a function
            if self.func and self.start_time != 0:
                self.func()

            # reset timer
            self.deactivate()

            # repeat the timer
            if self.repeated:
                self.activate()


if __name__ == '__main__':
    game = Tetris()
    game.run()