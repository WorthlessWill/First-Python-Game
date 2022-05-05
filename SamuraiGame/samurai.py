import pygame
import os
import time
import random
pygame.font.init()

WIDTH, HEIGHT = 750, 750
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Samurai Game")

# Load images
PURPLE_MONGOL = pygame.image.load(os.path.join("sassets", "mongol_purple.png"))
GREEN_MONGOL = pygame.image.load(os.path.join("sassets", "mongol_green.png"))
BLUE_MONGOL = pygame.image.load(os.path.join("sassets", "mongol_blue.png"))

# Player player
SAMURAI = pygame.image.load(os.path.join("sassets", "player.png"))

# Arrow
PURPLE_ARROW = pygame.image.load(os.path.join("sassets", "arrow_mongol.png"))
GREEN_ARROW = pygame.image.load(os.path.join("sassets", "arrow_mongol.png"))
BLUE_ARROW = pygame.image.load(os.path.join("sassets", "arrow_mongol.png"))
ARROW = pygame.image.load(os.path.join("sassets", "arrow.png"))

# Background
BG = pygame.transform.scale(pygame.image.load(os.path.join("sassets", "backgroundS.png")), (WIDTH, HEIGHT))

class Arrow:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def move(self, vel):
        self.y += vel

    def off_screen(self, height):
        return not(self.y <= height and self.y >= 0)

    def collision(self, obj):
        return collide(self, obj)


class Person:
    COOLDOWN = 30

    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.person_img = None
        self.arrow_img = None
        self.arrows = []
        self.cool_down_counter = 0

    def draw(self, window):
        window.blit(self.person_img, (self.x, self.y))
        for arrow in self.arrows:
            arrow.draw(window)

    def move_arrows(self, vel, obj):
        self.cooldown()
        for arrow in self.arrows:
            arrow.move(vel)
            if arrow.off_screen(HEIGHT):
                self.arrows.remove(arrow)
            elif arrow.collision(obj):
                obj.health -= 10
                self.arrows.remove(arrow)

    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1

    def shoot(self):
        if self.cool_down_counter == 0:
            arrow = Arrow(self.x, self.y, self.arrow_img)
            self.arrows.append(arrow)
            self.cool_down_counter = 1

    def get_width(self):
        return self.person_img.get_width()

    def get_height(self):
        return self.person_img.get_height()


class Player(Person):
    def __init__(self, x, y, health=200):
        super().__init__(x, y, health)
        self.person_img = SAMURAI
        self.arrow_img = ARROW
        self.mask = pygame.mask.from_surface(self.person_img)
        self.max_health = health

    def move_arrows(self, vel, objs):
        self.cooldown()
        for arrow in self.arrows:
            arrow.move(vel)
            if arrow.off_screen(HEIGHT):
                self.arrows.remove(arrow)
            else:
                for obj in objs:
                    if arrow.collision(obj):
                        objs.remove(obj)
                        if arrow in self.arrows:
                            self.arrows.remove(arrow)

    def draw(self, window):
        super().draw(window)
        self.healthbar(window)

    def healthbar(self, window):
        pygame.draw.rect(window, (255,0,0), (self.x, self.y + self.person_img.get_height() + 10, self.person_img.get_width(), 10))
        pygame.draw.rect(window, (0,255,0), (self.x, self.y + self.person_img.get_height() + 10, self.person_img.get_width() * (self.health/self.max_health), 10))


class Enemy(Person):
    COLOR_MAP = {
                "purple": (PURPLE_MONGOL, PURPLE_ARROW),
                "green": (GREEN_MONGOL, GREEN_ARROW),
                "blue": (BLUE_MONGOL, BLUE_ARROW)
                }

    def __init__(self, x, y, color, health=100):
        super().__init__(x, y, health)
        self.person_img, self.arrow_img = self.COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.person_img)

    def move(self, vel):
        self.y += vel

    def shoot(self):
        if self.cool_down_counter == 0:
            arrow = Arrow(self.x-20, self.y, self.arrow_img)
            self.arrows.append(arrow)
            self.cool_down_counter = 1


def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None

def main():
    run = True
    FPS = 60
    level = 0
    lives = 10
    main_font = pygame.font.SysFont("kosugimaru", 50)
    lost_font = pygame.font.SysFont("kosugimaru", 60)

    enemies = []
    wave_length = 5
    enemy_vel = 1

    player_vel = 5
    arrow_vel = 5

    player = Player(300, 630)

    clock = pygame.time.Clock()

    lost = False
    lost_count = 0

    def redraw_window():
        WIN.blit(BG, (0,0))
        # draw text
        lives_label = main_font.render(f"Castle: {lives}", 1, (255,255,255))
        level_label = main_font.render(f"Wave: {level}", 1, (255,255,255))

        WIN.blit(lives_label, (10, 10))
        WIN.blit(level_label, (WIDTH - level_label.get_width() - 10, 10))

        for enemy in enemies:
            enemy.draw(WIN)

        player.draw(WIN)

        if lost:
            lost_label = lost_font.render("The castle has fallen!", 1, (255,255,255))
            WIN.blit(lost_label, (WIDTH/2 - lost_label.get_width()/2, 350))

        pygame.display.update()

    while run:
        clock.tick(FPS)
        redraw_window()

        if lives <= 0 or player.health <= 0:
            lost = True
            lost_count += 1

        if lost:
            if lost_count > FPS * 3:
                run = False
            else:
                continue

        if len(enemies) == 0:
            level += 1
            wave_length += 5
            for i in range(wave_length):
                enemy = Enemy(random.randrange(50, WIDTH-100), random.randrange(-1500, -100), random.choice(["purple", "blue", "green"]))
                enemies.append(enemy)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] and player.x - player_vel > 0: # left
            player.x -= player_vel
        if keys[pygame.K_d] and player.x + player_vel + player.get_width() < WIDTH: # right
            player.x += player_vel
        if keys[pygame.K_w] and player.y - player_vel > 0: # up
            player.y -= player_vel
        if keys[pygame.K_s] and player.y + player_vel + player.get_height() + 15 < HEIGHT: # down
            player.y += player_vel
        if keys[pygame.K_SPACE]:
            player.shoot()

        for enemy in enemies[:]:
            enemy.move(enemy_vel)
            enemy.move_arrows(arrow_vel, player)

            if random.randrange(0, 2*60) == 1:
                enemy.shoot()

            if collide(enemy, player):
                player.health -= 10
                enemies.remove(enemy)
            elif enemy.y + enemy.get_height() > HEIGHT:
                lives -= 1
                enemies.remove(enemy)

        player.move_arrows(-arrow_vel, enemies)

def main_menu():
    title_font = pygame.font.SysFont("kosugimaru", 70)
    run = True
    while run:
        WIN.blit(BG, (0,0))
        title_label = title_font.render("Samurai Defense", 1, (255,255,255))
        WIN.blit(title_label, (WIDTH/2 - title_label.get_width()/2, 350))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                main()
    pygame.quit()


main_menu()