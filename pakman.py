import pygame
import sys
import math
import random

# Pygame-ni ishga tushirish
pygame.init()

# Ekran o'lchamlari va sozlamalari
WIDTH, HEIGHT = 560, 620
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pac-Man Classic (With Iconic Lives)")
clock = pygame.time.Clock()
FPS = 60

# Ranglar
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
PINK = (255, 182, 193)
CYAN = (0, 255, 255)
ORANGE = (255, 165, 0)
SCARED_BLUE = (0, 0, 139)

# Labirint andozasi
INITIAL_MAZE = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 1],
    [1, 0, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 0, 1],
    [1, 0, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 1],
    [1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 3, 1, 1, 3, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1],
    [3, 3, 3, 3, 3, 1, 0, 1, 1, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 1, 1, 0, 1, 3, 3, 3, 3, 3],
    [1, 1, 1, 1, 1, 1, 0, 1, 1, 3, 1, 1, 1, 3, 3, 1, 1, 1, 3, 1, 1, 0, 1, 1, 1, 1, 1, 1],
    [3, 3, 3, 3, 3, 3, 0, 3, 3, 3, 1, 3, 3, 3, 3, 3, 3, 1, 3, 3, 3, 0, 3, 3, 3, 3, 3, 3],
    [1, 1, 1, 1, 1, 1, 0, 1, 1, 3, 1, 1, 1, 1, 1, 1, 1, 1, 3, 1, 1, 0, 1, 1, 1, 1, 1, 1],
    [3, 3, 3, 3, 3, 1, 0, 1, 1, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 1, 1, 0, 1, 3, 3, 3, 3, 3],
    [1, 1, 1, 1, 1, 1, 0, 1, 1, 3, 1, 1, 1, 1, 1, 1, 1, 1, 3, 1, 1, 0, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 0, 1],
    [1, 2, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 3, 3, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 2, 1],
    [1, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
]

MAZE = [row[:] for row in INITIAL_MAZE]

TILE_SIZE = 20
font = pygame.font.SysFont("Arial", 24)
sub_font = pygame.font.SysFont("Arial", 18)


