import pygame
import sys
import random
import math


class Player:
    def __init__(self, screen_width, screen_height):
        self.x = screen_width // 2
        self.y = screen_height // 2

        self.radius = 15
        self.speed = 5
        self.XP = 100

        self.color = (0, 225, 220)

        self.screen_width = screen_width
        self.screen_height = screen_height

    def move(self, keys):
        # перемещение
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.x -= self.speed

        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.x += self.speed

        if keys[pygame.K_w] or keys[pygame.K_UP]:
            self.y -= self.speed

        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            self.y += self.speed

        # проверка границ - пока нет

    def draw(self, screen):
        # pygame.draw.circle(поверхность, цвет, (x, y), радиус)
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)



class Enemy:
    def __init__(self, screen_width, screen_height, player_x, player_y):
        self.pos = random.choice(['left', 'right', 'up', 'down'])

        if self.pos == 'left':
            self.x = -1
            self.y = random.randint(0, screen_height)

        elif self.pos == 'right':
            self.x = screen_width + 2
            self.y = random.randint(0, screen_height)

        elif self.pos == 'up':
            self.x = random.randint(-1, screen_width)
            self.y = -2

        elif self.pos == 'down':
            self.x = random.randint(-1, screen_width)
            self.y = screen_height + 2

        # параметры врага
        self.radius = 15
        self.speed = random.randint(1, 5)
        self.XP = 50
        self.color = (60, 0, 120)

        self.screen_width = screen_width
        self.screen_height = screen_height

        # цель
        self.target_x = player_x
        self.target_y = player_y

    def update(self, player_x, player_y):
         # вычисляем расстояние до цели
        dx = player_x - self.x
        dy = player_y - self.y

        # вычисляем длину нашего вектора
        distance = math.sqrt(dx**2 + dy**2)

        # проверяем расстояние (больше 0)
        if distance > 0:
            # Нормализуем вектор (делаем длину 1) и умножаем на скорость
            # dx / distance - косинус угла, dy / distance - синус угла
            self.x += (dx / distance) * self.speed
            self.y += (dy / distance) * self.speed

         # ОБНОВЛЯЕМ ЦЕЛЬ (для следования за движущимся игроком)
        self.target_x = player_x
        self.target_y = player_y


    def draw(self, screen):
        # 1. ОСНОВНОЙ КРУГ pygame.draw.circle(где мы рисуем, цвет, (х, у), радиус)
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)

        # 2. "ГЛАЗА" ВРАГА (для наглядности)
        pygame.draw.circle(screen, (225, 225, 225), (int(self.x - 5), int(self.y - 5)), 4)
        pygame.draw.circle(screen, (225, 225, 225), (int(self.x + 5), int(self.y + 5)), 4)

        # 3. Зрачки
        pygame.draw.circle(screen, (0, 0, 0), (int(self.x - 5), int(self.y - 5)), 1)
        pygame.draw.circle(screen, (0, 0, 0), (int(self.x + 5), int(self.y + 5)), 1)




class Bullet:
    def __init__(self, x, y, target_x, target_y, screen_width, screen_height):
        # НАЧАЛЬНАЯ ПОЗИЦИЯ (у игрока)
        self.x = x
        self.y = y

        # ПАРАМЕТРЫ ПУЛИ
        self.radius = 2
        self.speed = 25
        self.damage = 25
        self.color = (1, 10, 20)  # Желтый цвет

        # ГРАНИЦЫ ЭКРАНА (для удаления пуль за экраном)
        self.screen_width = screen_width
        self.screen_height = screen_height

        # Разница координат между целью и начальной позицией
        dx = target_x - x
        dy = target_y - y

        # Расстояние до цели
        distance = math.sqrt(dx**2 + dy**2)

        if distance > 0:
            # Нормализуем вектор (делаем длину 1) и умножаем на скорость
            # Это дает нам скорость по X и Y
            self.dx = (dx / distance) * self.speed
            self.dy = (dy / distance) * self.speed
            print(dx, dy)
        else:
            pass

    def update(self):
        # Двигаем пулю
        self.x += self.dx
        self.y += self.dy

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)

    def is_off_screen(self):
        return (self.x < 0 or self.x > self.screen_width or self.y < 0 or self.y > self.screen_height)




