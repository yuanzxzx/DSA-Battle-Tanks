import sys
from typing import Dict, Union
import pygame as pg

from battle_tanks.components.text import TextComponent
from battle_tanks.game import Game
from battle_tanks.commons.package import Struct
from battle_tanks.commons.tank_surface import tank_cover
from battle_tanks.components.network import NetworkComponent
from battle_tanks.commons.package import Struct
from battle_tanks.commons.tank_surface import tank_cover
from battle_tanks.components.network import NetworkComponent
from battle_tanks import ROUTE

GREEN_STATUS = (0, 128, 0)
RED_STATUS = (255,0,0)

@@ -25,45 +26,75 @@ class Menu:
        self.angle = 0
        self.angle_cannon = 0

        # Load background image
        self.background_image = pg.image.load(ROUTE('assets/images/camo shi.jpg')).convert()
        # Scale to fit the screen
        self.background_image = pg.transform.scale(self.background_image, (self.main_surface.get_width(), self.main_surface.get_height()))
    
        self.options:Dict[int,dict] =  {
            # 1:{
            #     "text_draw": Text((200,100),"TESTING MODE", font_size=45, color=NEU),
            #     "action": "SINGLE_PLAYER_MODE"
            # },
            2:{
                "text_draw": TextComponent((260,200),"MULTIPLAYER MODE", font_size=45, color=NEU),
                "text_draw": TextComponent((300,250),"MULTIPLAYER MODE", font_size=45, color=NEU),
                "action": "MULTIPLAYER_MODE"
            },
        }


    def multiplayer_mode(self,game_screen) -> Union[Game, None]:
        """ Menu mode """
        user_enter = False
    def multiplayer_mode(self, game_screen) -> Union[Game, None]:
        """Menu connection form."""
        ip_text = "localhost"
        name:str = "JOHN"
        user_text =  "8010"
        name: str = "JOHN"
        user_text = "8010"
        option_select = 0
        status =  NEU
        status = NEU

        while user_enter is not True:
        center_x = self.main_surface.get_width() // 2
        input_width = 360
        input_height = 44
        input_x = center_x - input_width // 2

        name_rect = pg.Rect(input_x, 120, input_width, input_height)
        ip_rect = pg.Rect(input_x, 180, input_width, input_height)
        port_rect = pg.Rect(input_x, 240, input_width, input_height)
        enter_label = TextComponent((center_x, 340), "ENTER", status, font_size=36)
        enter_label.update()
        enter_rect = enter_label._rect.inflate(30, 18)

        while True:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()

                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_DOWN:
                        option_select -= 1
                        if option_select < 0:
                            option_select = 0

                    if event.key == pg.K_UP:
                        option_select += 1
                        if option_select > 2:
                            option_select = 2
                elif event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                    mouse_pos = event.pos
                    if port_rect.collidepoint(mouse_pos):
                        option_select = 0
                    elif ip_rect.collidepoint(mouse_pos):
                        option_select = 1
                    elif name_rect.collidepoint(mouse_pos):
                        option_select = 2
                    elif enter_rect.collidepoint(mouse_pos):
                        try:
                            if len(user_text) > 0 and len(name) > 0:
                                check_name = NetworkComponent.check_name((ip_text, int(user_text)), name)
                                if check_name:
                                    game = Game((ip_text, int(user_text)), game_screen, name)
                                    if game.network.player_data != Struct.USER_NOT_AVAILABLE:
                                        return game
                                else:
                                    status = RED_STATUS
                        except ConnectionRefusedError as e:
                            print(e)
                            status = RED_STATUS

                    if event.key ==  pg.K_BACKSPACE:
                elif event.type == pg.KEYDOWN:
                    if event.key == pg.K_TAB:
                        option_select = (option_select + 1) % 3
                    elif event.key == pg.K_BACKSPACE:
                        if option_select == 2:
                            name = name[:-1]
                        elif option_select == 1:

