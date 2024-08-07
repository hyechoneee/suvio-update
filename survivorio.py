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
GREEN = (0, 255, 0)

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

class Boss:
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

class Effect:
    def __init__(self, player):
        self.player = player
        self.x = self.player.x + 25
        self.y = self.player.y + 25
        self.radius = 0
        self.max_radius = 500
        self.color = (255, 255, 0)  # 노란색

    def update(self):
        self.radius += 25
        self.x = self.player.x + 25
        self.y = self.player.y + 25
        if self.radius > self.max_radius:
            self.radius = self.max_radius

    def draw(self, screen, camera_y):
        if self.radius < self.max_radius:
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y - camera_y)), self.radius, 3)

class Game:
    def __init__(self):
        self.player = Player(screen_width // 2, screen_height // 2, 50, BLUE, 300, 5)
        self.monsters = []
        self.boss = []
        self.spawn_rate = 1  # 초당 몬스터 소환 속도 (1초에 1마리 소환)
        self.max_monsters = 50  # 최대 몬스터 수
        self.monster_spawn_timer = 0
        self.monster_size = 30
        self.boss_size = 90
        self.monster_hp = 2
        self.bullets = []
        self.bullet_radius = 10
        self.bullet_damage = 1
        self.bullet_speed = 15
        self.bullet_timer = 0  # 총알 발사 타이머 초기화
        self.camera_y = self.player.y  # 카메라 y 위치
        self.orbs = []
        self.effects = []
        self.orb_timer = 0
        self.start_time = pygame.time.get_ticks()  # 게임 시작 시간
        self.skill_timer = pygame.time.get_ticks()  # 추가된 기능의 타이머
        self.boss_timer = 0
        self.boss_flag = False
        self.monster_exp = 1
        self.killed_monster = 0
        
    def restart_game(self):
        self.player.hp = 100
        self.player.experience = 0  # 경험치 초기화
        self.player.bullet_count = 1
        self.boss.clear()
        self.monsters.clear()
        self.bullets.clear()
        self.monster_spawn_timer = 0
        self.camera_y = self.player.y  # 카메라 y 위치 초기화
        self.orbs.clear()
        self.orb_timer = 0
        self.start_time = pygame.time.get_ticks()  # 게임 시작 시간 초기화

    def shock_wave_update_effects(self):
        for effect in self.effects:
            effect.update()
        self.effects = [effect for effect in self.effects if effect.radius < effect.max_radius]

    def shock_wave_draw_effects(self, screen, camera_y):
        for effect in self.effects:
            effect.draw(screen, camera_y)

    def spawn_monster(self):
        side = random.choice(["left", "right", "top", "bottom"])
        max_attempts = 100  # 최대 시도 횟수
        attempts = 0
        spawn_valid = False
        while not spawn_valid and attempts < max_attempts:
            if side == "left":
                x = random.randint(0, self.player.x - self.player.size)
                y = random.randint(self.camera_y, self.camera_y + screen_height)
            elif side == "right":
                x = random.randint(self.player.x + self.player.size, screen_width)
                y = random.randint(self.camera_y, self.camera_y + screen_height)
            elif side == "top":
                x = random.randint(0, screen_width)
                y = random.randint(self.camera_y, self.player.y - self.player.size)
            elif side == "bottom":
                x = random.randint(0, screen_width)
                y = random.randint(self.player.y + self.player.size, self.camera_y + screen_height)
            
            # Check if the spawn location is at least 300 pixels away from the player
            if math.sqrt((x - self.player.x) ** 2 + (y - self.player.y) ** 2) >= 300:
                spawn_valid = True
            attempts += 1
        
        # If a valid position is not found within the maximum attempts, place the monster at the calculated position anyway
        if not spawn_valid:
            if side == "left":
                x = random.randint(0, screen_width // 4)
                y = random.randint(self.camera_y, self.camera_y + screen_height)
            elif side == "right":
                x = random.randint(3 * screen_width // 4, screen_width)
                y = random.randint(self.camera_y, self.camera_y + screen_height)
            elif side == "top":
                x = random.randint(0, screen_width)
                y = random.randint(self.camera_y, self.camera_y + screen_height // 4)
            elif side == "bottom":
                x = random.randint(0, screen_width)
                y = random.randint(3 * screen_height // 4, self.camera_y + screen_height)
        
        new_monster = Monster(
            x,
            y,
            self.monster_size,
            RED,
            self.monster_hp
        )
        
        if side == "left":
            new_monster.dx = random.uniform(0.5, 1.5) * self.player.speed / 4  # 속도 감소
            new_monster.dy = random.uniform(-0.5, 0.5) * self.player.speed / 4  # 속도 감소
        elif side == "right":
            new_monster.dx = random.uniform(-1.5, -0.5) * self.player.speed / 4  # 속도 감소
            new_monster.dy = random.uniform(-0.5, 0.5) * self.player.speed / 4  # 속도 감소
        elif side == "top":
            new_monster.dx = random.uniform(-0.5, 0.5) * self.player.speed / 4  # 속도 감소
            new_monster.dy = random.uniform(0.5, 1.5) * self.player.speed / 4  # 속도 감소
        elif side == "bottom":
            new_monster.dx = random.uniform(-0.5, 0.5) * self.player.speed / 4  # 속도 감소
            new_monster.dy = random.uniform(-1.5, -0.5) * self.player.speed / 4  # 속도 감소

        self.monsters.append(new_monster)
        self.monster_spawn_timer = 0


    def spawn_boss(self):
        if self.boss_flag != False:
            new_boss = Monster(
                random.randint(0, self.player.x - self.player.size),
                random.randint(self.camera_y, self.camera_y + screen_height),
                self.monster_size * 3,
                RED,
                self.monster_hp*500 
            )
            new_boss.dx = random.uniform(0.5, 1.5) * self.player.speed / 3  # 속도 감소
            new_boss.dy = random.uniform(-0.5, 0.5) * self.player.speed / 3  # 속도 감소
            

            self.boss.append(new_boss)
            self.boss_timer = 0
        self.boss_flag = True

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

    def closest_monsters(self, x, y):
        monsters_with_distance = [(monster, math.sqrt((monster.x - x) ** 2 + (monster.y - y) ** 2)) for monster in self.monsters]
        monsters_with_distance.sort(key=lambda item: item[1])  # 거리 기준으로 정렬
        return [monster for monster, _ in monsters_with_distance]
    
    def closest_boss(self, x, y):
        closest = None
        min_dist = float('inf')
        for boss in self.boss:
            dist = math.sqrt((boss.x - x)**2 + (boss.y - y)**2)
            if dist < min_dist:
                closest = boss
                min_dist = dist
        return closest
    

    def run(self):
        clock = pygame.time.Clock()
        running = True
        last_bullet_time = pygame.time.get_ticks()  # 마지막 총알 발사 시간
        time_since_last_increase = 0  # 몬스터 속성 증가를 위한 시간 초기화

        while running:
            try:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False

                # 키 입력 처리
                keys = pygame.key.get_pressed()
                if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                    self.player.x -= self.player.speed
                if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                    self.player.x += self.player.speed
                if keys[pygame.K_UP] or keys[pygame.K_w]:
                    self.player.y -= self.player.speed
                if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                    self.player.y += self.player.speed

                # 플레이어 위치 경계 처리
                if self.player.x < 25:
                    self.player.x = 25
                elif self.player.x > screen_width - 25 - self.player.size:
                    self.player.x = screen_width - 25 - self.player.size

                # 카메라 위치 업데이트
                self.camera_y = self.player.y - screen_height // 2

                # 경과 시간 확인 및 몬스터 속성 증가
                current_time = pygame.time.get_ticks()
                time_since_start = (current_time - self.start_time) // 1000  # 게임 시작 후 경과 시간 (초)
                if time_since_start - time_since_last_increase >= 10:  # 10초마다 몬스터 속성 증가
                    self.spawn_rate += 1  # 몬스터 생성 속도 증가
                    self.monster_hp += 1  # 몬스터 HP 증가
                    self.max_monsters += 30  # 최대 몬스터 수 증가
                    self.monster_exp += 0.166666
                    time_since_last_increase = time_since_start

                # 몬스터 소환 타이머 업데이트
                self.monster_spawn_timer += clock.get_time() / 1000.0
                if self.monster_spawn_timer >= 1 / self.spawn_rate and len(self.monsters) < self.max_monsters:
                    self.spawn_monster()

                # 몬스터 이동
                for monster in self.monsters:
                    self.move_towards_player(monster)
                    monster.x += monster.dx
                    monster.y += monster.dy
                    if pygame.Rect(monster.x, monster.y, monster.size, monster.size).colliderect(pygame.Rect(self.player.x, self.player.y, self.player.size, self.player.size)):
                        self.player.hp -= 1
                        if self.player.hp <= 0:
                            running = False

                # 보스 소환 타이머 업데이트
                self.boss_timer += clock.get_time() / 60000.0
                if self.boss_timer >= 1:
                    self.spawn_boss()

                # 보스 이동
                for boss in self.boss:
                    self.move_towards_player(boss)
                    boss.x += boss.dx
                    boss.y += boss.dy
                    if pygame.Rect(boss.x, boss.y, boss.size, boss.size).colliderect(pygame.Rect(self.player.x, self.player.y, self.player.size, self.player.size)):
                        self.player.hp -= 1
                        if self.player.hp <= 0:
                            running = False

                # 총알 발사
                current_time = pygame.time.get_ticks()
                # if self.player.bullet_count < 40:
                time_set = self.player.bullet_count * 10
                # else:
                #     time_set = 19 * 50

                if (current_time - last_bullet_time) >= (1000 - time_set):  # 1초 간격으로 총알 발사
                    if self.monsters or self.boss:
                        # 모든 가까운 몬스터를 찾고 거리 기준으로 정렬
                        closest_monsters = self.closest_monsters(self.player.x + self.player.size // 2, self.player.y + self.player.size // 2)
                        closest_boss = self.closest_boss(self.player.x + self.player.size // 2, self.player.y + self.player.size // 2)

                        # 보스를 포함한 모든 적들을 대상으로 설정
                        if closest_boss:
                            closest_monsters.append(closest_boss)
                            closest_monsters.sort(key=lambda target: math.sqrt((target.x - self.player.x) ** 2 + (target.y - self.player.y) ** 2))

                        # 발사할 총알의 수를 계산
                        num_targets = min(len(closest_monsters), 1 + int(self.player.bullet_count // 20))

                        for i in range(num_targets):
                            target = closest_monsters[i]
                            target_size = self.monster_size if target in self.monsters else self.boss_size

                            # 총알 발사
                            for i in range(self.player.bullet_count):
                                self.fire_bullet(self.player.x + self.player.size // 2, self.player.y + self.player.size // 2, target.x + target_size // 2, target.y + target_size // 2)

                        last_bullet_time = current_time
                

                # 총알 이동 및 충돌 처리
                for bullet in self.bullets[:]:
                    bullet["x"] += bullet["dx"]
                    bullet["y"] += bullet["dy"]
                    bullet_rect = pygame.Rect(bullet["x"] - self.bullet_radius, bullet["y"] - self.bullet_radius, self.bullet_radius * 2, self.bullet_radius * 2)
                    for monster in self.monsters[:]:
                        monster_rect = pygame.Rect(monster.x, monster.y, self.monster_size, self.monster_size)
                        if bullet_rect.colliderect(monster_rect):
                            monster.hp -= self.bullet_damage
                            if monster.hp <= 0:
                                self.monsters.remove(monster)
                                self.killed_monster += 1
                                
                                self.player.experience += self.monster_exp  # 경험치 증가
                                if self.player.hp <= 300:
                                    self.player.hp += 0.5
                                if self.player.experience >= self.player.experience_to_level_up:
                                    self.player.level_up()
                            try:
                                self.bullets.remove(bullet)
                            except:
                                pass
                            break

                    for boss in self.boss[:]:
                        boss_rect = pygame.Rect(boss.x, boss.y, self.monster_size*3, self.monster_size*3)
                        if bullet_rect.colliderect(boss_rect):
                            boss.hp -= self.bullet_damage
                            if boss.hp <= 0:
                                self.boss.remove(boss)
                                self.player.experience += self.player.bullet_count * 50  # 경험치 증가
                                self.player.hp = 300
                                if self.player.experience >= self.player.experience_to_level_up:
                                    self.player.level_up()
                            try:
                                self.bullets.remove(bullet)
                            except:
                                pass
                    else:
                        if bullet["x"] < 0 or bullet["x"] > screen_width or bullet["y"] < self.camera_y or bullet["y"] > self.camera_y + screen_height:
                            try:
                                self.bullets.remove(bullet)
                            except:
                                pass
                
                

                # 추가된 기능: 5초마다 주변 몬스터들에게 플레이어의 레벨만큼의 데미지를 줌
                if pygame.time.get_ticks() - self.skill_timer >= 5000:
                    self.skill_timer = pygame.time.get_ticks()  # 타이머 초기화
                    closest_monsters = sorted(self.monsters, key=lambda m: math.hypot(m.x - self.player.x, m.y - self.player.y))[:self.player.bullet_count]
                    
                    # 이펙트 생성
                    self.effects.append(Effect(self.player))
                    # 게임 루프 내부
                    
                    for monster in closest_monsters:
                        monster.hp -= self.player.bullet_count
                        if monster.hp <= 0:
                            self.player.experience += 1
                            self.player.hp += 0.5
                            self.monsters.remove(monster)
                            self.killed_monster += 1
                            if self.player.experience >= self.player.experience_to_level_up:
                                self.player.level_up()
                game.shock_wave_update_effects()

                # 구체 생성 및 제거 타이머 업데이트
                self.orb_timer += clock.get_time() / 1000.0
                if self.orb_timer >= 3:
                    if self.orbs:
                        self.orbs.clear()
                    else:
                        for _ in range(self.player.bullet_count):
                            self.orbs.append(Orb(self.player, 100, 0.05))
                    self.orb_timer = 0

                # 구체 이동 및 충돌 처리
                for orb in self.orbs:
                    orb.update()
                    orb_rect = pygame.Rect(orb.x - 10, orb.y - 10, 20, 20)
                    for monster in self.monsters[:]:
                        monster_rect = pygame.Rect(monster.x, monster.y, self.monster_size, self.monster_size)
                        if orb_rect.colliderect(monster_rect):
                            monster.hp -= 1
                            if monster.hp <= 0:
                                self.monsters.remove(monster)
                                self.killed_monster += 1
                                
                                self.player.experience += 1  
                                self.player.hp += 0.5
                                if self.player.experience >= self.player.experience_to_level_up:
                                    self.player.level_up()

                    for boss in self.boss[:]:
                        boss_rect = pygame.Rect(boss.x, boss.y, self.boss_size, self.boss_size)
                        if orb_rect.colliderect(boss_rect):
                            boss.hp -= 1
                            if boss.hp <= 0:
                                self.boss.remove(boss)
                                self.player.experience += 500  # 경험치 증가
                                self.player.hp = 300
                                if self.player.experience >= self.player.experience_to_level_up:
                                    self.player.level_up()

                # 화면 그리기
                screen.fill(WHITE)

                # 몬스터 및 플레이어 그리기
                self.player.draw_hp_bar(screen, self.camera_y)
                for monster in self.monsters:
                    monster.draw_hp_bar(screen, self.camera_y)
                    pygame.draw.circle(screen, monster.color, (int(monster.x + self.monster_size / 2), int(monster.y + self.monster_size / 2 - self.camera_y)), self.monster_size // 2)

                for boss in self.boss:
                    boss.draw_hp_bar(screen, self.camera_y)
                    pygame.draw.circle(screen, boss.color, (int(boss.x + self.monster_size*3 / 2), int(boss.y + self.monster_size*3 / 2 - self.camera_y)), self.monster_size*3 // 2)

                # 플레이어 그리기
                pygame.draw.rect(screen, self.player.color, (self.player.x, self.player.y - self.camera_y, self.player.size, self.player.size))

                # 구체 그리기
                for orb in self.orbs:
                    orb.draw(screen, self.camera_y)

                
                # ... other update functions ...
                game.shock_wave_draw_effects(screen,self.camera_y)

                # 하단 패널 그리기
                pygame.draw.rect(screen, BLACK, (0, screen_height, screen_width, bottom_panel_height))
                # 현재 몬스터 수, 경험치 토큰 표시
                monster_count_text = font.render(f"  Now Monsters: {len(self.monsters)}", True, BLUE)
                screen.blit(monster_count_text, (10, screen_height + bottom_panel_height // 3 - monster_count_text.get_height() // 3))
                monster_total_text = font.render(f"Killed Monsters: {int(self.killed_monster)}", True, RED)
                screen.blit(monster_total_text, (10, screen_height + bottom_panel_height // 1.5 - monster_total_text.get_height() // 1.5))
                player_score_text = font.render(f"Experience Tokens: {int(self.player.experience)}", True, GREEN)
                screen.blit(player_score_text, (screen_width // 2 - player_score_text.get_width() // 2, screen_height + bottom_panel_height // 2 - player_score_text.get_height() // 2))
                level_text = font.render(f"Level: {self.player.bullet_count}", True, GREEN)
                screen.blit(level_text, (screen_width - level_text.get_width() - 10, screen_height + bottom_panel_height // 2 - level_text.get_height() // 2))


                # 총알 그리기
                for bullet in self.bullets:
                    pygame.draw.circle(screen, BLACK, (int(bullet["x"]), int(bullet["y"] - self.camera_y)), self.bullet_radius)

                # 화면 업데이트
                pygame.display.flip()

                # FPS 설정
                clock.tick(60)
            except:
                pass

# 게임 실행
if __name__ == "__main__":
    game = Game()
    game.run()
    print("- - - GAME OVER - - -")
