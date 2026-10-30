"""The "Snake" game.

All of the game's logic is implemented in a single module. The player controls
a snake, collects apples, and tries to avoid colliding with obstacles.

Controls:
    Arrow keys: change direction.
    Exit: quit the game.

Dependencies:
    pygame-ce>= 2.5.7
"""

from random import randrange as rr, randint as ri

import pygame

# Constants for field and grid dimensions:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE
RECT_SIZE = (GRID_SIZE, GRID_SIZE)

# Directions:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Colors:
BOARD_BACKGROUND_COLOR = (53, 104, 45)
MESH_COLOR = (43, 115, 45)
BORDER_COLOR = (93, 216, 228)
ROCKS_BORDER_COLOR = (117, 127, 116)
APPLE_BORDER_COLOR = (150, 45, 35)
APPLE_COLOR = (201, 70, 30)
SNAKE_COLOR = (107, 142, 35)
ROCK_COLOR = (147, 147, 136)

# Snake movement speed:
SPEED = 10


# Configuring the game window:
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Gameplay Window Title:
pygame.display.set_caption('Змейка')

# Setting the time:
clock = pygame.time.Clock()


class Grid():
    """Provides a background grid for a comfortable gaming experience."""

    def __init__(self) -> None:
        self.grid_color = MESH_COLOR

    def draw(self, surface: pygame.Surface) -> None:
        """Draws an object on a specified surface."""
        screen.fill(BOARD_BACKGROUND_COLOR)

        for x in range(GRID_WIDTH):
            for y in range(GRID_HEIGHT):
                pygame.draw.rect(
                    surface,
                    self.grid_color,
                    pygame.Rect(
                        (x * GRID_SIZE, y * GRID_SIZE),
                        RECT_SIZE
                    ),
                    1
                )


class GameObject():
    """Base class for all interactive game entities."""

    def __init__(self) -> None:
        self.position: tuple[int, int] = (
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT // 2
        )
        self.body_color: tuple[int, int, int] | None = None

    def draw(self, surface: pygame.Surface) -> None:
        """Abstract draw method to be overridden by subclasses."""
        pass