@@ -71,182 +102,161 @@ class Menu:
                        else:
                            user_text = user_text[:-1]

                    elif event.key ==  pg.K_RETURN:
                    elif event.key == pg.K_RETURN:
                        try:
                            if len(user_text) > 0 and len(name) > 0:
                                check_name = NetworkComponent.check_name((ip_text, int(user_text)), name)
                                if check_name:
                                    game = Game((ip_text, int(user_text)),game_screen, name)
                                    game = Game((ip_text, int(user_text)), game_screen, name)
                                    if game.network.player_data != Struct.USER_NOT_AVAILABLE:
                                        return game
                                else:
                                    status = RED_STATUS

                        except ConnectionRefusedError as e:
                            print(e)
                            status = RED_STATUS

                    else:
                        if len(user_text) <= 7:
                            if option_select == 2:
                                name += event.dict.get("unicode")
                                name = name.upper()

                            elif option_select == 1:
                                ip_text += event.dict.get("unicode")
                            elif option_select == 0:
                                try:
                                    user_text += str(int(event.dict.get("unicode")))
                                except ValueError:
                                    pass


                    if event.key != pg.K_DOWN and event.key != pg.K_UP:
                        if len(name) > 0 and option_select == 2:
                            try:
                                port = int(user_text)
                                if 0 < port < 65535:
                                    check_name = NetworkComponent.check_name((ip_text, int(user_text)), name)
                                    if check_name is True:
                                        status = GREEN_STATUS
                                    elif check_name is False:
                                        status = RED_STATUS
                                    else:
                                        print(f"SOCKET NOT CONNECT: {check_name}")
                                        status = NEU
                            except ValueError as e:
                                print(f"ERROR VALUE: {e}")


            self.main_surface.fill(BACKGROUND)

            surface_input_port = pg.Surface((250,40))
            surface_input_ip = pg.Surface((250,40))
            surface_input_name = pg.Surface((250,40))

            text_input = TextComponent((50,20), user_text, (255,255,255))
                        char = event.dict.get("unicode")
                        if not char:
                            continue

                        if option_select == 2:
                            name += char.upper()
                        elif option_select == 1:
                            ip_text += char
                        elif option_select == 0:
                            if char.isdigit() and len(user_text) < 5:
                                user_text += char

                if event.type == pg.KEYDOWN and event.key not in (pg.K_DOWN, pg.K_UP):
                    if len(name) > 0 and option_select == 2:
                        try:
                            port = int(user_text)
                            if 0 < port < 65535:
                                check_name = NetworkComponent.check_name((ip_text, int(user_text)), name)
                                if check_name is True:
                                    status = GREEN_STATUS
                                elif check_name is False:
                                    status = RED_STATUS
                                else:
                                    status = NEU
                        except ValueError:
                            status = RED_STATUS

            self.main_surface.blit(self.background_image, (0, 0))

            title = TextComponent((self.main_surface.get_width() // 2, 40), "BATTLE TANKS", font_size=60, color=(255, 255, 255))
            title.update()
            title.draw(self.main_surface)

            input_padding = 16
            surface_input_port = pg.Surface((input_width, input_height))
            surface_input_ip = pg.Surface((input_width, input_height))
            surface_input_name = pg.Surface((input_width, input_height))

            port_bg = (40, 70, 40) if option_select == 0 else (20, 40, 20)
            ip_bg = (40, 70, 40) if option_select == 1 else (20, 40, 20)
            name_bg = (40, 70, 40) if option_select == 2 else (20, 40, 20)

            surface_input_port.fill(port_bg)
            surface_input_ip.fill(ip_bg)
            surface_input_name.fill(name_bg)

            port_border = (255, 255, 255) if option_select == 0 else NEU
            ip_border = (255, 255, 255) if option_select == 1 else NEU
            name_border = (255, 255, 255) if option_select == 2 else NEU

            pg.draw.rect(self.main_surface, port_border, port_rect, 3 if option_select == 0 else 2, border_radius=10)
            pg.draw.rect(self.main_surface, ip_border, ip_rect, 3 if option_select == 1 else 2, border_radius=10)
            pg.draw.rect(self.main_surface, name_border, name_rect, 3 if option_select == 2 else 2, border_radius=10)

            text_input = TextComponent((input_padding + 5, input_height // 2), user_text, (255, 255, 255), font_size=30)
            text_input._rect = text_input._surface.get_rect(midleft=(input_padding, input_height // 2))
            text_input.draw(surface_input_port)
            text_input_ip = TextComponent((100,20), ip_text, (255,255,255))

            text_input_ip = TextComponent((input_padding + 5, input_height // 2), ip_text, (255, 255, 255), font_size=30)
            text_input_ip._rect = text_input_ip._surface.get_rect(midleft=(input_padding, input_height // 2))
            text_input_ip.draw(surface_input_ip)

            text_input_name = TextComponent((50,20), name, (255,255,255))
            pg.draw.circle(surface_input_name, status, (230, 20), 15)
            text_input_name = TextComponent((input_padding + 5, input_height // 2), name, (255, 255, 255), font_size=30)
            text_input_name._rect = text_input_name._surface.get_rect(midleft=(input_padding, input_height // 2))
            text_input_name.draw(surface_input_name)

            text_name = TextComponent((70,60), "NAME: ")
            text_ip = TextComponent((70,120), "IP: ")
            text_port = TextComponent((70,180), "PORT: ")
            text_enter = TextComponent((70,240), "ENTER", status)

            if option_select == 2:
                text_name.color = (255,255,255)
                text_ip.color   = NEU
                text_port.color = NEU
            elif option_select == 1:
                text_ip.color   = (255,255,255)
                text_port.color = NEU
                text_name.color = NEU
            else:
                text_port.color = (255,255,255)
                text_ip.color = NEU
                text_name.color = NEU
            self.main_surface.blit(surface_input_name, name_rect.topleft)
            self.main_surface.blit(surface_input_ip, ip_rect.topleft)
            self.main_surface.blit(surface_input_port, port_rect.topleft)

            label_color_name = (255, 255, 255) if option_select == 2 else NEU
            label_color_ip = (255, 255, 255) if option_select == 1 else NEU
            label_color_port = (255, 255, 255) if option_select == 0 else NEU

            """
            LABELS: IP, PORT AND NAME
            """
            text_name = TextComponent((input_x - 80, name_rect.centery), "NAME:", color=label_color_name, font_size=30)
            text_ip = TextComponent((input_x - 80, ip_rect.centery), "SERVER:", color=label_color_ip, font_size=30)
            text_port = TextComponent((input_x - 80, port_rect.centery), "PORT:", color=label_color_port, font_size=30)
            text_enter = TextComponent((center_x, enter_rect.centery), "ENTER", status, font_size=36)
            text_name.update()
            text_ip.update()
            text_port.update()
            text_enter.update()

            pg.draw.rect(self.main_surface, (50, 90, 50), enter_rect, border_radius=8)
            pg.draw.rect(self.main_surface, status if status != NEU else (255, 255, 255), enter_rect, 2, border_radius=8)

            text_name.draw(self.main_surface)
            text_ip.draw(self.main_surface)
            text_port.draw(self.main_surface)
            text_name.draw(self.main_surface)
            text_enter.draw(self.main_surface)

            """
            INPUT
            """
            self.main_surface.blit(surface_input_port, (120,160))
            self.main_surface.blit(surface_input_ip, (120,100))
            self.main_surface.blit(surface_input_name,(120,40))
            if port_rect.collidepoint(pg.mouse.get_pos()) or ip_rect.collidepoint(pg.mouse.get_pos()) or name_rect.collidepoint(pg.mouse.get_pos()) or enter_rect.collidepoint(pg.mouse.get_pos()):
                pg.mouse.set_cursor(pg.SYSTEM_CURSOR_HAND)
            else:
                pg.mouse.set_cursor(pg.SYSTEM_CURSOR_ARROW)

            """
            TANK
            """
            self.angle += 0.5
            self.angle_cannon -= 0.5
            self.angle %= 360
            self.angle_cannon %= 360

            self.angle = self.angle % 360
            self.angle_cannon = self.angle_cannon % 360

            tank_cover(0, (150, 300), self.main_surface, scale=(200, 200), angle=self.angle, angle_cannon=self.angle_cannon)
            tank_cover(1, (450, 300), self.main_surface, scale=(200, 200), angle=self.angle, angle_cannon=self.angle_cannon)
            tank_cover(0, (100, 300), self.main_surface, scale=(200, 200), angle=self.angle, angle_cannon=self.angle_cannon)
            tank_cover(1, (500, 300), self.main_surface, scale=(200, 200), angle=self.angle, angle_cannon=self.angle_cannon)

            pg.display.flip()
            self.clock.tick(60)


        return None


    def single_local_mode(self) -> Game:
        """ Single local game """
        return Game(None, self.main_surface, "John")


    def update(self, main_game) -> Game:
        """ getting game state"""
        if len(self.options) == 1:
            self.select_option = [op for op in self.options.keys()][0]
            self.select_option = self.options.get(self.select_option).get("action")

        while self.select_option is None:
            for event in pg.event.get():
                if event.type == pg.KEYDOWN:
                    key = event.dict.get('key')

                    if key == pg.K_DOWN or key == pg.K_s:
                        if self.position < len(self.options):
                            self.position +=1

                    if key == pg.K_UP or  key == pg.K_w:
                        if len(self.options) <= self.position:
                            self.position -=1

                    elif key == pg.K_RETURN:
                        select_option: dict = self.options.get(self.position)
                        self.select_option = select_option.get("action")

                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()


            self.draw()
            pg.display.flip()

        return self.multiplayer_mode(main_game) if self.select_option == "MULTIPLAYER_MODE" \
            else self.single_local_mode()
        """Go directly to multiplayer connect menu."""
        return self.multiplayer_mode(main_game)


    def draw(self):
        """ Draw options"""
        self.main_surface.fill(BACKGROUND)

        if self.position != 0:
            select_option: dict = self.options.get(self.position)
            text_draw: TextComponent = select_option.get("text_draw")
            text_draw.color=(255,255,255)

            self.options.update({self.position: {
                "text_draw": text_draw,
                "action" : select_option.get("action")
                        }})

        for op,values in self.options.items():
        self.main_surface.blit(self.background_image, (0, 0))
        
        # Draw title at upper center
        title = TextComponent((300, 80), "BATTLE TANKS", font_size=67, color=(255, 255, 255))
        title.update()
        title.draw(self.main_surface)
        
        mouse_pos = pg.mouse.get_pos()

        for op, values in self.options.items():
            op_draw = values.get("text_draw")
            if op != self.position:
                op_draw.color=NEU
            
            # Highlight option if mouse is hovering over it or keyboard selected
            if op_draw._rect.collidepoint(mouse_pos) or self.position == op:
                op_draw.color = (255, 255, 255)
                if op_draw._rect.collidepoint(mouse_pos):
                    self.position = op
            else:
                op_draw.color = NEU

            op_draw.update()
            op_draw.draw(self.main_surface)

        tank_cover(0,(150,300),self.main_surface,scale=(200,200),angle=0,angle_cannon=0)
        tank_cover(1,(450,300),self.main_surface,scale=(200,200),angle=360,angle_cannon=180)
