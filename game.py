import pygame
import random
import heapq
from collections import deque

# Maze settings
ROWS, COLS = 31, 31
TILE_SIZE = 25
WIDTH, HEIGHT = COLS * TILE_SIZE, ROWS * TILE_SIZE

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (150, 150, 150)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
CYAN = (0, 200, 200)
MAGENTA = (200, 0, 200)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)
YELLOW = (255, 255, 0)
DARK_GREEN = (0, 100, 0)
PINK = (255, 105, 180)      # Color for killer obstacles
LIGHT_BLUE = (173, 216, 230) # Color for power-ups

directions = [(-2, 0), (2, 0), (0, -2), (0, 2)]

def is_valid(x, y, rows=None, cols=None):
    if rows is None:
        rows, cols = ROWS, COLS
    return 0 <= x < rows and 0 <= y < cols

def generate_dynamic_maze():
    # Initialize maze with walls
    maze = [['#' for _ in range(COLS)] for _ in range(ROWS)]
    
    # Function to carve paths using recursive backtracking
    def carve_maze(x, y):
        maze[x][y] = ' '
        random.shuffle(directions)
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if is_valid(nx, ny) and maze[nx][ny] == '#':
                maze[x + dx // 2][y + dy // 2] = ' '
                carve_maze(nx, ny)
    
    # Generate base perfect maze
    start_x, start_y = random.randrange(1, ROWS, 2), random.randrange(1, COLS, 2)
    carve_maze(start_x, start_y)
    
    # Add random paths to create loops
    extra_paths = int((ROWS * COLS) * 0.15)
    for _ in range(extra_paths):
        x = random.randrange(1, ROWS - 1)
        y = random.randrange(1, COLS - 1)
        
        # Only remove walls between existing paths
        if maze[x][y] == '#':
            adjacent_paths = 0
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, ny = x + dx, y + dy
                if is_valid(nx, ny) and maze[nx][ny] == ' ':
                    adjacent_paths += 1
            
            # Only create a new path if it connects existing paths
            if adjacent_paths >= 2:
                maze[x][y] = ' '
    
    # Ensure there's open space near start and end positions
    maze[1][1] = ' '
    maze[ROWS-2][COLS-2] = ' '
    
    # Set start and end
    maze[1][0] = 'S'
    maze[ROWS - 2][COLS - 1] = 'E'
    
    return maze

def manhattan_distance(p1, p2):
    return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])

def bfs(maze, start, end):
    rows, cols = len(maze), len(maze[0])
    queue = deque([(start, [start])])
    visited = set([start])

    while queue:
        (x, y), path = queue.popleft()

        if (x, y) == end:
            return path

        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < rows and 0 <= ny < cols and maze[nx][ny] != '#' and (nx, ny) not in visited:
                visited.add((nx, ny))
                queue.append(((nx, ny), path + [(nx, ny)]))

    return None

def astar(maze, start, end, ignore_walls=False):
    rows, cols = len(maze), len(maze[0])
    
    open_set = [(0 + manhattan_distance(start, end), 0, start, [start])]
    closed_set = set()
    
    while open_set:
        f, g, current, path = heapq.heappop(open_set)
        
        if current == end:
            return path
        
        if current in closed_set:
            continue
            
        closed_set.add(current)
        
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = current[0] + dx, current[1] + dy
            neighbor = (nx, ny)
            
            if not (0 <= nx < rows and 0 <= ny < cols):
                continue
                
            if not ignore_walls and maze[nx][ny] == '#':
                continue
                
            if neighbor in closed_set:
                continue
                
            new_g = g + 1
            h = manhattan_distance(neighbor, end)
            f = new_g + h
            
            heapq.heappush(open_set, (f, new_g, neighbor, path + [neighbor]))
    
    return None

