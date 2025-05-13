import pygame
import random
import heapq
from collections import deque
import math

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

class AICompetitor:
    def __init__(self, maze, start_pos):
        self.maze = maze
        self.position = list(start_pos)
        self.path = None
        self.move_timer = 0
        self.move_delay = 200  # Base movement speed
        self.has_speed_boost = False
        self.is_invisible = False
        self.collected_powerups = []
        self.trapped_count = 0
        self.intelligence = 0.3  # Intelligence factor (0.0 to 1.0)
        # Higher intelligence means better at finding optimal paths
        
    def update(self, current_time, player_pos, obstacles, killer_obstacles):
        if current_time is None or not isinstance(current_time, (int, float)):
            return
    
        if player_pos is None or not isinstance(player_pos, list) or len(player_pos) != 2:
            return
    
        if obstacles is None:
            obstacles = []
    
        if killer_obstacles is None:
            killer_obstacles = []
        
        if current_time - self.move_timer >= self.get_move_delay():
            self.move_timer = current_time
            self.move(player_pos, obstacles, killer_obstacles)
    
    
    def scale_with_level(self, level):
        # Intelligence scales up slightly per level, capped at 1.0
        self.intelligence = min(1.0, 0.3 + 0.05 * (level - 1))
        
        # Speed increases by decreasing move_delay slightly, capped at 100ms
        self.move_delay = max(100, 200 - 5 * (level - 1))
    
    def get_move_delay(self):
        return self.move_delay / 1.5 if self.has_speed_boost else self.move_delay
    
    def move(self, player_pos, obstacles, killer_obstacles):
        # AI pathfinding logic with different strategies based on current situation
        end = (len(self.maze) - 2, len(self.maze[0]) - 1)
        
        # Calculate path to exit if needed
        if random.random() < self.intelligence:
            # Smart move: Use A* to find path to exit
            self.path = astar(self.maze, tuple(self.position), end)
        else:
            # Sometimes make suboptimal moves to simulate human error
            directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
            random.shuffle(directions)
            self.path = None
        
        # If path exists, follow next step
        if self.path and len(self.path) > 1:
            next_pos = self.path[1]
            
            # Check if next position has an obstacle
            obstacle_at_pos = False
            for obs in obstacles + killer_obstacles:
                if list(obs.position) == list(next_pos) and not self.is_invisible:
                    obstacle_at_pos = True
                    break
            
            if not obstacle_at_pos:
                self.position = list(next_pos)
            else:
                # Try to find alternate path around obstacle
                self.path = None
                # Try each direction
                for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    new_x, new_y = self.position[0] + dx, self.position[1] + dy
                    if (is_valid(new_x, new_y, len(self.maze), len(self.maze[0])) and 
                        self.maze[new_x][new_y] != '#'):
                        
                        # Check if there's an obstacle
                        has_obstacle = False
                        for obs in obstacles + killer_obstacles:
                            if list(obs.position) == [new_x, new_y]:
                                has_obstacle = True
                                break
                        
                        if not has_obstacle:
                            self.position = [new_x, new_y]
                            break
        else:
            # No path or at end of path, try random valid move
            directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
            random.shuffle(directions)
            
            for dx, dy in directions:
                new_x, new_y = self.position[0] + dx, self.position[1] + dy
                if (is_valid(new_x, new_y, len(self.maze), len(self.maze[0])) and 
                    self.maze[new_x][new_y] != '#'):
                    
                    # Check if there's an obstacle
                    has_obstacle = False
                    for obs in obstacles + killer_obstacles:
                        if list(obs.position) == [new_x, new_y] and not self.is_invisible:
                            has_obstacle = True
                            break
                    
                    if not has_obstacle:
                        self.position = [new_x, new_y]
                        break

                    
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
        if current_time is None or not isinstance(current_time, (int, float)):
            return
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
        if current_time is None or not isinstance(current_time, (int, float)):
            return
        
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
        
        color = RED if self.low_time_warning else WHITE
        
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
        # Time limit decreases with level but never below 30 seconds
        self.time_limit = lambda level: max(30, 120 - (level - 1) * 5)
        # Maze update frequency increases with level but never below 5000ms
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
        time_bonus = int(max(0, time_left) * 10)  # Ensure time_left is not negative
        hint_penalty = max(0, hints_used * 200)   # Ensure hint_penalty is not negative
        
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
            self.speed_multiplier = 2
    
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
# First, let's add the missing SpecialPowerUp class that was referenced but not defined
class SpecialPowerUp:
    def __init__(self, maze, player_pos, ai_pos):
        self.maze = maze
        self.rows, self.cols = len(maze), len(maze[0])
        self.position = self.find_valid_position(tuple(player_pos), tuple(ai_pos))
        self.type = random.choice(['teleport', 'trap', 'wall_phase'])
        self.active = True
        
    def find_valid_position(self, player_pos, ai_pos):
        start = (1, 0)
        end = (self.rows - 2, self.cols - 1)
        
        # Try to place special power-ups strategically - farther from both players
        for _ in range(30):
            x = random.randrange(1, self.rows - 1)
            y = random.randrange(1, self.cols - 1)
            
            if (self.maze[x][y] == ' ' and 
                (x, y) != start and (x, y) != end and
                manhattan_distance((x, y), player_pos) > 5 and  
                manhattan_distance((x, y), ai_pos) > 5):
                
                # Check if no other element is at this position
                if self.maze[x][y] not in ['O', 'K', 'P', 'S']:
                    # Mark as special power-up
                    self.maze[x][y] = 'S'  # S for Special
                    return (x, y)
        
        # Fallback if no ideal position found
        while True:
            x = random.randrange(1, self.rows - 1)
            y = random.randrange(1, self.cols - 1)
            if self.maze[x][y] == ' ':
                self.maze[x][y] = 'S'
                return (x, y)
    
    def collect(self):
        """Player or AI collected this power-up"""
        if self.active:
            x, y = self.position
            self.maze[x][y] = ' '  # Remove from maze
            self.active = False
            return self.type
        return None

# Helper functions for special power-ups
def find_random_teleport_location(maze, current_pos):
    """Find a valid random location for teleportation"""
    if maze is None or not maze:
        return current_pos  # Return current position if maze is invalid
    
    rows, cols = len(maze), len(maze[0])
    end = (rows - 2, cols - 1)
    start = (1, 0)
    
    # Try to find a spot that's not too close to obstacles
    for _ in range(50):
        x = random.randrange(1, rows - 1)
        y = random.randrange(1, cols - 1)
        
        # Ensure it's empty, not an obstacle, power-up, or the exit
        if (maze[x][y] == ' ' and 
            manhattan_distance((x, y), current_pos) > 5 and  # Not too close to current position
            (x, y) != start and (x, y) != end):
            
            # Make sure there's a valid path to exit
            path = bfs(maze, (x, y), end)
            if path:
                return [x, y]
    
    # Fallback to any valid position
    for _ in range(100):  # Try 100 times to find valid position
        x = random.randrange(1, rows - 1)
        y = random.randrange(1, cols - 1)
        if maze[x][y] == ' ' and (x, y) != end:
            return [x, y]
    
    # If all else fails, return the original position
    return list(current_pos)

def add_trap(maze, position):
    """Add a trap at the player's position"""
    x, y = position
    maze[x][y] = 'T'  # Mark as trap in the maze
    return (x, y)

def create_wall_phase_path(maze, player_pos, direction):
    """Create a path through a wall when wall_phase power-up is used"""
    x, y = player_pos
    dx, dy = direction
    
    # Check if there's a wall in the chosen direction
    if 0 <= x + dx < len(maze) and 0 <= y + dy < len(maze[0]) and maze[x + dx][y + dy] == '#':
        # Create a temporary opening (will be restored after player passes)
        original_cell = maze[x + dx][y + dy]
        maze[x + dx][y + dy] = 'W'  # Mark as phased wall
        
        # Schedule to close the wall after a few seconds
        return (x + dx, y + dy, original_cell)
    
    return None


class SpecialPowerUpManager:
    def __init__(self):
        self.active_specials = {}  # {type: end_time}
        self.wall_phase_cells = []  # List of (x, y, original_cell) for wall phases
        self.traps = []  # List of trap positions
        
    def activate(self, powerup_type, current_time, player_pos=None, maze=None, direction=None):
        """Activate a special power-up"""
        duration = 5000  # Default duration (5 seconds)
        
        if powerup_type == 'teleport' and player_pos and maze:
            # Teleport player immediately
            new_pos = find_random_teleport_location(maze, player_pos)
            player_pos[0], player_pos[1] = new_pos[0], new_pos[1]
            return True
            
        elif powerup_type == 'trap' and player_pos and maze:
            # Create trap at current position
            trap_pos = add_trap(maze, player_pos)
            if trap_pos:
                self.traps.append(trap_pos)
            return True
            
        elif powerup_type == 'wall_phase' and player_pos and maze and direction:
            # Create temporary path through wall
            result = create_wall_phase_path(maze, player_pos, direction)
            if result:
                self.wall_phase_cells.append(result)
                # Schedule wall restoration
                self.active_specials['wall_phase'] = current_time + duration
            return True
            
        return False
    
    def update(self, current_time, maze):
        """Update active special power-ups, remove expired ones"""
        expired = []
        for powerup_type, end_time in self.active_specials.items():
            if current_time >= end_time:
                expired.append(powerup_type)
        
        # Process expired power-ups
        for powerup_type in expired:
            self.active_specials.pop(powerup_type)
            
            # Restore walls if wall_phase expired
            if powerup_type == 'wall_phase' and maze:
                for x, y, original_cell in self.wall_phase_cells:
                    if 0 <= x < len(maze) and 0 <= y < len(maze[0]):
                        maze[x][y] = original_cell
                self.wall_phase_cells = []
    
    def check_trap(self, position):
        """Check if position has a trap"""
        for trap_pos in self.traps:
            if list(trap_pos) == list(position):
                return True
        return False
    
    def remove_trap(self, position):
        """Remove a trap once triggered"""
        for i, trap_pos in enumerate(self.traps):
            if list(trap_pos) == list(position):
                self.traps.pop(i)
                return True
        return False

