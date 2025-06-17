"""Moduł gry 'Znajdź Województwo' z wykorzystaniem biblioteki Pygame."""

import sys
import pygame
from game_state import GameState
import os
from map import PolandMapWidget
import random

"""Inicjalizacja Pygame"""
pygame.init()

"""Stałe"""
SCREEN_WIDTH, SCREEN_HEIGHT = 1280, 720
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 200, 0)
DARK_GREEN = (0, 160, 0)
HEADER_HEIGHT = 60

"""Czcionki"""
FONT = pygame.font.SysFont('Arial', 32)
SMALL_FONT = pygame.font.SysFont('Arial', 24)
TITLE_FONT = pygame.font.SysFont('Arial', 64, bold=True)
HEADER_FONT = pygame.font.SysFont('Arial', 28)


class Game:
    """Główna klasa gry."""

    def __init__(self)-> None:
        """Inicjalizuje atrybuty gry i stan początkowy."""
        self.state: GameState = GameState.HOMEPAGE
        self.screen: pygame.Surface = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Znajdź Województwo")
        self.player_name: str = ""
        self.input_text: str = ""
        self.current_round: int = 0
        self.total_rounds: int = 3
        self.images: dict[str, str] = {}
        self.running: bool = True
        self.score: int = 0
        self.button_glow: int = 0
        self.glow_direction: int = 1
        self.kolory_wojewodztw: dict[tuple[int, int, int], str] = {
            (103, 186, 144): "dolnośląskie",
            (140, 96, 59): "kujawsko-pomorskie",
            (235, 88, 72): "lubelskie",
            (90, 192, 196): "lubuskie",
            (199, 157, 109): "łódzkie",
            (252, 225, 74): "małopolskie",
            (238, 114, 124): "mazowieckie",
            (89, 174, 83): "opolskie",
            (251, 196, 51): "podkarpackie",
            (204, 133, 175): "podlaskie",
            (103, 107, 170): "pomorskie",
            (178, 205, 74): "śląskie",
            (243, 149, 79): "świętokrzyskie",
            (190, 104, 151): "warmińsko-mazurskie",
            (166, 123, 81): "wielkopolskie",
            (87, 133, 195): "zachodniopomorskie"
        }
        self.load_images()

        """Przygotowanie listy plików i miejsca na aktualne zdjęcie"""
        self.image_folder: str = os.path.join(os.path.dirname(__file__), "..", "assets", "photo_assets")
        self.image_keys: list[str] = list(self.images.keys())  
        self.current_image: str = None                      
        self.current_image_surface: pygame.Surface = None              

    def load_images(self):
        """Ładuje zdjęcia z folderu "photo_assets" """
        folder = os.path.join(os.path.dirname(__file__), "..",  "assets", "photo_assets")
        if not os.path.exists(folder):
            return 1

        for zdjecie in os.listdir(folder):
            wojewodztwo = zdjecie.split("_")[0].lower()
            self.images[zdjecie] = wojewodztwo

    def pick_next_image(self) -> None:
        """Losuje nowe zdjęcie spośród dostępnych zdjęć"""        
        if not self.image_keys:
            self.current_image = None
            self.current_image_surface = None
            return    
        self.current_image = random.choice(self.image_keys)
        self.image_keys.remove(self.current_image)
        full_path = os.path.join(self.image_folder, self.current_image)
        surf = pygame.image.load(full_path).convert_alpha()    
        max_w, max_h = 300, 300
        w, h = surf.get_size()
        scale = min(max_w / w, max_h / h)
        new_size = (int(w * scale), int(h * scale))
        self.current_image_surface = pygame.transform.smoothscale(surf, new_size)

    def draw_header(self)-> None:
        """Rysuje nagłówek z informacjami o rundzie i wyniku."""
        """Tło nagłówka"""
        pygame.draw.rect(self.screen, (230, 245, 230), (0, 0, SCREEN_WIDTH, HEADER_HEIGHT))

        """Linia oddzielająca"""
        pygame.draw.line(self.screen, (180, 220, 180), (0, HEADER_HEIGHT), (SCREEN_WIDTH, HEADER_HEIGHT), 2)

        """Licznik rund (lewy górny róg)"""
        round_text = HEADER_FONT.render(f"Runda: {self.current_round + 1}/{self.total_rounds}", True, (0, 100, 0))
        self.screen.blit(round_text, (20, 15))

        """ Wynik (prawy górny róg)"""
        score_text = HEADER_FONT.render(f"Wynik: {self.score}", True, (0, 100, 0))
        self.screen.blit(score_text, (SCREEN_WIDTH - score_text.get_width() - 20, 15))

        """Pionowa linia oddzielająca"""
        pygame.draw.line(self.screen, (180, 220, 180), (SCREEN_WIDTH // 2, 0), (SCREEN_WIDTH // 2, HEADER_HEIGHT), 1)

    def run(self)-> None:
        """Główna pętla gry obsługująca przechodzenie między stanami."""
        clock = pygame.time.Clock()
        while self.state != GameState.END:
            if self.state == GameState.HOMEPAGE:
                self.handle_homepage()
            elif self.state == GameState.STARTPAGE:
                self.handle_startpage()
            elif self.state == GameState.STARTPAGE_HARD_MODE:
                self.handle_startpage_hard_mode()
            elif self.state == GameState.INSTRUCTIONPAGE:
                self.handle_instructionpage()
            elif self.state == GameState.GAMEPAGE:
                self.handle_gamepage()
            elif self.state == GameState.RESULTPAGE:
                self.handle_resultpage()
            elif self.state == GameState.DIFFICULTY_SELECT:
                self.handle_difficulty_select()
            elif self.state == GameState.GAMEPAGE_HARD_MODE:
                self.handle_gamepage_hard_mode()
            clock.tick(60)
        pygame.quit()
        sys.exit()

    def draw_button(self, text: str, rect: pygame.Rect, color: tuple[int, int, int],
                hover_color: tuple[int, int, int], mouse_pos: tuple[int, int],
                glow: bool = False) -> None:

        """Rysuje przycisk z tekstem i obsługuje efekt najechania oraz świecenia przycisku."""
        button_color = hover_color if rect.collidepoint(mouse_pos) else color
        if glow and rect.collidepoint(mouse_pos):
            glow_radius = int(10 + 5 * abs(pygame.time.get_ticks() % 1000 - 500) / 500)
            glow_surf = pygame.Surface((rect.width + glow_radius*2, rect.height + glow_radius*2), pygame.SRCALPHA)
            pygame.draw.rect(glow_surf, (*button_color[:3], 50),
                            (glow_radius, glow_radius, rect.width, rect.height),
                            border_radius=10)
            self.screen.blit(glow_surf, (rect.x - glow_radius, rect.y - glow_radius))

        pygame.draw.rect(self.screen, button_color, rect, border_radius=10)
        pygame.draw.rect(self.screen, BLACK, rect, 2, border_radius=10)
        text_surface = FONT.render(text, True, BLACK)
        text_rect = text_surface.get_rect(center=rect.center)
        self.screen.blit(text_surface, text_rect)

    def draw_animated_background(self)-> None:
        """Rysuje animowane tło z delikatnymi falami."""
        for y in range(HEADER_HEIGHT, SCREEN_HEIGHT, 20):
            offset = pygame.time.get_ticks() / 500
            wave = int(10 * abs(pygame.math.Vector2(0, y).rotate(offset).y / SCREEN_HEIGHT))
            pygame.draw.line(
                self.screen,
                (230, 245, 230),
                (0, y + wave),
                (SCREEN_WIDTH, y + wave),
                2
            )

    def handle_homepage(self)-> None:
        """Obsługuje ekran startowy z przyciskiem Start i Zakończ."""
        title_y = 100
        title_target_y = 120
        title_speed = 0.5

        while self.state == GameState.HOMEPAGE:
            mouse_pos = pygame.mouse.get_pos()
            if title_y < title_target_y:
                title_y += title_speed
            self.screen.fill((240, 250, 240))
            self.draw_animated_background()

            title = TITLE_FONT.render("Znajdź Województwo", True, (50, 100, 50))
            title_shadow = TITLE_FONT.render("Znajdź Województwo", True, (100, 150, 100))
            self.screen.blit(title_shadow, (SCREEN_WIDTH//2 - title_shadow.get_width()//2 + 3, title_y + 3))
            self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, title_y))
            start_btn = pygame.Rect(490, 250, 300, 70)
            rules_btn = pygame.Rect(490, 350, 300, 70)
            exit_btn = pygame.Rect(490, 450, 300, 70)
            self.draw_button("Start Gry", start_btn, GREEN, DARK_GREEN, mouse_pos, glow=True)
            self.draw_button("Zasady Gry", rules_btn, GREEN, DARK_GREEN, mouse_pos)
            self.draw_button("Zakończ", exit_btn, GREEN, DARK_GREEN, mouse_pos)

            for event in pygame.event.get(): #TODO: zdarzeniaaa
                if event.type == pygame.QUIT:
                    self.change_state(GameState.END)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if start_btn.collidepoint(event.pos):
                        pygame.display.flip()
                        pygame.time.delay(300)
                        self.change_state(GameState.DIFFICULTY_SELECT)
                        return
                    elif rules_btn.collidepoint(event.pos):
                        pygame.time.delay(300)
                        self.change_state(GameState.INSTRUCTIONPAGE)
                        return
                    elif exit_btn.collidepoint(event.pos):
                        self.change_state(GameState.END)
                        return

            pygame.display.flip()

    def handle_difficulty_select(self) -> None:
        while self.state == GameState.DIFFICULTY_SELECT:
            self.screen.fill((240,250,240))
            mouse_pos = pygame.mouse.get_pos()

            title = FONT.render("Wybierz poziom trudności", True, BLACK)
            self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 100))

            easy_btn = pygame.Rect(490, 250, 300, 70)
            hard_btn = pygame.Rect(490, 350, 300, 70)
            self.draw_button("Łatwy", easy_btn, GREEN, DARK_GREEN, mouse_pos)
            self.draw_button("Trudny", hard_btn, (200, 0, 0), (160, 0, 0), mouse_pos)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.change_state(GameState.END)
                    return
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if easy_btn.collidepoint(event.pos):
                        self.hard_mode = False
                        self.change_state(GameState.STARTPAGE)
                        return
                    elif hard_btn.collidepoint(event.pos):
                        self.hard_mode = True
                        self.change_state(GameState.STARTPAGE_HARD_MODE)
                        return
                    
            pygame.display.flip()

    def handle_startpage(self)-> None:
        """Obsługuje stronę rozpoczęcia rozgrywki z wprowadzeniem imienia i paskiem ładowania."""
        
        """inicjalizacja pola tekstowego"""
        input_active = False
        input_rect = pygame.Rect(SCREEN_WIDTH//2 - 200, SCREEN_HEIGHT//2 - 100, 400, 50)
        color_active = pygame.Color('lightskyblue3')
        color_inactive = pygame.Color('gray')
        color = color_inactive
        self.input_text = ''

        """Pętla wprowadzania imienia"""
        name_entered = False
        while self.state == GameState.STARTPAGE and not name_entered:
            mouse_pos = pygame.mouse.get_pos()
            self.screen.fill((240, 250, 240))
            
            title = FONT.render("Wprowadź swoje imię:", True, (50, 100, 50))
            self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, SCREEN_HEIGHT//3 - 50))
            
            pygame.draw.rect(self.screen, color, input_rect, 2, border_radius=10)
            text_surface = FONT.render(self.input_text, True, BLACK)
            self.screen.blit(text_surface, (input_rect.x + 10, input_rect.y + 10))
            
            continue_btn = pygame.Rect(SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2 + 20, 200, 60)
            self.draw_button("Dalej", continue_btn, GREEN, DARK_GREEN, mouse_pos, glow=bool(self.input_text))
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.change_state(GameState.END)
                    return
                    
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if input_rect.collidepoint(event.pos):
                        input_active = True
                        color = color_active
                    else:
                        input_active = False
                        color = color_inactive
                        
                    if continue_btn.collidepoint(event.pos) and self.input_text:
                        self.player_name = self.input_text
                        name_entered = True
                        
                if event.type == pygame.KEYDOWN and input_active:
                    if event.key == pygame.K_RETURN and self.input_text:
                        self.player_name = self.input_text
                        name_entered = True
                    elif event.key == pygame.K_BACKSPACE:
                        self.input_text = self.input_text[:-1]
                    else:
                        if len(self.input_text) < 20:
                            self.input_text += event.unicode
            
            pygame.display.flip()

    
        
        """Faza ładowania po wprowadzeniu imienia"""
        if name_entered:
            self.screen.fill((240, 250, 240))
            
            text = FONT.render(f"Witaj, {self.player_name}! Przygotuj się do gry!", True, BLACK)
            self.screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, SCREEN_HEIGHT//2 - 50))
            pygame.draw.rect(self.screen, (200, 200, 200), (SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT//2 + 50, 300, 20))
            pygame.display.flip()

            for i in range(1, 101):
                pygame.draw.rect(self.screen, GREEN, (SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT//2 + 50, 3 * i, 20))
                pygame.display.flip()
                pygame.time.wait(20)

            pygame.time.wait(500)
            self.change_state(GameState.GAMEPAGE)

    def handle_startpage_hard_mode(self)-> None:
        """Obsługuje stronę rozpoczęcia rozgrywki z wprowadzeniem imienia i paskiem ładowania."""
        
        """inicjalizacja pola tekstowego"""
        input_active = False
        input_rect = pygame.Rect(SCREEN_WIDTH//2 - 200, SCREEN_HEIGHT//2 - 100, 400, 50)
        color_active = pygame.Color('lightskyblue3')
        color_inactive = pygame.Color('gray')
        color = color_inactive
        self.input_text = ''

        """Pętla wprowadzania imienia"""
        name_entered = False
        while self.state == GameState.STARTPAGE_HARD_MODE and not name_entered:
            mouse_pos = pygame.mouse.get_pos()
            self.screen.fill((240, 250, 240))
            
            title = FONT.render("Wprowadź swoje imię:", True, (50, 100, 50))
            self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, SCREEN_HEIGHT//3 - 50))
            
            pygame.draw.rect(self.screen, color, input_rect, 2, border_radius=10)
            text_surface = FONT.render(self.input_text, True, BLACK)
            self.screen.blit(text_surface, (input_rect.x + 10, input_rect.y + 10))
            
            continue_btn = pygame.Rect(SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2 + 20, 200, 60)
            self.draw_button("Dalej", continue_btn, GREEN, DARK_GREEN, mouse_pos, glow=bool(self.input_text))
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.change_state(GameState.END)
                    return
                    
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if input_rect.collidepoint(event.pos):
                        input_active = True
                        color = color_active
                    else:
                        input_active = False
                        color = color_inactive
                        
                    if continue_btn.collidepoint(event.pos) and self.input_text:
                        self.player_name = self.input_text
                        name_entered = True
                        
                if event.type == pygame.KEYDOWN and input_active:
                    if event.key == pygame.K_RETURN and self.input_text:
                        self.player_name = self.input_text
                        name_entered = True
                    elif event.key == pygame.K_BACKSPACE:
                        self.input_text = self.input_text[:-1]
                    else:
                        if len(self.input_text) < 20:
                            self.input_text += event.unicode
            
            pygame.display.flip()

    
        
        """Faza ładowania po wprowadzeniu imienia"""
        if name_entered:
            self.screen.fill((240, 250, 240))
            
            text = FONT.render(f"Witaj, {self.player_name}! Przygotuj się do gry!", True, BLACK)
            self.screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, SCREEN_HEIGHT//2 - 50))
            pygame.draw.rect(self.screen, (200, 200, 200), (SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT//2 + 50, 300, 20))
            pygame.display.flip()

            for i in range(1, 101):
                pygame.draw.rect(self.screen, GREEN, (SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT//2 + 50, 3 * i, 20))
                pygame.display.flip()
                pygame.time.wait(20)

            pygame.time.wait(500)
            self.change_state(GameState.GAMEPAGE_HARD_MODE)


    def handle_instructionpage(self) -> None:
        """Wyświetla ekran z zasadami gry."""
        while self.state == GameState.INSTRUCTIONPAGE:
            self.screen.fill((240, 250, 240))
        
            """Naapis z efektem cienia"""
            title = TITLE_FONT.render("Zasady Gry", True, (50, 100, 50))
            title_shadow = TITLE_FONT.render("Zasady Gry", True, (100, 150, 100))
            self.screen.blit(title_shadow, (SCREEN_WIDTH//2 - title_shadow.get_width()//2 + 3, 100 + 3))
            self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 100))
        
            """Lista zasad"""
            rules_text = [
            "1. Kliknij na mapie województwo, które widzisz na zdjęciu.",
            "2. Masz 3 rundy, aby zdobyć jak najwięcej punktów.",
            "3. Każda poprawna odpowiedź to jeden punkt."
        ]
            
            """Zasady punkt po punkcie"""
            for i, line in enumerate(rules_text):
                text_surface = FONT.render(line, True, BLACK)
                self.screen.blit(text_surface, (SCREEN_WIDTH//2 - text_surface.get_width()//2, 200 + i * 40))
        
            mouse_pos = pygame.mouse.get_pos()
            back_btn = pygame.Rect(SCREEN_WIDTH//2 - 150, 400, 300, 70)
            self.draw_button("Powrót", back_btn, GREEN, DARK_GREEN, mouse_pos)
        
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.change_state(GameState.END)
                    return
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if back_btn.collidepoint(event.pos):
                        self.change_state(GameState.HOMEPAGE)
                        return
        
            pygame.display.flip()
        

    def handle_gamepage(self) -> None:
        """Obsługuje stronę gry (rozgrywkę)."""
        self.current_round = 0
        self.score = 0

        map_widget = self.load_map_widget()
        if not map_widget:
            return

        while self.running and self.current_round < self.total_rounds:
            self.pick_next_image()
            self.run_single_round(map_widget)
            self.current_round += 1

        self.change_state(GameState.RESULTPAGE)

    def handle_gamepage_hard_mode(self) -> None:
        """Obsługuje stronę gry (rozgrywkę)."""
        self.current_round = 0
        self.score = 0

        map_widget = self.load_map_widget()
        if not map_widget:
            return

        while self.running and self.current_round < self.total_rounds:
            self.pick_next_image()
            self.run_single_round_hard_mode(map_widget)
            self.current_round += 1

        self.change_state(GameState.RESULTPAGE)

    def load_map_widget(self) -> None:
        """Wczytuje widget mapy, zwraca obiekt lub None przy błędzie."""
        try:
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            shapefile_path = os.path.join(project_root, '..', 'assets', 'map_assets', 'wojewodztwa.shp')
            if not os.path.exists(shapefile_path):
                shapefile_path = os.path.join(os.path.dirname(__file__), '..', 'assets', 'map_assets', 'wojewodztwa.shp')
            if not os.path.exists(shapefile_path):
                raise FileNotFoundError("Nie znaleziono pliku z mapą województw!")

            return PolandMapWidget(200, 200, 400, 400, shapefile_path)

        except Exception as e:
            print(f"Błąd ładowania mapy: {e}")
            self.screen.fill((240, 240, 240))
            error_text = FONT.render("Błąd ładowania mapy!", True, (255, 0, 0))
            self.screen.blit(error_text, (50, 50))
            pygame.display.flip()
            pygame.time.wait(3000)
            self.change_state(GameState.HOMEPAGE)
            return None

    def run_single_round(self, map_widget) -> None:
        """Prowadzi jedną rundę gry."""
        round_running = True
        while round_running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    self.change_state(GameState.END)
                    return
                klikniete = map_widget.handle_event(event)
                if klikniete:
                    self.sprawdz_odpowiedz(self.current_image, klikniete)
                    round_running = False

            self.screen.fill((240, 240, 240))
            self.draw_header()

            if self.current_image_surface:
                x = SCREEN_WIDTH - self.current_image_surface.get_width() - 50
                y = HEADER_HEIGHT + 50
                self.screen.blit(self.current_image_surface, (x, y))

            map_widget.update()
            map_widget.draw(self.screen)
            pygame.display.flip()

    def run_single_round_hard_mode(self, map_widget) -> None:
        """Prowadzi jedną rundę gry z limitem 5 sekund na odpowiedź."""
        round_running = True
        start_time = pygame.time.get_ticks()  # czas startu w milisekundach
        time_limit = 5000  # 5000 ms = 5 sekund

        while round_running:
            current_time = pygame.time.get_ticks()
            elapsed_time = current_time - start_time

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    self.change_state(GameState.END)
                    return
                klikniete = map_widget.handle_event(event)
                if klikniete:
                    self.sprawdz_odpowiedz(self.current_image, klikniete)
                    round_running = False

            # Sprawdź czy czas się skończył
            if elapsed_time > time_limit:
                round_running = False
                self.sprawdz_odpowiedz(self.current_image, None) 

            self.screen.fill((240, 240, 240))
            self.draw_header()

            if self.current_image_surface:
                x = SCREEN_WIDTH - self.current_image_surface.get_width() - 50
                y = HEADER_HEIGHT + 50
                self.screen.blit(self.current_image_surface, (x, y))

            map_widget.update()
            map_widget.draw(self.screen)

            """Rysuje pasek czasu, licznik"""
        
            remaining_time_sec = max(0, (time_limit - elapsed_time) // 1000)
            timer_text = FONT.render(f"Czas: {remaining_time_sec}s", True, (0, 100, 0))
            self.screen.blit(timer_text, (20, 70))

            pygame.display.flip()

    def sprawdz_odpowiedz(self, zdjecie: str, klikniete_wojewodztwo: str) -> bool:
        """
        Sprawdza, czy kliknięte województwo odpowiada zdjęciu.
        """
        poprawne_wojewodztwo = self.images[zdjecie]
        if klikniete_wojewodztwo.lower() == poprawne_wojewodztwo:
            self.score += 1
            return True
        return False

    def handle_resultpage(self)-> None:
        """Wyświetla wynik końcowy i wraca do strony startowej."""
        self.screen.fill((240, 250, 240))
        result_text = FONT.render(f"Wynik końcowy: {self.score}/{self.total_rounds}", True, (50, 100, 50))
        self.screen.blit(result_text, (SCREEN_WIDTH//2 - result_text.get_width()//2, SCREEN_HEIGHT//2 - 50))

        """ Komentarze do wyniku""" 
        if self.score == self.total_rounds:
            comment = f"Perfekcyjnie, {self.player_name}!"
        elif self.score >= self.total_rounds // 2:
            comment = f"Dobry wynik,{self.player_name}!"
        else:
            comment = f"Spróbuj jeszcze raz, {self.player_name}!"

        comment_text = SMALL_FONT.render(comment, True, (100, 150, 100))
        self.screen.blit(comment_text, (SCREEN_WIDTH//2 - comment_text.get_width()//2, SCREEN_HEIGHT//2 + 20))
        pygame.display.flip()
        pygame.time.wait(3000)
        self.change_state(GameState.HOMEPAGE)

    def change_state(self, new_state: GameState) -> None:
        """Zmienia stan gry na nowy."""
        self.state = new_state
        print('Zmieniono stan')