def modify_maze_dynamically(maze, player_pos, difficulty_factor=0.05):
    rows, cols = len(maze), len(maze[0])
    start = tuple(player_pos)
    end = (rows - 2, cols - 1)
    
    # Check if there's a valid path from player to exit
    current_path = bfs(maze, start, end)
    if not current_path:
        create_escape_path(maze, start, end)
        return maze
    
    # Calculate how many walls to potentially add/remove
    change_count = int(rows * cols * difficulty_factor * 0.01)
    
    # Try to add walls (increase difficulty)
    for _ in range(change_count):
        for _ in range(10):
            x = random.randrange(1, rows - 1)
            y = random.randrange(1, cols - 1)
            
            if maze[x][y] == ' ' and (x, y) != start and (x, y) != end and (x, y) not in [(1,0), (rows-2, cols-1)]:
                maze[x][y] = '#'
                
                if bfs(maze, start, end):
                    break
                else:
                    maze[x][y] = ' '
    
    # Try to remove walls (possibly create shortcuts)
    for _ in range(change_count):
        x = random.randrange(1, rows - 1)
        y = random.randrange(1, cols - 1)
        
        if maze[x][y] == '#':
            adjacent_paths = 0
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, ny = x + dx, y + dy
                if is_valid(nx, ny, rows, cols) and maze[nx][ny] == ' ':
                    adjacent_paths += 1
            
            if adjacent_paths >= 2:
                if random.random() < 0.3:
                    maze[x][y] = ' '
    
    return maze

def create_escape_path(maze, start, end):
    rows, cols = len(maze), len(maze[0])
    
    path = astar(maze, start, end, ignore_walls=True)
    
    if path:
        for x, y in path:
            if maze[x][y] == '#':
                maze[x][y] = ' '
    
    return maze

class AIObstacle:
    def __init__(self, maze, player_pos):
        self.maze = maze
        self.rows, self.cols = len(maze), len(maze[0])
        self.position = self.find_valid_position(tuple(player_pos))
        self.original_cell = ' '
        self.move_timer = 0
        self.move_delay = 2000
        self.visible = True  # For invisibility power-up
        
    def find_valid_position(self, player_pos):
        start = (1, 0)
        end = (self.rows - 2, self.cols - 1)
        
        for _ in range(20):
            x = random.randrange(1, self.rows - 1)
            y = random.randrange(1, self.cols - 1)
            
            if (self.maze[x][y] == ' ' and 
                manhattan_distance((x, y), player_pos) > 5 and
                (x, y) != start and (x, y) != end):
                
                original = self.maze[x][y]
                self.maze[x][y] = 'O'
                
                if bfs(self.maze, player_pos, end):
                    self.maze[x][y] = original
                    return (x, y)
                
                self.maze[x][y] = original
        
        while True:
            x = random.randrange(1, self.rows - 1)
            y = random.randrange(1, self.cols - 1)
            if (self.maze[x][y] == ' ' and 
                manhattan_distance((x, y), player_pos) > 3):
                return (x, y)
    
    def update(self, current_time, player_pos):
        if current_time - self.move_timer >= self.move_delay:
            self.move_timer = current_time
            self.move(tuple(player_pos))
    
    def move(self, player_pos):
        end = (self.rows - 2, self.cols - 1)
        
        x, y = self.position
        self.maze[x][y] = self.original_cell
        
        if random.random() < 0.7:
            path = astar(self.maze, self.position, player_pos)
            if path and len(path) > 1:
                next_pos = path[1]
            else:
                directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
                random.shuffle(directions)
                next_pos = self.position
                for dx, dy in directions:
                    nx, ny = x + dx, y + dy
                    if (is_valid(nx, ny, self.rows, self.cols) and 
                        self.maze[nx][ny] == ' ' and
                        (nx, ny) != player_pos and 
                        (nx, ny) != end):
                        next_pos = (nx, ny)
                        break
        else:
            directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
            random.shuffle(directions)
            next_pos = self.position
            for dx, dy in directions:
                nx, ny = x + dx, y + dy
                if (is_valid(nx, ny, self.rows, self.cols) and 
                    self.maze[nx][ny] == ' ' and
                    (nx, ny) != player_pos and 
                    (nx, ny) != end):
                    next_pos = (nx, ny)
                    break
        
        new_x, new_y = next_pos
        self.original_cell = self.maze[new_x][new_y]
        
        self.maze[new_x][new_y] = 'O'
        self.position = next_pos