# Add a RotatingMazeSection class to create dynamic maze elements
class RotatingMazeSection:
    def __init__(self, maze, center_x, center_y, radius=2):
        self.maze = maze
        self.center = (center_x, center_y)
        self.radius = radius
        self.rotation_timer = 0
        self.rotation_interval = 10000  # Rotate every 10 seconds
        self.section_cells = self.get_section_cells()
        self.original_state = self.capture_state()
        
    def get_section_cells(self):
        """Get all cells in this rotating section"""
        cells = []
        cx, cy = self.center
        for dx in range(-self.radius, self.radius + 1):
            for dy in range(-self.radius, self.radius + 1):
                x, y = cx + dx, cy + dy
                if is_valid(x, y, len(self.maze), len(self.maze[0])):
                    cells.append((x, y))
        return cells
    
    def capture_state(self):
        """Capture the current state of the section"""
        state = {}
        for x, y in self.section_cells:
            state[(x, y)] = self.maze[x][y]
        return state
    
    def rotate_section(self):
    # First capture current state
        current_state = self.capture_state()
        
        # Make a temporary copy to avoid overwriting values
        new_state = {}
        
        # Calculate new positions
        cx, cy = self.center
        for x, y in self.section_cells:
            # Calculate position after rotation
            dx, dy = x - cx, y - cy
            new_x, new_y = cx + dy, cy - dx
            
            # Only update if the new position is valid
            if (new_x, new_y) in self.section_cells:
                # Store what will be at the new position
                if (x, y) in current_state:
                    cell_value = current_state[(x, y)]
                    new_state[(new_x, new_y)] = cell_value
        
        # Now apply the changes
        for pos, value in new_state.items():
            new_x, new_y = pos
            # Check if position is valid before updating
            if 0 <= new_x < len(self.maze) and 0 <= new_y < len(self.maze[0]):
                # Don't overwrite start or end positions
                if (new_x, new_y) != (1, 0) and (new_x, new_y) != (len(self.maze) - 2, len(self.maze[0]) - 1):
                    # Preserve special cells like 'S', 'E', 'P', etc.
                    if self.maze[new_x][new_y] not in ['S', 'E']:
                        self.maze[new_x][new_y] = value
        
    def update(self, current_time, player_pos, ai_pos):
        """Update the rotating section"""
        if current_time - self.rotation_timer >= self.rotation_interval:
            # Save player and AI positions if they're in the section
            player_in_section = tuple(player_pos) in self.section_cells
            ai_in_section = tuple(ai_pos) in self.section_cells
            
            # Remember positions before rotation
            player_original = tuple(player_pos) if player_in_section else None
            ai_original = tuple(ai_pos) if ai_in_section else None
            
            # Perform rotation
            self.rotate_section()
            self.rotation_timer = current_time
            
            # Update player and AI positions if they were in the section
            if player_in_section:
                cx, cy = self.center
                dx, dy = player_pos[0] - cx, player_pos[1] - cy
                player_pos[0], player_pos[1] = cx + dy, cy - dx
            
            if ai_in_section:
                cx, cy = self.center
                dx, dy = ai_pos[0] - cx, ai_pos[1] - cy
                ai_pos[0], ai_pos[1] = cx + dy, cy - dx
            
            return True
        return False

