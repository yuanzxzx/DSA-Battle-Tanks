
import pygame as pg
import pytmx 

from battle_tanks import ROUTE


class TileMap:
    """ Load tilemap with tmx"""
    def __init__(self,filename): #Initializes TileMap
        tm = pytmx.load_pygame(ROUTE(f"assets/maps/{filename}"),pixelalpha = True) #Loads TileMap
        self.WIDTH = tm.width * tm.tilewidth #Gets Width of TileMap
        self.HEIGHT = tm.height * tm.tileheight #Gets Height of TileMap
        self.tmxdata = tm #Stores TileMap Data


    def render(self,surface): #Renders TileMap
        """ load tilemap with surface """
        ti = self.tmxdata.get_tile_image_by_gid #Gets Tile Image by GID
        for layer in self.tmxdata.visible_layers: #Iterates through Layers
            if isinstance(layer,pytmx.TiledTileLayer): #Checks if Layer is Tile Layer
                for x,y,gid in layer: #Iterates through Tiles
                    tile = ti(gid) #Gets Tile
                    if tile: #Checks if Tile Exists
                        surface.blit(tile,(x* self.tmxdata.tilewidth,y* self.tmxdata.tileheight))


    def make_map(self): #Creates Surface Object 
        """ create surface object"""
        temp_surface = pg.Surface((self.WIDTH,self.HEIGHT))
        self.render(temp_surface)
        return temp_surface



    