# New class for killer obstacles
class KillerObstacle:
    def __init__(self, maze, player_pos):
        self.maze = maze
        self.rows, self.cols = len(maze), len(maze[0])
        self.position = self.find_valid_position(tuple(player_pos))
        self.original_cell = ' '
        self.move_timer = 0
        self.move_delay = 1500  # Slightly faster than regular obstacles
        self.visible = True  # For invisibility power-up
        
    def find_valid_position(self, player_pos):
        start = (1, 0)
        end = (self.rows - 2, self.cols - 1)
        
        # Place killer obstacles farther from player
        for _ in range(20):
            x = random.randrange(1, self.rows - 1)
            y = random.randrange(1, self.cols - 1)
            
            if (self.maze[x][y] == ' ' and 
                manhattan_distance((x, y), player_pos) > 8 and  # Farther than regular obstacles
                (x, y) != start and (x, y) != end):
                
                original = self.maze[x][y]
                self.maze[x][y] = 'K'  # Mark as killer
                
                if bfs(self.maze, player_pos, end):
                    self.maze[x][y] = original
                    return (x, y)
                
                self.maze[x][y] = original
        
        while True:
            x = random.randrange(1, self.rows - 1)
            y = random.randrange(1, self.cols - 1)
            if (self.maze[x][y] == ' ' and 
                manhattan_distance((x, y), player_pos) > 5):
                return (x, y)
    
    def update(self, current_time, player_pos):
        if current_time - self.move_timer >= self.move_delay:
            self.move_timer = current_time
            self.move(tuple(player_pos))
    
    def move(self, player_pos):
        end = (self.rows - 2, self.cols - 1)
        
        x, y = self.position
        self.maze[x][y] = self.original_cell
        
        # Killer obstacles are more aggressive - 90% chance to move towards player
        if random.random() < 0.9:
            path = astar(self.maze, self.position, player_pos)
            if path and len(path) > 1:
                next_pos = path[1]
            else:
                directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
                random.shuffle(directions)
                next_pos = self.position
                for dx, dy in directions:
                    nx, ny = x + dx, y + dy
                    if (is_valid(nx, ny, self.rows, self.cols) and 
                        self.maze[nx][ny] == ' ' and
                        (nx, ny) != player_pos and 
                        (nx, ny) != end):
                        next_pos = (nx, ny)
                        break
        else:
            directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
            random.shuffle(directions)
            next_pos = self.position
            for dx, dy in directions:
                nx, ny = x + dx, y + dy
                if (is_valid(nx, ny, self.rows, self.cols) and 
                    self.maze[nx][ny] == ' ' and
                    (nx, ny) != player_pos and 
                    (nx, ny) != end):
                    next_pos = (nx, ny)
                    break
        
        new_x, new_y = next_pos
        self.original_cell = self.maze[new_x][new_y]
        
        # Mark as killer obstacle in maze
        self.maze[new_x][new_y] = 'K'
        self.position = next_pos

# New class for power-ups
class PowerUp:
    def __init__(self, maze, player_pos):
        self.maze = maze
        self.rows, self.cols = len(maze), len(maze[0])
        self.position = self.find_valid_position(tuple(player_pos))
        self.type = random.choice(['speed', 'invisibility', 'time'])
        self.active = True
        
    def find_valid_position(self, player_pos):
        start = (1, 0)
        end = (self.rows - 2, self.cols - 1)
        
        # Try to place power-ups strategically
        for _ in range(30):
            x = random.randrange(1, self.rows - 1)
            y = random.randrange(1, self.cols - 1)
            
            # Place power-ups on empty spaces, not too close to start or end
            if (self.maze[x][y] == ' ' and 
                (x, y) != start and (x, y) != end and
                manhattan_distance((x, y), start) > 3 and  
                manhattan_distance((x, y), end) > 3):
                
                # Check if no obstacle is at this position
                if self.maze[x][y] not in ['O', 'K', 'P']:
                    # Mark as power-up
                    self.maze[x][y] = 'P'
                    return (x, y)
        
        # Fallback if no ideal position found
        while True:
            x = random.randrange(1, self.rows - 1)
            y = random.randrange(1, self.cols - 1)
            if self.maze[x][y] == ' ':
                self.maze[x][y] = 'P'
                return (x, y)
    
    def collect(self):
        """Player collected this power-up"""
        if self.active:
            x, y = self.position
            self.maze[x][y] = ' '  # Remove from maze
            self.active = False
            return self.type
        return None

