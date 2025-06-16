"""Moduł gry 'Znajdź Województwo' z wykorzystaniem biblioteki Pygame."""

import sys
import pygame
from game_state import GameState
import os
from map import PolandMapWidget
import random

""" Inicjalizacja Pygame"""
pygame.init()

""" Stałe"""
SCREEN_WIDTH, SCREEN_HEIGHT = 1280, 720
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 200, 0)
DARK_GREEN = (0, 160, 0)
HEADER_HEIGHT = 60

""" Czcionki"""
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
        self.button_glow = 0
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
        self.hard_mode: bool = False
        self.start_time = None

        """Przygotowanie listy plików i miejsca na aktualne zdjęcie"""
        self.image_folder: str = os.path.join(os.path.dirname(__file__), "zdjecia")
        self.image_keys: list[str] = list(self.images.keys())  
        self.current_image: str | None = None                      
        self.current_image_surface: pygame.Surface | None = None              

    def load_images(self) -> None:
        """Ładuje zdjęcia z folderu "zdjecia" """
        folder = os.path.join(os.path.dirname(__file__), "zdjecia")
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
        """ Tło nagłówka"""
        pygame.draw.rect(self.screen, (230, 245, 230), (0, 0, SCREEN_WIDTH, HEADER_HEIGHT))

        """Linia oddzielająca"""
        pygame.draw.line(self.screen, (180, 220, 180), (0, HEADER_HEIGHT), (SCREEN_WIDTH, HEADER_HEIGHT), 2)

        """Licznik rund (lewy górny róg)"""
        round_text = HEADER_FONT.render(f"Runda: {self.current_round + 1}/{self.total_rounds}", True, (0, 100, 0))
        self.screen.blit(round_text, (20, 15))

        """Wynik (prawy górny róg)"""
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
            elif self.state == GameState.HARDMODE_INSTRUCTION:
                self.handle_instructionpage()
            elif self.state == GameState.GAMEPAGE:
                self.handle_gamepage()
            elif self.state == GameState.RESULTPAGE:
                self.handle_resultpage()
            elif self.state == GameState.DIFFICULTY_SELECT:
                self.handle_difficulty_select()
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
            exit_btn = pygame.Rect(490, 350, 300, 70)
            self.draw_button("Start Gry", start_btn, GREEN, DARK_GREEN, mouse_pos, glow=True)
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
                        self.change_state(GameState.HARDMODE_INSTRUCTION)
                        return
                    
            pygame.display.flip()


    def handle_startpage(self)-> None:
        """Obsługuje stronę rozpoczęcia rozgrywki."""
        self.screen.fill((240, 250, 240))

        text = FONT.render("Przygotuj się do gry!", True, BLACK)
        self.screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, SCREEN_HEIGHT//2 - 50))
        pygame.draw.rect(self.screen, (200, 200, 200), (SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT//2 + 50, 300, 20))
        pygame.display.flip()

        for i in range(1, 101):
            pygame.draw.rect(self.screen, GREEN, (SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT//2 + 50, 3 * i, 20))
            pygame.display.flip()
            pygame.time.wait(20)

        pygame.time.wait(500)
        self.change_state(GameState.GAMEPAGE)

    def handle_instructionpage(self) -> None:
        while self.state == GameState.HARDMODE_INSTRUCTION:
            self.screen.fill((240, 250, 240))
            mouse_pos = pygame.mouse.get_pos()

            lines = [ 
                "Tryb Trudny:",
                "- Masz 10 sekund na każdą rundę.",
                "- Kliknij na poprawne województwo jak najszybciej!",
                "",
                "Powodzenia!"
            ]

            for i, line in enumerate(lines):
                txt = SMALL_FONT.render(line, True, BLACK)
                self.screen.blit(txt, (SCREEN_WIDTH//2 - txt.get_width()//2, 100 + i*40))

            play_btn = pygame.Rect(490, 400, 300, 70)
            self.draw_button("Graj", play_btn, GREEN, DARK_GREEN, mouse_pos)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.change_state(GameState.END)
                    return
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if play_btn.collidepoint(event.pos):
                        self.change_state(GameState.GAMEPAGE)
                        return
                    
        pygame.display.flip()


    def handle_gamepage(self) -> None:
        """Obsługuje stronę gry (rozgrywkę). """
        self.current_round = 0
        self.score = 0
        start_time = pygame.time.get_ticks()
        map_widget = PolandMapWidget(200, 200, 400, 400, 'map_assets/wojewodztwa.shp')  # TODO: Prawdziwa logika gry
        while self.running and self.current_round < self.total_rounds:
            self.pick_next_image()
            round_running = True
            while round_running:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False
                        self.change_state(GameState.END)
                        return
                    else:
                        klikniete_wojewodztwo = map_widget.handle_event(event)
                        if klikniete_wojewodztwo:
                            self.sprawdz_odpowiedz(self.current_image, klikniete_wojewodztwo)
                            round_running = False
                    if self.hard_mode:
                        elapsed_time = (pygame.time.get_ticks() - start_time) / 1000
                        if elapsed_time >= 10:
                            round_running = False  # kończymy rundę bez punktu
                self.draw_header()
                self.screen.fill((240, 240, 240))
                if self.current_image_surface:
                    x_pos = SCREEN_WIDTH - self.current_image_surface.get_width() - 50
                    y_pos = HEADER_HEIGHT + 50
                    self.screen.blit(self.current_image_surface, (x_pos, y_pos))
                map_widget.update()
                map_widget.draw(self.screen)
                if self.hard_mode:
                    remaining = max(0, 10 - int((pygame.time.get_ticks() - start_time) / 1000))
                    timer_text = FONT.render(f"Czas: {remaining}", True, (200, 0, 0))
                    self.screen.blit(timer_text, (50, HEADER_HEIGHT + 20))
                
                pygame.display.flip()
            self.current_round += 1
        self.change_state(GameState.RESULTPAGE)
 

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
            comment = "Perfekcyjnie!"
        elif self.score >= self.total_rounds // 2:
            comment = "Dobry wynik!"
        else:
            comment = "Spróbuj jeszcze raz!"

        comment_text = SMALL_FONT.render(comment, True, (100, 150, 100))
        self.screen.blit(comment_text, (SCREEN_WIDTH//2 - comment_text.get_width()//2, SCREEN_HEIGHT//2 + 20))
        pygame.display.flip()
        pygame.time.wait(3000)
        self.change_state(GameState.HOMEPAGE)
        
    def change_state(self, new_state: GameState) -> None:
        """Zmienia stan gry na nowy."""
        self.state = new_state
        print('Zmieniono stan')