# Let's add a new class for shifting walls
class ShiftingWall:
    def __init__(self, maze, orientation='horizontal'):
        self.maze = maze
        self.rows, self.cols = len(maze), len(maze[0])
        self.orientation = orientation  # 'horizontal' or 'vertical'
        self.position = self.find_valid_position()
        self.length = random.randint(3, 5)
        self.shift_timer = 0
        self.shift_interval = 5000  # Shift every 5 seconds
        
    def find_valid_position(self):
        """Find a valid position for the shifting wall"""
        if self.orientation == 'horizontal':
            # Find position for horizontal wall
            for _ in range(30):
                row = random.randint(3, self.rows - 4)
                col = random.randint(1, self.cols - 6)
                
                # Check if area is suitable
                valid = True
                for c in range(col, col + 5):
                    if not is_valid(row, c, self.rows, self.cols) or self.maze[row][c] != ' ':
                        valid = False
                        break
                
                if valid:
                    return (row, col)
        else:
            # Find position for vertical wall
            for _ in range(30):
                row = random.randint(1, self.rows - 6)
                col = random.randint(3, self.cols - 4)
                
                # Check if area is suitable
                valid = True
                for r in range(row, row + 5):
                    if not is_valid(r, col, self.rows, self.cols) or self.maze[r][col] != ' ':
                        valid = False
                        break
                
                if valid:
                    return (row, col)
        
        # Fallback - return any valid position
        if self.orientation == 'horizontal':
            return (self.rows // 2, 1)
        else:
            return (1, self.cols // 2)
    
    def shift(self):
        """Shift the wall to a new position"""
        row, col = self.position
        
        # Clear current wall
        if self.orientation == 'horizontal':
            for c in range(col, col + self.length):
                if self.maze[row][c] == '#':
                    self.maze[row][c] = ' '
            
            # Determine new position
            if random.random() < 0.5 and row > 2:
                # Move up
                new_row = row - 1
            elif row < self.rows - 3:
                # Move down
                new_row = row + 1
            else:
                # Stay in place
                new_row = row
            
            # Place wall at new position
            for c in range(col, col + self.length):
                if is_valid(new_row, c, self.rows, self.cols) and self.maze[new_row][c] == ' ':
                    self.maze[new_row][c] = '#'
            
            self.position = (new_row, col)
        else:
            # Vertical wall shifting
            for r in range(row, row + self.length):
                if self.maze[r][col] == '#':
                    self.maze[r][col] = ' '
            
            # Determine new position
            if random.random() < 0.5 and col > 2:
                # Move left
                new_col = col - 1
            elif col < self.cols - 3:
                # Move right
                new_col = col + 1
            else:
                # Stay in place
                new_col = col
            
            # Place wall at new position
            for r in range(row, row + self.length):
                if is_valid(r, new_col, self.rows, self.cols) and self.maze[r][new_col] == ' ':
                    self.maze[r][new_col] = '#'
            
            self.position = (row, new_col)
    
    def update(self, current_time, player_pos, ai_pos):
        """Update the shifting wall"""
        if current_time - self.shift_timer >= self.shift_interval:
            self.shift_timer = current_time
            self.shift()
            
            # Ensure player and AI aren't trapped
            end = (self.rows - 2, self.cols - 1)
            
            # Check if player is trapped
            if not bfs(self.maze, tuple(player_pos), end):
                create_escape_path(self.maze, tuple(player_pos), end)
            
            # Check if AI is trapped
            if not bfs(self.maze, tuple(ai_pos), end):
                create_escape_path(self.maze, tuple(ai_pos), end)

# Let's add a CheckpointSystem for a checkpoint race mode
class CheckpointSystem:
    def __init__(self, maze, checkpoint_count=3):
        self.maze = maze
        self.rows, self.cols = len(maze), len(maze[0])
        self.checkpoint_count = checkpoint_count
        self.checkpoints = self.create_checkpoints()
        self.player_reached = [False] * checkpoint_count
        self.ai_reached = [False] * checkpoint_count
    
    def create_checkpoints(self):
        """Create checkpoints throughout the maze"""
        checkpoints = []
        end = (self.rows - 2, self.cols - 1)
        start = (1, 0)
        
        # Find path from start to end
        path = astar(self.maze, start, end)
        
        if path:
            # Divide path into segments
            segment_length = len(path) // (self.checkpoint_count + 1)
            
            for i in range(1, self.checkpoint_count + 1):
                idx = i * segment_length
                if idx < len(path):
                    checkpoint_pos = path[idx]
                    # Mark checkpoint in maze
                    self.maze[checkpoint_pos[0]][checkpoint_pos[1]] = 'C'
                    checkpoints.append(checkpoint_pos)
        
        # If not enough checkpoints were created, add random ones
        while len(checkpoints) < self.checkpoint_count:
            for _ in range(20):
                x = random.randrange(1, self.rows - 1)
                y = random.randrange(1, self.cols - 1)
                
                if (self.maze[x][y] == ' ' and 
                    (x, y) != start and (x, y) != end and
                    (x, y) not in checkpoints):
                    
                    # Make sure there's a valid path from start to this checkpoint and from here to end
                    if bfs(self.maze, start, (x, y)) and bfs(self.maze, (x, y), end):
                        self.maze[x][y] = 'C'
                        checkpoints.append((x, y))
                        break
        
        return checkpoints
    
    def check_player_progress(self, player_pos):
        """Check if player has reached any checkpoints"""
        pos_tuple = tuple(player_pos)
        
        for i, checkpoint in enumerate(self.checkpoints):
            if pos_tuple == checkpoint and not self.player_reached[i]:
                self.player_reached[i] = True
                return i  # Return checkpoint index
        
        return -1
    
    def check_ai_progress(self, ai_pos):
        """Check if AI has reached any checkpoints"""
        pos_tuple = tuple(ai_pos)
        
        for i, checkpoint in enumerate(self.checkpoints):
            if pos_tuple == checkpoint and not self.ai_reached[i]:
                self.ai_reached[i] = True
                return i  # Return checkpoint index
        
        return -1
    
    def player_completed(self):
        """Check if player has reached all checkpoints"""
        return all(self.player_reached)
    
    def ai_completed(self):
        """Check if AI has reached all checkpoints"""
        return all(self.ai_reached)
    
    def draw(self, screen, tile_size):
        """Draw checkpoints and progress indicators"""
        for i, (row, col) in enumerate(self.checkpoints):
            x, y = col * tile_size, row * tile_size
            
            # Draw checkpoint
            if self.player_reached[i] and self.ai_reached[i]:
                # Both reached
                color = PURPLE
            elif self.player_reached[i]:
                # Only player reached
                color = BLUE
            elif self.ai_reached[i]:
                # Only AI reached
                color = RED
            else:
                # Nobody reached yet
                color = YELLOW
            
            pygame.draw.rect(screen, color, (x, y, tile_size, tile_size))
            # Draw checkpoint number
            font = pygame.font.SysFont('Arial', 12)
            number = font.render(str(i + 1), True, BLACK)
            screen.blit(number, (x + tile_size//2 - number.get_width()//2, 
                                y + tile_size//2 - number.get_height()//2))

# Add a class for competitive sabotage items
class SabotageItem:
    def __init__(self, maze, player_pos, ai_pos):
        self.maze = maze
        self.rows, self.cols = len(maze), len(maze[0])
        self.position = self.find_valid_position(tuple(player_pos), tuple(ai_pos))
        # Types: 'freeze' - freezes opponent, 'confuse' - reverses controls, 'blind' - limited visibility
        self.type = random.choice(['freeze', 'confuse', 'blind'])
        self.active = True
        
    def find_valid_position(self, player_pos, ai_pos):
        """Find a valid position for the sabotage item"""
        start = (1, 0)
        end = (self.rows - 2, self.cols - 1)
        
        for _ in range(30):
            x = random.randrange(1, self.rows - 1)
            y = random.randrange(1, self.cols - 1)
            
            if (self.maze[x][y] == ' ' and 
                (x, y) != start and (x, y) != end and
                manhattan_distance((x, y), player_pos) > 5 and
                manhattan_distance((x, y), ai_pos) > 5):
                
                if self.maze[x][y] not in ['O', 'K', 'P', 'S', 'C']:
                    self.maze[x][y] = 'B'  # B for Sabotage
                    return (x, y)
        
        # Fallback
        while True:
            x = random.randrange(1, self.rows - 1)
            y = random.randrange(1, self.cols - 1)
            if self.maze[x][y] == ' ':
                self.maze[x][y] = 'B'
                return (x, y)
    
    def collect(self):
        """Player or AI collected this sabotage item"""
        if self.active:
            x, y = self.position
            self.maze[x][y] = ' '
            self.active = False
            return self.type
        return 
def display_tutorial_screen(screen, tile_size):
    """
    Display a streamlined tutorial/loading screen explaining game elements.
    
    Args:
        screen: The pygame screen surface
        tile_size: Size of each tile in the game
    """
    # Set up colors
    background_color = (30, 30, 50)
    text_color = (255, 255, 255)
    header_color = (200, 200, 255)
    
    # Fill background
    screen.fill(background_color)
    
    # Get screen dimensions
    screen_width, screen_height = screen.get_size()
    
    # Adjust tile size for tutorial display (smaller than in-game)
    display_tile_size = tile_size * 0.8
    
    # Initialize pygame font
    pygame.font.init()
    title_font = pygame.font.SysFont('arial', 32, bold=True)
    header_font = pygame.font.SysFont('arial', 20, bold=True)
    text_font = pygame.font.SysFont('arial', 16)
    timer_font = pygame.font.SysFont('arial', 24, bold=True)
    
    # Draw title
    title_text = title_font.render("GAME TUTORIAL", True, header_color)
    screen.blit(title_text, (screen_width//2 - title_text.get_width()//2, 30))
    
    # Create example elements - organized by category
    elements = [
        # Player states
        {
            "name": "Player",
            "description": "You! Use arrow keys to move.",
            "draw_func": lambda x, y: pygame.draw.rect(screen, (50, 100, 255), 
                (x, y, display_tile_size, display_tile_size))
        },
        {
            "name": "Speed Boost",
            "description": "Temporary speed increase (green glow).",
            "draw_func": lambda x, y: (
                pygame.draw.rect(screen, (50, 100, 255), (x, y, display_tile_size, display_tile_size)),
                pygame.draw.circle(screen, (0, 200, 100, 100), 
                    (x + display_tile_size//2, y + display_tile_size//2), display_tile_size)
            )
        },
        {
            "name": "Invisibility",
            "description": "Partially invisible to enemies.",
            "draw_func": lambda x, y: (
                screen.blit((lambda: (s := pygame.Surface((display_tile_size, display_tile_size), pygame.SRCALPHA), 
                            s.fill((50, 100, 255, 150)), s)[2])(), (x, y))
            )
        },
        # Obstacles
        {
            "name": "Regular Obstacle",
            "description": "Blocks your path.",
            "draw_func": lambda x, y: (
                pygame.draw.rect(screen, (100, 100, 120), (x, y, display_tile_size, display_tile_size)),
                pygame.draw.circle(screen, (50, 50, 60), 
                    (x + display_tile_size//2, y + display_tile_size//2), display_tile_size//3)
            )
        },
        {
            "name": "Killer Obstacle",
            "description": "DANGER! Game over if touched.",
            "draw_func": lambda x, y: (
                pygame.draw.rect(screen, (255, 100, 150), (x, y, display_tile_size, display_tile_size)),
                pygame.draw.circle(screen, (0, 0, 0), 
                    (x + display_tile_size//2, y + display_tile_size//2), display_tile_size//3),
                pygame.draw.circle(screen, (255, 255, 255), 
                    (x + display_tile_size//3, y + display_tile_size//3), display_tile_size//8),
                pygame.draw.circle(screen, (255, 255, 255), 
                    (x + 2*display_tile_size//3, y + display_tile_size//3), display_tile_size//8),
                pygame.draw.arc(screen, (255, 255, 255), 
                    (x + display_tile_size//4, y + display_tile_size//2, 
                     display_tile_size//2, display_tile_size//3), 0, 3.14159, 2)
            )
        },
        # Traps & Sabotage
        {
            "name": "Trap",
            "description": "Slows you down if triggered.",
            "draw_func": lambda x, y: (
                pygame.draw.rect(screen, (0, 120, 0), (x, y, display_tile_size, display_tile_size)),
                pygame.draw.line(screen, (0, 0, 0), 
                    (x + display_tile_size//4, y + display_tile_size//2),
                    (x + 3*display_tile_size//4, y + display_tile_size//2), 2),
                pygame.draw.line(screen, (0, 0, 0), 
                    (x + display_tile_size//2, y + display_tile_size//4),
                    (x + display_tile_size//2, y + 3*display_tile_size//4), 2)
            )
        },
        {
            "name": "Sabotage Item",
            "description": "Blocks path with an X mark.",
            "draw_func": lambda x, y: (
                pygame.draw.rect(screen, (150, 50, 200), (x, y, display_tile_size, display_tile_size)),
                pygame.draw.line(screen, (255, 255, 255), 
                    (x + display_tile_size//4, y + display_tile_size//4),
                    (x + 3*display_tile_size//4, y + 3*display_tile_size//4), 2),
                pygame.draw.line(screen, (255, 255, 255), 
                    (x + display_tile_size//4, y + 3*display_tile_size//4),
                    (x + 3*display_tile_size//4, y + display_tile_size//4), 2)
            )
        },
        # Power-ups
{
    "name": "Time Bonus",
    "description": "Adds extra time to your clock.",
    "draw_func": lambda x, y: (
        pygame.draw.rect(screen, (255, 170, 0), (x, y, display_tile_size, display_tile_size)),
        pygame.draw.polygon(screen, (255, 255, 255), [
            (x + display_tile_size // 2 + int((display_tile_size // 3) * math.cos(2 * math.pi * i / 5 - math.pi / 2)),
             y + display_tile_size // 2 + int((display_tile_size // 3) * math.sin(2 * math.pi * i / 5 - math.pi / 2)))
            if i % 2 == 0 else
            (x + display_tile_size // 2 + int((display_tile_size // 6) * math.cos(2 * math.pi * i / 5 - math.pi / 2)),
             y + display_tile_size // 2 + int((display_tile_size // 6) * math.sin(2 * math.pi * i / 5 - math.pi / 2)))
            for i in range(5)
        ])
    )
},
{
    "name": "Teleport",
    "description": "Instantly move to another location.",
    "draw_func": lambda x, y: (
        pygame.draw.rect(screen, (200, 50, 200), (x, y, display_tile_size, display_tile_size)),
        pygame.draw.polygon(screen, (255, 255, 255), [
            (x + display_tile_size // 2, y + display_tile_size // 4),
            (x + 3 * display_tile_size // 4, y + display_tile_size // 2),
            (x + display_tile_size // 2, y + 3 * display_tile_size // 4),
            (x + display_tile_size // 4, y + display_tile_size // 2)
        ])
    )
},
{
    "name": "Wall Phase",
    "description": "Pass through walls briefly.",
    "draw_func": lambda x, y: (
        pygame.draw.rect(screen, (50, 200, 255), (x, y, display_tile_size, display_tile_size)),
        pygame.draw.polygon(screen, (255, 255, 255), [
            (x + display_tile_size // 2, y + display_tile_size // 4),
            (x + 3 * display_tile_size // 4, y + display_tile_size // 2),
            (x + display_tile_size // 2, y + 3 * display_tile_size // 4),
            (x + display_tile_size // 4, y + display_tile_size // 2)
        ])
    )
}

    ]
    
    # Display each element with description in a grid
    y_offset = 90
    elements_per_row = 4
    spacing_x = screen_width // elements_per_row
    spacing_y = display_tile_size + 50  # Space between rows
    
    for i, element in enumerate(elements):
        row = i // elements_per_row
        col = i % elements_per_row
        
        x_pos = (spacing_x // 2) - (display_tile_size // 2) + col * spacing_x
        y_pos = y_offset + row * spacing_y
        
        # Draw element icon
        element["draw_func"](x_pos, y_pos)
        
        # Draw element name
        name_text = header_font.render(element["name"], True, header_color)
        name_x = x_pos + (display_tile_size // 2) - (name_text.get_width() // 2)
        screen.blit(name_text, (name_x, y_pos + display_tile_size + 5))
        
        # Draw element description (wrapped if needed)
        desc_text = text_font.render(element["description"], True, text_color)
        desc_x = x_pos + (display_tile_size // 2) - (desc_text.get_width() // 2)
        screen.blit(desc_text, (desc_x, y_pos + display_tile_size + 30))
    
    # Draw game instructions
    instructions = [
        "Objective: Navigate the maze while avoiding obstacles.",
        "Collect power-ups for special abilities.",
        "Watch out for traps and deadly obstacles!",
        "Press ARROW KEYS to move. Good luck!"
    ]
    
    instruction_y = screen_height - 120
    for instruction in instructions:
        inst_text = text_font.render(instruction, True, text_color)
        screen.blit(inst_text, (screen_width//2 - inst_text.get_width()//2, instruction_y))
        instruction_y += 25
    
    # Initial display
    pygame.display.flip()
    
    # Wait with countdown
    start_time = pygame.time.get_ticks()
    running = True
    countdown_duration = 10  # Reduced from 15 seconds to 10
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    running = False  # Allow skipping with spacebar
        
        # Calculate remaining time
        elapsed_time = (pygame.time.get_ticks() - start_time) // 1000  # Convert to seconds
        remaining_time = max(0, countdown_duration - elapsed_time)
        
        if remaining_time <= 0:
            break
        
        # Update countdown timer
        timer_surface = pygame.Surface((180, 35), pygame.SRCALPHA)
        timer_surface.fill((0, 0, 0, 150))
        screen.blit(timer_surface, (screen_width - 200, 20))
        
        timer_text = timer_font.render(f"Starting: {remaining_time}s", True, text_color)
        screen.blit(timer_text, (screen_width - 190, 25))
        
        skip_text = text_font.render("Press SPACE to skip", True, text_color)
        screen.blit(skip_text, (screen_width - 190, 50))
        
        pygame.display.flip()
        pygame.time.Clock().tick(60)  # Limit to 60 FPS

        
MOVE_DELAY = 100  # Delay between movements (in milliseconds)
last_move_time = 0  # Initialize the last move time


def main():
    global last_move_time
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    tile_size = 32  # Adjust according to your game
    display_tutorial_screen(screen, tile_size)
        
    # Display settings
    screen = pygame.display.set_mode((WIDTH, HEIGHT + 60))  # Extra height for UI panel
    pygame.display.set_caption("Dynamic Maze Escape Challenge")
    
    clock = pygame.time.Clock()
    title_font = pygame.font.SysFont('Arial', 32, bold=True)
    header_font = pygame.font.SysFont('Arial', 24, bold=True)
    font = pygame.font.SysFont('Arial', 20)
    small_font = pygame.font.SysFont('Arial', 20)
    
    # Game state variables
    game_active = False
    game_over = False
    level_complete = False
    player_won = False
    ai_won = False
    current_score = 0
    high_score = 0
    
    # Initialize difficulty manager
    difficulty = DifficultyManager()
    
    # Colors for UI
    UI_BG = (40, 44, 52)
    UI_TEXT = (240, 240, 240)
    UI_ACCENT = (86, 182, 194)
    UI_HIGHLIGHT = (255, 170, 0)
    UI_BUTTON = (65, 135, 155)
    UI_BUTTON_HOVER = (95, 165, 185)
    
    def initialize_game():
        nonlocal game_active, game_over, level_complete, player_won, ai_won
        
        # Reset game state
        game_active = True
        game_over = False
        level_complete = False
        player_won = False
        ai_won = False
        
        # Get current difficulty settings
        settings = difficulty.get_settings()
        
        # Generate a new maze
        maze = generate_dynamic_maze()
        
        # Find start position (always at the entrance)
        start_pos = [1, 1]
        
        # Player and AI start at the same position
        player_pos = start_pos.copy()
        ai_competitor = AICompetitor(maze, start_pos.copy())
        
        # Initialize game elements
        regular_obstacles = []
        for _ in range(settings['obstacles']):
            regular_obstacles.append(AIObstacle(maze, player_pos))
        
        killer_obstacles = []
        for _ in range(settings['killer_obstacles']):
            killer_obstacles.append(KillerObstacle(maze, player_pos))
        
        powerups = []
        for _ in range(settings['powerups']):
            powerups.append(PowerUp(maze, player_pos))
        
        # Special features (fewer than regular powerups)
        special_powerups = []
        for _ in range(max(1, settings['powerups'] // 2)):
            special_powerups.append(SpecialPowerUp(maze, player_pos, ai_competitor.position))
        
        # Create sabotage items (competitive elements)
        sabotage_items = []
        for _ in range(max(1, settings['level'] // 2)):
            sabotage_items.append(SabotageItem(maze, player_pos, ai_competitor.position))
        
        # Dynamic maze elements (more with higher levels)
        rotating_sections = []
        if settings['level'] >= 3:
            # Add rotating sections based on level
            for _ in range(1 + min(3, settings['level'] // 2)):
                center_x = random.randint(5, ROWS - 6)
                center_y = random.randint(5, COLS - 6)
                rotating_sections.append(RotatingMazeSection(maze, center_x, center_y))
        
        shifting_walls = []
        if settings['level'] >= 4:
            # Add shifting walls based on level
            for _ in range(1 + min(4, settings['level'] // 2)):
                orientation = random.choice(['horizontal', 'vertical'])
                shifting_walls.append(ShiftingWall(maze, orientation))
        
        # Initialize game systems
        game_timer = GameTimer(settings['time_limit'])
        hint_system = HintSystem(maze)
        powerup_manager = PowerUpManager()
        special_powerup_manager = SpecialPowerUpManager()
        
        # Checkpoint system (for race mode)
        checkpoints = None
        if settings['level'] >= 5:
            checkpoint_count = min(5, 1 + settings['level'] // 2)
            checkpoints = CheckpointSystem(maze, checkpoint_count)
        
        # Get maze update time
        maze_update_time = settings['maze_update_ms']
        last_maze_update = pygame.time.get_ticks()
        
        # Player status effects
        player_frozen = False
        player_frozen_until = 0
        player_confused = False
        player_confused_until = 0
        player_blinded = False
        player_blinded_until = 0
        
        # AI status effects
        ai_frozen = False
        ai_frozen_until = 0
        ai_confused = False
        ai_confused_until = 0
        
        return (maze, player_pos, ai_competitor, regular_obstacles, killer_obstacles, 
                powerups, special_powerups, sabotage_items, rotating_sections, shifting_walls, 
                game_timer, hint_system, powerup_manager, special_powerup_manager, checkpoints,
                maze_update_time, last_maze_update, player_frozen, player_frozen_until,
                player_confused, player_confused_until, player_blinded, player_blinded_until,
                ai_frozen, ai_frozen_until, ai_confused, ai_confused_until)
    
    # Button class for UI
    class Button:
        def __init__(self, x, y, width, height, text, action=None):
            self.rect = pygame.Rect(x, y, width, height)
            self.text = text
            self.action = action
            self.hovered = False
            
        def draw(self, surface):
            color = UI_BUTTON_HOVER if self.hovered else UI_BUTTON
            pygame.draw.rect(surface, color, self.rect, border_radius=8)
            pygame.draw.rect(surface, UI_ACCENT, self.rect, width=2, border_radius=8)
            
            text_surf = font.render(self.text, True, UI_TEXT)
            text_rect = text_surf.get_rect(center=self.rect.center)
            surface.blit(text_surf, text_rect)
            
        def update(self, mouse_pos):
            self.hovered = self.rect.collidepoint(mouse_pos)
            
        def check_click(self, mouse_pos, mouse_click):
            if self.rect.collidepoint(mouse_pos) and mouse_click:
                if self.action:
                    return self.action
                return True
            return False
    
    # Menu states
    menu_state = "main"
    
    # Create buttons
    start_button = Button(WIDTH//2 - 100, HEIGHT//2, 200, 50, "START GAME", "start_game")
    controls_button = Button(WIDTH//2 - 100, HEIGHT//2 + 60, 200, 50, "CONTROLS", "show_controls")
    settings_button = Button(WIDTH//2 - 100, HEIGHT//2 + 120, 200, 50, "SETTINGS", "show_settings")
    back_button = Button(WIDTH//2 - 100, HEIGHT - 100, 200, 50, "BACK", "main_menu")
    continue_button = Button(WIDTH//2 - 100, HEIGHT//2 + 120, 200, 50, "CONTINUE", "continue")
    menu_button = Button(WIDTH//2 - 100, HEIGHT//2 + 180, 200, 50, "MAIN MENU", "main_menu")
    
    # Difficulty buttons
    easy_button = Button(WIDTH//4 - 75, HEIGHT//2, 150, 50, "EASY", "set_easy")
    medium_button = Button(WIDTH//2 - 75, HEIGHT//2, 150, 50, "MEDIUM", "set_medium")
    hard_button = Button(3*WIDTH//4 - 75, HEIGHT//2, 150, 50, "HARD", "set_hard")
    
    def draw_menu():
        nonlocal menu_state
        
        screen.fill((30, 30, 40))
        
        # Draw animated background
        current_time = pygame.time.get_ticks()
        for i in range(20):
            shift = int(10 * math.sin(current_time/1000 + i/2))
            pygame.draw.line(screen, (40, 40, 60), (0, i*30 + shift), (WIDTH, i*30 + shift), 4)
            
        # Draw game title with shadow
        title_shadow = title_font.render("DYNAMIC MAZE ESCAPE CHALLENGE", True, (20, 20, 30))
        title_text = title_font.render("DYNAMIC MAZE ESCAPE CHALLENGE", True, UI_HIGHLIGHT)
        screen.blit(title_shadow, (WIDTH//2 - title_shadow.get_width()//2 + 2, HEIGHT//4 + 2))
        screen.blit(title_text, (WIDTH//2 - title_text.get_width()//2, HEIGHT//4))
        
        if menu_state == "main":
            # Main menu buttons
            start_button.draw(screen)
            controls_button.draw(screen)
            settings_button.draw(screen)
            
            # Show high score
            score_text = font.render(f"HIGH SCORE: {high_score}", True, UI_TEXT)
            screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, HEIGHT - 60))
            
            # Show current level
            level_text = font.render(f"CURRENT LEVEL: {difficulty.level}", True, UI_TEXT)
            screen.blit(level_text, (WIDTH//2 - level_text.get_width()//2, HEIGHT - 30))
            
        elif menu_state == "controls":
            # Controls menu
            controls_title = header_font.render("CONTROLS", True, UI_ACCENT)
            screen.blit(controls_title, (WIDTH//2 - controls_title.get_width()//2, HEIGHT//4 + 60))
            
            # Control instructions
            controls = [
                "ARROWS / WASD - Move player",
                "H - Request hint (limited per level)",
                "ESC - Pause game",
                "",
                "POWERUPS:",
                "Speed Boost - Move faster",
                "Invisibility - Avoid obstacles",
                "Time Bonus - Extra time",
                "Teleport - Random teleportation",
                "Trap - Place trap for AI",
                "Wall Phase - Pass through walls",
                "",
                "SABOTAGE ITEMS:",
                "Freeze - Temporarily stop AI",
                "Confuse - Make AI move randomly"
            ]
            
            for i, text in enumerate(controls):
                control_text = font.render(text, True, UI_TEXT)
                screen.blit(control_text, (WIDTH//2 - control_text.get_width()//2, HEIGHT//4 + 100 + i*24))
            
            back_button.draw(screen)
            
        elif menu_state == "settings":
            # Settings menu
            settings_title = header_font.render("DIFFICULTY SETTINGS", True, UI_ACCENT)
            screen.blit(settings_title, (WIDTH//2 - settings_title.get_width()//2, HEIGHT//4 + 60))
            
            # Difficulty options
            easy_button.draw(screen)
            medium_button.draw(screen)
            hard_button.draw(screen)
            
            # Current difficulty indicator
            current_difficulty = "EASY" if difficulty.level <= 3 else "MEDIUM" if difficulty.level <= 6 else "HARD"
            diff_text = font.render(f"CURRENT: {current_difficulty}", True, UI_HIGHLIGHT)
            screen.blit(diff_text, (WIDTH//2 - diff_text.get_width()//2, HEIGHT//2 + 70))
            
            # Show difficulty effects
            settings = difficulty.get_settings()
            effects = [
                f"Maze Size: {settings['maze_size']}x{settings['maze_size']}",
                f"Obstacles: {settings['obstacles']}",
                f"Killer Obstacles: {settings['killer_obstacles']}",
                f"Time Limit: {settings['time_limit']//1000} seconds",
                f"Maze Update Speed: {settings['maze_update_ms']//1000} seconds",
                f"Powerups: {settings['powerups']}"
            ]
            
            for i, text in enumerate(effects):
                effect_text = small_font.render(text, True, UI_TEXT)
                screen.blit(effect_text, (WIDTH//2 - effect_text.get_width()//2, HEIGHT//2 + 100 + i*20))
            
            back_button.draw(screen)
        
        return menu_state
    
    def draw_game_over():
        overlay = pygame.Surface((WIDTH, HEIGHT + 60))
        overlay.set_alpha(180)
        overlay.fill((20, 20, 30))
        screen.blit(overlay, (0, 0))
        
        # Draw game over text with shadow
        gameover_shadow = title_font.render("GAME OVER", True, (120, 0, 0))
        gameover_text = title_font.render("GAME OVER", True, (255, 0, 0))
        screen.blit(gameover_shadow, (WIDTH//2 - gameover_shadow.get_width()//2 + 2, HEIGHT//3 + 2))
        screen.blit(gameover_text, (WIDTH//2 - gameover_text.get_width()//2, HEIGHT//3))
        
        # Draw score
        score_text = header_font.render(f"FINAL SCORE: {current_score}", True, UI_TEXT)
        screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, HEIGHT//2))
        
        # Show level reached
        level_text = font.render(f"REACHED LEVEL: {difficulty.level}", True, UI_TEXT)
        screen.blit(level_text, (WIDTH//2 - level_text.get_width()//2, HEIGHT//2 + 40))
        
        # Update high score if needed
        if current_score > high_score:
            high_score_text = font.render("NEW HIGH SCORE!", True, UI_HIGHLIGHT)
            screen.blit(high_score_text, (WIDTH//2 - high_score_text.get_width()//2, HEIGHT//2 + 70))
        
        # Draw buttons
        continue_button.draw(screen)
        menu_button.draw(screen)
    
    def draw_level_complete():
        overlay = pygame.Surface((WIDTH, HEIGHT + 60))
        overlay.set_alpha(180)
        overlay.fill((20, 30, 40))
        screen.blit(overlay, (0, 0))
        
        if player_won:
            # Level complete text with shadow
            complete_shadow = title_font.render("LEVEL COMPLETE!", True, (0, 80, 0))
            complete_text = title_font.render("LEVEL COMPLETE!", True, (0, 255, 0))
            screen.blit(complete_shadow, (WIDTH//2 - complete_shadow.get_width()//2 + 2, HEIGHT//3 + 2))
            screen.blit(complete_text, (WIDTH//2 - complete_text.get_width()//2, HEIGHT//3))
            
            # Show bonus information
            settings = difficulty.get_settings()
            time_bonus = int(game_timer.time_remaining / 100)
            level_bonus = difficulty.level * 200
            
            # Calculate and display score components
            lines = [
                f"TIME BONUS: +{time_bonus}",
                f"LEVEL BONUS: +{level_bonus}",
                f"LEVEL SCORE: {current_score}",
                f"CURRENT LEVEL: {difficulty.level}"
            ]
            
            for i, line in enumerate(lines):
                line_text = font.render(line, True, UI_TEXT)
                screen.blit(line_text, (WIDTH//2 - line_text.get_width()//2, HEIGHT//2 + i*30))
            
            # Next level button (if not at max level)
            if difficulty.level < difficulty.max_level:
                next_level_button = Button(WIDTH//2 - 100, HEIGHT//2 + 140, 200, 50, "NEXT LEVEL", "next_level")
                next_level_button.draw(screen)
                
                # Get mouse position and check for clicks
                mouse_pos = pygame.mouse.get_pos()
                mouse_click = pygame.mouse.get_pressed()[0]
                next_level_button.update(mouse_pos)
                
                if next_level_button.check_click(mouse_pos, mouse_click):
                    difficulty.next_level()
                    ai_competitor.scale_with_level(difficulty.level)
                    game_elements = initialize_game()
                    return game_elements
            
        else:  # AI won
            # AI won text
            ai_shadow = title_font.render("AI WINS!", True, (80, 0, 0))
            ai_text = title_font.render("AI WINS!", True, (255, 0, 0))
            screen.blit(ai_shadow, (WIDTH//2 - ai_shadow.get_width()//2 + 2, HEIGHT//3 + 2))
            screen.blit(ai_text, (WIDTH//2 - ai_text.get_width()//2, HEIGHT//3))
            
            # Display encouraging message
            message = "Better luck next time! The AI reached the exit first."
            message_text = font.render(message, True, UI_TEXT)
            screen.blit(message_text, (WIDTH//2 - message_text.get_width()//2, HEIGHT//2))
        
        # Draw buttons
        continue_button.draw(screen)
        menu_button.draw(screen)
        
        return None  # No game elements update
    
    def draw_pause_menu():
        overlay = pygame.Surface((WIDTH, HEIGHT + 60))
        overlay.set_alpha(180)
        overlay.fill((20, 20, 30))
        screen.blit(overlay, (0, 0))
        
        # Draw pause text
        pause_text = title_font.render("PAUSED", True, UI_ACCENT)
        screen.blit(pause_text, (WIDTH//2 - pause_text.get_width()//2, HEIGHT//3))
        
        # Draw buttons
        resume_button = Button(WIDTH//2 - 100, HEIGHT//2, 200, 50, "RESUME", "resume")
        resume_button.draw(screen)
        
        controls_button = Button(WIDTH//2 - 100, HEIGHT//2 + 60, 200, 50, "CONTROLS", "show_controls")
        controls_button.draw(screen)
        
        quit_button = Button(WIDTH//2 - 100, HEIGHT//2 + 120, 200, 50, "QUIT TO MENU", "main_menu")
        quit_button.draw(screen)
        
        # Get mouse position and check for clicks
        mouse_pos = pygame.mouse.get_pos()
        mouse_click = pygame.mouse.get_pressed()[0]
        
        resume_button.update(mouse_pos)
        controls_button.update(mouse_pos)
        quit_button.update(mouse_pos)
        
        if resume_button.check_click(mouse_pos, mouse_click):
            return "resume"
        elif controls_button.check_click(mouse_pos, mouse_click):
            return "show_controls"
        elif quit_button.check_click(mouse_pos, mouse_click):
            return "main_menu"
        
        return None
    
    def draw_ui_panel(maze, player_pos, ai_competitor, game_timer, hint_system, powerup_manager, status_effects):
        # Draw UI panel background
        pygame.draw.rect(screen, UI_BG, (0, HEIGHT, WIDTH, 60))
        
        # Left side - timer and hints
        game_timer.draw(screen, font)
        hint_text = font.render(f"HINTS: {hint_system.hint_count}/{hint_system.max_hints}", True, UI_TEXT)
        screen.blit(hint_text, (10, HEIGHT + 30))
        
        # Middle - level and score
        level_text = font.render(f"LEVEL: {difficulty.level}", True, UI_TEXT)
        screen.blit(level_text, (WIDTH//2 - level_text.get_width()//2, HEIGHT + 10))
        
        score_text = font.render(f"SCORE: {current_score}", True, UI_TEXT)
        screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, HEIGHT + 30))
        
        # Right side - player position and AI position
        p_pos_text = small_font.render(f"YOU: ({player_pos[0]},{player_pos[1]})", True, UI_TEXT)
        screen.blit(p_pos_text, (WIDTH - 120, HEIGHT + 10))
        
        ai_pos_text = small_font.render(f"AI: ({ai_competitor.position[0]},{ai_competitor.position[1]})", True, UI_TEXT)
        screen.blit(ai_pos_text, (WIDTH - 120, HEIGHT + 30))
        
        # Draw status effects if any
        player_frozen, player_frozen_until, player_confused, player_confused_until, player_blinded, player_blinded_until = status_effects
        
        status_x = WIDTH//2 + 100
        current_time = pygame.time.get_ticks()
        
        if player_frozen and current_time < player_frozen_until:
            status_text = small_font.render("FROZEN", True, (100, 200, 255))
            screen.blit(status_text, (status_x, HEIGHT + 10))
            
        if player_confused and current_time < player_confused_until:
            status_text = small_font.render("CONFUSED", True, (200, 100, 255))
            screen.blit(status_text, (status_x + 70, HEIGHT + 10))
            
        if player_blinded and current_time < player_blinded_until:
            status_text = small_font.render("BLINDED", True, (255, 255, 100))
            screen.blit(status_text, (status_x + 150, HEIGHT + 10))
        
        # Draw active powerups
        powerup_manager.draw(screen, small_font)
    
    # Initialize game elements to None
    game_elements = None
    paused = False
    
    # Main game loop
    running = True
    while running:
        current_time = pygame.time.get_ticks()
        mouse_pos = pygame.mouse.get_pos()
        mouse_click = False
        
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    mouse_click = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE and game_active:
                    paused = not paused
                elif event.key == pygame.K_h and game_active and not paused and not game_over and not level_complete:
                    # Request hint
                    game_elements[11].request_hint(game_elements[1], current_time)
        
        # Handle mouse movement for button hover
        if not game_active or paused or game_over or level_complete:
            if menu_state == "main":
                start_button.update(mouse_pos)
                controls_button.update(mouse_pos)
                settings_button.update(mouse_pos)
            elif menu_state in ["controls", "settings"]:
                back_button.update(mouse_pos)
                if menu_state == "settings":
                    easy_button.update(mouse_pos)
                    medium_button.update(mouse_pos)
                    hard_button.update(mouse_pos)
            
            if game_over or level_complete:
                continue_button.update(mouse_pos)
                menu_button.update(mouse_pos)
        
        # Handle menu button clicks
        if (not game_active or paused) and mouse_click:
            if menu_state == "main":
                if start_button.check_click(mouse_pos, mouse_click) == "start_game":
                    menu_state = "main"
                    game_elements = initialize_game()
                    paused = False
                elif controls_button.check_click(mouse_pos, mouse_click) == "show_controls":
                    menu_state = "controls"
                elif settings_button.check_click(mouse_pos, mouse_click) == "show_settings":
                    menu_state = "settings"
            elif menu_state == "controls" or menu_state == "settings":
                if back_button.check_click(mouse_pos, mouse_click) == "main_menu":
                    menu_state = "main"
                
                # Handle difficulty settings
                if menu_state == "settings":
                    if easy_button.check_click(mouse_pos, mouse_click) == "set_easy":
                        difficulty.level = 1
                    elif medium_button.check_click(mouse_pos, mouse_click) == "set_medium":
                        difficulty.level = 4
                    elif hard_button.check_click(mouse_pos, mouse_click) == "set_hard":
                        difficulty.level = 7
        
        # Handle game over or level complete button clicks
        if (game_over or level_complete) and mouse_click:
            if continue_button.check_click(mouse_pos, mouse_click) == "continue":
                if level_complete and player_won and difficulty.level < difficulty.max_level:
                    difficulty.next_level()
                    game_elements = initialize_game()
                else:
                    game_active = False
                    menu_state = "main"
                    
                    # Update high score if needed
                    high_score = max(high_score, current_score)
                    
                    # Reset score if game over
                    if game_over or ai_won:
                        current_score = 0
                        difficulty.level = 1
            
            elif menu_button.check_click(mouse_pos, mouse_click) == "main_menu":
                game_active = False
                menu_state = "main"
                
                # Update high score
                high_score = max(high_score, current_score)
                
                # Reset score when going to menu
                current_score = 0
                difficulty.level = 1
        
        # Handle pause menu actions
        if paused and game_active:
            pause_action = draw_pause_menu()
            if pause_action == "resume":
                paused = False
            elif pause_action == "show_controls":
                menu_state = "controls"
                paused = False
                game_active = False
            elif pause_action == "main_menu":
                paused = False
                game_active = False
                menu_state = "main"
                # Update high score
                high_score = max(high_score, current_score)
                current_score = 0
                difficulty.level = 1
        
        # Game logic
        if game_active and not paused and not game_over and not level_complete:
            if game_elements:
                (maze, player_pos, ai_competitor, regular_obstacles, killer_obstacles, 
                 powerups, special_powerups, sabotage_items, rotating_sections, shifting_walls, 
                 game_timer, hint_system, powerup_manager, special_powerup_manager, checkpoints,
                 maze_update_time, last_maze_update, player_frozen, player_frozen_until,
                 player_confused, player_confused_until, player_blinded, player_blinded_until,
                 ai_frozen, ai_frozen_until, ai_confused, ai_confused_until) = game_elements
                
                # Update timer
                time_left = game_timer.update()
                if time_left <= 0:
                    game_over = True
                
                # Handle player movement using keyboard
               # Handle player movement using keyboard
                keys = pygame.key.get_pressed()
                current_time = pygame.time.get_ticks()  # Ensure this is updated every frame

                # Skip movement if player is frozen or not enough time has passed
                if not (player_frozen and current_time < player_frozen_until) and current_time - last_move_time > MOVE_DELAY:
                    dx, dy = 0, 0
                    if keys[pygame.K_UP] or keys[pygame.K_w]:
                        dx = -1
                    elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
                        dx = 1
                    elif keys[pygame.K_LEFT] or keys[pygame.K_a]:
                        dy = -1
                    elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                        dy = 1

                    # Apply confusion effect (reverse controls)
                    if player_confused and current_time < player_confused_until:
                        dx, dy = -dx, -dy

                    # Calculate new position
                    if dx != 0 or dy != 0:
                        new_x, new_y = player_pos[0] + dx, player_pos[1] + dy

                        # Check if new position is valid
                        if is_valid(new_x, new_y) and maze[new_x][new_y] != '#':
                            # Move player
                            player_pos[0], player_pos[1] = new_x, new_y
                            last_move_time = current_time  # update cooldown time

                            # --- (rest of your powerups, traps, checkpoints, etc.) ---
                            if new_x == len(maze) - 2 and new_y == len(maze[0]) - 1:
                                level_complete = True
                                player_won = True
                                current_score += difficulty.calculate_score(game_timer.time_remaining / 1000, hint_system.hint_count)

                            for powerup in powerups[:]:
                                if list(powerup.position) == player_pos:
                                    powerup_type = powerup.collect()
                                    if powerup_type:
                                        if powerup_type == 'speed':
                                            powerup_manager.activate('speed', current_time, 10000)
                                        elif powerup_type == 'invisibility':
                                            powerup_manager.activate('invisibility', current_time, 8000)
                                        elif powerup_type == 'time':
                                            game_timer.add_time(15)
                                        powerups.remove(powerup)

                            for special in special_powerups[:]:
                                if list(special.position) == player_pos:
                                    special_type = special.collect()
                                    if special_type:
                                        special_powerup_manager.activate(special_type, current_time, player_pos, maze, (dx, dy))
                                        special_powerups.remove(special)

                            for item in sabotage_items[:]:
                                if list(item.position) == player_pos:
                                    sabotage_type = item.collect()
                                    if sabotage_type == 'freeze':
                                        ai_frozen = True
                                        ai_frozen_until = current_time + 5000
                                    elif sabotage_type == 'confuse':
                                        ai_confused = True
                                        ai_confused_until = current_time + 7000
                                    sabotage_items.remove(item)

                            if special_powerup_manager.check_trap(player_pos):
                                special_powerup_manager.remove_trap(player_pos)
                                player_frozen = True
                                player_frozen_until = current_time + 3000

                            if checkpoints:
                                checkpoint_reached = checkpoints.check_player_progress(player_pos)
                                if checkpoint_reached >= 0:
                                    current_score += 100 * (checkpoint_reached + 1)

                
                # Update powerups
                powerup_manager.update(current_time)
                special_powerup_manager.update(current_time, maze)
                
                # Update AI competitor if not frozen
                if not (ai_frozen and current_time < ai_frozen_until):
                    ai_competitor.has_speed_boost = False
                    ai_competitor.is_invisible = False
                    
                    # Apply confusion to AI if active
                    original_intelligence = ai_competitor.intelligence
                    if ai_confused and current_time < ai_confused_until:
                        ai_competitor.intelligence = 0.2  # Make AI less intelligent when confused
                    
                    ai_competitor.update(current_time, player_pos, regular_obstacles, killer_obstacles)
                    
                    # Restore original AI intelligence
                    ai_competitor.intelligence = original_intelligence
                    
                    # Check if AI reached end
                    if ai_competitor.position[0] == len(maze) - 2 and ai_competitor.position[1] == len(maze[0]) - 1:
                        level_complete = True
                        ai_won = True
                    
                    # Check if AI reached checkpoints
                    if checkpoints:
                        checkpoints.check_ai_progress(ai_competitor.position)
                
                # Update obstacles
                for obstacle in regular_obstacles:
                    obstacle.visible = not powerup_manager.is_active('invisibility')
                    obstacle.update(current_time, player_pos)
                    
                    # Check collision with player
                    if list(obstacle.position) == player_pos and not powerup_manager.is_active('invisibility'):
                        # Player gets pushed back to start
                        player_pos[0], player_pos[1] = 1, 1
                
                # Update killer obstacles
                for obstacle in killer_obstacles:
                    obstacle.visible = not powerup_manager.is_active('invisibility')
                    obstacle.update(current_time, player_pos)
                    
                    # Check collision with player
                    if list(obstacle.position) == player_pos and not powerup_manager.is_active('invisibility'):
                        # Game over if hit by killer obstacle
                        game_over = True
                
                # Update rotating sections
                for section in rotating_sections:
                    section.update(current_time, player_pos, ai_competitor.position)
                
                # Update shifting walls
                for wall in shifting_walls:
                    wall.update(current_time, player_pos, ai_competitor.position)
                
                # Update hints
                hint_system.update(current_time)
                
                # Periodically update maze
                if current_time - last_maze_update > maze_update_time:
                    last_maze_update = current_time
                    maze = modify_maze_dynamically(maze, player_pos, 0.05 + (difficulty.level * 0.01))
                    
                    # Regenerate path to ensure it's still valid
                    end = (len(maze) - 2, len(maze[0]) - 1)
                    if not bfs(maze, tuple(player_pos), end):
                        create_escape_path(maze, tuple(player_pos), end)
                
                game_elements = (maze, player_pos, ai_competitor, regular_obstacles, killer_obstacles, 
                            powerups, special_powerups, sabotage_items, rotating_sections, shifting_walls, 
                            game_timer, hint_system, powerup_manager, special_powerup_manager, checkpoints,
                            maze_update_time, last_maze_update, player_frozen, player_frozen_until,
                            player_confused, player_confused_until, player_blinded, player_blinded_until,
                            ai_frozen, ai_frozen_until, ai_confused, ai_confused_until)
        
        # Rendering
        screen.fill((20, 20, 30))  # Dark background color
        
        if not game_active:
            menu_state = draw_menu()
        else:
            if game_elements:
                (maze, player_pos, ai_competitor, regular_obstacles, killer_obstacles, 
                powerups, special_powerups, sabotage_items, rotating_sections, shifting_walls, 
                game_timer, hint_system, powerup_manager, special_powerup_manager, checkpoints,
                maze_update_time, last_maze_update, player_frozen, player_frozen_until,
                player_confused, player_confused_until, player_blinded, player_blinded_until,
                ai_frozen, ai_frozen_until, ai_confused, ai_confused_until) = game_elements
                
                # Calculate tile size based on maze dimensions
                tile_size = min(HEIGHT // len(maze), WIDTH // len(maze[0]))
                
                # Center the maze on screen
                maze_width = len(maze[0]) * tile_size
                maze_height = len(maze) * tile_size
                offset_x = (WIDTH - maze_width) // 2
                offset_y = (HEIGHT - maze_height) // 2
                
                # Create a semi-transparent fog if player is blinded
                if player_blinded and current_time < player_blinded_until:
                    fog_surface = pygame.Surface((WIDTH, HEIGHT))
                    fog_surface.fill((20, 20, 30))
                    fog_surface.set_alpha(200)  # Semi-transparent
                    
                    # Only show area around player when blinded
                    visible_radius = 3
                    for row in range(max(0, player_pos[0] - visible_radius), min(len(maze), player_pos[0] + visible_radius + 1)):
                        for col in range(max(0, player_pos[1] - visible_radius), min(len(maze[0]), player_pos[1] + visible_radius + 1)):
                            distance = math.sqrt((row - player_pos[0])**2 + (col - player_pos[1])**2)
                            if distance <= visible_radius:
                                # Clear fog around player
                                pygame.draw.rect(fog_surface, (0, 0, 0, 0), 
                                                (offset_x + col * tile_size, offset_y + row * tile_size, 
                                                 tile_size, tile_size))
                
                # Draw maze
                for row in range(len(maze)):
                    for col in range(len(maze[0])):
                        x, y = offset_x + col * tile_size, offset_y + row * tile_size
                        cell = maze[row][col]
                        
                        if cell == '#':
                            # Draw walls with gradient effect
                            wall_color = (40, 44, 52)
                            highlight = min(255, 40 + row * 2)  # Top walls lighter
                            wall_color = (highlight, highlight, highlight)
                            pygame.draw.rect(screen, wall_color, (x, y, tile_size, tile_size))
                            pygame.draw.rect(screen, (60, 64, 72), (x, y, tile_size, tile_size), 1)
                        elif cell == 'S':
                            pygame.draw.rect(screen, (0, 200, 100), (x, y, tile_size, tile_size))
                            pygame.draw.rect(screen, (0, 255, 150), (x + 2, y + 2, tile_size - 4, tile_size - 4))
                        elif cell == 'E':
                            pygame.draw.rect(screen, (200, 50, 50), (x, y, tile_size, tile_size))
                            pygame.draw.rect(screen, (255, 100, 100), (x + 2, y + 2, tile_size - 4, tile_size - 4))
                        else:
                            # Empty path with subtle grid pattern
                            pygame.draw.rect(screen, (30, 30, 40), (x, y, tile_size, tile_size))
                            pygame.draw.rect(screen, (50, 50, 60), (x, y, tile_size, tile_size), 1)
                
                # Draw hints if active
                if not (player_blinded and current_time < player_blinded_until):
                    hint_system.draw(screen, tile_size)
                
                # Draw checkpoints if enabled
                if checkpoints:
                    checkpoints.draw(screen, tile_size)
                
                # Draw power-ups
                for powerup in powerups:
                    if powerup.active:
                        x, y = offset_x + powerup.position[1] * tile_size, offset_y + powerup.position[0] * tile_size
                        if powerup.type == 'speed':
                            color = (0, 200, 100)
                        elif powerup.type == 'invisibility':
                            color = (50, 150, 255)
                        else:  # time
                            color = (255, 170, 0)
                        pygame.draw.rect(screen, color, (x, y, tile_size, tile_size))
                        # Draw a star or symbol
                        points = []
                        for i in range(5):
                            angle = 2 * 3.14159 * i / 5 - 3.14159 / 2
                            radius = tile_size // 3 if i % 2 == 0 else tile_size // 6
                            points.append((x + tile_size // 2 + int(radius * math.cos(angle)),
                                          y + tile_size // 2 + int(radius * math.sin(angle))))
                        pygame.draw.polygon(screen, (255, 255, 255), points)
                
                # Draw special power-ups
                for special in special_powerups:
                    if special.active:
                        x, y = offset_x + special.position[1] * tile_size, offset_y + special.position[0] * tile_size
                        if special.type == 'teleport':
                            color = (200, 50, 200)
                        elif special.type == 'trap':
                            color = (0, 120, 0)
                        else:  # wall_phase
                            color = (50, 200, 255)
                        pygame.draw.rect(screen, color, (x, y, tile_size, tile_size))
                        # Draw diamond shape
                        points = [
                            (x + tile_size // 2, y + tile_size // 4),
                            (x + 3 * tile_size // 4, y + tile_size // 2),
                            (x + tile_size // 2, y + 3 * tile_size // 4),
                            (x + tile_size // 4, y + tile_size // 2)
                        ]
                        pygame.draw.polygon(screen, (255, 255, 255), points)
                
                # Draw sabotage items
                for item in sabotage_items:
                    if item.active:
                        x, y = offset_x + item.position[1] * tile_size, offset_y + item.position[0] * tile_size
                        pygame.draw.rect(screen, (150, 50, 200), (x, y, tile_size, tile_size))
                        # Draw X shape
                        pygame.draw.line(screen, (255, 255, 255), (x + tile_size // 4, y + tile_size // 4),
                                        (x + 3 * tile_size // 4, y + 3 * tile_size // 4), 2)
                        pygame.draw.line(screen, (255, 255, 255), (x + tile_size // 4, y + 3 * tile_size // 4),
                                        (x + 3 * tile_size // 4, y + tile_size // 4), 2)
                
                # Draw traps
                for trap_pos in special_powerup_manager.traps:
                    x, y = offset_x + trap_pos[1] * tile_size, offset_y + trap_pos[0] * tile_size
                    pygame.draw.rect(screen, (0, 120, 0), (x, y, tile_size, tile_size))
                    # Draw trap symbol
                    pygame.draw.line(screen, (0, 0, 0), (x + tile_size // 4, y + tile_size // 2),
                                    (x + 3 * tile_size // 4, y + tile_size // 2), 2)
                    pygame.draw.line(screen, (0, 0, 0), (x + tile_size // 2, y + tile_size // 4),
                                    (x + tile_size // 2, y + 3 * tile_size // 4), 2)
                
                # Draw regular obstacles
                for obstacle in regular_obstacles:
                    if obstacle.visible:
                        x, y = offset_x + obstacle.position[1] * tile_size, offset_y + obstacle.position[0] * tile_size
                        pygame.draw.rect(screen, (100, 100, 120), (x, y, tile_size, tile_size))
                        # Draw circular obstacle
                        pygame.draw.circle(screen, (50, 50, 60), (x + tile_size // 2, y + tile_size // 2), tile_size // 3)
                
                # Draw killer obstacles
                for obstacle in killer_obstacles:
                    if obstacle.visible:
                        x, y = offset_x + obstacle.position[1] * tile_size, offset_y + obstacle.position[0] * tile_size
                        pygame.draw.rect(screen, (255, 100, 150), (x, y, tile_size, tile_size))
                        # Draw skull or danger symbol
                        pygame.draw.circle(screen, (0, 0, 0), (x + tile_size // 2, y + tile_size // 2), tile_size // 3)
                        # Eyes
                        pygame.draw.circle(screen, (255, 255, 255), (x + tile_size // 3, y + tile_size // 3), tile_size // 8)
                        pygame.draw.circle(screen, (255, 255, 255), (x + 2 * tile_size // 3, y + tile_size // 3), tile_size // 8)
                        # Mouth
                        pygame.draw.arc(screen, (255, 255, 255), (x + tile_size // 4, y + tile_size // 2, tile_size // 2, tile_size // 3), 0, 3.14159, 2)
                
                # Draw player
                player_x, player_y = offset_x + player_pos[1] * tile_size, offset_y + player_pos[0] * tile_size
                # Player glow effect
                if powerup_manager.is_active('speed'):
                    glow_radius = tile_size * 1.5
                    glow_surface = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
                    pygame.draw.circle(glow_surface, (0, 200, 100, 100), (glow_radius, glow_radius), glow_radius)
                    screen.blit(glow_surface, (player_x + tile_size//2 - glow_radius, player_y + tile_size//2 - glow_radius))
                
                # Draw invisibility effect
                if powerup_manager.is_active('invisibility'):
                    # Semi-transparent player when invisible
                    s = pygame.Surface((tile_size, tile_size), pygame.SRCALPHA)
                    s.fill((50, 100, 255, 150))
                    screen.blit(s, (player_x, player_y))
                else:
                    pygame.draw.rect(screen, (50, 100, 255), (player_x, player_y, tile_size, tile_size))
                
                # Draw player symbol
                pygame.draw.circle(screen, (255, 255, 255), (player_x + tile_size // 2, player_y + tile_size // 2), tile_size // 3)
                pygame.draw.circle(screen, (0, 0, 0), (player_x + tile_size // 2, player_y + tile_size // 2), tile_size // 3, 2)
                
                # Draw AI competitor
                ai_x, ai_y = offset_x + ai_competitor.position[1] * tile_size, offset_y + ai_competitor.position[0] * tile_size
                # AI status effects
                if ai_frozen and current_time < ai_frozen_until:
                    # Ice effect when frozen
                    s = pygame.Surface((tile_size, tile_size), pygame.SRCALPHA)
                    s.fill((200, 200, 255, 200))
                    screen.blit(s, (ai_x, ai_y))
                else:
                    pygame.draw.rect(screen, (200, 50, 50), (ai_x, ai_y, tile_size, tile_size))
                
                # Draw AI symbol
                pygame.draw.polygon(screen, (255, 255, 255), [
                    (ai_x + tile_size // 2, ai_y + tile_size // 4),
                    (ai_x + tile_size // 4, ai_y + 3 * tile_size // 4),
                    (ai_x + 3 * tile_size // 4, ai_y + 3 * tile_size // 4)
                ])
                
                # Apply fog effect if player is blinded
                if player_blinded and current_time < player_blinded_until:
                    screen.blit(fog_surface, (0, 0))
                
                # Draw UI elements
                status_effects = (player_frozen, player_frozen_until, player_confused, 
                                  player_confused_until, player_blinded, player_blinded_until)
                draw_ui_panel(maze, player_pos, ai_competitor, game_timer, hint_system, 
                              powerup_manager, status_effects)
                
                # Draw pause instructions
                pause_text = small_font.render("Press ESC to pause", True, (200, 200, 200))
                screen.blit(pause_text, (10, HEIGHT + 45))
                
                # Draw game over overlay
                if game_over:
                    result = draw_game_over()
                    if result:
                        game_elements = result
                
                # Draw level complete overlay
                if level_complete:
                    result = draw_level_complete()
                    if result:
                        game_elements = result
                
                # Handle pause overlay
                if paused:
                    pause_result = draw_pause_menu()
                    if pause_result == "resume":
                        paused = False
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()

if __name__ == "__main__":
    main()
                                        