import pygame
import random

CELL_SIZE = 30
COLS = 10
ROWS = 20
LEFT_PANEL = 120
RIGHT_PANEL = 180
WIDTH = CELL_SIZE * COLS
HEIGHT = CELL_SIZE * ROWS

SHAPES = [
    [[1, 1, 1, 1]],  # I
    [[1, 1], [1, 1]],  # O
    [[0, 1, 0], [1, 1, 1]],  # T
    [[1, 1, 0], [0, 1, 1]],  # S
    [[0, 1, 1], [1, 1, 0]],  # Z
    [[1, 0, 0], [1, 1, 1]],  # J
    [[0, 0, 1], [1, 1, 1]],  # L
]

COLORS = [
    (0, 255, 255),  # I
    (255, 255, 0),  # O
    (128, 0, 128),  # T
    (0, 255, 0),    # S
    (255, 0, 0),    # Z
    (0, 0, 255),    # J
    (255, 165, 0),  # L
]

class Tetromino:
    def __init__(self, x, y, shape, color, shape_idx):
        self.x = x
        self.y = y
        self.shape = shape
        self.color = color
        self.shape_idx = shape_idx

    def rotate(self):
        self.shape = [list(row) for row in zip(*self.shape[::-1])]

    def get_cells(self, x_offset=0, y_offset=0, shape_override=None):
        shape = shape_override if shape_override else self.shape
        cells = []
        for dy, row in enumerate(shape):
            for dx, val in enumerate(row):
                if val:
                    cells.append((self.x + dx + x_offset, self.y + dy + y_offset))
        return cells

    def copy(self):
        return Tetromino(self.x, self.y, [row[:] for row in self.shape], self.color, self.shape_idx)