class Snake(GameObject):
    """Represents the player-controlled snake entity."""

    def __init__(
            self,
            length: int = 1,
            direction: tuple[int, int] = RIGHT,
            next_direction: tuple[int, int] | None = None,
            last: tuple[int, int] | None = None
    ) -> None:
        super().__init__()
        self.positions: list[tuple[int, int]] = [
            (SCREEN_WIDTH // 2,
             SCREEN_HEIGHT // 2)
        ]
        self.body_color: tuple[int, int, int] = SNAKE_COLOR
        self.length = length
        self.direction = direction
        self.next_direction = next_direction
        self._last = last

    def draw(self, surface: pygame.Surface) -> None:
        """Draw all segments of the snake on the surface."""
        for position in self.positions:
            rect = pygame.Rect(position, RECT_SIZE)
            pygame.draw.rect(surface, self.body_color, rect)
            pygame.draw.rect(surface, BORDER_COLOR, rect, 1)

    @property
    def get_head_position(self) -> tuple[int, int]:
        """Return the coordinates of the snake's head."""
        return self.positions[0]

    def move(self) -> None:
        """The method organizes the logic of the snake's movement."""
        head_position = self.get_head_position
        # Calculate coordinates for the next position.
        next_head_pos = (
            head_position[0] + (self.direction[0] * GRID_SIZE),
            head_position[1] + (self.direction[1] * GRID_SIZE)
        )
        # If you go beyond the boundary, the snake will reappear
        # on the other side.
        new_head_pos = (
            next_head_pos[0] % SCREEN_WIDTH,
            next_head_pos[1] % SCREEN_HEIGHT
        )

        self.positions.insert(0, new_head_pos)
        # Remove the last segment to simulate movement.
        if len(self.positions) > self.length:
            self._last = self.positions[-1]
            del self.positions[-1]

    def update_direction(self) -> None:
        """Changes the direction of travel."""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def reset(self) -> None:
        """Restarts the game when it collides with an obstacle."""
        self.positions = [self.position]
        self.length = 1
        self.direction = RIGHT
        self.next_direction = None


class Apple(GameObject):
    """The method provides food for the snake."""

    def __init__(self) -> None:
        super().__init__()
        self.body_color: tuple[int, int, int] = APPLE_COLOR

    def randomize_position(self, snake: Snake, rocks: Rocks) -> None:
        """The method implements a random apple spawn."""
        while (
            self.position in snake.positions
            or self.position in rocks.positions
        ):
            self.position = (
                rr(0, SCREEN_WIDTH - GRID_SIZE, GRID_SIZE),
                rr(0, SCREEN_HEIGHT - GRID_SIZE, GRID_SIZE)
            )

    def draw(self, surface: pygame.Surface) -> None:
        """Draws an apple on the selected surface."""
        rect = pygame.Rect(self.position, RECT_SIZE)
        pygame.draw.rect(surface, self.body_color, rect)
        pygame.draw.rect(surface, APPLE_BORDER_COLOR, rect, 1)


class Rocks(GameObject):
    """The method implements obstacles for the snake game."""

    def __init__(self) -> None:
        super().__init__()
        self.body_color: tuple[int, int, int] = ROCK_COLOR
        self.positions: list[tuple[int, int]] = []

    def spawn_rock(self) -> None:
        """Creates a list of coordinates for obstacles."""
        self.positions.clear()
        for _ in range(ri(7, 15)):
            # Multiply GRID_SIZE by 3 to increase the distance between
            # obstacles.
            self.positions.append(
                (rr(0, SCREEN_WIDTH - GRID_SIZE, GRID_SIZE * 3),
                 rr(0, SCREEN_HEIGHT - GRID_SIZE, GRID_SIZE * 3))
            )

    def draw(self, surface: pygame.Surface) -> None:
        """Draws obstacles on the selected surface."""
        for rock in self.positions:
            rock_rect = pygame.Rect(rock, RECT_SIZE)
            pygame.draw.rect(surface, self.body_color, rock_rect)
            pygame.draw.rect(surface, ROCKS_BORDER_COLOR, rock_rect, 1)


def handle_keys(game_object: Snake) -> None:
    """Handles keyboard events and changes the object's direction."""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
        elif event.type == pygame.KEYDOWN:
            if (
                event.key == pygame.K_UP
                and game_object.direction != DOWN
            ):
                game_object.next_direction = UP
            elif (
                event.key == pygame.K_DOWN
                and game_object.direction != UP
            ):
                game_object.next_direction = DOWN

            elif (
                event.key == pygame.K_LEFT
                and game_object.direction != RIGHT
            ):
                game_object.next_direction = LEFT

            elif (
                event.key == pygame.K_RIGHT
                and game_object.direction != LEFT
            ):
                game_object.next_direction = RIGHT


def spawn_objects(
        obj_rocks: Rocks,
        obj_apple: Apple,
        obj_snake: Snake
) -> None:
    """Spawns objects."""
    obj_rocks.spawn_rock()
    obj_apple.randomize_position(obj_snake, obj_rocks)


def draw_objects(surface: pygame.Surface, *args: GameObject | Grid) -> None:
    """Draws the objects that have been passed to it."""
    for obj in args:
        obj.draw(surface)


def main() -> None:
    """The main game control function.

    Performs: initializes pygame, creates objects, and runs an infinite loop
    that includes collision checks, screen clearing, rendering objects,
    and frame rate monitoring. It runs until the user closes the game window.

    Args:
        None

    Returns:
        None
    """
    pygame.init()

    grid = Grid()
    snake = Snake()
    apple = Apple()
    rocks = Rocks()

    spawn_objects(rocks, apple, snake)

    while True:
        handle_keys(snake)
        snake.update_direction()
        snake.move()

        if snake.get_head_position in snake.positions[2:]:
            spawn_objects(rocks, apple, snake)
            snake.reset()

        if snake.get_head_position in rocks.positions:
            spawn_objects(rocks, apple, snake)
            snake.reset()

        if snake.get_head_position == apple.position:
            snake.length += 1
            apple.randomize_position(snake, rocks)

        draw_objects(screen, grid, rocks, apple, snake)

        pygame.display.update()
        clock.tick(SPEED)


if __name__ == '__main__':
    main()
