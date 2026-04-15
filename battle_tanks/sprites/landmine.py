import pygame as pg
import math

class LandMine(pg.sprite.Sprite):
    SIZE = 20
    EXPLOSION_RADIUS = 80
    DAMAGE = 40

    def __init__(self, x: int, y: int, owner_name: str):
        super().__init__()
        self.world_x = x
        self.world_y = y
        self.owner_name = owner_name
        self.armed = False  # arms after owner walks away
        self._arm_timer = 90  # frames until armed

        self.image = pg.Surface((self.SIZE, self.SIZE), pg.SRCALPHA)
        self._draw(armed=False)
        self.rect = self.image.get_rect(topleft=(x, y))

    def _draw(self, armed: bool):
        self.image.fill((0, 0, 0, 0))
        color = (180, 50, 50) if armed else (100, 100, 100)
        pg.draw.circle(self.image, color, (10, 10), 10)
        pg.draw.circle(self.image, (30, 30, 30), (10, 10), 6)
        # spikes
        for i in range(8):
            angle = math.radians(i * 45)
            x1 = 10 + 8 * math.cos(angle)
            y1 = 10 + 8 * math.sin(angle)
            x2 = 10 + 11 * math.cos(angle)
            y2 = 10 + 11 * math.sin(angle)
            pg.draw.line(self.image, (220, 220, 50), (int(x1), int(y1)), (int(x2), int(y2)), 2)

    def update(self, players: list, owner_name: str):
        if not self.armed:
            self._arm_timer -= 1
            if self._arm_timer <= 0:
                self.armed = True
                self._draw(armed=True)
        return None  # no explosion yet

    def check_trigger(self, players: list):
        """Returns list of players hit if triggered, else empty list."""
        if not self.armed:
            return []
        mine_rect = pg.Rect(self.world_x, self.world_y, self.SIZE, self.SIZE)
        for player in players:
            if player.get("name") == self.owner_name:
                continue
            px, py = player.get("x", 0), player.get("y", 0)
            dist = math.sqrt((px - self.world_x) ** 2 + (py - self.world_y) ** 2)
            if dist < self.EXPLOSION_RADIUS * 0.3:  # trigger radius
                return players  # explode, damage everyone in radius
        return []