import pygame as pg 

class CameraComponent:
    def __init__(self,width,height,screen_size): # Inits camera bounds and shake variables
        self.camera = pg.Rect((0,0),(width,height))
        self.width = width
        self.height = height
        self.screen_size = screen_size
        self.shake_duration = 0
        self.shake_intensity = 5

    def apply(self,entity): #Adjusts entity rect by camera offset
        return entity.rect.move(self.camera.topleft)

    def apply_rect(self,rect): #Adjusts raw rect by camera offset
        return rect.move(self.camera.topleft)

    def shake(self, duration=15, intensity=5): #Sets shake duration and intensity
        self.shake_duration = duration #Sets shake duration
        self.shake_intensity = intensity #Sets shake intensity

    def update(self,target): #Centers camera on target, clamps to map bounds, applies shake
        x_pos = -target.rect.centerx + self.screen_size[0] // 2 #Calculates x position for centering
        y_pos = -target.rect.centery + self.screen_size[1] // 2 #Calculates y position for centering
        x_pos = min(0,x_pos) #Clamps x position to map bounds
        y_pos = min(0,y_pos) #Clamps y position to map bounds
        x_pos = max(-(self.width - self.screen_size[0]),x_pos)
        y_pos = max(-(self.height - self.screen_size[1]),y_pos)
        self.camera = pg.Rect(x_pos,y_pos,self.width,self.height)
        
        if self.shake_duration > 0: #Adds random offset to camera for shake effect
            import random
            offset_x = random.randint(-self.shake_intensity, self.shake_intensity) #Random offset for shake effect horizontally
            offset_y = random.randint(-self.shake_intensity, self.shake_intensity) #Random offset for shake effect vertically
            self.camera.x += offset_x
            self.camera.y += offset_y
            self.shake_duration -= 1 #Decrements shake duration
