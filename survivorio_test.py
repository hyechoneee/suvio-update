import pygame
import random
import math

# 초기화 및 화면 설정
pygame.init()
screen_width = 800
screen_height = 600
bottom_panel_height = 100  # 하단 패널 높이
screen = pygame.display.set_mode((screen_width, screen_height + bottom_panel_height))
pygame.display.set_caption("Survivor.io Clone - Monster Invasion")

# 색상 정의
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# 게임 설정 및 폰트
font = pygame.font.SysFont(None, 30)
monster_hp_font = pygame.font.SysFont(None, 20)  # 몬스터 체력 표기용 폰트

class Player:
    def __init__(self, x, y, size, color, hp, speed):
        self.x = x
        self.y = y
        self.size = size
        self.color = color
        self.hp = hp
        self.max_hp = hp
        self.speed = speed
        self.experience = 0  # 경험치 초기화
        self.experience_to_level_up = 10  # 레벨업에 필요한 초기 경험치 토큰 수
        self.bullet_count = 1
        self.hp_bar_length = self.size  # 체력 바 길이
        self.last_score_increase = 0

    def draw_hp_bar(self, screen, camera_y):
        bar_width = int(self.hp_bar_length * (self.hp / self.max_hp))
        pygame.draw.rect(screen, RED, (self.x, self.y + self.size + 5 - camera_y, bar_width, 5))

    def increase_bullet_count(self):
        self.bullet_count += 1

    def level_up(self):
        self.experience -= self.experience_to_level_up
        self.experience_to_level_up = int(self.experience_to_level_up * 1.1)  # 레벨업에 필요한 경험치 토큰 수 증가
        self.increase_bullet_count()

class Monster:
    def __init__(self, x, y, size, color, hp):
        self.x = x
        self.y = y
        self.size = size
        self.color = color
        self.hp = hp
        self.max_hp = hp
        self.dx = 0
        self.dy = 0
        self.hp_bar_length = self.size  # 체력 바 길이

    def draw_hp_bar(self, screen, camera_y):
        bar_width = int(self.hp_bar_length * (self.hp / self.max_hp))
        pygame.draw.rect(screen, RED, (self.x, self.y + self.size + 5 - camera_y, bar_width, 5))

class Orb:
    def __init__(self, player, radius, speed):
        self.player = player
        self.radius = radius
        self.speed = speed
        self.angle = random.uniform(0, 2 * math.pi)
        self.x = player.x + 25 + math.cos(self.angle) * radius
        self.y = player.y + 25 + math.sin(self.angle) * radius

    def update(self):
        self.angle += self.speed
        self.x = self.player.x + 25 + math.cos(self.angle) * self.radius
        self.y = self.player.y + 25 + math.sin(self.angle) * self.radius

    def draw(self, screen, camera_y):
        pygame.draw.circle(screen, BLUE, (int(self.x), int(self.y - camera_y)), 10)