class PacMan:
    def __init__(self):
        self.reset()
        self.score = 0
        self.lives = 3

    def reset(self):
        self.x = 14 * TILE_SIZE
        self.y = 16 * TILE_SIZE
        self.vel = 2
        self.dir_x = 0
        self.dir_y = 0
        self.next_dir_x = 0
        self.next_dir_y = 0
        self.mouth_angle = 0
        self.mouth_closing = False

    def move(self):
        if self.x % TILE_SIZE == 0 and self.y % TILE_SIZE == 0:
            next_tile_x = int((self.x + self.next_dir_x * TILE_SIZE) / TILE_SIZE)
            next_tile_y = int((self.y + self.next_dir_y * TILE_SIZE) / TILE_SIZE)

            if next_tile_x < 0:
                self.x = (len(MAZE[0]) - 1) * TILE_SIZE
            elif next_tile_x >= len(MAZE[0]):
                self.x = 0

            if 0 <= next_tile_x < len(MAZE[0]) and 0 <= next_tile_y < len(MAZE):
                if MAZE[next_tile_y][next_tile_x] != 1:
                    self.dir_x = self.next_dir_x
                    self.dir_y = self.next_dir_y

        new_x = self.x + self.dir_x * self.vel
        new_y = self.y + self.dir_y * self.vel

        tile_x1, tile_y1 = int(new_x / TILE_SIZE), int(new_y / TILE_SIZE)
        tile_x2, tile_y2 = int((new_x + TILE_SIZE - 1) / TILE_SIZE), int((new_y + TILE_SIZE - 1) / TILE_SIZE)

        if new_x < 0:
            self.x = WIDTH - TILE_SIZE
            return
        elif new_x >= WIDTH:
            self.x = 0
            return

        if MAZE[tile_y1][tile_x1] != 1 and MAZE[tile_y2][tile_x2] != 1 and \
                MAZE[tile_y1][tile_x2] != 1 and MAZE[tile_y2][tile_x1] != 1:
            self.x = new_x
            self.y = new_y

        if self.dir_x != 0 or self.dir_y != 0:
            if self.mouth_closing:
                self.mouth_angle -= 3
                if self.mouth_angle <= 0:
                    self.mouth_angle = 0
                    self.mouth_closing = False
            else:
                self.mouth_angle += 3
                if self.mouth_angle >= 45:
                    self.mouth_angle = 45
                    self.mouth_closing = True
        else:
            self.mouth_angle = 0

    def eat(self):
        current_tile_x = int((self.x + TILE_SIZE // 2) / TILE_SIZE)
        current_tile_y = int((self.y + TILE_SIZE // 2) / TILE_SIZE)

        if 0 <= current_tile_x < len(MAZE[0]) and 0 <= current_tile_y < len(MAZE):
            if MAZE[current_tile_y][current_tile_x] == 0:
                MAZE[current_tile_y][current_tile_x] = 3
                self.score += 10
            elif MAZE[current_tile_y][current_tile_x] == 2:
                MAZE[current_tile_y][current_tile_x] = 3
                self.score += 50
                return True
        return False

    def draw(self):
        center = (self.x + TILE_SIZE // 2, self.y + TILE_SIZE // 2)
        radius = TILE_SIZE // 2

        base_angle = 0
        if self.dir_x == 1:
            base_angle = 0
        elif self.dir_x == -1:
            base_angle = 180
        elif self.dir_y == -1:
            base_angle = 90
        elif self.dir_y == 1:
            base_angle = 270

        start_angle = math.radians(base_angle + self.mouth_angle)
        end_angle = math.radians(base_angle + 360 - self.mouth_angle)

        if self.mouth_angle == 0:
            pygame.draw.circle(screen, YELLOW, center, radius)
        else:
            points = [center]
            num_segments = 30
            step = (end_angle - start_angle) / num_segments
            for i in range(num_segments + 1):
                ang = start_angle + i * step
                px = center[0] + radius * math.cos(ang)
                py = center[1] - radius * math.sin(ang)
                points.append((px, py))

            pygame.draw.polygon(screen, YELLOW, points)


class Ghost:
    def __init__(self, x, y, color, behavior):
        self.start_x = x
        self.start_y = y
        self.color = color
        self.behavior = behavior
        self.reset()

    def reset(self):
        self.x = self.start_x * TILE_SIZE
        self.y = self.start_y * TILE_SIZE
        self.vel = 2
        self.dir_x = 0
        self.dir_y = -1
        self.scared = False
        self.scared_timer = 0
        self.animation_count = 0

    def move(self, pacman):
        self.animation_count += 1
        if self.scared:
            self.vel = 1
            if self.scared_timer > 0:
                self.scared_timer -= 1
            else:
                self.scared = False
        else:
            self.vel = 2

        if self.x % TILE_SIZE == 0 and self.y % TILE_SIZE == 0:
            possible_dirs = []
            for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
                if dx == -self.dir_x and dy == -self.dir_y:
                    continue
                nx = int((self.x + dx * TILE_SIZE) / TILE_SIZE)
                ny = int((self.y + dy * TILE_SIZE) / TILE_SIZE)
                if 0 <= nx < len(MAZE[0]) and 0 <= ny < len(MAZE):
                    if MAZE[ny][nx] != 1:
                        possible_dirs.append((dx, dy))

            if not possible_dirs:
                self.dir_x, self.dir_y = -self.dir_x, -self.dir_y
                return

            if self.scared:
                self.dir_x, self.dir_y = random.choice(possible_dirs)
            else:
                target_x, target_y = pacman.x, pacman.y
                if self.behavior == 'pinky':
                    target_x += pacman.dir_x * TILE_SIZE * 4
                    target_y += pacman.dir_y * TILE_SIZE * 4
                elif self.behavior == 'clyde':
                    dist = ((self.x - pacman.x) ** 2 + (self.y - pacman.y) ** 2) ** 0.5
                    if dist < TILE_SIZE * 8:
                        target_x, target_y = 0, HEIGHT

                best_dir = possible_dirs[0]
                min_dist = float('inf')
                for dx, dy in possible_dirs:
                    next_px = self.x + dx * TILE_SIZE
                    next_py = self.y + dy * TILE_SIZE
                    dist = ((next_px - target_x) ** 2 + (next_py - target_y) ** 2) ** 0.5
                    if dist < min_dist:
                        min_dist = dist
                        best_dir = (dx, dy)

                self.dir_x, self.dir_y = best_dir

        self.x += self.dir_x * self.vel
        self.y += self.dir_y * self.vel

    def draw(self):
        color = SCARED_BLUE if self.scared else self.color
        cx = self.x + TILE_SIZE // 2
        cy = self.y + TILE_SIZE // 2
        r = TILE_SIZE // 2

        points = []
        for angle in range(180, 361):
            rad = math.radians(angle)
            px = cx + r * math.cos(rad)
            py = cy + r * math.sin(rad)
            points.append((px, py))

        wave_offset = (self.animation_count // 10) % 2 * 3
        points.append((cx + r, cy + r - 2))
        points.append((cx + r - 3, cy + r - wave_offset))
        points.append((cx, cy + r - (3 - wave_offset)))
        points.append((cx - r + 3, cy + r - wave_offset))
        points.append((cx - r, cy + r - 2))

        pygame.draw.polygon(screen, color, points)

        if not self.scared:
            pygame.draw.circle(screen, WHITE, (cx - 4, cy - 2), 3)
            pygame.draw.circle(screen, BLUE, (cx - 4 + self.dir_x, cy - 2 + self.dir_y), 1.5)
            pygame.draw.circle(screen, WHITE, (cx + 4, cy - 2), 3)
            pygame.draw.circle(screen, BLUE, (cx + 4 + self.dir_x, cy - 2 + self.dir_y), 1.5)
        else:
            pygame.draw.circle(screen, ORANGE, (cx - 4, cy - 2), 2)
            pygame.draw.circle(screen, ORANGE, (cx + 4, cy - 2), 2)
            pygame.draw.line(screen, ORANGE, (cx - 4, cy + 3), (cx + 4, cy + 3), 2)


def draw_maze():
    for row_idx, row in enumerate(MAZE):
        for col_idx, tile in enumerate(row):
            if tile == 1:
                pygame.draw.rect(screen, BLUE, (col_idx * TILE_SIZE, row_idx * TILE_SIZE, TILE_SIZE, TILE_SIZE), 2)
            elif tile == 0:
                pygame.draw.circle(screen, WHITE,
                                   (col_idx * TILE_SIZE + TILE_SIZE // 2, row_idx * TILE_SIZE + TILE_SIZE // 2), 3)
            elif tile == 2:
                pygame.draw.circle(screen, WHITE,
                                   (col_idx * TILE_SIZE + TILE_SIZE // 2, row_idx * TILE_SIZE + TILE_SIZE // 2), 6)


def check_win():
    for row in MAZE:
        if 0 in row or 2 in row:
            return False
    return True


def restart_game():
    global MAZE, game_over, win
    MAZE = [row[:] for row in INITIAL_MAZE]
    pacman.reset()
    pacman.score = 0
    pacman.lives = 3
    for ghost in ghosts:
        ghost.reset()
    game_over = False
    win = False


# Hayotlar piktogrammasini (Og'zi ochiq Pacman) pastga chizish funksiyasi
def draw_lives(lives_count):
    # "Lives:" matni
    lives_label = font.render("Lives: ", True, WHITE)
    screen.blit(lives_label, (WIDTH - 190, HEIGHT - 40))

    start_x = WIDTH - 120
    y_pos = HEIGHT - 28
    radius = 9  # Kichikroq o'lchamdagi Pac-Man shakli

    # Qolgan hayotlar soniga qarab chapga qaragan va og'zi ochiq Pac-Man piktogrammalarini chizish
    for i in range(lives_count):
        cx = start_x + (i * 24)
        center = (cx, y_pos)

        # Chap tomonga og'zi ochiq holatda (180 daraja yo'nalish, 35 daraja burchakda ochiq)
        start_angle = math.radians(180 + 35)
        end_angle = math.radians(180 + 360 - 35)

        points = [center]
        num_segments = 20
        step = (end_angle - start_angle) / num_segments
        for j in range(num_segments + 1):
            ang = start_angle + j * step
            px = center[0] + radius * math.cos(ang)
            py = center[1] - radius * math.sin(ang)
            points.append((px, py))

        pygame.draw.polygon(screen, YELLOW, points)


# Ob'ektlarni yaratish
pacman = PacMan()
ghosts = [
    Ghost(13, 9, RED, 'blinky'),
    Ghost(14, 9, PINK, 'pinky'),
    Ghost(12, 11, CYAN, 'inky'),
    Ghost(15, 11, ORANGE, 'clyde')
]

running = True
game_over = False
win = False

while running:
    screen.fill(BLACK)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                restart_game()

            if not game_over and not win:
                if event.key == pygame.K_UP:
                    pacman.next_dir_x, pacman.next_dir_y = 0, -1
                elif event.key == pygame.K_DOWN:
                    pacman.next_dir_x, pacman.next_dir_y = 0, 1
                elif event.key == pygame.K_LEFT:
                    pacman.next_dir_x, pacman.next_dir_y = -1, 0
                elif event.key == pygame.K_RIGHT:
                    pacman.next_dir_x, pacman.next_dir_y = 1, 0

    if not game_over and not win:
        pacman.move()

        if pacman.eat():
            for ghost in ghosts:
                ghost.scared = True
                ghost.scared_timer = 300

        for ghost in ghosts:
            ghost.move(pacman)

            pac_rect = pygame.Rect(pacman.x, pacman.y, TILE_SIZE, TILE_SIZE)
            ghost_rect = pygame.Rect(ghost.x, ghost.y, TILE_SIZE, TILE_SIZE)

            if pac_rect.colliderect(ghost_rect):
                if ghost.scared:
                    ghost.x = 14 * TILE_SIZE
                    ghost.y = 9 * TILE_SIZE
                    ghost.scared = False
                    pacman.score += 200
                else:
                    pacman.lives -= 1
                    pacman.x = 14 * TILE_SIZE
                    pacman.y = 16 * TILE_SIZE
                    if pacman.lives <= 0:
                        game_over = True

        if check_win():
            win = True

    # Chizish operatsiyalari
    draw_maze()
    pacman.draw()
    for ghost in ghosts:
        ghost.draw()

    # Interfeys (Ochko matni va Yangi Grafik Hayotlar)
    score_text = font.render(f"Score: {pacman.score}", True, WHITE)
    screen.blit(score_text, (15, HEIGHT - 40))

    # Mana shu joyda matn o'rniga sariq rangli og'zi ochiq Pacmanciklar chiziladi
    draw_lives(pacman.lives)

    if game_over:
        over_text = font.render("GAME OVER", True, RED)
        restart_text = sub_font.render("Qayta o'ynash uchun [ R ] tugmasini bosing", True, WHITE)
        screen.blit(over_text, (WIDTH // 2 - 60, HEIGHT // 2 - 20))
        screen.blit(restart_text, (WIDTH // 2 - 150, HEIGHT // 2 + 15))
    elif win:
        win_text = font.render("YOU WIN!", True, YELLOW)
        restart_text = sub_font.render("Qayta o'ynash uchun [ R ] tugmasini bosing", True, WHITE)
        screen.blit(win_text, (WIDTH // 2 - 50, HEIGHT // 2 - 20))
        screen.blit(restart_text, (WIDTH // 2 - 150, HEIGHT // 2 + 15))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()