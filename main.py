# sprite 是py內建類別 可用來表示一個個物件 石頭 飛機等等
import pygame
import random
import os

FPS = 60
WIDTH = 500
HEIGHT = 600

WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
BLACK = (0, 0, 0)

# 遊戲初始化&創建視窗
pygame.init() #模組初始化
pygame.mixer.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT)) # 可放入tuple 設定畫面長寬
pygame.display.set_caption("space adventure")
clock = pygame.time.Clock()

# 載入圖片 需在初始化之後 不然會發生錯誤
background_img = pygame.image.load(os.path.join("img", "background.png")).convert() # 最後轉換至方便pygame讀取格式
player_img = pygame.image.load(os.path.join("img", "player.png")).convert()
player_mine_img = pygame.transform.scale(player_img, (25, 19))
player_mine_img.set_colorkey(BLACK)
pygame.display.set_icon(player_mine_img)
# rock_img = pygame.image.load(os.path.join("img", "rock.png")).convert()
bullet_img = pygame.image.load(os.path.join("img", "bullet.png")).convert()
rock_imgs = []
for i in range(7):
    rock_imgs.append(pygame.image.load(os.path.join("img", f"rock{i}.png")).convert())

expl_anim = {}
expl_anim['lg'] = []
expl_anim['sm'] = []
expl_anim['player'] = []
for i in range(9):
    expl_img = pygame.image.load(os.path.join("img", f"expl{i}.png")).convert()
    expl_img.set_colorkey(BLACK)
    expl_anim['lg'].append(pygame.transform.scale(expl_img, (75, 75)))
    expl_anim['sm'].append(pygame.transform.scale(expl_img, (30, 30)))
    player_expl_img = pygame.image.load(os.path.join("img", f"player_expl{i}.png")).convert()
    player_expl_img.set_colorkey(BLACK)
    expl_anim['player'].append(player_expl_img)
power_imgs = {}
power_imgs['shield'] = pygame.image.load(os.path.join("img", "shield.png")).convert()
power_imgs['gun'] = pygame.image.load(os.path.join("img", "gun.png")).convert()


# 載入音樂
shoot_sound = pygame.mixer.Sound(os.path.join("sound", "shoot.wav"))
gun_sound = pygame.mixer.Sound(os.path.join("sound", "pow1.wav"))
shield_sound = pygame.mixer.Sound(os.path.join("sound", "pow0.wav"))
die_sound = pygame.mixer.Sound(os.path.join("sound", "rumble.ogg"))
expl_sounds = [
    pygame.mixer.Sound(os.path.join("sound", "expl0.wav")),
    pygame.mixer.Sound(os.path.join("sound", "expl1.wav"))
]
pygame.mixer.music.load(os.path.join("sound", "background.ogg"))
pygame.mixer.music.set_volume(0.3)

font_name = os.path.join("font.ttf") # 引入字體
def draw_text(surf, text, size, x, y):
    font = pygame.font.Font(font_name, size) # 創建文字物件
    text_surface = font.render(text, True, WHITE) # 文字 啟用反鋸齒 顏色
    text_rect = text_surface.get_rect()
    text_rect.centerx = x
    text_rect.top = y
    surf.blit(text_surface,  text_rect)

def new_rock():
    r = Rock()
    all_sprites.add(r)
    rocks.add(r)

def draw_health(surf, hp, x, y):
    if hp <= 0:
        hp = 0
    BAR_LENGTH = 100
    BAR_HEIGHT = 10
    fill = (hp/100)*BAR_LENGTH
    outline_rect = pygame.Rect(x, y, BAR_LENGTH, BAR_HEIGHT)
    fill_rect = pygame.Rect(x, y, fill, BAR_HEIGHT)
    pygame.draw.rect(surf, GREEN, fill_rect)
    pygame.draw.rect(surf, WHITE, outline_rect, 2)

def draw_lifes(surf, lives, img, x, y):
    for i in range(lives):
        img_rect = img.get_rect()
        img_rect.x = x +  33*i
        img_rect.y = y
        surf.blit(img, img_rect)
        
def draw_init():
    screen.blit(background_img, (0,0))
    draw_text(screen, 'SPACE ADVENTURE!', 50, WIDTH/2, HEIGHT/4)
    draw_text(screen, 'Use arrow keys to control space ship.', 24, WIDTH/2, HEIGHT/2)
    draw_text(screen, 'Press space key to shoot.', 24, WIDTH/2, HEIGHT*3/5)
    draw_text(screen, 'Press any key to start...', 22, WIDTH/2, HEIGHT*3/4)
    
    pygame.display.update()
    waiting = True
    while waiting:
        clock.tick(FPS)    
        for event in pygame.event.get(): 
            if event.type == pygame.QUIT:
                pygame.quit()
                return True
            elif event.type == pygame.KEYUP:
                waiting = False
                return False

