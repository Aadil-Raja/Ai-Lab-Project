import pygame
import random

# Maze settings
ROWS, COLS = 21, 21
TILE_SIZE = 25
WIDTH, HEIGHT = COLS * TILE_SIZE, ROWS * TILE_SIZE

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (150, 150, 150)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# Initialize pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("AI Maze Escape")

# Maze generation
maze = [['#' for _ in range(COLS)] for _ in range(ROWS)]
directions = [(-2, 0), (2, 0), (0, -2), (0, 2)]

def is_valid(x, y):
    return 0 <= x < ROWS and 0 <= y < COLS

def carve_maze(x, y):
    maze[x][y] = ' '
    random.shuffle(directions)
    for dx, dy in directions:
        nx, ny = x + dx, y + dy
        if is_valid(nx, ny) and maze[nx][ny] == '#':
            maze[x + dx // 2][y + dy // 2] = ' '
            carve_maze(nx, ny)

# Generate maze
start_x, start_y = random.randrange(1, ROWS, 2), random.randrange(1, COLS, 2)
carve_maze(start_x, start_y)
maze[1][0] = 'S'
maze[ROWS - 2][COLS - 1] = 'E'

# Player position (start)
player_pos = [1, 0]

# Draw maze
def draw_maze():
    for row in range(ROWS):
        for col in range(COLS):
            x, y = col * TILE_SIZE, row * TILE_SIZE
            cell = maze[row][col]
            if cell == '#':
                pygame.draw.rect(screen, BLACK, (x, y, TILE_SIZE, TILE_SIZE))
            elif cell == 'S':
                pygame.draw.rect(screen, GREEN, (x, y, TILE_SIZE, TILE_SIZE))
            elif cell == 'E':
                pygame.draw.rect(screen, RED, (x, y, TILE_SIZE, TILE_SIZE))
            else:
                pygame.draw.rect(screen, WHITE, (x, y, TILE_SIZE, TILE_SIZE))
                pygame.draw.rect(screen, GRAY, (x, y, TILE_SIZE, TILE_SIZE), 1)

    # Draw player
    px, py = player_pos[1] * TILE_SIZE, player_pos[0] * TILE_SIZE
    pygame.draw.rect(screen, BLUE, (px, py, TILE_SIZE, TILE_SIZE))

# Game loop
clock = pygame.time.Clock()
running = True
win = False

while running:
    screen.fill(WHITE)
    draw_maze()
    pygame.display.flip()

    if win:
        print("🎉 You reached the exit!")
        pygame.time.wait(2000)
        running = False

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    row, col = player_pos

    # Move player
    if keys[pygame.K_UP] and is_valid(row - 1, col) and maze[row - 1][col] != '#':
        player_pos = [row - 1, col]
        pygame.time.wait(100)
    elif keys[pygame.K_DOWN] and is_valid(row + 1, col) and maze[row + 1][col] != '#':
        player_pos = [row + 1, col]
        pygame.time.wait(100)
    elif keys[pygame.K_LEFT] and is_valid(row, col - 1) and maze[row][col - 1] != '#':
        player_pos = [row, col - 1]
        pygame.time.wait(100)
    elif keys[pygame.K_RIGHT] and is_valid(row, col + 1) and maze[row][col + 1] != '#':
        player_pos = [row, col + 1]
        pygame.time.wait(100)

    # Check for win
    if maze[player_pos[0]][player_pos[1]] == 'E':
        win = True

    clock.tick(60)

pygame.quit()
