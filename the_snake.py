"""The "Snake" game.

All of the game's logic is implemented in a single module. The player controls
a snake, collects apples, and tries to avoid colliding with obstacles.

Controls:
    Arrow keys: change direction.
    Exit: quit the game.

Dependencies:
    pygame-ce>= 2.5.7
"""

from random import randint as ri
from random import randrange as rr

import pygame as pg

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
SPEED = 12


# Configuring the game window:
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Gameplay Window Title:
pg.display.set_caption('Змейка')

# Setting the time:
clock = pg.time.Clock()


class Grid():
    """Provides a background grid for a comfortable gaming experience."""

    def __init__(self) -> None:
        self.grid_color = MESH_COLOR

    def draw(self, surface: pg.Surface) -> None:
        """Draws an object on a specified surface."""
        screen.fill(BOARD_BACKGROUND_COLOR)

        for x in range(GRID_WIDTH):
            for y in range(GRID_HEIGHT):
                pg.draw.rect(
                    surface,
                    self.grid_color,
                    pg.Rect(
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

    def draw(self, surface: pg.Surface) -> None:
        """Abstract draw method to be overridden by subclasses."""
        raise NotImplementedError(
            f'Метод draw не реализован в классе {type(self).__name__}'
        )

    def spawn(self) -> None:
        """Creates an object on the surface.

        This method is used only if object creation is not implemented by
        other methods of the class.
        """
        raise NotImplementedError(
            f'Метод spawn не реализован в классе {type(self).__name__}'
        )


class Snake(GameObject):
    """Represents the player-controlled snake entity."""

    def __init__(self) -> None:
        super().__init__()
        #  We declare the class attributes and call the “reset” method, which
        # will assign values to them, since—according to the author's
        # design—the snake's initial parameters cannot be changed when the
        # object is created.
        self.body_color: tuple[int, int, int] = SNAKE_COLOR
        self.positions: list[tuple[int, int]]
        self.direction: tuple[int, int]
        self.next_direction: tuple[int, int] | None
        self.reset()

    def draw(self, surface: pg.Surface) -> None:
        """Draw all segments of the snake on the surface."""
        for position in self.positions:
            rect = pg.Rect(position, RECT_SIZE)
            pg.draw.rect(surface, self.body_color, rect)
            pg.draw.rect(surface, BORDER_COLOR, rect, 1)

    @property
    def get_head_position(self) -> tuple[int, int]:
        """Return the coordinates of the snake's head."""
        return self.positions[0]

    def move(self) -> None:
        """The method organizes the logic of the snake's movement."""
        head_position_x, head_position_y = self.get_head_position
        direction_x, direction_y = self.direction

        # Calculate coordinates for the next position.
        next_head_position = (
            head_position_x + (direction_x * GRID_SIZE),
            head_position_y + (direction_y * GRID_SIZE)
        )
        # If you go beyond the boundary, the snake will reappear
        # on the other side.
        new_head_position = (
            next_head_position[0] % SCREEN_WIDTH,
            next_head_position[1] % SCREEN_HEIGHT
        )

        self.positions.insert(0, new_head_position)
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

    def __init__(
            self,
            occupied_positions: list[tuple[int, int]] | None = None
    ) -> None:
        super().__init__()
        self.body_color: tuple[int, int, int] = APPLE_COLOR
        self.randomize_position(occupied_positions)

    def randomize_position(
        self,
        occupied_positions: list[tuple[int, int]] | None
    ) -> None:
        """The method implements a random apple spawn."""
        if occupied_positions is None:
            occupied_positions = []
        while self.position in occupied_positions:
            self.position = (
                rr(0, SCREEN_WIDTH - GRID_SIZE, GRID_SIZE),
                rr(0, SCREEN_HEIGHT - GRID_SIZE, GRID_SIZE)
            )

    def draw(self, surface: pg.Surface) -> None:
        """Draws an apple on the selected surface."""
        rect = pg.Rect(self.position, RECT_SIZE)
        pg.draw.rect(surface, self.body_color, rect)
        pg.draw.rect(surface, APPLE_BORDER_COLOR, rect, 1)


class Rocks(GameObject):
    """The method implements obstacles for the snake game."""

    def __init__(self) -> None:
        super().__init__()
        self.body_color: tuple[int, int, int] = ROCK_COLOR
        self.positions: list[tuple[int, int]] = []

    def spawn(self) -> None:
        """Creates a list of coordinates for obstacles."""
        self.positions.clear()
        for _ in range(ri(7, 15)):
            # Multiply GRID_SIZE by 3 to increase the distance between
            # obstacles.
            random_position = (rr(0, SCREEN_WIDTH - GRID_SIZE, GRID_SIZE * 3),
                               rr(0, SCREEN_HEIGHT - GRID_SIZE, GRID_SIZE * 3))
            if random_position in self.positions:
                continue
            else:
                self.positions.append(random_position)

    def draw(self, surface: pg.Surface) -> None:
        """Draws obstacles on the selected surface."""
        for rock in self.positions:
            rock_rect = pg.Rect(rock, RECT_SIZE)
            pg.draw.rect(surface, self.body_color, rock_rect)
            pg.draw.rect(surface, ROCKS_BORDER_COLOR, rock_rect, 1)


def handle_keys(game_object: Snake) -> None:
    """Handles keyboard events and changes the object's direction."""
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            raise SystemExit
        elif event.type == pg.KEYDOWN:
            if (
                event.key == pg.K_UP
                and game_object.direction != DOWN
            ):
                game_object.next_direction = UP
            elif (
                event.key == pg.K_DOWN
                and game_object.direction != UP
            ):
                game_object.next_direction = DOWN

            elif (
                event.key == pg.K_LEFT
                and game_object.direction != RIGHT
            ):
                game_object.next_direction = LEFT

            elif (
                event.key == pg.K_RIGHT
                and game_object.direction != LEFT
            ):
                game_object.next_direction = RIGHT


def spawn_objects(*args: GameObject) -> None:
    """Spawns objects."""
    for obj in args:
        obj.spawn()


def draw_objects(surface: pg.Surface, *args: GameObject | Grid) -> None:
    """Draws the objects that have been passed to it."""
    for obj in args:
        obj.draw(surface)


def main() -> None:
    """The main game control function.

    Performs: initializes pg, creates objects, and runs an infinite loop
    that includes collision checks, screen clearing, rendering objects,
    and frame rate monitoring. It runs until the user closes the game window.

    Args:
        None

    Returns:
        None
    """
    pg.init()

    grid = Grid()
    snake = Snake()
    rocks = Rocks()
    spawn_objects(rocks)
    apple = Apple(snake.positions + rocks.positions)

    while True:
        handle_keys(snake)
        snake.update_direction()
        snake.move()

        if snake.get_head_position in snake.positions[4:]:
            spawn_objects(rocks)
            snake.reset()

        elif snake.get_head_position in rocks.positions:
            spawn_objects(rocks)
            snake.reset()

        elif snake.get_head_position == apple.position:
            snake.length += 1
            apple.randomize_position(snake.positions + rocks.positions)

        draw_objects(screen, grid, rocks, apple, snake)

        pg.display.update()
        clock.tick(SPEED)


if __name__ == '__main__':
    main()
