import pygame as pg
import math
from battle_tanks import ROUTE

class SpriteBasic(pg.sprite.Sprite): # Abstract Class
    def __init__(self, x_pos,y_pos,width,height): # Initial position, width and height of element
        super().__init__()
        self._data = None
        self.rect = pg.Rect((x_pos, y_pos), (width, height))

    @classmethod # Method that plays explosion sound    
    def boom(cls):
        pass

    @property # Property for data
    def data(self):
        return self._data

    @data.setter # Setter for data
    def data(self, data: bytes):
       self._data = data

class Brick(SpriteBasic): # Concrete Class
    """Class representing a Brick object"""
    def __init__(self,x_pos,y_pos,width,height): # Initial position, width and height of brick
        super().__init__(x_pos,y_pos,width,height)
        self.box_img = pg.image.load(ROUTE("assets/images/tiles.png"))
        self.image = self.box_img.subsurface((0,0),(32,32))
        self.mask = pg.mask.from_surface(self.image)

class Block(SpriteBasic): # Concrete Class
    """ Class representing a Block object """
    def __init__(self,x_pos,y_pos,width,height): # Initial position, width and height of block
        super().__init__(x_pos,y_pos,width,height)

class Bullet(pg.sprite.Sprite): # Concrete Class
    def __init__(self, x, y, angle_cannon, max_distance=300): # Initial position, angle and max distance of bullet
        super().__init__()
        self.image = pg.Surface((6, 6), pg.SRCALPHA)
        pg.draw.circle(self.image, (255, 255, 0), (3, 3), 3) # Yellow bullet
        self.rect = self.image.get_rect(center=(x, y))
        self.distance_traveled = 0
        self.max_distance = max_distance # Maximum distance the bullet can travel
        
        radian_angle = math.radians(angle_cannon) # Convert angle to radians
        self.vx = -math.sin(radian_angle) * 15 # Velocity x
        self.vy = -math.cos(radian_angle) * 15 # Velocity y

    def update(self):
        self.rect.x += self.vx # Update position
        self.rect.y += self.vy
        self.distance_traveled += math.sqrt(self.vx**2 + self.vy**2)
        if self.distance_traveled >= self.max_distance: # Removes bullet if it goes out of bounds or travels too far
            self.kill()

class Particle(pg.sprite.Sprite): # Concrete Class
    """Particle effect for wall destruction"""
    def __init__(self, x, y, vx, vy, color=(139, 69, 19), lifetime=30): # Initial position, velocity, color and lifetime of particle
        super().__init__()
        self.rect = pg.Rect(x, y, 4, 4)
        self.vx = vx
        self.vy = vy
        self.color = color
        self.lifetime = lifetime
        self.age = 0 # Age of particle
        self.image = pg.Surface((4, 4), pg.SRCALPHA)
        self._update_image()

    def _update_image(self): # Updates the image of the particle
        alpha = int(255 * (1 - self.age / self.lifetime)) # Alpha of particle
        self.image.fill((0, 0, 0, 0))
        pg.draw.circle(self.image, (*self.color, alpha), (2, 2), 2)

    def update(self): # Updates the position of the particle
        self.age += 1
        self.rect.x += self.vx
        self.rect.y += self.vy
        self.vy += 0.1  # gravity
        self._update_image()
        if self.age >= self.lifetime: # Removes particle if it reaches its lifetime
            self.kill()

class PowerUp(pg.sprite.Sprite): # Concrete Class
    def __init__(self, x: int, y: int): # Initial position of power up
        super().__init__()
        
        self.image = pg.Surface((24, 24), pg.SRCALPHA)
        self.image.fill((255, 255, 0))  
        pg.draw.rect(self.image, (255, 165, 0), self.image.get_rect(), 3) 
        
        font = pg.font.Font(None, 24)
        text = font.render("M", True, (255, 165, 0)) # Power up type
        text_rect = text.get_rect(center=(12, 12))
        self.image.blit(text, text_rect)

        self.rect = self.image.get_rect()
        self.rect.x = x # Position x of power up
        self.rect.y = y # Position y of power up

    def update(self): # Updates the power up
        pass


class LandMine(pg.sprite.Sprite): # Concrete Class
    EXPLOSION_RADIUS = 75 # Explosion radius of landmine
    DAMAGE = 50 # Damage of landmine

    def __init__(self, x: int, y: int, owner_id: int): # Initial position and owner id of landmine
        super().__init__()
        self.owner_id = owner_id 
        
        self.world_x = x # World position x of landmine
        self.world_y = y # World position y of landmine

        self.image = pg.Surface((20, 20), pg.SRCALPHA) # Image of landmine
        pg.draw.circle(self.image, (50, 50, 50), (10, 10), 10)  
        pg.draw.circle(self.image, (255, 50, 50), (10, 10), 4)  # Landmine design

        self.rect = self.image.get_rect()
        self.rect.centerx = x # Center position x of landmine
        self.rect.centery = y # Center position y of landmine

        self.active = False
        self.activation_timer = 60  

    def update(self, players: list, local_id: int): # Updates the landmine
        if self.activation_timer > 0:
            self.activation_timer -= 1
        else:
            self.active = True

        if self.owner_id == local_id:
            self.image.set_alpha(150)
        else:
            self.image.set_alpha(255)

    def check_trigger(self, players: list) -> bool: # Checks if the landmine is triggered
        if not self.active:
            return False

        for p in players:
            if p.get("id") == self.owner_id:
                continue

            dist = math.sqrt((p["x"] - self.world_x)**2 + (p["y"] - self.world_y)**2) # Distance between landmine and player
            if dist < 25:  
                return True
                
        return False
