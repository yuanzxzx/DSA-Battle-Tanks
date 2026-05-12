from typing import Tuple
import pygame as pg
from battle_tanks import ROUTE

FONT = ROUTE("assets/Pixel Digivolve.otf")

class TextComponent:

    """Surface for text rendering """
    def __init__(self, position, text, color=None, font_size=32, outline_color=None): #Initializes Text Component
        self._color = color if color is not None else (160, 0, 0) #Sets Color
        self.size_font = font_size #Sets Font Size
        self._outline_color = outline_color #Sets Outline Color
        self._text = text #Sets Text
        
        self._surface = self.render(self._text, FONT, self._color, self.size_font, self._outline_color) #Renders Text
        self._rect = self._surface.get_rect() #Gets Rectangle of Text
        self._rect.center = position #Sets Center of Text

    @staticmethod
    def render(text: str, font_path: str, color: Tuple[int, int, int], size: int, outline_color=None): #Renders Text
        font = pg.font.Font(font_path, size) #Creates Font
        base_text = font.render(text, True, color) #Renders Text
    
        if outline_color is None: #Checks if Outline Color is None
            return base_text #Returns Text
        
        out_img = font.render(text, True, outline_color) #Renders Outline
        w, h = base_text.get_size() #Gets Size of Text
        outline_surf = pg.Surface((w + 2, h + 2), pg.SRCALPHA) #Creates Surface for Outline
    
        outline_surf.blit(out_img, (0, 3)) #Blits Outline
        outline_surf.blit(out_img, (2, 3)) #Blits Outline
        outline_surf.blit(out_img, (3, 0)) #Blits Outline
        outline_surf.blit(out_img, (3, 2)) #Blits Outline
        outline_surf.blit(base_text, (3, 3)) #Blits Outline
    
        return outline_surf    

    def update(self): #Updates the surface and maintains centering
        """ Updates the surface and maintains centering """
        old_center = self._rect.center #Gets Center of Text
        self._surface = self.render(self._text, FONT, self._color, self.size_font, self._outline_color) #Updates Text
        self._rect = self._surface.get_rect() #Updates Rectangle of Text
        self._rect.center = old_center #Updates Center of Text

    @property
    def color(self):
        """getter color"""
        return self._color

    @color.setter
    def color(self, color: Tuple[int, int, int]):
        """Update color and maintain centering/outline"""
        self._color = color
        center = self._rect.center
        self._surface = self.render(self._text, FONT, self._color, self.size_font, self._outline_color)
        self._rect = self._surface.get_rect(center=center)

    @property
    def text(self):
        """getting """
        return self._text
        
    @text.setter
    def text(self, text):
        """Update text and maintain centering/outline"""
        center = self._rect.center
        self._text = text
        self._surface = self.render(self._text, FONT, self._color, self.size_font, self._outline_color)
        self._rect = self._surface.get_rect(center=center)

    def draw(self,screen):
        """ draw"""
        screen.blit(self._surface,self._rect)