def draw_end():
    screen.blit(background_img, (0,0))
    draw_text(screen, 'You got '+ str(score) + ' points!', 24, WIDTH/2, HEIGHT/2)
    draw_text(screen, 'Press any key to restart...', 22, WIDTH/2, HEIGHT*3/4)
    pygame.display.update()
    waiting = True
    while waiting:
        clock.tick(FPS)    
        for event in pygame.event.get(): 
            if event.type == pygame.QUIT:
                pygame.quit()
            elif event.type == pygame.KEYUP:
                waiting = False

class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(player_img, (50, 38)) # 重新定義圖片
        self.image.set_colorkey(BLACK) # 將什麼顏色透明
        self.rect = self.image.get_rect()
        self.radius = 20
        # pygame.draw.circle(self.image, RED, self.rect.center, self.radius)
        self.rect.centerx = WIDTH/2
        self.rect.bottom = HEIGHT - 10
        self.speedx = 8
        self.health = 100
        self.lives = 3
        self.hidden = False
        self.hide_time = 0
        self.gun = 1
        self.gun_time = 0

    def update(self):
        now = pygame.time.get_ticks()
        if self.gun > 1 and now - self.gun_time > 5000:
            self.gun -= 1
            self.gun_time = now

        if self.hidden and now - self.hide_time > 1000:
            self.hidden = False
            self.rect.centerx = WIDTH/2
            self.rect.bottom = HEIGHT - 10

        key_pressed = pygame.key.get_pressed() # 判斷按鍵 是否 有被按下去
        if key_pressed[pygame.K_RIGHT]:
            self.rect.x += self.speedx
        if key_pressed[pygame.K_LEFT]:
            self.rect.x -= self.speedx
        if key_pressed[pygame.K_UP]:
            self.rect.y -= self.speedx
        if key_pressed[pygame.K_DOWN]:
            self.rect.y += self.speedx

        if self.rect.right < 0:
            self.rect.right = WIDTH
        if self.rect.left > WIDTH:
            self.rect.left = 0
        #if self.rect.right > WIDTH:
        #    self.rect.right = WIDTH
        #if self.rect.left < 0:
        #    self.rect.left = 0
        if self.rect.bottom < 0:
            self.rect.bottom = HEIGHT
        if self.rect.top > HEIGHT:
            self.rect.top = 0

    def shoot(self):
        if not(self.hidden):
            if self.gun == 1:
                bullet = Bullet(self.rect.centerx, self.rect.top)
                all_sprites.add(bullet)
                bullets.add(bullet)
                shoot_sound.play()
            elif self.gun == 2:
                bullet1 = Bullet(self.rect.left, self.rect.centery)
                bullet2 = Bullet(self.rect.right, self.rect.centery)
                all_sprites.add(bullet1)
                all_sprites.add(bullet2)
                bullets.add(bullet1)
                bullets.add(bullet2)
                shoot_sound.play()
            elif self.gun >= 3:
                bullet3 = Bullet(self.rect.centerx, self.rect.centery)
                bullet4 = Bullet(self.rect.left, self.rect.centery)
                bullet5 = Bullet(self.rect.right, self.rect.centery)
                all_sprites.add(bullet3)
                all_sprites.add(bullet4)
                all_sprites.add(bullet5)
                bullets.add(bullet3)
                bullets.add(bullet4)
                bullets.add(bullet5)
                shoot_sound.play()
          
    def hide(self):
        self.hidden = True
        self.hide_time = pygame.time.get_ticks()
        self.rect.center = (WIDTH/2, HEIGHT+700)

    def gun_up(self):
        self.gun += 1
        self.gun_time = pygame.time.get_ticks()

class Rock(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image_ori = random.choice(rock_imgs)
        self.image_ori.set_colorkey(BLACK)
        self.image = self.image_ori.copy()
        self.rect = self.image.get_rect()
        self.radius = int(self.rect.width * 0.85 / 2)
        # pygame.draw.circle(self.image, RED, self.rect.center, self.radius)
        self.rect.x = random.randrange(0, WIDTH - self.rect.width) # 在括號內位置隨機給予一數字
        self.rect.y = random.randrange(-180, -100)
        self.speedy = random.randrange(2, 10)
        self.speedx = random.randrange(-3, 3)
        self.total_degree = 0
        self.rot_degree = random.randrange(-3, 3)

    def rotate(self):
        self.total_degree += self.rot_degree
        self.total_degree = self.total_degree % 360
        self.image = pygame.transform.rotate(self.image_ori, self.total_degree)
        center = self.rect.center
        self.rect = self.image.get_rect()
        self.rect.center = center

    def update(self):
        self.rotate()
        self.rect.y += self.speedy
        self.rect.x += self.speedx
        if self.rect.top > HEIGHT or self.rect.left > WIDTH or self.rect.right < 0:
            self.rect.x = random.randrange(0, WIDTH - self.rect.width)
            self.rect.y = random.randrange(-100, -40)
            self.speedy = random.randrange(2, 10)
            self.speedx = random.randrange(-3, 3)

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y): # xy傳入飛船位置
        pygame.sprite.Sprite.__init__(self)
        self.image = bullet_img
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speedy = -10
        

    def update(self):
        self.rect.y += self.speedy
        if self.rect.bottom < 0:
            self.kill() # 移除有子彈的sprite群組

