import pygame as pg
import math
from battle_tanks import ROUTE


class SpriteBasic(pg.sprite.Sprite):
    def __init__(self, x_pos,y_pos,width,height):
        super().__init__()
        self._data = None
        self.rect = pg.Rect((x_pos, y_pos), (width, height))


    @classmethod
    def boom(cls):
        pass
        # cls.SOUND_BOOM.play()


    @property
    def data(self):
        return self._data


    @data.setter
    def data(self, data: bytes):
       self._data = data


class Brick(SpriteBasic):
    """Class representing a Brick object"""
    def __init__(self,x_pos,y_pos,width,height):
        super().__init__(x_pos,y_pos,width,height)
        self.box_img = pg.image.load(ROUTE("assets/images/tiles.png"))
        self.image = self.box_img.subsurface((0,0),(32,32))
        self.mask = pg.mask.from_surface(self.image)


class Block(SpriteBasic):
    """ Class representing a Block object """
    def __init__(self,x_pos,y_pos,width,height):
        super().__init__(x_pos,y_pos,width,height)

class Bullet(pg.sprite.Sprite):
    def __init__(self, x, y, angle_cannon, max_distance=300):
        super().__init__()
        self.image = pg.Surface((6, 6), pg.SRCALPHA)
        pg.draw.circle(self.image, (255, 255, 0), (3, 3), 3) # Yellow bullet
        self.rect = self.image.get_rect(center=(x, y))
        self.distance_traveled = 0
        self.max_distance = max_distance
        
        radian_angle = math.radians(angle_cannon)
        self.vx = -math.sin(radian_angle) * 15
        self.vy = -math.cos(radian_angle) * 15

    def update(self):
        self.rect.x += self.vx
        self.rect.y += self.vy
        self.distance_traveled += math.sqrt(self.vx**2 + self.vy**2)
        if self.distance_traveled >= self.max_distance:
            self.kill()

class Particle(pg.sprite.Sprite):
    """Particle effect for wall destruction"""
    def __init__(self, x, y, vx, vy, color=(139, 69, 19), lifetime=30):
        super().__init__()
        self.rect = pg.Rect(x, y, 4, 4)
        self.vx = vx
        self.vy = vy
        self.color = color
        self.lifetime = lifetime
        self.age = 0
        self.image = pg.Surface((4, 4), pg.SRCALPHA)
        self._update_image()

    def _update_image(self):
        alpha = int(255 * (1 - self.age / self.lifetime))
        self.image.fill((0, 0, 0, 0))
        pg.draw.circle(self.image, (*self.color, alpha), (2, 2), 2)

    def update(self):
        self.age += 1
        self.rect.x += self.vx
        self.rect.y += self.vy
        self.vy += 0.1  # gravity
        self._update_image()
        if self.age >= self.lifetime:
            self.kill()

class PowerUp(pg.sprite.Sprite):
    def __init__(self, x: int, y: int):
        super().__init__()
        
        self.image = pg.Surface((24, 24), pg.SRCALPHA)
        self.image.fill((255, 255, 0))  
        pg.draw.rect(self.image, (255, 165, 0), self.image.get_rect(), 3) 
        
        font = pg.font.Font(None, 24)
        text = font.render("M", True, (255, 165, 0))
        text_rect = text.get_rect(center=(12, 12))
        self.image.blit(text, text_rect)

        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def update(self):
        pass


class LandMine(pg.sprite.Sprite):
    EXPLOSION_RADIUS = 75
    DAMAGE = 50

    def __init__(self, x: int, y: int, owner: str):
        super().__init__()
        self.owner = owner

        self.world_x = x
        self.world_y = y

        self.image = pg.Surface((20, 20), pg.SRCALPHA)
        pg.draw.circle(self.image, (50, 50, 50), (10, 10), 10)  
        pg.draw.circle(self.image, (255, 50, 50), (10, 10), 4)  

        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y

        self.active = False
        self.activation_timer = 60  

    def update(self, players: list, local_name: str):
        if self.activation_timer > 0:
            self.activation_timer -= 1
        else:
            self.active = True

        if self.owner == local_name:
            self.image.set_alpha(150)
        else:
            self.image.set_alpha(0)

    def check_trigger(self, players: list) -> bool:
        if not self.active:
            return False

        for p in players:
            if p.get("name") == self.owner:
                continue

            dist = math.sqrt((p["x"] - self.world_x)**2 + (p["y"] - self.world_y)**2)
            
            if dist < 25: 
                return True
                
        return False
