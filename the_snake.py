from random import choice, randint

import pygame

# Инициализация PyGame:
pygame.init()

# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Направления движения:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Цвет фона - черный:
BOARD_BACKGROUND_COLOR = (0, 0, 0)

# Цвет границы ячейки
BORDER_COLOR = (93, 216, 228)

# Цвет яблока
APPLE_COLOR = (255, 0, 0)

# Цвет змейки
SNAKE_COLOR = (0, 255, 0)

# Скорость движения змейки:
SPEED = 5

# Настройка игрового окна:
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Заголовок окна игрового поля:
pygame.display.set_caption("Змейка")

# Настройка времени:
clock = pygame.time.Clock()


# Тут опишите все классы игры.


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

        # Отрисовка головы змейки
        head_rect = pygame.Rect(self.positions[0], (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(surface, self.body_color, head_rect)
        pygame.draw.rect(surface, BORDER_COLOR, head_rect, 1)

        # Затирание последнего сегмента
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

        # изменение смещения
        position = (
            (head_x + (delta_x * GRID_SIZE)) % SCREEN_WIDTH,
            (head_y + (delta_y * GRID_SIZE)) % SCREEN_HEIGHT,
        )
        self.positions.insert(0, position)
        if len(self.positions) > self.length:
            self.last = self.positions.pop()
        else:
            self.last = None

        # проверка на самостолкновение
        if len(self.positions) > 4:
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
        self.last = None

        screen.fill(BOARD_BACKGROUND_COLOR)


class Apple(GameObject):
    """
    класс, унаследованный от GameObject, описывающий яблоко и действия
    с ним. Яблоко должно отображаться в случайных клетках игрового поля.
    """

    def __init__(self, body_color=APPLE_COLOR):
        super().__init__(body_color)
        # задать рандомную позицию
        self.randomize_position()

    # Метод draw класса Apple
    def draw(self, surface):
        """отрисовывает яблоко на игровой поверхности"""
        rect = pygame.Rect(
            (self.position[0], self.position[1]),
            (GRID_SIZE, GRID_SIZE)
        )
        pygame.draw.rect(surface, self.body_color, rect)
        pygame.draw.rect(surface, BORDER_COLOR, rect, 1)

    # Рандомное расположение яблока
    def randomize_position(self):
        """
        устанавливает случайное положение яблока на игровом поле — задаёт
        атрибуту position новое значение. Координаты выбираются так, чтобы
        яблоко оказалось в пределах игрового поля.
        """
        self.position = (
            randint(0, GRID_WIDTH - 1) * GRID_SIZE,
            randint(0, GRID_HEIGHT - 1) * GRID_SIZE
        )


# Функция обработки действий пользователя
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
            if event.key == pygame.K_UP and game_object.direction != DOWN:
                game_object.next_direction = UP
            elif event.key == pygame.K_DOWN and game_object.direction != UP:
                game_object.next_direction = DOWN
            elif event.key == pygame.K_LEFT and game_object.direction != RIGHT:
                game_object.next_direction = LEFT
            elif event.key == pygame.K_RIGHT and game_object.direction != LEFT:
                game_object.next_direction = RIGHT


def main():
    """Основная программа"""
    apple = Apple()
    snake = Snake()

    screen.fill(BOARD_BACKGROUND_COLOR)

    while True:
        clock.tick(SPEED)

        handle_keys(snake)
        snake.update_direction()
        snake.move()

        # пересечение с яблоком
        if snake.get_head_position() == apple.position:
            # обновление змейки
            snake.positions.insert(0, apple.position)
            # обновление позиции для яблока
            apple.randomize_position()

        apple.draw(screen)
        snake.draw(screen)

        pygame.display.update()


if __name__ == "__main__":
    main()
