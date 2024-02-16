import os 
import random
import math
import pygame
from os import listdir
from os.path import isfile,join
pygame.init()

pygame.display.set_caption("Platformer")

WIDTH, HEIGHT = 1000,650
FPS = 50
PLAYER_VEL = 5

window = pygame.display.set_mode((WIDTH, HEIGHT))

def flip(sprites):
    return [pygame.transform.flip(sprite, True, False) for sprite in sprites]

def load_sprite_sheets(dir1,dir2, width, height, direction=False):#images flipped if direction is true
    path = join("assets", dir1,dir2)
    images = [f for f in listdir(path) if isfile(join(path,f))]

    all_sprites = {}

    for image in images:
        sprite_sheet = pygame.image.load(join(path,image)).convert_alpha()
    
        sprites = []
        for i in range(sprite_sheet.get_width()//width):
            surface = pygame.Surface((width,height),pygame.SRCALPHA, 32)
            rect = pygame.Rect(i*width, 0, width,height)
            surface.blit(sprite_sheet,(0,0),rect)
            sprites.append(pygame.transform.scale2x(surface))


        if direction: 
            all_sprites[image.replace(".png","") + "_right"] = sprites
            all_sprites[image.replace(".png","") + "_left"] = flip(sprites)
        else:
            all_sprites[image.replace(".png","")] = sprites
        
    return all_sprites

def get_block(size):
    path = join("assets", "Terrain", "Terrain.png")
    image = pygame.image.load(path).convert_alpha()
    surface = pygame.Surface((size,size), pygame.SRCALPHA, 32)
    rect = pygame.Rect(96,0,size,size)
    surface.blit(image,(0,0), rect)
    return pygame.transform.scale2x(surface)

class Player(pygame.sprite.Sprite):
    COLOR = (255,0,0)
    GRAVITY = 1
    SPRITES = load_sprite_sheets("MainCharacters","MaskDude", 32, 32, True)
    ANIMATION_DELAY = 3

    def __init__(self, x, y, width, height):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.x_vel = 0
        self.y_vel = 0
        self.mask = None
        self.direction = "right"
        self.animation_count = 0
        self.fall_count = 0
        self.jump_count = 0
        self.hit = False
        self.hit_count = 0

    def jump(self):
        self.y_vel = -self.GRAVITY*8
        self.animation_count = 0
        self.jump_count+=1
        if self.jump_count == 1:
            self.fall_count = 0

    def move(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy

    def make_hit(self):
        self.hit = True
        self.hit_count = 0

    def move_left(self,vel):
        self.x_vel = -vel
        if self.direction != "left":
            self.direction = "left"
            self.animation_count = 0

    def move_right(self,vel):
        self.x_vel = vel
        if self.direction != "right":
            self.direction = "right"
            self.animation_count = 0

    def loop(self,fps):
        self.y_vel += min(1, (self.fall_count/fps)*self.GRAVITY)
        self.move(self.x_vel, self.y_vel)

        if self.hit:
            self.hit_count +=1
        if self.hit_count > fps*2:
            self.hit = False
            self.hit_count = 0

        self.fall_count += 1
        self.update_sprite()

    def landed(self):
        self.fall_count = 0
        self.y_vel = 0
        self.jump_count = 0

    def hit_head(self):
        self.count = 0
        self.y_vel *= -1

    def update_sprite(self):
        sprite_sheet = "idle"
        if self.hit:
            sprite_sheet = "hit"
        if self.y_vel < 0:
            if self.jump_count == 1:
                sprite_sheet = "jump"
            elif self.jump_count == 2:
                sprite_sheet = "double_jump"
        elif self.y_vel > self.GRAVITY*2:
                sprite_sheet = "fall"
        elif self.x_vel != 0:
                sprite_sheet = "run"
        
        sprite_sheet_name = sprite_sheet + "_" +  self.direction
        sprites = self.SPRITES[sprite_sheet_name]
        sprite_index = (self.animation_count//self.ANIMATION_DELAY)%len(sprites)
        self.sprite = sprites[sprite_index]
        self.animation_count += 1
        self.update()

    def update(self):
        self.rect = self.sprite.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.sprite)


    def draw(self, win, offset_x):
        win.blit(self.sprite, (self.rect.x-offset_x,self.rect.y))

class Object(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, name = None):
        super().__init__()
        self.rect = pygame.Rect(x,y,width,height)
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.width = width
        self.height = height
        self.name = name
 
    def draw(self, win, offset_x):
        win.blit(self.image,(self.rect.x-offset_x,self.rect.y))

class Block(Object):
    def __init__(self, x, y, size):
        super().__init__(x,y,size,size)
        block = get_block(size)
        self.image.blit(block,(0,0))
        self.mask = pygame.mask.from_surface(self.image)

class Fire(Object):
    ANIMATION_DELAY = 3

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "fire")
        self.fire = load_sprite_sheets("Traps", "Fire", width, height)
        self.image = self.fire["off"][0]
        self.mask = pygame.mask.from_surface(self.image)
        self.animation_count = 0
        self.animation_name = "off"

    def on(self):
        self.animation_name = "on"

    def off(self):
        self.animation_name = "off"

    def loop(self):
        sprites = self.fire[self.animation_name]
        sprite_index = (self.animation_count//
                        self.ANIMATION_DELAY)%len(sprites)
        self.image = sprites[sprite_index]
        self.animation_count += 1

        self.rect = self.image.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.image)

        if self.animation_count // self.ANIMATION_DELAY > len(sprites):
            self.animation_count = 0