class Explosion(pygame.sprite.Sprite):
    def __init__(self, center, size):
        pygame.sprite.Sprite.__init__(self)
        self.size = size
        self.image = expl_anim[self.size][0]
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.frame = 0
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 40
        

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame += 1
            if self.frame == len(expl_anim[self.size]):
                self.kill()
            else:
                self.image = expl_anim[self.size][self.frame]
                center = self.rect.center
                self.rect = self.image.get_rect()
                self.rect.center = center

class Power(pygame.sprite.Sprite):
    def __init__(self, center): 
        pygame.sprite.Sprite.__init__(self)
        self.type = random.choice(['shield', 'gun'])
        self.image = power_imgs[self.type]
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.speedy = 3
        

    def update(self):
        self.rect.y += self.speedy
        if self.rect.top > HEIGHT:
            self.kill()


pygame.mixer.music.play(-1)

# 遊戲迴圈 三步驟
show_init = True
running = True
show_end = False
while running:
    if show_init:
        close = draw_init()
        if close:
            break
        show_init = False
        all_sprites = pygame.sprite.Group()      # 加入後可去 顯示 畫出來
        rocks = pygame.sprite.Group()
        bullets = pygame.sprite.Group()
        powers = pygame.sprite.Group()  
        player = Player()
        all_sprites.add(player )
        rock = Rock()
        all_sprites.add(rock)
        for i in range(8):
            new_rock()
        score = 0

    clock.tick(FPS) # 表示一秒鐘內最多執行60次 相當於FPS
    # 取得輸入
    for event in pygame.event.get(): # 回傳所有事件 回傳一個列表
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                player.shoot()

    # 更新遊戲
    all_sprites.update() # 更新新物件 畫面
    # 判斷石頭 子彈 相撞
    hits = pygame.sprite.groupcollide(rocks, bullets, True, True) # 判斷是否碰撞並消除 該函式回傳 字典
    for hit in hits:
        random.choice(expl_sounds).play()
        score += hit.radius
        expl = Explosion(hit.rect.center, 'lg')
        all_sprites.add(expl)
        if random.random() > 0.95:
            pow = Power(hit.rect.center)
            all_sprites.add(pow)
            powers.add(pow)
        new_rock()

    # 判斷飛船 石頭 相撞
    hits = pygame.sprite.spritecollide(player, rocks, True, pygame.sprite.collide_circle) # 判斷是否碰撞 該函釋回傳 列表
    for hit in hits:
        new_rock()
        player.health -= hit.radius 
        expl = Explosion(hit.rect.center, 'sm')
        all_sprites.add(expl)
        if player.health <= 0:
            death_expl = Explosion(player.rect.center, 'player')
            all_sprites.add(death_expl)
            die_sound.play()
            player.lives -= 1
            player.health = 100
            player.hide()
            # running = False
    
        # 判斷寶物 飛船 相撞
    hits = pygame.sprite.spritecollide(player, powers, True)
    for hit in hits:
        if hit.type == 'shield':
            player.health += 20
            if player.health > 100:
                player.health = 100
            shield_sound.play()
        elif hit.type == 'gun':
            player.gun_up()
            gun_sound.play()

    if player.lives == 0  and not(death_expl.alive()):
        show_end = True
        # show_init = True
    
    if show_end:
        draw_end()
        draw_init()
        show_init = True
        show_end = False

    # 畫面顯示
    screen.fill(BLACK) # 將畫面填滿顏色 放入tuple(R,G,B)
    screen.blit(background_img, (0,0))
    all_sprites.draw(screen) # 將all_sprite群組內所有東西畫到screen
    draw_text(screen, str(score), 20, WIDTH/2, 10)
    draw_health(screen, player.health, 10, 15)
    draw_lifes(screen, player.lives, player_mine_img, WIDTH - 100, 15)
    pygame.display.update()

pygame.quit()    