class Game:
    def __init__(self):
        self.player = Player(screen_width // 2, screen_height // 2, 50, BLUE, 300, 5)
        self.monsters = []
        self.spawn_rate = 1  # 초당 몬스터 소환 속도 (1초에 1마리 소환)
        self.max_monsters = 50  # 최대 몬스터 수
        self.monster_spawn_timer = 0
        self.monster_size = 30
        self.monster_hp = 2
        self.bullets = []
        self.bullet_radius = 10
        self.bullet_damage = 1
        self.bullet_speed = 15
        self.bullet_timer = 0  # 총알 발사 타이머 초기화
        self.camera_y = self.player.y  # 카메라 y 위치
        self.orbs = []
        self.orb_timer = 0
        self.start_time = pygame.time.get_ticks()  # 게임 시작 시간
        self.skill_timer = pygame.time.get_ticks()  # 추가된 기능의 타이머

    def restart_game(self):
        self.player.hp = 100
        self.player.experience = 0  # 경험치 초기화
        self.player.bullet_count = 1
        self.monsters.clear()
        self.bullets.clear()
        self.monster_spawn_timer = 0
        self.camera_y = self.player.y  # 카메라 y 위치 초기화
        self.orbs.clear()
        self.orb_timer = 0
        self.start_time = pygame.time.get_ticks()  # 게임 시작 시간 초기화
        self.skill_timer = pygame.time.get_ticks()  # 추가된 기능의 타이머 초기화

    def spawn_monster(self):
        side = random.choice(["left", "right", "top", "bottom"])
        if side == "left":
            new_monster = Monster(
                random.randint(0, self.player.x - self.player.size),
                random.randint(self.camera_y, self.camera_y + screen_height),
                self.monster_size,
                RED,
                self.monster_hp
            )
            new_monster.dx = random.uniform(0.5, 1.5) * self.player.speed / 4  # 속도 감소
            new_monster.dy = random.uniform(-0.5, 0.5) * self.player.speed / 4  # 속도 감소
        elif side == "right":
            new_monster = Monster(
                random.randint(self.player.x + self.player.size, screen_width),
                random.randint(self.camera_y, self.camera_y + screen_height),
                self.monster_size,
                RED,
                self.monster_hp
            )
            new_monster.dx = random.uniform(-1.5, -0.5) * self.player.speed / 4  # 속도 감소
            new_monster.dy = random.uniform(-0.5, 0.5) * self.player.speed / 4  # 속도 감소
        elif side == "top":
            new_monster = Monster(
                random.randint(0, screen_width),
                random.randint(self.camera_y, self.player.y - self.player.size),
                self.monster_size,
                RED,
                self.monster_hp
            )
            new_monster.dx = random.uniform(-0.5, 0.5) * self.player.speed / 4  # 속도 감소
            new_monster.dy = random.uniform(0.5, 1.5) * self.player.speed / 4  # 속도 감소
        elif side == "bottom":
            new_monster = Monster(
                random.randint(0, screen_width),
                random.randint(self.player.y + self.player.size, self.camera_y + screen_height),
                self.monster_size,
                RED,
                self.monster_hp
            )
            new_monster.dx = random.uniform(-0.5, 0.5) * self.player.speed / 4  # 속도 감소
            new_monster.dy = random.uniform(-1.5, -0.5) * self.player.speed / 4  # 속도 감소

        self.monsters.append(new_monster)
        self.monster_spawn_timer = 0

    def fire_bullet(self, x, y, target_x, target_y):
        dx = target_x - x
        dy = target_y - y
        dist = math.sqrt(dx**2 + dy**2)
        if dist == 0:
            dist = 1
        dx = dx / dist
        dy = dy / dist

        # 여러 발의 총알 발사
        bullet_offset_x = random.uniform(-15, 15)
        bullet_offset_y = random.uniform(-15, 15)

        start_x = x + bullet_offset_x
        start_y = y + bullet_offset_y
        

        self.bullets.append({"x": start_x, "y": start_y, "dx": dx * self.bullet_speed, "dy": dy * self.bullet_speed})
        # pygame.time.wait(self.player.bullet_delay)  # 발사 딜레이 적용

    def move_towards_player(self, monster):
        dx = self.player.x - monster.x
        dy = self.player.y - monster.y
        dist = math.sqrt(dx**2 + dy**2)
        if dist != 0:
            dx = dx / dist
            dy = dy / dist
        monster.dx = dx * self.player.speed / 4  # 속도 감소
        monster.dy = dy * self.player.speed / 4  # 속도 감소

    def update(self):
        current_time = pygame.time.get_ticks()
        elapsed_time = (current_time - self.start_time) / 1000  # 경과 시간(초)
        self.monster_spawn_timer += elapsed_time
        self.bullet_timer += elapsed_time  # 총알 발사 타이머 업데이트
        self.start_time = current_time

        # 플레이어 위치 업데이트
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.player.x -= self.player.speed
        if keys[pygame.K_RIGHT]:
            self.player.x += self.player.speed
        if keys[pygame.K_UP]:
            self.player.y -= self.player.speed
        if keys[pygame.K_DOWN]:
            self.player.y += self.player.speed

        # 플레이어의 이동 경계를 화면 내부로 제한
        self.player.x = max(0, min(self.player.x, screen_width - self.player.size))
        self.player.y = max(0, min(self.player.y, screen_height - self.player.size))

        # 카메라 y 위치 업데이트
        self.camera_y = self.player.y - screen_height // 2

        # 몬스터 스폰
        if len(self.monsters) < self.max_monsters and self.monster_spawn_timer >= self.spawn_rate:
            self.spawn_monster()

        # 몬스터 이동
        for monster in self.monsters:
            self.move_towards_player(monster)
            monster.x += monster.dx
            monster.y += monster.dy

        # 총알 이동 및 충돌 처리
        for bullet in self.bullets[:]:
            bullet["x"] += bullet["dx"]
            bullet["y"] += bullet["dy"]

            if bullet["x"] < 0 or bullet["x"] > screen_width or bullet["y"] < 0 or bullet["y"] > screen_height:
                self.bullets.remove(bullet)
                continue

            for monster in self.monsters[:]:
                if math.hypot(monster.x - bullet["x"], monster.y - bullet["y"]) < self.bullet_radius + monster.size / 2:
                    monster.hp -= self.bullet_damage
                    if monster.hp <= 0:
                        self.player.experience += 1
                        self.monsters.remove(monster)
                    if bullet in self.bullets:
                        self.bullets.remove(bullet)
                    break

        # 플레이어 레벨업 처리
        if self.player.experience >= self.player.experience_to_level_up:
            self.player.level_up()

        # 몬스터와 플레이어의 충돌 처리
        for monster in self.monsters:
            if math.hypot(monster.x - self.player.x, monster.y - self.player.y) < self.player.size:
                self.player.hp -= 1
                if self.player.hp <= 0:
                    print("Game Over!")
                    self.restart_game()

        # 추가된 기능: 5초마다 주변 몬스터들에게 플레이어의 레벨만큼의 데미지를 줌
        if pygame.time.get_ticks() - self.skill_timer >= 5000:
            self.skill_timer = pygame.time.get_ticks()  # 타이머 초기화
            closest_monsters = sorted(self.monsters, key=lambda m: math.hypot(m.x - self.player.x, m.y - self.player.y))[:self.player.bullet_count]
            for monster in closest_monsters:
                monster.hp -= self.player.bullet_count
                if monster.hp <= 0:
                    self.player.experience += 1
                    self.monsters.remove(monster)

        # 오브 업데이트
        for orb in self.orbs:
            orb.update()

    def draw(self, screen):
        screen.fill(WHITE)
        self.player.draw_hp_bar(screen, self.camera_y)  # 플레이어 체력 바 그리기
        for monster in self.monsters:
            pygame.draw.circle(screen, monster.color, (int(monster.x), int(monster.y - self.camera_y)), monster.size)
            monster.draw_hp_bar(screen, self.camera_y)  # 몬스터 체력 바 그리기
        for bullet in self.bullets:
            pygame.draw.circle(screen, BLACK, (int(bullet["x"]), int(bullet["y"] - self.camera_y)), self.bullet_radius)
        for orb in self.orbs:
            orb.draw(screen, self.camera_y)

        # 하단 패널에 정보 표시
        pygame.draw.rect(screen, BLACK, (0, screen_height, screen_width, bottom_panel_height))
        hp_text = font.render(f"HP: {self.player.hp}", True, WHITE)
        screen.blit(hp_text, (10, screen_height + 10))
        experience_text = font.render(f"EXP: {self.player.experience}/{self.player.experience_to_level_up}", True, WHITE)
        screen.blit(experience_text, (10, screen_height + 40))
        bullet_count_text = font.render(f"Bullets: {self.player.bullet_count}", True, WHITE)
        screen.blit(bullet_count_text, (10, screen_height + 70))

def main():
    game = Game()
    clock = pygame.time.Clock()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                for _ in range(game.player.bullet_count):
                    game.fire_bullet(game.player.x + game.player.size // 2, game.player.y + game.player.size // 2, mouse_x, mouse_y)

        game.update()
        game.draw(screen)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