class GameCore:
    def __init__(self):
        pygame.init()

        # параметры окна
        self.WIDTH = 1000
        self.HEIGHT = 800

        #  создаем дисплей
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT)) # pygame.display.set_mode() создает окно с указанными размерами

        # заголовок окна
        pygame.display.set_caption("2d Game")

        # создаем часы для контроля фпс
        self.clock = pygame.time.Clock()
        self.FPS = 60

        # флаги
        self.running = True
        self.game_over = False

        # игрок
        self.player = Player(self.WIDTH, self.HEIGHT)

            # враг
        # [] - пустой список для хранения врагов
        self.enemies = []
        # ТАЙМЕР ДЛЯ СОЗДАНИЯ ВРАГОВ
        self.enemy_timer = 0 # Счетчик кадров
        self.enemy_spawn_delay = 60 # Враги появляются каждые 60 кадров (1 секунда)

        # шрифты
        self.font = pygame.font.SysFont('Arial', 24)
        self.font_big = pygame.font.SysFont('Arial', 30)

        # пули
        self.bullets = []

        #
        self.score = 0




    def handle_events(self): # обработка событий
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                # Получаем позицию мыши
                mouse_x, mouse_y = pygame.mouse.get_pos()

                # создаем пулю
                # Bullet(начало_x, начало_y, цель_x, цель_y, ширина_экрана, высота_экрана)
                new_bullet = Bullet(self.player.x, self.player.y, mouse_x, mouse_y, self.WIDTH, self.HEIGHT)
                # Добавляем пулю в список
                self.bullets.append(new_bullet)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r and self.game_over == True:
                    self.restart_game()


    def update_game(self): # обновление состояния игры

        # Если игра окончена, не обновляем состояние
        if self.game_over:
            return

        # УПРАВЛЕНИЕ ИГРОКОМ
        keys = pygame.key.get_pressed()
        self.player.move(keys)

        # СОЗДАНИЕ НОВЫХ ВРАГОВ
        self.enemy_timer += 1 # увеличиваем счетчик врагов

        if self.enemy_timer > self.enemy_spawn_delay:
            # Создаем нового врага
            new_enemy = Enemy(self.WIDTH, self.HEIGHT, self.player.x, self.player.y)

            self.enemies.append(new_enemy)

            self.enemy_timer = 0 # Сбрасываем таймер

        #   УДАЛЕНИЕ ВРАГОВ, КОТОРЫЕ ДАЛЕКО ОТ ИГРОКА (НЕ ОБЯЗАТЕЛЬНО)

        # обновление врагов
        for enemy in self.enemies:
            enemy.update(self.player.x, self.player.y)

        for enemy in self.enemies[:]:
        # Вычисляем расстояние между врагом и игроком
            dx = enemy.x - self.player.x
            dy = enemy.y - self.player.y
            distance = math.sqrt(dx**2 + dy**2)

            # Если расстояние меньше суммы радиусов - СТОЛКНОВЕНИЕ!
            if distance < (enemy.radius + self.player.radius):
                self.player.XP -= 25
                self.enemies.remove(enemy)

                if self.player.XP <= 0:
                    self.player.XP = 0
                    self.game_over = True


        # обновление пуль
        for bullet in self.bullets[:]: # Используем копию списка для безопасного удаления
            bullet.update()

            if bullet.is_off_screen():
                self.bullets.remove(bullet)
                continue

        for bullet in self.bullets[:]:
            for enemy in self.enemies[:]:
                dx = bullet.x - enemy.x
                dy = bullet.y - enemy.y
                distance  = math.sqrt(dx**2 + dy**2)

                if distance < (bullet.radius + enemy.radius):
                    enemy.XP -= bullet.damage

                    if enemy.XP <= 0:
                        self.score += 1
                        self.enemies.remove(enemy)

                    if bullet in self.bullets:  # Удаляем пулю (пуля исчезает при попадании)
                        self.bullets.remove(bullet)

                    break  # Прерываем цикл по врагам (пуля попала, проверять дальше не нужно)


    def draw_game_over(self):
        win = pygame.Surface((self.WIDTH, self.HEIGHT), pygame.SRCALPHA)
        win.fill(0, 0, 0)
        self.screen.blit(win, (0, 0))
        game_over_text = self.font_big.render("Потрачено", True,  (225, 50, 50))
        self.screen.blit(game_over_text, (self.WIDTH // 2 - game_over_text.get_width, self.HEIGHT // 2 - 100))




    def drow_game(self):
        self.screen.fill((225, 225, 225))

        # РИСУЕМ ВСЕХ ВРАГОВ
        for enemy in self.enemies:
            enemy.draw(self.screen)

        for bullet in self.bullets:
            bullet.draw(self.screen)


        font = pygame.font.SysFont('Arial', 24)

        # создаем текст
        score = font.render(f'Kills: {self.score}', True, (0, 0, 0))
        XP = font.render(f'XP: {self.player.XP}', True, (100, 20, 20))
        text2  = font.render('press WASD to move', True, (0, 220, 220))

        self.player.draw(self.screen)


        # screen.blit(текст, (x, y)) - рисует текст в указанных координатах
        self.screen.blit(score, (self.WIDTH // 2 - score.get_width() // 2, 30))
        self.screen.blit(XP, (self.WIDTH // 2 - score.get_width() // 2, 60))
        self.screen.blit(text2, (self.WIDTH // 2 - text2.get_width() // 2, 90))

    def restart_game(self):
        self.player = Player(self.WIDTH, self.HEIGHT)
        self.enemies = []
        self.bullets =[]
        self.enemy_timer = 0
        self.score = 0
        self.game_over = False

    def run(self):

        while self.running:
            # 1 -
            self.handle_events()

            # 2 -
            self.update_game()

            # 3 -
            self.drow_game()

            # 4 -
            pygame.display.flip()

            # 5 -

            self.clock.tick(self.FPS)

        pygame.quit()
        sys.exit()





if __name__ == '__main__':
    game = GameCore()
    game.run()