class GameTimer:
    def __init__(self, total_time_seconds):
        self.total_time = total_time_seconds * 1000
        self.start_time = pygame.time.get_ticks()
        self.time_remaining = self.total_time
        self.low_time_warning = False
    
    def update(self):
        current_time = pygame.time.get_ticks()
        elapsed = current_time - self.start_time
        self.time_remaining = max(0, self.total_time - elapsed)
        
        if self.time_remaining < self.total_time * 0.25:
            self.low_time_warning = True
        
        return self.time_remaining / 1000
    
    def add_time(self, seconds):
        """Add time bonus from power-up"""
        self.time_remaining += seconds * 1000
        # Recalibrate the start time so the display updates properly
        self.start_time = pygame.time.get_ticks() - (self.total_time - self.time_remaining)
        
    def is_expired(self):
        return self.time_remaining <= 0
    
    def draw(self, screen, font):
        seconds_left = int(self.time_remaining / 1000)
        minutes = seconds_left // 60
        seconds = seconds_left % 60
        
        color = RED if self.low_time_warning else BLACK
        
        timer_text = font.render(f"Time: {minutes:02d}:{seconds:02d}", True, color)
        screen.blit(timer_text, (WIDTH - 150, HEIGHT - 40))

class HintSystem:
    def __init__(self, maze):
        self.maze = maze
        self.hint_path = None
        self.hint_display_time = 0
        self.hint_duration = 5000
        self.hint_cooldown = 10000
        self.last_hint_time = -self.hint_cooldown
        self.hint_count = 0
        self.max_hints = 3
    
    def request_hint(self, player_pos, current_time):
        if (current_time - self.last_hint_time < self.hint_cooldown or 
            self.hint_count >= self.max_hints):
            return False
        
        end = (len(self.maze) - 2, len(self.maze[0]) - 1)
        path = astar(self.maze, tuple(player_pos), end)
        
        if path:
            self.hint_path = path
            self.hint_display_time = current_time
            self.last_hint_time = current_time
            self.hint_count += 1
            return True
        return False
    
    def update(self, current_time):
        if self.hint_path and current_time - self.hint_display_time > self.hint_duration:
            self.hint_path = None
    
    def draw(self, screen, tile_size):
        if self.hint_path:
            for i, (row, col) in enumerate(self.hint_path):
                ratio = i / max(1, len(self.hint_path) - 1)
                color = (int(255 * ratio), 255, int(255 * (1 - ratio)))
                
                padding = tile_size // 4
                rect_size = tile_size - padding * 2
                pygame.draw.rect(screen, color, 
                                (col * tile_size + padding, 
                                 row * tile_size + padding, 
                                 rect_size, rect_size))

