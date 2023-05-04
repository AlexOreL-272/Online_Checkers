from src.globals import Globals
import pygame


class Auth:
    """
    Class to perform player's authorization
    """

    pygame.init()
    pygame.display.set_caption('Authorization')

    font = pygame.font.SysFont('Calibri', 14, True, False)
    medium_font = pygame.font.SysFont('Calibri', 20, True, False)
    large_font = pygame.font.SysFont('Calibri', 26, True, False)

    def __init__(self):
        """
        Constructs a default authorization screen
        """

        self.login = ''
        self.passwd = ''
        self.room_id = ''
        self.screen = pygame.display.set_mode(Globals.auth_size)

    def __draw_init_screen__(self, login_rect, password_rect):
        """
        :param login_rect: login rectangle to draw
        :param password_rect: password rectangle to draw

        Draws initial screen with two textareas and two buttons
        """

        self.screen.fill(Globals.font_colors['White'])
        pygame.draw.rect(self.screen, Globals.font_colors['Blue'], login_rect, 2, border_radius=5)
        pygame.draw.rect(self.screen, Globals.font_colors['Blue'], password_rect, 2, border_radius=5)
        login_text = Auth.font.render(f'Enter login:    {self.login}', True, Globals.font_colors['Black'])
        password_text = Auth.font.render('Enter password:    ' + '*' * len(self.passwd), True,
                                         Globals.font_colors['Black'])
        self.screen.blit(login_text, (login_rect.x - 70, login_rect.y + 8))
        self.screen.blit(password_text, (password_rect.x - 100, password_rect.y + 8))

    def __handle_mouse_auth__(self):
        """
        Handes mouse clicks
        """

        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()
        if 70 <= mouse[0] <= 170 and 150 <= mouse[1] <= 200:
            pygame.draw.rect(self.screen, Globals.font_colors['Green'], (70, 150, 100, 50), border_radius=10)
            if click[0] == 1 and self.login != '' and self.passwd != '':
                return True

        if 230 <= mouse[0] <= 300 and 150 <= mouse[1] <= 200:
            pygame.draw.rect(self.screen, Globals.font_colors['Red'], (220, 150, 100, 50), border_radius=10)
            if click[0] == 1:
                pygame.quit()
                quit()

        return False

    def __render_auth_text__(self):
        """
        Shows appropriate text
        """

        enter = Auth.medium_font.render("Let's go", True, Globals.font_colors['Black'])
        self.screen.blit(enter, (88, 165))
        cancel = Auth.medium_font.render('Cancel', True, Globals.font_colors['Black'])
        self.screen.blit(cancel, (243, 165))

    def show_login_form(self):
        """
        Shows login screen
        """

        login_rect = pygame.Rect(150, 50, 200, 32)
        password_rect = pygame.Rect(150, 100, 200, 32)
        login_active, pass_active = False, False

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    login_active = login_rect.collidepoint(event.pos)
                    pass_active = password_rect.collidepoint(event.pos)
                if event.type == pygame.KEYDOWN:
                    if login_active:
                        self.login = self.login[:-1] if event.key == pygame.K_BACKSPACE else self.login + event.unicode
                    if pass_active:
                        self.passwd = password[:-1] if event.key == pygame.K_BACKSPACE else self.passwd + event.unicode

            self.__draw_init_screen__(login_rect, password_rect)
            if self.__handle_mouse_auth__():
                return

            self.__render_auth_text__()
            pygame.display.update()

    def __btns_query__(self, room_rect):
        """
        :param room_rect: rectangle to enter room id

        Checks if a button was pressed
        """

        pygame.draw.rect(self.screen, Globals.font_colors['Blue'], room_rect, 2, border_radius=10)

        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()
        if 50 <= mouse[0] <= 350 and 50 <= mouse[1] <= 100:
            pygame.draw.rect(self.screen, Globals.font_colors['Green'], (50, 50, 300, 50), border_radius=10)
            if click[0] == 1:
                return 'new'
        else:
            pygame.draw.rect(self.screen, Globals.font_colors['Blue'], (50, 50, 300, 50), border_radius=10)

        if 50 <= mouse[0] <= 190 and 125 <= mouse[1] <= 175:
            pygame.draw.rect(self.screen, Globals.font_colors['Green'], (50, 125, 140, 50), border_radius=10)
            if click[0] == 1 and self.room_id:
                return 'join'
        else:
            pygame.draw.rect(self.screen, Globals.font_colors['Blue'], (50, 125, 140, 50), border_radius=10)

    def __render_main_menu_text__(self):
        """
        Shows text in main menu
        """

        welcome_text = Auth.medium_font.render(f'Welcome, {self.login}!', True, Globals.font_colors['Black'])
        create_room = Auth.large_font.render("Create room", True, Globals.font_colors['White'])
        join_room = Auth.large_font.render('Join room', True, Globals.font_colors['White'])
        join_room_id = Auth.large_font.render(f'{self.room_id}', True, Globals.font_colors['Black'])
        self.screen.blit(welcome_text, (25, 15))
        self.screen.blit(create_room, (130, 60))
        self.screen.blit(join_room, (70, 135))
        self.screen.blit(join_room_id, (225, 135))

    def main_menu(self):
        """
        Shows main menu
        """

        active_enter = False
        room_rect = pygame.Rect(210, 125, 150, 50)

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                if event.type == pygame.MOUSEBUTTONDOWN:
                    active_enter = room_rect.collidepoint(event.pos)
                if event.type == pygame.KEYDOWN and active_enter:
                    if event.key == pygame.K_BACKSPACE:
                        self.room_id = self.room_id[:-1]
                    elif event.unicode.isdigit() and len(self.room_id) <= 8:
                        self.room_id += event.unicode

            self.screen.fill(Globals.font_colors['White'])
            query = self.__btns_query__(room_rect)
            self.__render_main_menu_text__()
            if query is not None:
                return query
            pygame.display.update()

    @staticmethod
    def close():
        """
        Closes the authorization screen
        """

        pygame.display.quit()