def get_background(name):
    image = pygame.image.load(join("assets", "Background", name))
    _,_, width, height = image.get_rect()
    tiles = []

    for i in range(WIDTH// width +1):
        for j in range(HEIGHT//height +1):
            pos = (i*width, j*height)
            tiles.append(pos)

    return tiles, image

def draw(window, background, bg_image,player, objects,offset_x):
    for tile in background:
        window.blit(bg_image, tile)

    for obj in objects:
        obj.draw(window,offset_x)

    player.draw(window,offset_x)

    pygame.display.update()

def handle_vertical_collision(player,objects,dy):
    collided_objects = []
    for obj in objects:
        if pygame.sprite.collide_mask(player,obj):
            if dy > 0:
                player.rect.bottom = obj.rect.top
                player.landed()
            elif dy < 0:
                player.rect.top = obj.rect.bottom
                player.hit_head()

            collided_objects.append(obj)

    return collided_objects

def collide(player, objects, dx):
    player.move(dx, 0)
    player.update()
    collided_object = None
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):
            collided_object = obj
            break
    
    player.move(-dx,0)
    player.update()
    return collided_object

def handle_move(player,objects):
    keys = pygame.key.get_pressed()

    player.x_vel = 0
    collide_left = collide(player,objects, -PLAYER_VEL*2)
    collide_right = collide(player, objects, PLAYER_VEL*2)
    if keys[pygame.K_LEFT] and not collide_left:
        player.move_left(PLAYER_VEL)
    if keys[pygame.K_RIGHT] and not collide_right:
        player.move_right(PLAYER_VEL)
        
    vertical_collide = handle_vertical_collision(player, objects, player.y_vel)
    to_check = [collide_left, collide_right, *vertical_collide]
    for obj in to_check:
        if obj and obj.name == "fire":
            player.make_hit()

def main(window):
    clock = pygame.time.Clock()
    background, bg_image = get_background("Pink.png")

    block_size = 96

    player = Player(100,100,50,50)
    fire1 = Fire(100,HEIGHT-block_size-65,16,32)#16-32 is the diemensions of the image.
    fire2 = Fire(165,HEIGHT-block_size-65,16,32)
    fire3 = Fire(230,HEIGHT-block_size-65,16,32)
    fire4 = Fire(295,HEIGHT-block_size-65,16,32)
    fire5 = Fire(360,HEIGHT-block_size-65,16,32)
    fire6 = Fire(435,HEIGHT-block_size-65,16,32) 
    fire7 = Fire(500,HEIGHT-block_size-65,16,32) 

    fire8 = Fire(1245,HEIGHT-block_size-65,16,32)
    fire9 = Fire(1310,HEIGHT-block_size-65,16,32)
    fire10 = Fire(1375,HEIGHT-block_size-65,16,32)
    fire11 = Fire(1440,HEIGHT-block_size-65,16,32)
    fire12 = Fire(1505,HEIGHT-block_size-65,16,32)
    fire13 = Fire(1570,HEIGHT-block_size-65,16,32)
    fire14 = Fire(1635,HEIGHT-block_size-65,16,32)
    fire15 = Fire(3140,HEIGHT-block_size-65,16,32)
    fire16 = Fire(3205,HEIGHT-block_size-65,16,32)
    fire1.on(),fire2.on(),fire3.on(),fire4.on(),fire5.on(),fire6.on(),fire7.on(),fire8.on(),fire9.on(),fire10.on(),fire11.on()
    fire12.on(), fire13.on(), fire14.on(), fire15.on(), fire16.on()

    floor = [Block(i*block_size, HEIGHT-block_size, block_size)
             for i in range(0,(WIDTH*4)//block_size)]
    blocks = [Block(i*90+730, HEIGHT-block_size*3.5, block_size)
            for i in range(1,6)]
    
    blocks2 = [Block((i*90+1560), HEIGHT-block_size*3.5, block_size)
            for i in range(1,6)]
    
    blocks3 = [Block((i*90+2600), HEIGHT-block_size*4.5, block_size)
            for i in range(1,6)]
    
    blocks4 = [Block(3300, HEIGHT-block_size*(5+i), block_size)
                for i in range(0,3)]
    
    blocks5 = [Block(3300, HEIGHT-block_size*(2+i), block_size)
                for i in range(0,2)]



    objects = [*floor,Block(0,HEIGHT-block_size*2, block_size),Block(0,HEIGHT-block_size*3, block_size),Block(0,HEIGHT-block_size*4, block_size),
               Block(0,HEIGHT-block_size*5, block_size),Block(0,HEIGHT-block_size*6, block_size),Block(0,HEIGHT-block_size*7, block_size),#Floor and left pillar
               
               Block(100,HEIGHT-block_size*4, block_size),
               Block(445,HEIGHT-block_size*4, block_size),

               Block(540,HEIGHT-block_size*5, block_size),
               Block(540,HEIGHT-block_size*6, block_size),
               Block(2400, HEIGHT-block_size*4, block_size),
               
               fire1,fire2,fire3,fire4,fire5,fire6,fire7,fire8,fire9,fire10,fire11,fire12,fire13,fire14,fire15,fire16,*blocks, *blocks2
               ,*blocks3,*blocks4,*blocks5]
    
    offset_x = 0
    scroll_area_width = 250


    run = True
    while run:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_UP and player.jump_count < 2:
                    player.jump()
                elif event.key == pygame.K_SPACE and player.jump_count < 2:
                    player.jump()

        player.loop(FPS)
        fire1.loop(),fire2.loop(),fire3.loop(),fire4.loop(),fire5.loop(),fire6.loop(),fire7.loop(),
        fire8.loop(),fire9.loop(),fire10.loop(),fire11.loop(),fire12.loop(),fire13.loop(),fire14.loop(),fire15.loop(),fire16.loop()
        handle_move(player,objects)
        draw(window, background, bg_image,player, objects,offset_x)

        if ((player.rect.right - offset_x >= WIDTH - scroll_area_width) and player.x_vel > 0) or (
            (player.rect.left - offset_x <= WIDTH - scroll_area_width) and player.x_vel < 0):
            offset_x += player.x_vel

        
    pygame.quit()


if __name__ == "__main__":
    main(window)

