from random import choice, randint

import pygame

pygame.init()

SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

BOARD_BACKGROUND_COLOR = (0, 0, 0)

BORDER_COLOR = (93, 216, 228)

APPLE_COLOR = (255, 0, 0)

SNAKE_COLOR = (0, 255, 0)

SPEED = 5

TURNS = {
    (pygame.K_UP, DOWN): UP,
    (pygame.K_DOWN, UP): DOWN,
    (pygame.K_RIGHT, LEFT): RIGHT,
    (pygame.K_LEFT, RIGHT): LEFT,
}

DANGEROUS_LENGHT = 4

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

clock = pygame.time.Clock()


class GameObject:
    """
    Это базовый класс, от которого наследуются другие игровые объекты.
    Он содержит общие атрибуты игровых объектов — например, эти атрибуты
    описывают позицию и цвет объекта. Этот же класс содержит и заготовку
    метода для отрисовки объекта на игровом поле
    """

    def __init__(self, body_color=None):
        self.position = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.body_color = body_color

    def draw(self):
        """
        это абстрактный метод, который предназначен для переопределения в
        дочерних классах. Этот метод должен определять, как объект будет
          отрисовываться на экране.
        """
        raise NotImplementedError("Important...please implement it.")


class Snake(GameObject):
    """
    Класс, унаследованный от GameObject, описывающий змейку и её
    поведение. Этот класс управляет её движением, отрисовкой, а также
    обрабатывает действия пользователя.
    """

    def __init__(self, body_color=SNAKE_COLOR):
        super().__init__(body_color)
        self.direction = RIGHT
        self.next_direction = None

        self.positions = [self.position]
        self.length = 1
        self.max_length = []
        self.speed = SPEED
        self.last = None

    def draw(self, surface):
        """отрисовывает змейку на экране, затирая след"""
        for position in self.positions[:-1]:
            rect = pygame.Rect(
                (position[0], position[1]),
                (GRID_SIZE, GRID_SIZE)
            )
            pygame.draw.rect(surface, self.body_color, rect)
            pygame.draw.rect(surface, BORDER_COLOR, rect, 1)

        head_rect = pygame.Rect(self.positions[0], (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(surface, self.body_color, head_rect)
        pygame.draw.rect(surface, BORDER_COLOR, head_rect, 1)

        if self.last:
            last_rect = pygame.Rect(
                (self.last[0], self.last[1]), (GRID_SIZE, GRID_SIZE)
            )
            pygame.draw.rect(surface, BOARD_BACKGROUND_COLOR, last_rect)

    def move(self):
        """
        обновляет позицию змейки (координаты каждой секции), добавляя новую
        голову в начало списка positions и удаляя последний элемент, если
        длина змейки не увеличилась.
        """
        head_x, head_y = self.positions[0]
        delta_x, delta_y = self.direction

        position = (
            (head_x + (delta_x * GRID_SIZE)) % SCREEN_WIDTH,
            (head_y + (delta_y * GRID_SIZE)) % SCREEN_HEIGHT,
        )
        self.positions.insert(0, position)
        if len(self.positions) > self.length:
            self.last = self.positions.pop()
        else:
            self.last = None

        if len(self.positions) > DANGEROUS_LENGHT:
            for pos in self.positions[2:]:
                if pos == self.get_head_position():
                    self.reset()

    def update_direction(self):
        """обновляет направление движения змейки."""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def get_head_position(self):
        """возвращает позицию головы змейки."""
        return self.positions[0]

    def reset(self):
        """сбрасывает змейку в начальное состояние"""
        self.direction = choice([RIGHT, DOWN, LEFT, UP])
        self.next_direction = None

        self.positions = [self.position]
        self.length = 1
        self.speed = SPEED
        self.last = None

        screen.fill(BOARD_BACKGROUND_COLOR)


class Apple(GameObject):
    """
    класс, унаследованный от GameObject, описывающий яблоко и действия
    с ним. Яблоко должно отображаться в случайных клетках игрового поля.
    """

    def __init__(self, body_color=APPLE_COLOR):
        super().__init__(body_color)
        self.randomize_position()

    def draw(self, surface):
        """отрисовывает яблоко на игровой поверхности"""
        rect = pygame.Rect(
            (self.position[0], self.position[1]),
            (GRID_SIZE, GRID_SIZE)
        )
        pygame.draw.rect(surface, self.body_color, rect)
        pygame.draw.rect(surface, BORDER_COLOR, rect, 1)

    def randomize_position(self):
        """
        устанавливает случайное положение яблока на игровом поле — задаёт
        атрибуту position новое значение. Координаты выбираются так, чтобы
        яблоко оказалось в пределах игрового поля.
        """
        self.position = (
            randint(0, GRID_WIDTH - 1) * GRID_SIZE,
            randint(0, GRID_HEIGHT - 1) * GRID_SIZE,
        )


def handle_keys(game_object):
    """
    обрабатывает нажатия клавиш,
    чтобы изменить направление движения змейки
    """
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
        elif event.type == pygame.KEYDOWN:
            for turn in TURNS:
                if event.key == turn[0] and game_object.direction != turn[1]:
                    game_object.next_direction = TURNS[turn]


def main():
    """Основная программа"""
    apple = Apple()
    snake = Snake()

    screen.fill(BOARD_BACKGROUND_COLOR)

    while True:
        clock.tick(snake.speed)

        handle_keys(snake)
        snake.update_direction()
        snake.move()

        if snake.get_head_position() == apple.position:
            snake.positions.insert(0, apple.position)
            apple.randomize_position()
            snake.length += 1
            snake.speed += 1

        if snake.length not in snake.max_length:
            snake.max_length.insert(0, snake.length)

        apple.draw(screen)
        snake.draw(screen)

        pygame.display.update()
        pygame.display.set_caption(
            "Змейка | Скорость игры: "
            + str(snake.speed)
            + " | Размер змейки: "
            + str(snake.length)
            + " | Рекорд: "
            + str(max(snake.max_length))
        )


if __name__ == "__main__":
    main()