# Enhanced difficulty manager with level-based features
class DifficultyManager:
    def __init__(self):
        self.level = 1
        self.max_level = 10
        # Base obstacle count (regular obstacles)
        self.obstacle_count = lambda level: max(1, level // 2)
        # Killer obstacles appear from level 3
        self.killer_obstacle_count = lambda level: 0 if level < 3 else max(1, (level - 2) // 2)
        # Power-ups increase with level
        self.powerup_count = lambda level: max(1, level // 3 + 1)
        # Time limit decreases with level
        self.time_limit = lambda level: max(30, 120 - (level - 1) * 5)
        # Maze update frequency increases with level
        self.maze_update_frequency = lambda level: max(5000, 15000 - (level - 1) * 1000)
        self.player_trapped_count = 0
    
    def next_level(self):
        if self.level < self.max_level:
            self.level += 1
            return True
        return False
    
    def get_settings(self):
        return {
            'level': self.level,
            'obstacles': self.obstacle_count(self.level),
            'killer_obstacles': self.killer_obstacle_count(self.level),
            'powerups': self.powerup_count(self.level),
            'time_limit': self.time_limit(self.level),
            'maze_update_ms': self.maze_update_frequency(self.level)
        }
    
    def calculate_score(self, time_left, hints_used):
        base_score = 1000 * self.level
        time_bonus = int(time_left * 10)
        hint_penalty = hints_used * 200
        
        return max(0, base_score + time_bonus - hint_penalty)

# Class to manage active power-ups
class PowerUpManager:
    def __init__(self):
        self.active_powerups = {} 
        self.speed_multiplier = 1.0
        
    def activate(self, powerup_type, current_time, duration=5000):
        """Activate a power-up for specified duration"""
        self.active_powerups[powerup_type] = current_time + duration
        
        # Set speed multiplier if it's a speed power-up
        if powerup_type == 'speed':
            self.speed_multiplier = 1.5
    
    def update(self, current_time):
        """Update active power-ups, remove expired ones"""
        expired = []
        for powerup_type, end_time in self.active_powerups.items():
            if current_time >= end_time:
                expired.append(powerup_type)
        
        # Remove expired power-ups
        for powerup_type in expired:
            self.active_powerups.pop(powerup_type)
            
            # Reset speed if speed power-up expired
            if powerup_type == 'speed':
                self.speed_multiplier = 1.0
    
    def is_active(self, powerup_type):
        """Check if a specific power-up is active"""
        return powerup_type in self.active_powerups
    
    def get_time_remaining(self, powerup_type, current_time):
        """Get remaining time for a power-up in seconds"""
        if powerup_type in self.active_powerups:
            return max(0, (self.active_powerups[powerup_type] - current_time) / 1000)
        return 0
    
    def draw(self, screen, font):
        """Draw active power-ups on screen"""
        current_time = pygame.time.get_ticks()
        y_offset = 70  # Start position below hints
        
        for powerup_type in self.active_powerups:
            remaining = self.get_time_remaining(powerup_type, current_time)
            if remaining <= 0:
                continue
                
            if powerup_type == 'speed':
                text = f"Speed Boost: {remaining:.1f}s"
                color = GREEN
            elif powerup_type == 'invisibility':
                text = f"Invisibility: {remaining:.1f}s"
                color = BLUE
            elif powerup_type == 'time':
                text = f"Time Bonus Active"
                color = ORANGE
            else:
                continue
                
            powerup_text = font.render(text, True, color)
            screen.blit(powerup_text, (10, y_offset))
            y_offset += 20

def main():
    # Initialize pygame
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("AI-Powered Maze Escape")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont('Arial', 16)
    
    # Initialize difficulty manager
    difficulty = DifficultyManager()
    
    # Game state
    game_state = "menu"
    score = 0
    
    # Define function to start a new level
    def start_new_level():
        # Get current difficulty settings
        settings = difficulty.get_settings()
        
        # Generate new maze
        maze = generate_dynamic_maze()
        
        # Initialize player at start
        player_pos = [1, 0]
        
        # Set up timer
        timer = GameTimer(settings['time_limit'])
        
        # Create hint system
        hint_system = HintSystem(maze)
        
        # Create obstacles
        obstacles = []
        for _ in range(settings['obstacles']):
            obstacles.append(AIObstacle(maze, player_pos))
        
        # Create killer obstacles (if level appropriate)
        killer_obstacles = []
        for _ in range(settings['killer_obstacles']):
            killer_obstacles.append(KillerObstacle(maze, player_pos))
        
        # Create power-ups
        powerups = []
        for _ in range(settings['powerups']):
            powerups.append(PowerUp(maze, player_pos))
        
        # Create power-up manager
        powerup_manager = PowerUpManager()
        
        # Set up maze update timer
        maze_update_timer = 0
        
        return (maze, player_pos, timer, hint_system, obstacles, 
                killer_obstacles, powerups, powerup_manager, maze_update_timer, settings)
    
    # Main game loop
    running = True
    
    # Start with menu
    while running:
        current_time = pygame.time.get_ticks()
        
        if game_state == "menu":
            screen.fill(WHITE)
            
            # Draw title
            title_font = pygame.font.SysFont('Arial', 36)
            title = title_font.render("AI-Powered Maze Escape", True, BLACK)
            screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//4))
            
            # Draw instructions
            instr_font = pygame.font.SysFont('Arial', 18)
            instructions = [
                "Navigate to the exit before time runs out!",
                "Avoid obstacles and watch for changing walls.",
                "",
                "NEW FEATURES:",
                "- Red obstacles will kill you (appear at level 3+)",
                "- Collect power-ups for special abilities:",
                "  • Blue: Speed boost",
                "  • Green: Invisibility to obstacles",
                "  • Yellow: Time bonus",
                "",
                "Controls:",
                "- Arrow keys to move",
                "- H for hint (limited to 3 per level)",
                "- R to restart level",
                "- ESC to quit",
                "",
                "Press SPACE to start!"
            ]
            
            for i, line in enumerate(instructions):
                instr = instr_font.render(line, True, BLACK)
                screen.blit(instr, (WIDTH//2 - instr.get_width()//2, HEIGHT//3 + i*25))
            
            pygame.display.flip()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        game_state = "playing"
                        (maze, player_pos, timer, hint_system, obstacles, 
                         killer_obstacles, powerups, powerup_manager, 
                         maze_update_timer, settings) = start_new_level()
                    elif event.key == pygame.K_ESCAPE:
                        running = False
                        
        elif game_state == "playing":
            # Update power-up manager
            powerup_manager.update(current_time)
            
            # Update timer
            time_left = timer.update()
            if timer.is_expired():
                game_state = "game_over"
                game_over_time = current_time
            
            # Update hints
            hint_system.update(current_time)
            
            # Update obstacles (if not invisible to player)
            if not powerup_manager.is_active('invisibility'):
                for obstacle in obstacles:
                    obstacle.update(current_time, player_pos)
                
                for killer in killer_obstacles:
                    killer.update(current_time, player_pos)
            
            # Periodically update maze
            if current_time - maze_update_timer >= settings['maze_update_ms']:
                maze_update_timer = current_time
                modify_maze_dynamically(maze, player_pos, difficulty_factor=0.02 * difficulty.level)
                
                # Check if player is trapped after modification
                end = (len(maze) - 2, len(maze[0]) - 1)
                if not bfs(maze, tuple(player_pos), end):
                    # Player is trapped, create escape path
                    create_escape_path(maze, tuple(player_pos), end)
                    difficulty.player_trapped_count += 1
            
            # Handle input
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_h:
                        # Request hint
                        hint_system.request_hint(player_pos, current_time)
                    elif event.key == pygame.K_r:
                        # Restart level
                        (maze, player_pos, timer, hintsystem, obstacles, maze_update_timer, settings) = start_new_level()
                    elif event.key == pygame.K_ESCAPE:
                        running = False
            
            # Handle movement
            keys = pygame.key.get_pressed()
            row, col = player_pos
            moved = False
            
            # Apply speed boost if active
            move_cooldown = 80  # Default movement delay in ms
            if powerup_manager.is_active('speed'):
                move_cooldown = int(move_cooldown / powerup_manager.speed_multiplier)
            
            # Only move if enough time has passed since last move
            if pygame.time.get_ticks() % move_cooldown < 20:  # Small window to detect keypresses
                if keys[pygame.K_UP] and is_valid(row - 1, col) and maze[row - 1][col] != '#':
                    player_pos = [row - 1, col]
                    moved = True
                elif keys[pygame.K_DOWN] and is_valid(row + 1, col) and maze[row + 1][col] != '#':
                    player_pos = [row + 1, col]
                    moved = True
                elif keys[pygame.K_LEFT] and is_valid(row, col - 1) and maze[row][col - 1] != '#':
                    player_pos = [row, col - 1]
                    moved = True
                elif keys[pygame.K_RIGHT] and is_valid(row, col + 1) and maze[row][col + 1] != '#':
                    player_pos = [row, col + 1]
                    moved = True
                
            if moved:
                # Check for collision with regular obstacle
                for obstacle in obstacles:
                    if player_pos == list(obstacle.position) and obstacle.visible:
                        # Player hit obstacle - penalty
                        timer.time_remaining -= 5000  # 5 second penalty
                        timer.start_time = pygame.time.get_ticks() - (timer.total_time - timer.time_remaining)  # Recalibrate the timer
                        # Move player back
                        player_pos = [row, col]
                        break
                
                # Check for collision with killer obstacle
                for killer in killer_obstacles:
                    if player_pos == list(killer.position) and killer.visible:
                        # Player hit killer obstacle - game over
                        game_state = "game_over"
                        game_over_time = current_time
                        break
                
                # Check for power-up collection
                for powerup in powerups[:]:
                    if player_pos == list(powerup.position) and powerup.active:
                        powerup_type = powerup.collect()
                        if powerup_type:
                            # Activate the power-up
                            if powerup_type == 'time':
                                # Time power-up adds 10 seconds
                                timer.add_time(10)
                            else:
                                # Speed and invisibility last for 5 seconds
                                powerup_manager.activate(powerup_type, current_time, 5000)
                                
                            # Remove this power-up from the list
                            powerups.remove(powerup)
                
                # Check if player reached exit
                if maze[player_pos[0]][player_pos[1]] == 'E':
                    # Calculate score
                    level_score = difficulty.calculate_score(time_left, hint_system.hint_count)
                    score += level_score
                    game_state = "level_complete"
                    level_complete_time = current_time
            
            # Draw everything
            screen.fill(WHITE)
            
            # Draw maze
            for row in range(len(maze)):
                for col in range(len(maze[0])):
                    x, y = col * TILE_SIZE, row * TILE_SIZE
                    cell = maze[row][col]
                    
                    if cell == '#':
                        pygame.draw.rect(screen, BLACK, (x, y, TILE_SIZE, TILE_SIZE))
                    elif cell == 'S':
                        pygame.draw.rect(screen, GREEN, (x, y, TILE_SIZE, TILE_SIZE))
                    elif cell == 'E':
                        pygame.draw.rect(screen, RED, (x, y, TILE_SIZE, TILE_SIZE))
                    elif cell == 'O':  # Regular obstacle
                        pygame.draw.rect(screen, WHITE, (x, y, TILE_SIZE, TILE_SIZE))
                        pygame.draw.rect(screen, GRAY, (x, y, TILE_SIZE, TILE_SIZE), 1)
                        # Draw obstacle if not invisible to player
                        if not powerup_manager.is_active('invisibility'):
                            pygame.draw.circle(screen, ORANGE, 
                                           (x + TILE_SIZE//2, y + TILE_SIZE//2), 
                                           TILE_SIZE//2 - 2)
                    elif cell == 'K':  # Killer obstacle
                        pygame.draw.rect(screen, WHITE, (x, y, TILE_SIZE, TILE_SIZE))
                        pygame.draw.rect(screen, GRAY, (x, y, TILE_SIZE, TILE_SIZE), 1)
                        # Draw killer obstacle if not invisible to player
                        if not powerup_manager.is_active('invisibility'):
                            pygame.draw.circle(screen, PINK, 
                                           (x + TILE_SIZE//2, y + TILE_SIZE//2), 
                                           TILE_SIZE//2 - 2)
                    elif cell == 'P':  # Power-up
                        pygame.draw.rect(screen, WHITE, (x, y, TILE_SIZE, TILE_SIZE))
                        pygame.draw.rect(screen, GRAY, (x, y, TILE_SIZE, TILE_SIZE), 1)
                        
                        # Find which power-up is at this position
                        for powerup in powerups:
                            if powerup.position == (row, col) and powerup.active:
                                if powerup.type == 'speed':
                                    color = BLUE
                                elif powerup.type == 'invisibility':
                                    color = GREEN
                                elif powerup.type == 'time':
                                    color = YELLOW
                                
                                pygame.draw.circle(screen, color, 
                                               (x + TILE_SIZE//2, y + TILE_SIZE//2), 
                                               TILE_SIZE//3)
                                break
                    else:
                        pygame.draw.rect(screen, WHITE, (x, y, TILE_SIZE, TILE_SIZE))
                        pygame.draw.rect(screen, GRAY, (x, y, TILE_SIZE, TILE_SIZE), 1)
            
            # Draw hints if active
            hint_system.draw(screen, TILE_SIZE)
            
            # Draw player
            px, py = player_pos[1] * TILE_SIZE, player_pos[0] * TILE_SIZE
            pygame.draw.rect(screen, BLUE, (px, py, TILE_SIZE, TILE_SIZE))
            
            # Draw UI
            timer.draw(screen, font)
            
            # Display level and score
            level_text = font.render(f"Level: {difficulty.level}", True, BLACK)
            screen.blit(level_text, (10, 10))
            
            score_text = font.render(f"Score: {score}", True, BLACK)
            screen.blit(score_text, (10, 30))
            
            hints_text = font.render(f"Hints: {hint_system.hint_count}/{hint_system.max_hints}", True, BLACK)
            screen.blit(hints_text, (10, 50))
            
            # Display active power-ups
            powerup_manager.draw(screen, font)
        
        elif game_state == "level_complete":
            # Show level complete screen for 3 seconds
            if current_time - level_complete_time > 3000:
                if difficulty.next_level():
                    # Start next level
                    (maze, player_pos, timer, hint_system, obstacles, 
                     killer_obstacles, powerups, powerup_manager, maze_update_timer, settings) = start_new_level()
                    game_state = "playing"
                else:
                    # Game completed
                    game_state = "game_over"
                    game_over_time = current_time
            
            screen.fill(WHITE)
            
            # Draw level complete message
            title_font = pygame.font.SysFont('Arial', 36)
            title = title_font.render(f"Level {difficulty.level - 1} Complete!", True, GREEN)
            screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//3))
            
            # Show score
            score_font = pygame.font.SysFont('Arial', 24)
            score_text = score_font.render(f"Level Score: {difficulty.calculate_score(time_left, hint_system.hint_count)}", True, BLACK)
            screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, HEIGHT//2))
            
            total_score = score_font.render(f"Total Score: {score}", True, BLACK)
            screen.blit(total_score, (WIDTH//2 - total_score.get_width()//2, HEIGHT//2 + 30))
            
            # Show next level message
            if difficulty.level <= difficulty.max_level:
                next_text = font.render("Next level starting soon...", True, BLACK)
                screen.blit(next_text, (WIDTH//2 - next_text.get_width()//2, HEIGHT//2 + 80))
                
                # Preview of next level features
                if difficulty.level == 3:
                    warning = font.render("Warning: Killer obstacles will appear in the next level!", True, RED)
                    screen.blit(warning, (WIDTH//2 - warning.get_width()//2, HEIGHT//2 + 110))
            else:
                next_text = font.render("Game complete! Well done!", True, BLACK)
                screen.blit(next_text, (WIDTH//2 - next_text.get_width()//2, HEIGHT//2 + 80))
            
        elif game_state == "game_over":
            # Show game over screen
            if current_time - game_over_time > 5000:
                # Return to menu after 5 seconds
                game_state = "menu"
                score = 0
            
            screen.fill(WHITE)
            
            # Draw game over message
            title_font = pygame.font.SysFont('Arial', 36)
            
            if difficulty.level > difficulty.max_level:
                # Player beat all levels
                title = title_font.render("Congratulations! Game Complete!", True, GREEN)
            else:
                # Player lost
                title = title_font.render("Game Over", True, RED)
            
            screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//3))
            
            # Show final score
            score_font = pygame.font.SysFont('Arial', 24)
            score_text = score_font.render(f"Final Score: {score}", True, BLACK)
            screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, HEIGHT//2))
            
            level_text = score_font.render(f"Reached Level: {difficulty.level}", True, BLACK)
            screen.blit(level_text, (WIDTH//2 - level_text.get_width()//2, HEIGHT//2 + 30))
            
            # Show menu message
            menu_text = font.render("Returning to menu soon...", True, BLACK)
            screen.blit(menu_text, (WIDTH//2 - menu_text.get_width()//2, HEIGHT//2 + 80))
        
        # Update display
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()

if __name__ == "__main__":
    main()