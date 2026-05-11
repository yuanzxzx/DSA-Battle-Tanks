import pygame as pg 


class CameraComponent: # Viewport manager
    def __init__(self,width,height,screen_size): # Inits state
        self.camera = pg.Rect((0,0),(width,height))
        self.width = width
        self.height = height
        self.screen_size = screen_size
        self.shake_duration = 0
        self.shake_intensity = 5

    def apply(self,entity): # Offsets entity
        return entity.rect.move(self.camera.topleft)

    def apply_rect(self,rect): # Offsets rect
        return rect.move(self.camera.topleft)

    def shake(self, duration=15, intensity=5): # Sets shake vars
        self.shake_duration = duration
        self.shake_intensity = intensity

    def update(self,target): # Updates camera pos
        x_pos = -target.rect.centerx + self.screen_size[0] // 2 # Center X calc
        y_pos = -target.rect.centery + self.screen_size[1] // 2 # Center Y calc
        x_pos = min(0,x_pos) # Clamp left edge
        y_pos = min(0,y_pos) # Clamp top edge
        x_pos = max(-(self.width - self.screen_size[0]),x_pos) # Clamp right edge
        y_pos = max(-(self.height - self.screen_size[1]),y_pos) # Clamp bottom edge
        
        self.camera = pg.Rect(x_pos,y_pos,self.width,self.height) # Create view rect
        
        if self.shake_duration > 0:
            import random
            offset_x = random.randint(-self.shake_intensity, self.shake_intensity) # Rand X offset
            offset_y = random.randint(-self.shake_intensity, self.shake_intensity) # Rand Y offset
            self.camera.x += offset_x # Apply X shake
            self.camera.y += offset_y # Apply Y shake
            self.shake_duration -= 1 # Decrement timer