class Game:
    def __init__(self, screen):
        self.screen = screen
        self.reset()

    def reset(self):
        self.board = [[None for _ in range(COLS)] for _ in range(ROWS)]
        self.score = 0
        self.game_over = False
        self.hold_tetromino = None
        self.hold_used = False
        self.next_queue = [self.random_tetromino() for _ in range(5)]
        self.spawn_tetromino()

    def random_tetromino(self):
        idx = random.randint(0, len(SHAPES) - 1)
        shape = SHAPES[idx]
        color = COLORS[idx]
        x = COLS // 2 - len(shape[0]) // 2
        y = 0
        return Tetromino(x, y, [row[:] for row in shape], color, idx)

    def spawn_tetromino(self):
        self.tetromino = self.next_queue.pop(0)
        self.next_queue.append(self.random_tetromino())
        self.hold_used = False
        if self.collision(self.tetromino, dx=0, dy=0):
            self.game_over = True

    def collision(self, tetromino, dx, dy, rotated_shape=None):
        shape = rotated_shape if rotated_shape else tetromino.shape
        for y, row in enumerate(shape):
            for x, cell in enumerate(row):
                if cell:
                    nx = tetromino.x + x + dx
                    ny = tetromino.y + y + dy
                    if nx < 0 or nx >= COLS or ny >= ROWS:
                        return True
                    if ny >= 0 and self.board[ny][nx]:
                        return True
        return False

    def lock_tetromino(self):
        for x, y in self.tetromino.get_cells():
            if 0 <= y < ROWS and 0 <= x < COLS:
                self.board[y][x] = self.tetromino.color
        self.clear_lines()
        self.spawn_tetromino()

    def clear_lines(self):
        new_board = [row for row in self.board if any(cell is None for cell in row)]
        lines_cleared = ROWS - len(new_board)
        for _ in range(lines_cleared):
            new_board.insert(0, [None for _ in range(COLS)])
        self.board = new_board
        self.score += lines_cleared * 100

    def move(self, dx, dy):
        if not self.collision(self.tetromino, dx, dy):
            self.tetromino.x += dx
            self.tetromino.y += dy
            return True
        return False

    def rotate(self):
        rotated = [list(row) for row in zip(*self.tetromino.shape[::-1])]
        if not self.collision(self.tetromino, 0, 0, rotated):
            self.tetromino.shape = rotated

    def hard_drop(self):
        while self.move(0, 1):
            pass
        self.lock_tetromino()

    def hold(self):
        if self.hold_used:
            return
        if self.hold_tetromino is None:
            self.hold_tetromino = self.tetromino.copy()
            self.spawn_tetromino()
        else:
            self.tetromino, self.hold_tetromino = self.hold_tetromino, self.tetromino
            self.tetromino.x = COLS // 2 - len(self.tetromino.shape[0]) // 2
            self.tetromino.y = 0
            if self.collision(self.tetromino, 0, 0):
                self.game_over = True
        self.hold_used = True

    def update(self):
        if not self.move(0, 1):
            self.lock_tetromino()

    def draw_board(self):
        for y in range(ROWS):
            for x in range(COLS):
                rect = pygame.Rect(LEFT_PANEL + x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                color = self.board[y][x] if self.board[y][x] else (40, 40, 40)
                pygame.draw.rect(self.screen, color, rect)
                pygame.draw.rect(self.screen, (30, 30, 30), rect, 1)

    def draw_tetromino(self):
        for x, y in self.tetromino.get_cells():
            if y >= 0:
                rect = pygame.Rect(LEFT_PANEL + x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(self.screen, self.tetromino.color, rect)
                pygame.draw.rect(self.screen, (255, 255, 255), rect, 1)

    def draw_shadow(self):
        shadow = self.tetromino.copy()
        while not self.collision(shadow, 0, 1):
            shadow.y += 1
        for x, y in shadow.get_cells():
            if y >= 0:
                rect = pygame.Rect(LEFT_PANEL + x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                s = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
                s.fill((*self.tetromino.color, 80))  # semi-transparent
                self.screen.blit(s, rect.topleft)
                pygame.draw.rect(self.screen, (200, 200, 200), rect, 1)

    def draw_next(self):
        font = pygame.font.SysFont("Arial", 24)
        label = font.render("Next:", True, (255, 255, 255))
        self.screen.blit(label, (LEFT_PANEL + WIDTH + 20, 30))
        for i, tetro in enumerate(self.next_queue):
            shape = tetro.shape
            color = tetro.color
            for y, row in enumerate(shape):
                for x, cell in enumerate(row):
                    if cell:
                        rect = pygame.Rect(LEFT_PANEL + WIDTH + 30 + x * CELL_SIZE, 70 + i * 70 + y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                        pygame.draw.rect(self.screen, color, rect)
                        pygame.draw.rect(self.screen, (255, 255, 255), rect, 1)

    def draw_hold(self):
        font = pygame.font.SysFont("Arial", 24)
        label = font.render("Hold:", True, (255, 255, 255))
        self.screen.blit(label, (20, 30))
        if self.hold_tetromino:
            shape = self.hold_tetromino.shape
            color = self.hold_tetromino.color
            for y, row in enumerate(shape):
                for x, cell in enumerate(row):
                    if cell:
                        rect = pygame.Rect(30 + x * CELL_SIZE, 70 + y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                        pygame.draw.rect(self.screen, color, rect)
                        pygame.draw.rect(self.screen, (255, 255, 255), rect, 1)

    def draw_score(self):
        font = pygame.font.SysFont("Arial", 24)
        score_surf = font.render(f"Score: {self.score}", True, (255, 255, 255))
        self.screen.blit(score_surf, (LEFT_PANEL + WIDTH + 20, 550))

    def run(self):
        clock = pygame.time.Clock()
        fall_time = 0
        fall_speed = 500  # milliseconds

        pygame.display.set_mode((LEFT_PANEL + WIDTH + RIGHT_PANEL, HEIGHT))

        running = True
        while running:
            dt = clock.tick(60)
            fall_time += dt

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    self.game_over = True
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        self.move(-1, 0)
                    elif event.key == pygame.K_RIGHT:
                        self.move(1, 0)
                    elif event.key == pygame.K_DOWN:
                        self.move(0, 1)
                    elif event.key == pygame.K_UP:
                        self.rotate()
                    elif event.key == pygame.K_SPACE:
                        self.hard_drop()
                    elif event.key == pygame.K_c:
                        self.hold()
                    elif event.key == pygame.K_ESCAPE:
                        running = False
                        self.game_over = True
                    elif event.key == pygame.K_r:
                        self.reset()

            if not self.game_over and fall_time > fall_speed:
                self.update()
                fall_time = 0

            self.screen.fill((0, 0, 0))
            self.draw_board()
            self.draw_shadow()
            self.draw_tetromino()
            self.draw_next()
            self.draw_hold()
            self.draw_score()
            pygame.display.flip()

            if self.game_over:
                font = pygame.font.SysFont("Arial", 48)
                text = font.render("Game Over", True, (255, 0, 0))
                self.screen.blit(text, (LEFT_PANEL + WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - text.get_height() // 2))
                pygame.display.flip()
                pygame.time.wait(1000)
                # Wait for R or ESC
                waiting = True
                while waiting:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            running = False
                            waiting = False
                        elif event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_r:
                                self.reset()
                                waiting = False
                                self.game_over = False
                            elif event.key == pygame.K_ESCAPE:
                                running = False
                                waiting = False